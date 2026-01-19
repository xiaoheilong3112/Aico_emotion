# VAD 情感状态模型规格说明

## 概述

VAD (Valence-Arousal-Dominance) 情感状态模型是 AICO 系统的核心情感表示方法，提供连续的三维情感空间，优于离散情感分类。

## 理论基础

### Russell's Circumplex Model
VAD 模型基于 Russell 的环形情感模型，将情感表示为三个独立维度：

1. **Valence (效价)**: 情感的正负性
   - 范围: -1.0 (极负面) 到 +1.0 (极正面)
   - 例子: -1.0 = 极度痛苦, 0.0 = 中性, +1.0 = 极度快乐

2. **Arousal (唤醒度)**: 情感的激活水平
   - 范围: 0.0 (完全平静) 到 1.0 (高度激活)
   - 例子: 0.0 = 放松/睡眠, 0.5 = 正常, 1.0 = 极度兴奋/惊恐

3. **Dominance (支配性)**: 对情境的控制感
   - 范围: -1.0 (完全被动) 到 +1.0 (完全主动)
   - 例子: -1.0 = 无助/恐惧, 0.0 = 中性, +1.0 = 掌控/自信

## 功能需求

### FR1: 情感状态创建
- **描述**: 从 VAD 三维值创建情感状态对象
- **输入**: (valence, arousal, dominance) 元组
- **输出**: AffectState 对象
- **验证**:
  - valence ∈ [-1.0, 1.0]
  - arousal ∈ [0.0, 1.0]
  - dominance ∈ [-1.0, 1.0]
  - 超出范围的值进行裁剪

### FR2: 离散情感到 VAD 映射
- **描述**: 将离散情感标签转换为 VAD 坐标
- **输入**: 情感标签字符串 (如 "happy", "sad")
- **输出**: (valence, arousal, dominance) 元组

#### 标准映射表

| 情感 | Valence | Arousal | Dominance | 描述 |
|------|---------|---------|-----------|------|
| **neutral** | 0.0 | 0.0 | 0.0 | 中性、平静 |
| **happy** | +0.8 | 0.7 | +0.5 | 开心、快乐 |
| **sad** | -0.7 | 0.3 | -0.4 | 悲伤、沮丧 |
| **angry** | -0.6 | 0.9 | +0.6 | 愤怒、生气 |
| **fear** | -0.8 | 0.8 | -0.7 | 恐惧、害怕 |
| **surprise** | +0.4 | 0.8 | 0.0 | 惊讶、意外 |
| **disgust** | -0.7 | 0.5 | +0.3 | 厌恶、反感 |
| **excited** | +0.7 | 0.9 | +0.5 | 兴奋、激动 |
| **calm** | +0.3 | 0.1 | 0.0 | 平静、放松 |
| **anxious** | -0.4 | 0.7 | -0.5 | 焦虑、不安 |

### FR3: VAD 到离散情感映射
- **描述**: 将 VAD 坐标映射回最接近的离散情感
- **输入**: (valence, arousal, dominance) 元组
- **输出**: 情感标签字符串
- **算法**: 欧氏距离最近邻

### FR4: 情感空间距离计算
- **描述**: 计算两个情感状态之间的相似度
- **输入**: 两个 AffectState 对象
- **输出**: 距离值 (0.0-2.0+)
- **公式**:
  ```
  distance = sqrt(
    (v1 - v2)^2 + 
    (a1 - a2)^2 + 
    (d1 - d2)^2
  )
  ```

### FR5: 情感插值
- **描述**: 在两个情感状态之间平滑过渡
- **输入**: 
  - start_state: 起始情感
  - end_state: 目标情感
  - t: 插值参数 (0.0-1.0)
- **输出**: 插值后的情感状态
- **算法**: 线性插值 (LERP)
  ```
  new_v = start_v + (end_v - start_v) * t
  new_a = start_a + (end_a - start_a) * t
  new_d = start_d + (end_d - start_d) * t
  ```

### FR6: 情感强度计算
- **描述**: 计算情感的整体强度
- **输入**: AffectState 对象
- **输出**: 强度值 (0.0-1.0)
- **公式**:
  ```
  intensity = sqrt(valence^2 + arousal^2 + dominance^2) / sqrt(3)
  ```
  归一化到 [0, 1] 范围

## 非功能需求

### NFR1: 性能
- VAD 对象创建: < 0.1ms
- 情感映射: < 0.5ms
- 距离计算: < 0.1ms
- 插值计算: < 0.1ms

### NFR2: 精度
- 浮点数精度: 至少 2 位小数
- 范围裁剪误差: < 1e-6

### NFR3: 可扩展性
- 支持自定义情感映射
- 支持动态添加新情感标签
- 支持情感权重调整

## 技术实现

### 核心类: `AffectState`

```python
class AffectState:
    """表示 VAD 三维情感状态"""
    
    def __init__(self, valence: float, arousal: float, dominance: float):
        """
        Args:
            valence: 效价 [-1.0, 1.0]
            arousal: 唤醒度 [0.0, 1.0]
            dominance: 支配性 [-1.0, 1.0]
        """
        
    @classmethod
    def from_emotion(cls, emotion: str) -> 'AffectState':
        """从离散情感标签创建"""
        
    def to_emotion(self) -> str:
        """转换为最接近的离散情感"""
        
    def distance_to(self, other: 'AffectState') -> float:
        """计算到另一个状态的距离"""
        
    def interpolate(self, target: 'AffectState', t: float) -> 'AffectState':
        """插值到目标状态"""
        
    def intensity(self) -> float:
        """计算情感强度"""
        
    @property
    def valence(self) -> float:
        """效价值"""
        
    @property
    def arousal(self) -> float:
        """唤醒度值"""
        
    @property
    def dominance(self) -> float:
        """支配性值"""
```

### 工具类: `AffectSpace`

```python
class AffectSpace:
    """情感空间映射工具"""
    
    @staticmethod
    def discrete_to_vad(emotion: str) -> Tuple[float, float, float]:
        """离散情感 → VAD"""
        
    @staticmethod
    def vad_to_discrete(v: float, a: float, d: float) -> str:
        """VAD → 离散情感"""
        
    @staticmethod
    def blend_emotions(emotions: Dict[str, float]) -> Tuple[float, float, float]:
        """混合多个情感 (加权平均)"""
```

## 使用示例

### 基本用法
```python
from src.affect.affect_state import AffectState
from src.affect.affect_space import AffectSpace

# 创建情感状态
happy = AffectState(valence=0.8, arousal=0.7, dominance=0.5)

# 从离散情感创建
sad = AffectState.from_emotion("sad")

# 计算距离
dist = happy.distance_to(sad)  # ~1.73

# 情感插值 (50% 开心 + 50% 悲伤)
mixed = happy.interpolate(sad, t=0.5)

# 转换回离散情感
label = mixed.to_emotion()  # "neutral" or "anxious"
```

### 多情感混合
```python
# Blendshapes 情感分数
emotion_scores = {
    'happy': 0.7,
    'surprise': 0.3,
    'neutral': 0.1
}

# 加权混合
v, a, d = AffectSpace.blend_emotions(emotion_scores)
affect = AffectState(v, a, d)
```

### 时序情感跟踪
```python
# 平滑过渡 (避免情感突变)
current_affect = AffectState(0.5, 0.4, 0.2)
target_affect = AffectState(0.8, 0.7, 0.5)

# 逐帧插值 (alpha=0.1 平滑系数)
for frame in frames:
    current_affect = current_affect.interpolate(target_affect, t=0.1)
    # 使用 current_affect 进行机器人控制
```

## 情感空间可视化

### 3D 空间表示
```
         Arousal (↑)
            |
            |  Fear (-0.8, 0.8, -0.7)
            |  
  Angry ----+---- Excited
  (-0.6, 0.9, 0.6)  (0.7, 0.9, 0.5)
            |
            |  Happy (0.8, 0.7, 0.5)
     -------+------- Valence (→)
            |
      Sad   |  Calm (0.3, 0.1, 0.0)
  (-0.7, 0.3, -0.4)
            |
       Dominance (⊗)
```

### 2D 切片 (Valence-Arousal, Dominance=0)
```
  Arousal
     ↑
   1.0 |    Angry        Excited
       |        \       /
   0.8 |         \   /
       |          \ /   Happy
   0.6 |         / X \
       |       /   |   \
   0.4 |     /  Neutral  \
       |   /       |       \
   0.2 | Sad      Calm
       |
   0.0 +--+----+----+----+--+→ Valence
      -1.0  -0.5  0.0  0.5  1.0
```

## 测试需求

### 单元测试
- ✅ 测试 VAD 范围验证
- ✅ 测试离散情感映射
- ✅ 测试距离计算
- ✅ 测试情感插值
- ✅ 测试强度计算
- ✅ 测试边界情况

### 集成测试
- 测试多模态情感融合
- 测试时序情感平滑
- 测试极端情感转换

### 性能测试
- 大量情感对象创建
- 频繁插值操作
- 距离计算性能

## 已知限制

1. **线性插值**: 使用简单线性插值，未考虑情感空间的非线性特性
2. **文化差异**: 情感映射基于西方心理学研究，可能不适用所有文化
3. **个体差异**: 未考虑个体的情感表达差异
4. **上下文缺失**: 不考虑情境信息

## 未来改进方向

1. **非线性插值**: 使用样条或贝塞尔曲线
2. **文化适配**: 支持不同文化的情感映射
3. **个性化**: 学习用户的情感模式
4. **情感历史**: 考虑历史情感状态
5. **4D 扩展**: 添加时间维度 (情感持续时间)

## 参考资料

- [Russell's Circumplex Model](https://en.wikipedia.org/wiki/Emotion_classification#Circumplex_model)
- [PAD Emotional State Model](https://en.wikipedia.org/wiki/PAD_emotional_state_model)
- [Dimensional Models of Emotion](https://www.paulekman.com/resources/dimensional-models-emotion/)
- [Affective Computing](https://affect.media.mit.edu/)

## 维护记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2025-01-14 | 1.0 | 初始版本，96% 测试覆盖率 |
