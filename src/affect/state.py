"""情感状态核心定义

本模块定义了AICO情感系统的核心数据结构：
- AffectState: VAD情感状态空间
- Percept: 感知输入统一接口
- ExpressionCommand: 表达指令抽象
- EmotionCategory: 离散情感类别（用于标注和调试）
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import time


class EmotionCategory(Enum):
    """离散情感类别（用于标注和调试）
    
    这些是传统的离散情感分类，主要用于：
    1. 与外部情感识别库（如FER）的接口
    2. 调试和可视化
    3. 映射到VAD连续空间
    """
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    SURPRISE = "surprise"
    FEAR = "fear"
    DISGUST = "disgust"


@dataclass
class AffectState:
    """VAD情感状态空间
    
    基于心理学的情感维度模型（Russell's Circumplex Model）：
    - Valence（愉悦度）: 情感的积极/消极程度
    - Arousal（激活度）: 情感的唤醒/平静程度
    - Dominance（主导度）: 情感的主动/被动程度
    
    此外还包含长期状态变量：
    - Mood（心境）: 长期情绪倾向
    - Fatigue（疲劳）: 资源消耗状态
    - Trust（信任）: 与用户的关系变量
    """
    
    # VAD 核心维度
    valence: float = 0.0      # [-1, 1] 不愉快 → 愉快
    arousal: float = 0.5      # [0, 1]  平静 → 激动
    dominance: float = 0.0    # [-1, 1] 被动 → 主动
    
    # 长期状态变量
    mood: float = 0.0         # [-1, 1] 长期情绪（慢变量，分钟~小时级）
    fatigue: float = 0.0      # [0, 1]  疲劳/资源消耗
    trust: float = 0.5        # [0, 1]  与当前用户的信任关系
    
    # 元数据
    timestamp: float = field(default_factory=time.time)
    
    def clamp(self):
        """边界约束，确保所有值在有效范围内"""
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.dominance = max(-1.0, min(1.0, self.dominance))
        self.mood = max(-1.0, min(1.0, self.mood))
        self.fatigue = max(0.0, min(1.0, self.fatigue))
        self.trust = max(0.0, min(1.0, self.trust))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于日志、序列化）"""
        return {
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "dominance": round(self.dominance, 3),
            "mood": round(self.mood, 3),
            "fatigue": round(self.fatigue, 3),
            "trust": round(self.trust, 3),
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        """人类可读的字符串表示"""
        return (
            f"AffectState(V:{self.valence:+.2f} A:{self.arousal:.2f} "
            f"D:{self.dominance:+.2f} | Mood:{self.mood:+.2f})"
        )


@dataclass
class Percept:
    """感知输入统一接口
    
    所有感知模块（视觉、语音、语言、交互）的输出都统一为Percept对象。
    每个Percept包含对VAD三个维度的"提示"（hint），以及置信度。
    
    这种设计的优势：
    1. 解耦感知层和推断层
    2. 便于多模态融合
    3. 可追溯每个情感判断的来源
    """
    
    source: str              # 感知来源: "vision" | "audio" | "language" | "interaction" | "time"
    valence_hint: float      # [-1, 1] 对愉悦度的暗示
    arousal_hint: float      # [0, 1]  对激活度的暗示
    dominance_hint: float = 0.0  # [-1, 1] 对主导度的暗示（可选）
    confidence: float = 1.0  # [0, 1]  置信度（影响融合权重）
    
    # 额外信息（用于调试和分析）
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """验证输入有效性"""
        assert -1 <= self.valence_hint <= 1, "valence_hint 必须在 [-1, 1] 范围内"
        assert 0 <= self.arousal_hint <= 1, "arousal_hint 必须在 [0, 1] 范围内"
        assert -1 <= self.dominance_hint <= 1, "dominance_hint 必须在 [-1, 1] 范围内"
        assert 0 <= self.confidence <= 1, "confidence 必须在 [0, 1] 范围内"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source": self.source,
            "valence_hint": round(self.valence_hint, 3),
            "arousal_hint": round(self.arousal_hint, 3),
            "dominance_hint": round(self.dominance_hint, 3),
            "confidence": round(self.confidence, 3),
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        """人类可读的字符串表示"""
        return (
            f"Percept({self.source}: V:{self.valence_hint:+.2f} "
            f"A:{self.arousal_hint:.2f} conf:{self.confidence:.2f})"
        )


@dataclass
class ExpressionCommand:
    """表达指令抽象
    
    情感系统的输出不是直接的动作指令，而是抽象的表达参数。
    这些参数由下游的表达适配器（Adapter）转换为具体的硬件指令。
    
    这种设计的优势：
    1. 解耦情感逻辑和硬件控制
    2. 同一情感系统可适配不同机器人平台
    3. 便于测试和调试（Mock模式）
    """
    
    # 语音风格
    speech_style: str = "normal"  # "calm" | "excited" | "comforting" | "playful"
    
    # 动作风格
    motion_style: str = "idle"    # "idle" | "active" | "gentle" | "protective" | "energetic"
    
    # 能量等级（影响动作幅度、语速等）
    energy_level: float = 0.5     # [0, 1]
    
    # 是否允许打断（影响交互优先级）
    interruption_allowed: bool = True
    
    # 额外控制参数（扩展用）
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """验证输入有效性"""
        assert 0 <= self.energy_level <= 1, "energy_level 必须在 [0, 1] 范围内"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "speech_style": self.speech_style,
            "motion_style": self.motion_style,
            "energy_level": round(self.energy_level, 3),
            "interruption_allowed": self.interruption_allowed,
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        """人类可读的字符串表示"""
        return (
            f"Expression(speech:{self.speech_style} motion:{self.motion_style} "
            f"energy:{self.energy_level:.1%})"
        )


# 辅助函数：离散情感到VAD的映射
# 基于心理学研究（Russell's Circumplex Model 和相关文献）
EMOTION_TO_VAD = {
    EmotionCategory.HAPPY:    (0.8,  0.7,  0.5),   # 高愉悦、高激活、略主动
    EmotionCategory.SAD:      (-0.7, 0.3, -0.3),   # 低愉悦、低激活、略被动
    EmotionCategory.ANGRY:    (-0.8, 0.9,  0.7),   # 低愉悦、高激活、很主动
    EmotionCategory.NEUTRAL:  (0.0,  0.4,  0.0),   # 中性愉悦、略低激活、中性主动
    EmotionCategory.SURPRISE: (0.4,  0.9, -0.2),   # 略正愉悦、很高激活、略被动
    EmotionCategory.FEAR:     (-0.6, 0.8, -0.5),   # 低愉悦、高激活、被动
    EmotionCategory.DISGUST:  (-0.6, 0.5,  0.2),   # 低愉悦、中激活、略主动
}


def emotion_to_vad(emotion: EmotionCategory) -> tuple[float, float, float]:
    """将离散情感类别转换为VAD坐标
    
    Args:
        emotion: 离散情感类别
        
    Returns:
        (valence, arousal, dominance) 元组
    """
    return EMOTION_TO_VAD.get(emotion, (0.0, 0.5, 0.0))
