"""
数据模型定义模块
提供常量、字段映射等定义
"""

from .constants import (
    BodyTypes,
    WeaponTypes,
    EquipTypes,
    DocumentTypes,
    QuestTypes,
    TalkRoleTypes,
    IDOffsets,
)

from .field_maps import (
    QuestFieldMap,
    TalkFieldMap,
    SubQuestFieldMap,
    DialogFieldMap,
    TalkRoleFieldMap,
)

__all__ = [
    # 常量类
    'BodyTypes',
    'WeaponTypes',
    'EquipTypes',
    'DocumentTypes',
    'QuestTypes',
    'TalkRoleTypes',
    'IDOffsets',
    # 字段映射类
    'QuestFieldMap',
    'TalkFieldMap',
    'SubQuestFieldMap',
    'DialogFieldMap',
    'TalkRoleFieldMap',
]
