# 手势识别规格说明

## 概述

手势识别模块负责从视频帧中检测手部，识别手势类型，并将手势映射到情感空间 (VAD)。

## 功能需求

### FR1: 手部检测
- **描述**: 从图像/视频帧中检测手部位置和边界框
- **输入**: RGB 图像 (numpy.ndarray)
- **输出**: 手部边界框列表 [(x, y, w, h), ...]
- **要求**:
  - 支持双手检测
  - 检测置信度阈值可配置 (默认 0.5)
  - 区分左手/右手
  - 处理不同光照和背景

### FR2: 手部关键点检测
- **描述**: 提取 21 个手部关键点
- **输入**: 手部图像区域
- **输出**: 21 个 3D 关键点坐标 (x, y, z)
  - 0: 手腕 (wrist)
  - 1-4: 拇指 (thumb)
  - 5-8: 食指 (index finger)
  - 9-12: 中指 (middle finger)
  - 13-16: 无名指 (ring finger)
  - 17-20: 小指 (pinky)
- **要求**:
  - 使用 MediaPipe Hand Landmarker
  - 实时性能 (< 30ms/手)
  - 鲁棒性 (快速移动、不同姿态)

### FR3: 手势分类
- **描述**: 识别预定义的手势类型
- **输入**: 21 个手部关键点 + 手部图像
- **输出**: 手势类型和置信度
- **支持的手势**:
  1. **None** - 未识别手势
  2. **Closed_Fist** - 握拳 ✊
  3. **Open_Palm** - 张开手掌 ✋
  4. **Pointing_Up** - 食指向上 ☝️
  5. **Thumb_Down** - 拇指向下 👎
  6. **Thumb_Up** - 拇指向上 👍
  7. **Victory** - 胜利手势 ✌️
  8. **ILoveYou** - 爱你手势 🤟
- **要求**:
  - 使用 MediaPipe Gesture Recognizer
  - 置信度阈值可配置 (默认 0.6)
  - 支持实时识别

### FR4: 手势到 VAD 情感映射
- **描述**: 将手势类型映射到 VAD 情感空间
- **输入**: 手势类型
- **输出**: VAD 三维向量

| 手势 | Valence | Arousal | Dominance | 情感含义 |
|------|---------|---------|-----------|----------|
| Thumb_Up | +0.7 | 0.5 | +0.5 | 积极、赞同 |
| Thumb_Down | -0.7 | 0.5 | +0.3 | 消极、反对 |
| Victory | +0.6 | 0.6 | +0.4 | 胜利、开心 |
| ILoveYou | +0.8 | 0.7 | +0.2 | 爱、温暖 |
| Open_Palm | +0.3 | 0.3 | +0.5 | 友好、展示 |
| Closed_Fist | -0.3 | 0.8 | +0.7 | 愤怒、决心 |
| Pointing_Up | 0.0 | 0.4 | +0.6 | 指示、提醒 |
| None | 0.0 | 0.0 | 0.0 | 中性 |

## 性能需求

### NFR1: 实时性能
- 单手处理时间 < 30ms
- 双手处理时间 < 60ms
- 视频流 FPS > 30

### NFR2: 准确率
- RPS 数据集准确率 > 85%
- 真实场景准确率 > 75%
- 误报率 < 15%

### NFR3: 资源占用
- CPU 占用 < 15% (单核)
- 内存占用 < 150MB (不含模型)
- 模型文件大小 < 15MB

### NFR4: 鲁棒性
- 不同光照条件下稳定
- 不同肤色适用
- 快速移动下可用
- 不同距离和角度 (30cm-2m, ±30°)

## 技术实现

### 依赖库
- MediaPipe 0.10.31+
- OpenCV 4.8+
- NumPy 1.23+

### 模型文件
- `models/gesture_recognizer.task` (MediaPipe 预训练模型)
- 下载地址: https://developers.google.com/mediapipe/solutions/vision/gesture_recognizer

### 核心类: `HandGesturePerception`

#### 方法
```python
class HandGesturePerception:
    def __init__(self, model_path: str, max_num_hands: int = 2)
    def perceive(self, image: np.ndarray) -> Optional[Dict]
    def perceive_all_hands(self, image: np.ndarray) -> List[Dict]
    def _gesture_to_vad(self, gesture: str) -> Tuple[float, float, float]
```

#### 返回数据结构
```python
{
    'handedness': 'Left' | 'Right',
    'hand_landmarks': [(x, y, z), ...],  # 21 个点
    'gesture': {
        'type': 'Thumb_Up',
        'confidence': 0.95
    },
    'vad': {
        'valence': 0.7,
        'arousal': 0.5,
        'dominance': 0.5
    }
}
```

## 测试需求

### 单元测试
- 测试手势到 VAD 的映射
- 测试边界情况 (空输入、无手部)
- 测试双手检测

### 集成测试
- 测试真实图像处理
- 测试视频流处理
- 测试多手场景

### 性能测试
- 基准测试脚本 (待创建)
- 性能指标验证
- 资源占用监控

### 数据集测试
- **RPS Dataset** (Rock-Paper-Scissors)
  - 测试脚本: `tests/test_rps_dataset.py`
  - 已测试准确率: 86.7% (rock: 96%, paper: 76%, scissors: 88%)
- 自定义手势数据集
- 边缘情况测试集

## 已知限制

1. **Paper 手势**: 识别率较低 (76%)，可能需要改进
2. **快速移动**: 极快移动时可能丢失跟踪
3. **手部重叠**: 双手重叠时识别困难
4. **背景干扰**: 复杂背景可能产生误检
5. **手套/饰品**: 影响关键点检测准确性

## 未来改进方向

1. **自定义手势**: 支持用户自定义手势
2. **动态手势**: 支持动作序列识别 (挥手、画圈)
3. **手势轨迹**: 记录手势运动轨迹
4. **双手协同**: 识别需要双手的手势
5. **上下文理解**: 结合场景理解手势含义

## 应用场景

### 机器人交互
- **指令控制**: Pointing_Up (注意), Closed_Fist (停止)
- **情感反馈**: Thumb_Up (满意), Thumb_Down (不满意)
- **社交手势**: Victory (打招呼), ILoveYou (友好)

### 游戏控制
- **石头剪刀布**: Closed_Fist, Victory, Open_Palm
- **手势菜单**: 不同手势对应不同功能

### 无接触交互
- **音量控制**: Open_Palm (增大), Closed_Fist (减小)
- **翻页**: Pointing_Up (下一页), 其他 (上一页)

## 测试数据集

### RPS Dataset
- **来源**: Kaggle Rock Paper Scissors Images
- **大小**: 2188 训练图像, 372 测试图像
- **类别**: rock, paper, scissors
- **测试结果** (2025-01-16):
  - Overall: 86.7%
  - Rock: 96.0% ✅
  - Paper: 76.0% ⚠️
  - Scissors: 88.0% ✅

### 自定义测试集
- 不同光照条件
- 不同肤色
- 不同年龄
- 不同距离和角度

## 参考资料

- [MediaPipe Gesture Recognizer](https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer)
- [Hand Landmarks Model Card](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20MediaPipe%20Hands%20(Lite%3ABaseline).pdf)
- [Gesture Recognition in HCI](https://en.wikipedia.org/wiki/Gesture_recognition)
- [VAD Emotion Model](https://en.wikipedia.org/wiki/PAD_emotional_state_model)

## 维护记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2025-01-16 | 1.1 | 添加 RPS 数据集测试 |
| 2025-01-16 | 1.0 | 初始版本 |
