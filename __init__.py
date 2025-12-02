"""
Genshin Impact 数据提取器
基于ID映射规律分析的新版本提取器
"""

from .weapon_extractor import WeaponExtractor
from .reliquary_extractor import ReliquaryExtractor
from .book_extractor import BookExtractor
from .avatar_extractor import AvatarExtractor

__all__ = ['WeaponExtractor', 'ReliquaryExtractor', 'BookExtractor', 'AvatarExtractor']
