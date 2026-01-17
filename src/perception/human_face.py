"""视觉情感感知模块 - MediaPipe完整版

采用三层架构进行人脸情感识别：
1. MediaPipe Face Detection - Google BlazeFace模型（轻量、高速、准确）
2. MediaPipe Face Landmarker - 468个3D人脸特征点 + 52个面部表情混合形状
3. FER (Facial Expression Recognition) - CNN情感识别模型

设计理念（基于MediaPipe最佳实践）：
- Calculator节点模式：检测器、特征点和分析器解耦
- 流式处理：支持实时视频流和静态图片
- GPU加速：可选的GPU计算支持
- 性能追踪：记录关键节点耗时
- 优雅降级：MediaPipe → Haar Cascade自动切换

MediaPipe管道流程：
  Input Frame → Preprocess → Face Detection → Face Landmarks (468 points) → 
  Blendshapes (52 expressions) → Emotion Analysis → VAD Mapping → Percept

参考资料：
- MediaPipe Framework: https://viso.ai/computer-vision/mediapipe/
- MediaPipe Face Detection: https://ai.google.dev/edge/mediapipe/solutions/vision/face_detector?hl=zh-cn
- MediaPipe Face Landmarker: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/python?hl=zh-cn
- FER: https://github.com/justinshenk/fer
- VAD Model: Russell's Circumplex Model of Affect
"""

import cv2
import numpy as np
from typing import Optional, List, Tuple
import logging
import os
from pathlib import Path

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision as mp_vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None
    logger = logging.getLogger(__name__)
    logger.warning("MediaPipe not available, falling back to Haar Cascade")

from fer.fer import FER

from ..affect.state import Percept, EmotionCategory, emotion_to_vad
import time
from functools import wraps

logger = logging.getLogger(__name__)


def performance_trace(func):
    """性能追踪装饰器（MediaPipe Tracer模式）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        logger.debug(f"{func.__name__} executed in {elapsed*1000:.2f}ms")
        return result
    return wrapper

# 项目根目录下的models文件夹
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"


class VisionPerceptor:
    """视觉情感感知器
    
    基于FER库进行人脸检测和情感识别。
    
    特性：
    - 自动人脸检测
    - 7种基础情感识别（angry/disgust/fear/happy/sad/surprise/neutral）
    - 情感到VAD空间的映射
    - 支持实时摄像头和静态图片
    
    示例用法：
        perceptor = VisionPerceptor(camera_id=0)
        percept = perceptor.perceive()
        if percept:
            print(f"检测到情感: {percept.valence_hint}, {percept.arousal_hint}")
        perceptor.release()
    """
    
    # 情感类别到VAD的映射（基于Russell圆环模型）
    # 这些映射值来自心理学研究，表示不同情感在VAD空间中的典型位置
    EMOTION_TO_VAD = {
        'happy': (0.8, 0.7, 0.5),      # 高愉悦、高激活、略主动
        'sad': (-0.7, 0.3, -0.3),      # 低愉悦、低激活、略被动
        'angry': (-0.8, 0.9, 0.7),     # 低愉悦、高激活、很主动
        'neutral': (0.0, 0.4, 0.0),    # 中性愉悦、略低激活、中性主动
        'surprise': (0.4, 0.9, -0.2),  # 略正愉悦、很高激活、略被动
        'fear': (-0.6, 0.8, -0.5),     # 低愉悦、高激活、被动
        'disgust': (-0.6, 0.5, 0.2),   # 低愉悦、中激活、略主动
    }
    
    def __init__(
        self,
        camera_id: int = 0,
        use_mediapipe: bool = True,
        use_landmarks: bool = True,
        min_confidence: float = 0.3,
        detection_confidence: float = 0.5
    ):
        """初始化视觉感知器
        
        Args:
            camera_id: 摄像头设备ID（0为默认摄像头）
            use_mediapipe: 是否使用MediaPipe进行人脸检测（推荐）
            use_landmarks: 是否使用MediaPipe Face Landmarker检测特征点和表情
            min_confidence: 最低情感置信度阈值
            detection_confidence: MediaPipe人脸检测置信度阈值
        """
        self.camera_id = camera_id
        self.min_confidence = min_confidence
        self.detection_confidence = detection_confidence
        self.cap = None
        self.use_mediapipe = use_mediapipe and MEDIAPIPE_AVAILABLE
        self.use_landmarks = use_landmarks and MEDIAPIPE_AVAILABLE
        self.face_landmarker = None
        
        # 初始化MediaPipe人脸检测
        if self.use_mediapipe:
            logger.info("Using MediaPipe Face Detection")
            try:
                # 使用MediaPipe的FaceDetection（legacy solution）
                mp_face_detection = mp.solutions.face_detection
                self.face_detector = mp_face_detection.FaceDetection(
                    min_detection_confidence=detection_confidence
                )
                self.mp_face_detection = mp_face_detection
            except AttributeError:
                # 如果solutions不可用，尝试使用新的tasks API
                logger.warning("MediaPipe solutions API not available, trying tasks API")
                try:
                    # 尝试使用MediaPipe官方模型 (优先级顺序)
                    model_candidates = [
                        MODELS_DIR / 'blaze_face_short_range.tflite',  # Google官方轻量模型
                        MODELS_DIR / 'MediaPipeFaceDetector.tflite',   # 本地模型
                        MODELS_DIR / 'face_detection.tflite',          # 通用名称
                    ]
                    
                    model_path = None
                    for candidate in model_candidates:
                        if candidate.exists():
                            model_path = candidate
                            break
                    
                    if model_path is None:
                        raise FileNotFoundError("No MediaPipe face detection model found. Run download_mediapipe_models.sh")
                    
                    logger.info(f"Loading MediaPipe model from: {model_path}")
                    
                    # 创建FaceDetector的选项
                    base_options = python.BaseOptions(
                        model_asset_path=str(model_path)
                    )
                    options = mp_vision.FaceDetectorOptions(
                        base_options=base_options,
                        min_detection_confidence=detection_confidence,
                        running_mode=mp_vision.RunningMode.IMAGE
                    )
                    self.face_detector = mp_vision.FaceDetector.create_from_options(options)
                    self.mp_face_detection = None
                    self.use_new_api = True
                    logger.info(f"✓ MediaPipe Face Detector initialized with {model_path.name}")
                except Exception as e:
                    logger.error(f"Failed to initialize MediaPipe: {e}")
                    logger.info("Falling back to Haar Cascade")
                    self.use_mediapipe = False
                    self.face_detector = None
                    self.use_new_api = False
        else:
            logger.info("Using Haar Cascade Face Detection")
            self.face_detector = None
            self.use_new_api = False
        
        # 初始化MediaPipe FaceLandmarker（用于特征点和表情检测）
        if self.use_landmarks:
            logger.info("Initializing MediaPipe Face Landmarker")
            try:
                # 查找face_landmarker模型
                landmarker_candidates = [
                    MODELS_DIR / 'face_landmarker.task',
                    MODELS_DIR / 'face_landmarker_v2_with_blendshapes.task',
                ]
                
                landmarker_model_path = None
                for candidate in landmarker_candidates:
                    if candidate.exists():
                        landmarker_model_path = candidate
                        break
                
                if landmarker_model_path:
                    logger.info(f"Loading Face Landmarker model from: {landmarker_model_path}")
                    base_options = python.BaseOptions(
                        model_asset_path=str(landmarker_model_path)
                    )
                    landmarker_options = mp_vision.FaceLandmarkerOptions(
                        base_options=base_options,
                        running_mode=mp_vision.RunningMode.IMAGE,
                        num_faces=5,  # 支持检测最多5张人脸
                        min_face_detection_confidence=detection_confidence,
                        min_face_presence_confidence=0.5,
                        min_tracking_confidence=0.5,
                        output_face_blendshapes=True,  # 输出面部表情混合形状
                        output_facial_transformation_matrixes=False
                    )
                    self.face_landmarker = mp_vision.FaceLandmarker.create_from_options(landmarker_options)
                    logger.info(f"✓ Face Landmarker initialized with {landmarker_model_path.name}")
                else:
                    logger.warning("Face Landmarker model not found, feature disabled")
                    logger.info("Download from: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task")
                    self.use_landmarks = False
            except Exception as e:
                logger.error(f"Face Landmarker initialization failed: {e}")
                self.use_landmarks = False
        
        # 初始化FER情感识别器（不使用其人脸检测功能）
        try:
            logger.info("Initializing FER emotion detector")
            self.emotion_detector = FER(mtcnn=False)
        except Exception as e:
            logger.error(f"FER initialization failed: {e}")
            raise
        
        logger.info(f"Vision perceptor initialized (camera_id={camera_id}, mediapipe={self.use_mediapipe}, landmarks={self.use_landmarks})")
    
    def _open_camera(self):
        """打开摄像头（延迟初始化）"""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                raise RuntimeError(f"Cannot open camera {self.camera_id}")
            logger.info(f"Camera {self.camera_id} opened")
    
    @staticmethod
    def _preprocess_frame(frame: np.ndarray) -> np.ndarray:
        """预处理输入帧（MediaPipe最佳实践）
        
        Args:
            frame: BGR格式的输入图像
            
        Returns:
            预处理后的图像
            
        优化措施：
        - 自动调整图像大小（避免过大图像影响性能）
        - 颜色空间转换准备
        """
        h, w = frame.shape[:2]
        max_dimension = 1280  # MediaPipe推荐的最大尺寸
        
        if max(h, w) > max_dimension:
            scale = max_dimension / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
            logger.debug(f"Frame resized from {w}x{h} to {new_w}x{new_h}")
        
        return frame
    
    @performance_trace
    def _detect_faces_mediapipe(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """使用MediaPipe检测人脸（优化版）
        
        采用MediaPipe计算图模式：
        Input → RGB Conversion → MediaPipe Detector → Bounding Box Extraction
        
        Args:
            frame: 输入图像（BGR格式）
        
        Returns:
            人脸框列表 [(x, y, w, h), ...]
        """
        # 转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 检查是使用哪个API
        if hasattr(self, 'use_new_api') and self.use_new_api:
            # 使用新的tasks API
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.face_detector.detect(mp_image)
            
            faces = []
            if detection_result.detections:
                h, w, _ = frame.shape
                for detection in detection_result.detections:
                    bbox = detection.bounding_box
                    x = int(bbox.origin_x)
                    y = int(bbox.origin_y)
                    width = int(bbox.width)
                    height = int(bbox.height)
                    
                    # 确保边界在图像范围内
                    x = max(0, x)
                    y = max(0, y)
                    width = min(width, w - x)
                    height = min(height, h - y)
                    
                    faces.append((x, y, width, height))
        else:
            # 使用legacy solutions API
            results = self.face_detector.process(rgb_frame)
            
            faces = []
            if results.detections:
                h, w, _ = frame.shape
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    
                    # 确保边界在图像范围内
                    x = max(0, x)
                    y = max(0, y)
                    width = min(width, w - x)
                    height = min(height, h - y)
                    
                    faces.append((x, y, width, height))
        
        return faces
    
    @performance_trace
    def _detect_faces_haar(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """使用Haar Cascade检测人脸（优化版）
        
        优化参数（基于OpenCV最佳实践）：
        - scaleFactor: 1.1（平衡速度和准确度）
        - minNeighbors: 4（减少误检）
        - minSize: (30, 30)（过滤小人脸）
        
        Args:
            frame: 输入图像（BGR格式）
        
        Returns:
            人脸框列表 [(x, y, w, h), ...]
        """
        # 加载Haar Cascade（如果有本地模型）
        cascade_path = MODELS_DIR / "haarcascade_frontalface_default.xml"
        if cascade_path.exists():
            face_cascade = cv2.CascadeClassifier(str(cascade_path))
        else:
            # 使用OpenCV内置的
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
    
    @performance_trace
    def _analyze_face_landmarks(self, frame: np.ndarray, max_faces: int = 1) -> Optional[List[dict]]:
        """使用MediaPipe FaceLandmarker分析人脸特征点和表情（支持多人脸）
        
        返回每张人脸的468个3D特征点和52个面部表情混合形状（blendshapes）
        
        Args:
            frame: 输入图像（BGR格式）
            max_faces: 最大检测人脸数（默认1）
        
        Returns:
            人脸数据列表，每个字典包含：
            - 'landmarks': List of 468 face landmarks (x, y, z)
            - 'blendshapes': Dict of 52 facial expression coefficients
            - 'detection_confidence': 检测置信度
            如果失败返回 None
        """
        if not self.use_landmarks or self.face_landmarker is None:
            return None
        
        try:
            # 转换为RGB（MediaPipe要求）
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # 执行人脸特征点检测
            result = self.face_landmarker.detect(mp_image)
            
            if not result.face_landmarks:
                logger.debug("No face landmarks detected")
                return None
            
            # 处理所有检测到的人脸（最多max_faces个）
            all_faces_data = []
            num_faces = min(len(result.face_landmarks), max_faces)
            
            for face_idx in range(num_faces):
                landmarks = result.face_landmarks[face_idx]
                
                # 提取特征点坐标
                landmarks_list = []
                for landmark in landmarks:
                    landmarks_list.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z if hasattr(landmark, 'z') else 0.0
                    })
                
                # 提取混合形状（blendshapes，表示面部表情）
                blendshapes_dict = {}
                if result.face_blendshapes and face_idx < len(result.face_blendshapes):
                    for category in result.face_blendshapes[face_idx]:
                        blendshapes_dict[category.category_name] = category.score
                
                all_faces_data.append({
                    'landmarks': landmarks_list,
                    'blendshapes': blendshapes_dict,
                    'num_landmarks': len(landmarks_list),
                    'num_blendshapes': len(blendshapes_dict),
                    'face_index': face_idx
                })
            
            return all_faces_data
        
        except Exception as e:
            logger.error(f"Face landmarks analysis failed: {e}")
            return None
    
    @performance_trace
    def perceive(self, frame: Optional[np.ndarray] = None) -> Optional[Percept]:
        """感知人脸情感（MediaPipe完整管道）
        
        处理流程（Calculator Graph模式）：
        1. 输入获取（Camera/File）
        2. 帧预处理（Resize/Normalize）
        3. 人脸检测（MediaPipe/Haar）
        4. 人脸特征点检测（468 landmarks + 52 blendshapes）
        5. 人脸裁剪（ROI Extraction）
        6. 情感分析（FER CNN）
        7. VAD映射（Emotion → VAD）
        8. Percept构建（Output with landmarks）
        
        Args:
            frame: 可选的输入帧。如果不提供，则从摄像头读取
        
        Returns:
            Percept对象，如果检测失败则返回None
        """
        # Calculator 1: 输入获取
        if frame is None:
            self._open_camera()
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to read frame from camera")
                return None
        
        # Calculator 2: 帧预处理
        frame = self._preprocess_frame(frame)
        
        # Calculator 3: 人脸检测
        if self.use_mediapipe:
            faces = self._detect_faces_mediapipe(frame)
        else:
            faces = self._detect_faces_haar(frame)
        
        if not faces:
            logger.debug("No faces detected")
            return None
        
        # 取第一张脸（主要人脸）
        x, y, w, h = faces[0]
        
        # Calculator 3.5: 人脸特征点和表情分析（MediaPipe FaceLandmarker）
        landmarks_data = None
        if self.use_landmarks:
            all_landmarks = self._analyze_face_landmarks(frame, max_faces=1)
            if all_landmarks and len(all_landmarks) > 0:
                landmarks_data = all_landmarks[0]  # 只取第一张脸
                logger.debug(f"Detected {landmarks_data['num_landmarks']} landmarks, {landmarks_data['num_blendshapes']} blendshapes")
        
        # Calculator 4: 裁剪人脸区域
        face_img = frame[y:y+h, x:x+w]
        
        # Calculator 5: 使用FER分析情感
        try:
            emotions_list = self.emotion_detector.detect_emotions(face_img)
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            return None
        
        # 如果FER没有检测到情感（但MediaPipe检测到了人脸）
        if not emotions_list:
            logger.debug("FER could not detect emotions in face region")
            # 尝试在全图上检测
            try:
                emotions_list = self.emotion_detector.detect_emotions(frame)
            except:
                return None
            
            if not emotions_list:
                return None
        
        # 取第一个结果
        face_data = emotions_list[0]
        emotions = face_data['emotions']
        
        # 找到主导情感
        dominant_emotion = max(emotions, key=emotions.get)
        confidence = emotions[dominant_emotion]
        
        # 如果置信度太低，忽略
        if confidence < self.min_confidence:
            logger.debug(f"Confidence too low: {confidence:.2f} < {self.min_confidence}")
            return None
        
        # Calculator 6: 映射到VAD空间
        v, a, d = self.EMOTION_TO_VAD.get(
            dominant_emotion,
            (0.0, 0.5, 0.0)  # 默认中性
        )
        
        # Calculator 7: 创建Percept对象（包含特征点和表情数据）
        metadata = {
            "dominant_emotion": dominant_emotion,
            "all_emotions": emotions,
            "bounding_box": [x, y, w, h],
            "num_faces": len(faces),
            "detector": "mediapipe" if self.use_mediapipe else "haar"
        }
        
        # 添加特征点和混合形状数据
        if landmarks_data:
            metadata["face_landmarks"] = landmarks_data['landmarks']
            metadata["face_blendshapes"] = landmarks_data['blendshapes']
            metadata["num_landmarks"] = landmarks_data['num_landmarks']
            metadata["num_blendshapes"] = landmarks_data['num_blendshapes']
        
        percept = Percept(
            source="vision",
            valence_hint=v,
            arousal_hint=a,
            dominance_hint=d,
            confidence=confidence,
            metadata=metadata
        )
        
        logger.debug(f"Detected emotion: {dominant_emotion} (conf: {confidence:.2f})")
        return percept
    
    @performance_trace
    def perceive_all_faces(self, frame: Optional[np.ndarray] = None, max_faces: int = 5) -> List[Optional[Percept]]:
        """感知所有人脸的情感（多人脸版本）
        
        处理流程（支持多人脸）：
        1. 输入获取（Camera/File）
        2. 帧预处理（Resize/Normalize）
        3. 人脸检测（MediaPipe/Haar）- 检测所有人脸
        4. 人脸特征点检测（所有人脸的468 landmarks + 52 blendshapes）
        5. 逐个分析每张人脸的情感
        6. 返回所有人脸的Percept列表
        
        Args:
            frame: 可选的输入帧。如果不提供，则从摄像头读取
            max_faces: 最大检测人脸数（默认5）
        
        Returns:
            Percept对象列表，每个对象对应一张人脸
        """
        # Calculator 1: 输入获取
        if frame is None:
            self._open_camera()
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to read frame from camera")
                return []
        
        # Calculator 2: 帧预处理
        frame = self._preprocess_frame(frame)
        
        # Calculator 3: 人脸检测（检测所有人脸）
        if self.use_mediapipe:
            faces = self._detect_faces_mediapipe(frame)
        else:
            faces = self._detect_faces_haar(frame)
        
        if not faces:
            logger.debug("No faces detected")
            return []
        
        # 限制检测人脸数
        faces = faces[:max_faces]
        logger.info(f"Detected {len(faces)} faces")
        
        # Calculator 3.5: 获取所有人脸的特征点和表情（批量）
        all_landmarks_data = None
        if self.use_landmarks:
            all_landmarks_data = self._analyze_face_landmarks(frame, max_faces=len(faces))
        
        # Calculator 4-7: 逐个处理每张人脸
        percepts = []
        for face_idx, (x, y, w, h) in enumerate(faces):
            # 裁剪人脸区域
            face_img = frame[y:y+h, x:x+w]
            
            # 使用FER分析情感
            try:
                emotions_list = self.emotion_detector.detect_emotions(face_img)
            except Exception as e:
                logger.error(f"Emotion detection failed for face {face_idx}: {e}")
                percepts.append(None)
                continue
            
            # 如果FER没有检测到情感
            if not emotions_list:
                logger.debug(f"FER could not detect emotions for face {face_idx}")
                percepts.append(None)
                continue
            
            # 取第一个结果
            face_data = emotions_list[0]
            emotions = face_data['emotions']
            
            # 找到主导情感
            dominant_emotion = max(emotions, key=emotions.get)
            confidence = emotions[dominant_emotion]
            
            # 如果置信度太低，忽略
            if confidence < self.min_confidence:
                logger.debug(f"Face {face_idx}: Confidence too low: {confidence:.2f} < {self.min_confidence}")
                percepts.append(None)
                continue
            
            # 映射到VAD空间
            v, a, d = self.EMOTION_TO_VAD.get(
                dominant_emotion,
                (0.0, 0.5, 0.0)  # 默认中性
            )
            
            # 创建Percept对象（包含特征点和表情数据）
            metadata = {
                "dominant_emotion": dominant_emotion,
                "all_emotions": emotions,
                "bounding_box": [x, y, w, h],
                "face_index": face_idx,
                "total_faces": len(faces),
                "detector": "mediapipe" if self.use_mediapipe else "haar"
            }
            
            # 添加特征点和混合形状数据（如果有）
            if all_landmarks_data and face_idx < len(all_landmarks_data):
                landmarks_data = all_landmarks_data[face_idx]
                metadata["face_landmarks"] = landmarks_data['landmarks']
                metadata["face_blendshapes"] = landmarks_data['blendshapes']
                metadata["num_landmarks"] = landmarks_data['num_landmarks']
                metadata["num_blendshapes"] = landmarks_data['num_blendshapes']
            
            percept = Percept(
                source="vision",
                valence_hint=v,
                arousal_hint=a,
                dominance_hint=d,
                confidence=confidence,
                metadata=metadata
            )
            
            logger.debug(f"Face {face_idx}: {dominant_emotion} (conf: {confidence:.2f})")
            percepts.append(percept)
        
        return percepts
    
    def perceive_from_image(self, image_path: str) -> Optional[Percept]:
        """从图片文件感知情感
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            Percept对象，如果没有检测到人脸则返回None
        """
        frame = cv2.imread(image_path)
        if frame is None:
            logger.error(f"无法读取图片: {image_path}")
            return None
        
        return self.perceive(frame)
    
    def batch_perceive(
        self,
        frames: List[np.ndarray]
    ) -> List[Optional[Percept]]:
        """批量处理多帧图像（提升性能）
        
        Args:
            frames: 图像列表
        
        Returns:
            Percept对象列表
        """
        results = []
        for frame in frames:
            percept = self.perceive(frame)
            results.append(percept)
        return results
    
    def get_dominant_emotion_str(self, frame: Optional[np.ndarray] = None) -> str:
        """便捷方法：直接获取主导情感字符串
        
        Args:
            frame: 可选的输入图片
        
        Returns:
            情感名称字符串，如 "happy", "sad" 等
        """
        percept = self.perceive(frame)
        if percept and percept.metadata:
            return percept.metadata.get('dominant_emotion', 'unknown')
        return 'none'
    
    def release(self):
        """释放摄像头资源"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("摄像头已释放")
    
    def __enter__(self):
        """支持上下文管理器"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出时自动释放资源"""
        self.release()
        return False
    
    def __del__(self):
        """析构时确保释放资源"""
        self.release()


# 便捷函数：快速从图片检测情感
def detect_emotion_from_image(image_path: str, use_mediapipe: bool = True) -> Optional[Percept]:
    """从图片快速检测情感（无需创建对象）
    
    Args:
        image_path: 图片文件路径
        use_mediapipe: 是否使用MediaPipe人脸检测（默认True）
    
    Returns:
        Percept对象或None
    
    示例:
        percept = detect_emotion_from_image("face.jpg")
        if percept:
            print(f"情感: V={percept.valence_hint:.2f}")
    """
    with VisionPerceptor(camera_id=-1, use_mediapipe=use_mediapipe) as vp:  # 不打开摄像头
        return vp.perceive_from_image(image_path)


def visualize_face_analysis(
    image_path: str,
    output_path: Optional[str] = None,
    show_landmarks: bool = True,
    show_blendshapes: bool = True
) -> np.ndarray:
    """可视化人脸分析结果（特征点 + 表情混合形状）
    
    Args:
        image_path: 输入图片路径
        output_path: 输出图片路径（可选）
        show_landmarks: 是否绘制468个人脸特征点
        show_blendshapes: 是否显示表情混合形状
    
    Returns:
        带标注的图像
    
    示例:
        visualize_face_analysis("face.jpg", "output.jpg")
    """
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"无法读取图片: {image_path}")
        return None
    
    h, w = image.shape[:2]
    
    # 使用VisionPerceptor进行分析
    with VisionPerceptor(camera_id=-1, use_mediapipe=True, use_landmarks=True) as vp:
        percept = vp.perceive(image)
        
        if percept is None or 'face_landmarks' not in percept.metadata:
            logger.warning("未检测到人脸特征点")
            return image
        
        # 绘制人脸边界框
        if 'bounding_box' in percept.metadata:
            x, y, fw, fh = percept.metadata['bounding_box']
            cv2.rectangle(image, (x, y), (x+fw, y+fh), (0, 255, 0), 2)
        
        # 绘制468个人脸特征点
        if show_landmarks and 'face_landmarks' in percept.metadata:
            landmarks = percept.metadata['face_landmarks']
            for landmark in landmarks:
                # 转换归一化坐标到像素坐标
                px = int(landmark['x'] * w)
                py = int(landmark['y'] * h)
                # 绘制小圆点
                cv2.circle(image, (px, py), 1, (0, 255, 255), -1)
            
            logger.info(f"绘制了 {len(landmarks)} 个人脸特征点")
        
        # 显示混合形状（面部表情系数）
        if show_blendshapes and 'face_blendshapes' in percept.metadata:
            blendshapes = percept.metadata['face_blendshapes']
            
            # 选择前10个最显著的混合形状
            sorted_blendshapes = sorted(
                blendshapes.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # 在图像右侧创建信息面板
            panel_width = 400
            panel = np.zeros((h, panel_width, 3), dtype=np.uint8)
            
            # 标题
            cv2.putText(
                panel, "Top 10 Blendshapes", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
            
            # 显示混合形状
            y_offset = 60
            for name, score in sorted_blendshapes:
                # 缩短名称
                display_name = name.replace('_', ' ').title()[:25]
                text = f"{display_name}: {score:.3f}"
                
                cv2.putText(
                    panel, text, (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                )
                
                # 绘制进度条
                bar_length = int(score * 350)
                cv2.rectangle(
                    panel,
                    (10, y_offset + 5),
                    (10 + bar_length, y_offset + 15),
                    (0, 255, 0), -1
                )
                
                y_offset += 35
            
            # 显示主导情感
            emotion_text = f"Emotion: {percept.metadata['dominant_emotion'].upper()}"
            confidence_text = f"Confidence: {percept.confidence:.1%}"
            
            cv2.putText(
                panel, emotion_text, (10, y_offset + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2
            )
            cv2.putText(
                panel, confidence_text, (10, y_offset + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
            )
            
            # 合并图像和面板
            image = np.hstack([image, panel])
            
            logger.info(f"显示了 {len(sorted_blendshapes)} 个混合形状")
    
    # 保存输出
    if output_path:
        cv2.imwrite(output_path, image)
        logger.info(f"已保存到: {output_path}")
    
    return image


def visualize_all_faces(
    image_path: str,
    output_path: Optional[str] = None,
    show_landmarks: bool = True,
    show_emotions: bool = True,
    max_faces: int = 10,
    min_confidence: float = 0.2
) -> np.ndarray:
    """可视化多人脸分析结果
    
    Args:
        image_path: 输入图片路径
        output_path: 输出图片路径（可选）
        show_landmarks: 是否绘制468个人脸特征点
        show_emotions: 是否显示情感标签
        max_faces: 最大检测人脸数
        min_confidence: 最低置信度阈值
    
    Returns:
        带标注的图像
    
    示例:
        visualize_all_faces("group.jpg", "output.jpg", max_faces=5, min_confidence=0.2)
    """
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"无法读取图片: {image_path}")
        return None
    
    h, w = image.shape[:2]
    
    # 使用VisionPerceptor进行分析（使用自定义置信度）
    with VisionPerceptor(
        camera_id=-1,
        use_mediapipe=True,
        use_landmarks=True,
        min_confidence=min_confidence
    ) as vp:
        percepts = vp.perceive_all_faces(image, max_faces=max_faces)
        
        if not percepts:
            logger.warning("未检测到人脸")
            return image
        
        # 为每张人脸分配不同的颜色
        colors = [
            (255, 0, 0),    # 蓝色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 红色
            (255, 255, 0),  # 青色
            (255, 0, 255),  # 品红
            (0, 255, 255),  # 黄色
            (128, 0, 128),  # 紫色
            (255, 128, 0),  # 橙色
            (0, 128, 255),  # 天蓝
            (128, 255, 0),  # 黄绿
        ]
        
        logger.info(f"处理 {len(percepts)} 张人脸")
        
        # 处理每张人脸
        for idx, percept in enumerate(percepts):
            if percept is None:
                continue
            
            color = colors[idx % len(colors)]
            
            # 绘制人脸边界框
            if 'bounding_box' in percept.metadata:
                x, y, fw, fh = percept.metadata['bounding_box']
                cv2.rectangle(image, (x, y), (x+fw, y+fh), color, 2)
                
                # 显示人脸编号
                label = f"Face #{idx+1}"
                cv2.putText(
                    image, label, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
                )
            
            # 显示情感标签
            if show_emotions and 'dominant_emotion' in percept.metadata:
                emotion = percept.metadata['dominant_emotion'].upper()
                confidence = percept.confidence
                emotion_text = f"{emotion} {confidence:.0%}"
                
                # 计算文本位置（边界框底部）
                x, y, fw, fh = percept.metadata['bounding_box']
                text_y = y + fh + 20
                
                cv2.putText(
                    image, emotion_text, (x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                )
            
            # 绘制人脸特征点
            if show_landmarks and 'face_landmarks' in percept.metadata:
                landmarks = percept.metadata['face_landmarks']
                for landmark in landmarks:
                    # 转换归一化坐标到像素坐标
                    px = int(landmark['x'] * w)
                    py = int(landmark['y'] * h)
                    # 绘制小圆点（使用对应人脸的颜色）
                    cv2.circle(image, (px, py), 1, color, -1)
        
        # 在图像顶部显示统计信息
        valid_faces = sum(1 for p in percepts if p is not None)
        stats_text = f"Detected {valid_faces}/{len(percepts)} valid faces"
        cv2.putText(
            image, stats_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2
        )
        
        logger.info(f"已标注 {valid_faces} 张有效人脸")
    
    # 保存输出
    if output_path:
        cv2.imwrite(output_path, image)
        logger.info(f"已保存到: {output_path}")
    
    return image
