"""
情感检测结果数据库模块
用于存储详细的检测结果、VAD值、情感分布等信息
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


class EmotionDatabase:
    """情感检测结果数据库"""
    
    def __init__(self, db_path: str = "test_outputs/emotion_detection.db"):
        """初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # 使用字典访问
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()
        
        # 检测结果主表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                image_file TEXT NOT NULL,
                expected_category TEXT,
                detected_emotion TEXT NOT NULL,
                confidence REAL NOT NULL,
                detector_type TEXT NOT NULL,
                face_x INTEGER,
                face_y INTEGER,
                face_w INTEGER,
                face_h INTEGER,
                valence REAL NOT NULL,
                arousal REAL NOT NULL,
                dominance REAL NOT NULL,
                source TEXT,
                is_correct BOOLEAN,
                output_image TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 情感概率分布表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotion_probabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id INTEGER NOT NULL,
                emotion TEXT NOT NULL,
                probability REAL NOT NULL,
                FOREIGN KEY (detection_id) REFERENCES detections(id)
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_detections_timestamp 
            ON detections(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_detections_emotion 
            ON detections(detected_emotion)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_detections_expected 
            ON detections(expected_category)
        """)
        
        self.conn.commit()
    
    def save_detection(
        self,
        image_file: str,
        detected_emotion: str,
        confidence: float,
        detector_type: str,
        face_box: tuple,
        vad_values: tuple,
        all_emotions: Dict[str, float],
        expected_category: Optional[str] = None,
        source: str = "vision",
        output_image: Optional[str] = None
    ) -> int:
        """保存检测结果
        
        Args:
            image_file: 图片文件名
            detected_emotion: 检测到的情感
            confidence: 置信度
            detector_type: 检测器类型
            face_box: 人脸框 (x, y, w, h)
            vad_values: VAD值 (valence, arousal, dominance)
            all_emotions: 所有情感概率字典
            expected_category: 预期类别
            source: 数据源
            output_image: 输出图片路径
        
        Returns:
            detection_id: 插入记录的ID
        """
        cursor = self.conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        x, y, w, h = face_box
        valence, arousal, dominance = vad_values
        
        # 判断检测是否正确
        is_correct = None
        if expected_category:
            is_correct = (detected_emotion.lower() == expected_category.lower())
        
        # 插入主记录
        cursor.execute("""
            INSERT INTO detections (
                timestamp, image_file, expected_category, detected_emotion,
                confidence, detector_type, face_x, face_y, face_w, face_h,
                valence, arousal, dominance, source, is_correct, output_image
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, image_file, expected_category, detected_emotion,
            confidence, detector_type, x, y, w, h,
            valence, arousal, dominance, source, is_correct, output_image
        ))
        
        detection_id = cursor.lastrowid
        
        # 插入情感概率
        for emotion, probability in all_emotions.items():
            cursor.execute("""
                INSERT INTO emotion_probabilities (detection_id, emotion, probability)
                VALUES (?, ?, ?)
            """, (detection_id, emotion, probability))
        
        self.conn.commit()
        return detection_id
    
    def get_detection(self, detection_id: int) -> Optional[Dict[str, Any]]:
        """获取检测结果
        
        Args:
            detection_id: 检测记录ID
        
        Returns:
            检测结果字典，包含情感概率
        """
        cursor = self.conn.cursor()
        
        # 获取主记录
        cursor.execute("SELECT * FROM detections WHERE id = ?", (detection_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        result = dict(row)
        
        # 获取情感概率
        cursor.execute("""
            SELECT emotion, probability 
            FROM emotion_probabilities 
            WHERE detection_id = ?
            ORDER BY probability DESC
        """, (detection_id,))
        
        result['emotion_probabilities'] = {
            row['emotion']: row['probability']
            for row in cursor.fetchall()
        }
        
        return result
    
    def get_recent_detections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的检测结果
        
        Args:
            limit: 返回记录数
        
        Returns:
            检测结果列表
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM detections 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self, emotion: Optional[str] = None) -> Dict[str, Any]:
        """获取统计信息
        
        Args:
            emotion: 筛选特定情感（可选）
        
        Returns:
            统计信息字典
        """
        cursor = self.conn.cursor()
        
        # 总体统计
        if emotion:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                    AVG(confidence) as avg_confidence,
                    AVG(valence) as avg_valence,
                    AVG(arousal) as avg_arousal,
                    AVG(dominance) as avg_dominance
                FROM detections
                WHERE detected_emotion = ?
            """, (emotion,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                    AVG(confidence) as avg_confidence,
                    AVG(valence) as avg_valence,
                    AVG(arousal) as avg_arousal,
                    AVG(dominance) as avg_dominance
                FROM detections
            """)
        
        row = cursor.fetchone()
        stats = dict(row)
        
        # 计算准确率
        if stats['total'] > 0 and stats['correct'] is not None:
            stats['accuracy'] = stats['correct'] / stats['total']
        else:
            stats['accuracy'] = None
        
        # 各情感统计
        cursor.execute("""
            SELECT 
                detected_emotion,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM detections
            GROUP BY detected_emotion
            ORDER BY count DESC
        """)
        
        stats['emotion_counts'] = [dict(row) for row in cursor.fetchall()]
        
        # 检测器统计
        cursor.execute("""
            SELECT 
                detector_type,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM detections
            GROUP BY detector_type
        """)
        
        stats['detector_stats'] = [dict(row) for row in cursor.fetchall()]
        
        return stats
    
    def export_to_json(self, output_path: str, limit: Optional[int] = None):
        """导出数据到JSON
        
        Args:
            output_path: 输出文件路径
            limit: 限制导出记录数（可选）
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM detections ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        detections = []
        
        for row in cursor.fetchall():
            detection = dict(row)
            
            # 获取情感概率
            cursor.execute("""
                SELECT emotion, probability 
                FROM emotion_probabilities 
                WHERE detection_id = ?
            """, (detection['id'],))
            
            detection['emotion_probabilities'] = {
                r['emotion']: r['probability']
                for r in cursor.fetchall()
            }
            
            detections.append(detection)
        
        # 写入JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detections, f, indent=2, ensure_ascii=False)
    
    def clear_old_records(self, days: int = 30):
        """清理旧记录
        
        Args:
            days: 保留最近N天的记录
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            DELETE FROM emotion_probabilities
            WHERE detection_id IN (
                SELECT id FROM detections
                WHERE datetime(created_at) < datetime('now', '-' || ? || ' days')
            )
        """, (days,))
        
        cursor.execute("""
            DELETE FROM detections
            WHERE datetime(created_at) < datetime('now', '-' || ? || ' days')
        """, (days,))
        
        self.conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
