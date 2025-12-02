"""
数据提取器模块
包含各类游戏数据的提取器
"""

from .avatar import AvatarExtractor
from .weapon import WeaponExtractor
from .reliquary import ReliquaryExtractor
from .book import BookExtractor
from .quest import QuestDialogueExtractor

__all__ = [
    'AvatarExtractor',
    'WeaponExtractor',
    'ReliquaryExtractor',
    'BookExtractor',
    'QuestDialogueExtractor',
]
