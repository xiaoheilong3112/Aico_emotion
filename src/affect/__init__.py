"""AICO 情感核心模块

本模块包含情感系统的核心数据结构和配置管理：
- state: 情感状态定义（AffectState, Percept, ExpressionCommand）
- personality: 人格配置管理
- inference: 情感推断引擎（待实现）
"""

from .state import (
    AffectState,
    Percept,
    ExpressionCommand,
    EmotionCategory,
    emotion_to_vad,
    EMOTION_TO_VAD,
)

from .personality import Personality

__all__ = [
    'AffectState',
    'Percept',
    'ExpressionCommand',
    'EmotionCategory',
    'emotion_to_vad',
    'EMOTION_TO_VAD',
    'Personality',
]
