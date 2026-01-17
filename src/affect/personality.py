"""人格配置管理

本模块负责加载和管理AICO的人格配置。
通过YAML配置文件，可以在不修改代码的情况下调整AICO的性格特征。

人格参数影响：
- 情绪敏感度（emotional_gain）
- 情绪恢复速度（recovery_rate）
- 表达强度（expressiveness）
- 情感惯性（inertia）
- 融合权重（fusion_weights）
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Personality:
    """人格配置管理器
    
    示例用法：
        personality = Personality("config/personality.yaml")
        gain = personality.emotional_gain
        weights = personality.fusion_weights
    """
    
    def __init__(self, config_path: str = "config/personality.yaml"):
        """加载人格配置
        
        Args:
            config_path: YAML配置文件路径
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: 配置文件格式错误
        """
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
            self.cfg = self._default_config()
        else:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self.cfg = config.get('personality', {})
                logger.info(f"成功加载人格配置: {self.cfg.get('name', 'Unknown')}")
            except yaml.YAMLError as e:
                logger.error(f"配置文件格式错误: {e}")
                raise
    
    def _default_config(self) -> Dict[str, Any]:
        """默认人格配置（当配置文件不存在时使用）"""
        return {
            "name": "AICO_Default",
            "version": "1.0",
            "emotional_gain": 0.7,
            "recovery_rate": 0.01,
            "expressiveness": 0.8,
            "baseline_valence": 0.2,
            "baseline_arousal": 0.4,
            "baseline_dominance": 0.1,
            "inertia_valence": 0.85,
            "inertia_arousal": 0.75,
            "inertia_dominance": 0.90,
            "fusion_weights": {
                "vision": 0.4,
                "audio": 0.3,
                "language": 0.3
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值，如果不存在则返回默认值
        """
        return self.cfg.get(key, default)
    
    @property
    def name(self) -> str:
        """人格名称"""
        return self.cfg.get('name', 'Unknown')
    
    @property
    def emotional_gain(self) -> float:
        """情绪敏感度 [0, 2]
        
        - 值越大，情绪变化越剧烈
        - 典型值：0.5（迟钝）~ 1.0（正常）~ 1.5（敏感）
        """
        return self.cfg.get('emotional_gain', 0.7)
    
    @property
    def recovery_rate(self) -> float:
        """情绪恢复速度 [0, 1]
        
        - 值越大，情绪恢复到基线越快
        - 典型值：0.005（慢）~ 0.01（正常）~ 0.02（快）
        """
        return self.cfg.get('recovery_rate', 0.01)
    
    @property
    def expressiveness(self) -> float:
        """表达强度 [0, 1]
        
        - 值越大，情绪外显越明显
        - 影响表达指令的能量等级
        """
        return self.cfg.get('expressiveness', 0.8)
    
    @property
    def baseline_valence(self) -> float:
        """愉悦度基线 [-1, 1]"""
        return self.cfg.get('baseline_valence', 0.2)
    
    @property
    def baseline_arousal(self) -> float:
        """激活度基线 [0, 1]"""
        return self.cfg.get('baseline_arousal', 0.4)
    
    @property
    def baseline_dominance(self) -> float:
        """主导度基线 [-1, 1]"""
        return self.cfg.get('baseline_dominance', 0.1)
    
    @property
    def inertia_valence(self) -> float:
        """愉悦度惯性系数 [0, 1]"""
        return self.cfg.get('inertia_valence', 0.85)
    
    @property
    def inertia_arousal(self) -> float:
        """激活度惯性系数 [0, 1]"""
        return self.cfg.get('inertia_arousal', 0.75)
    
    @property
    def inertia_dominance(self) -> float:
        """主导度惯性系数 [0, 1]"""
        return self.cfg.get('inertia_dominance', 0.90)
    
    @property
    def fusion_weights(self) -> Dict[str, float]:
        """多模态融合权重
        
        Returns:
            字典，键为模态名称（vision/audio/language），值为权重
        """
        return self.cfg.get('fusion_weights', {
            'vision': 0.4,
            'audio': 0.3,
            'language': 0.3
        })
    
    def save(self, path: Optional[str] = None):
        """保存当前配置到文件
        
        Args:
            path: 保存路径，默认使用加载路径
        """
        save_path = Path(path) if path else self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump({'personality': self.cfg}, f, 
                     allow_unicode=True, default_flow_style=False)
        logger.info(f"配置已保存到: {save_path}")
    
    def __repr__(self) -> str:
        return f"Personality(name={self.name}, gain={self.emotional_gain})"
