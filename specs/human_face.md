# 人脸情感识别规格说明

## 概述

人脸情感识别模块负责从视频帧中检测人脸，提取面部特征，并基于 MediaPipe Blendshapes 识别情感状态。

## 功能需求

### FR1: 人脸检测
- **描述**: 从图像/视频帧中检测人脸位置和边界框
- **输入**: RGB 图像 (numpy.ndarray)
- **输出**: 人脸边界框列表 [(x, y, w, h), ...]
- **要求**:
  - 支持多人脸检测 (最多 5 人)
  - 检测置信度阈值可配置 (默认 0.5)
  - 处理不同光照条件
  - 处理不同人脸角度 (±45°)

### FR2: 面部关键点检测
- **描述**: 提取 468 个面部关键点和 52 个 blendshapes 系数
- **输入**: 人脸图像区域
- **输出**: 
  - 468 个 3D 关键点坐标 (x, y, z)
  - 52 个 blendshapes 系数 (0.0-1.0)
- **要求**:
  - 使用 MediaPipe FaceLandmarker
  - 实时性能 (< 30ms/帧)
  - 鲁棒性 (遮挡、表情变化)

### FR3: 情感识别
- **描述**: 基于 blendshapes 分析情感状态
- **输入**: 52 个 blendshapes 系数
- **输出**: 7 种基本情感分数
  - happy (开心)
  - sad (悲伤)
  - angry (愤怒)
  - surprise (惊讶)
  - fear (恐惧)
  - disgust (厌恶)
  - neutral (中性)
- **要求**:
  - 基于 FACS (Facial Action Coding System)
  - 权重映射可调整
  - 支持多情感并存

### FR4: VAD 情感空间映射
- **描述**: 将离散情感转换为 VAD 连续空间
- **输入**: 7 种情感分数
- **输出**: VAD 三维向量
  - Valence: -1.0 (负面) 到 +1.0 (正面)
  - Arousal: 0.0 (平静) 到 1.0 (激动)
  - Dominance: -1.0 (被动) 到 +1.0 (主动)
- **要求**:
  - 基于 Russell's Circumplex Model
  - 平滑插值算法
  - 时序一致性

## 性能需求

### NFR1: 实时性能
- 单人脸处理时间 < 40ms
- 多人脸 (5人) 处理时间 < 200ms
- 视频流 FPS > 25

### NFR2: 准确率
- 标准情感数据集准确率 > 80%
- 真实场景准确率 > 70%
- 误报率 < 10%

### NFR3: 资源占用
- CPU 占用 < 20% (单核)
- 内存占用 < 200MB (不含模型)
- 模型文件大小 < 20MB

### NFR4: 鲁棒性
- 不同光照条件下稳定运行
- 不同人种/年龄/性别适用
- 部分遮挡情况下可用 (遮挡 < 30%)

## 技术实现

### 依赖库
- MediaPipe 0.10.31+
- OpenCV 4.8+
- NumPy 1.23+

### 模型文件
- `models/face_landmarker.task` (MediaPipe 预训练模型)
- 下载地址: https://developers.google.com/mediapipe/solutions/vision/face_landmarker

### 核心类: `HumanFacePerception`

#### 方法
```python
class HumanFacePerception:
    def __init__(self, model_path: str, max_num_faces: int = 5)
    def perceive(self, image: np.ndarray) -> Optional[Dict]
    def perceive_all_faces(self, image: np.ndarray) -> List[Dict]
    def _analyze_emotion_from_blendshapes(self, blendshapes: Dict) -> Tuple[Dict, str]
```

#### 返回数据结构
```python
{
    'face_landmarks': [(x, y, z), ...],  # 468 个点
    'blendshapes': {
        'browDownLeft': 0.1,
        'eyeSquintLeft': 0.3,
        ...  # 52 个 blendshapes
    },
    'emotion_scores': {
        'happy': 0.7,
        'sad': 0.1,
        'angry': 0.0,
        ...
    },
    'primary_emotion': 'happy',
    'vad': {
        'valence': 0.6,
        'arousal': 0.7,
        'dominance': 0.5
    }
}
```

## Blendshapes 权重映射

### 基于 FACS 的映射规则

| 情感 | 关键 Blendshapes | 权重 |
|------|------------------|------|
| Happy | mouthSmileLeft/Right | 0.5 |
|       | cheekSquintLeft/Right | 0.3 |
| Sad | mouthFrownLeft/Right | 0.5 |
|     | browDownLeft/Right | 0.4 |
| Angry | browDownLeft/Right | 0.5 |
|       | eyeSquintLeft/Right | 0.4 |
| Surprise | browInnerUp | 0.5 |
|          | jawOpen | 0.4 |
| Fear | eyeWideLeft/Right | 0.5 |
|      | browInnerUp | 0.4 |
| Disgust | noseSneerLeft/Right | 0.5 |
|         | mouthUpperUpLeft/Right | 0.4 |
| Neutral | 低激活阈值检测 | - |

详细权重配置见 `src/perception/human_face.py` 中的 `BLENDSHAPE_EMOTION_WEIGHTS` 字典。

## 测试需求

### 单元测试
- 测试 blendshapes 到情感的映射
- 测试 VAD 空间转换
- 测试边界情况 (空输入、无人脸)

### 集成测试
- 测试真实图像处理
- 测试视频流处理
- 测试多人脸场景

### 性能测试
- 基准测试脚本: `tests/benchmark_blendshapes.py`
- 性能指标验证
- 资源占用监控

### 数据集测试
- FER2013 / AffectNet (如果可用)
- 自定义测试集
- 边缘情况测试集

## 已知限制

1. **极端表情**: 夸张表情可能识别不准
2. **遮挡**: 大面积遮挡 (> 30%) 影响准确率
3. **侧脸**: 角度 > 45° 时准确率下降
4. **低光照**: 极低光照下检测失败
5. **年龄影响**: 婴幼儿和老年人准确率较低

## 未来改进方向

1. **时序建模**: 利用前后帧信息提升稳定性
2. **多模态融合**: 结合语音、手势信息
3. **个性化**: 针对特定用户校准
4. **微表情**: 支持微表情识别
5. **3D 情感空间**: 扩展 VAD 模型

## 参考资料

- [MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker)
- [FACS Manual](https://www.cs.cmu.edu/~face/facs.htm)
- [Russell's Circumplex Model](https://en.wikipedia.org/wiki/Emotion_classification#Circumplex_model)
- [Blendshapes Documentation](https://github.com/google/mediapipe/blob/master/docs/solutions/face_mesh.md)

## 维护记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2025-01-19 | 2.0 | 移除 FER，使用 Blendshapes |
| 2025-01-16 | 1.1 | 添加多人脸支持 |
| 2025-01-14 | 1.0 | 初始版本 |
