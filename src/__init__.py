"""
Genshin Impact 数据提取器
基于 ID 映射规律分析的新版本提取器

包结构:
- core: 核心工具模块（配置、IO、文本解析等）
- extractors: 各类数据提取器
- models: 常量和数据模型定义
- cli: 命令行接口
"""

__version__ = "1.0.0"
__author__ = "Genshin Extractors Team"

# 导出主要提取器类，方便外部使用
from .extractors import (
    AvatarExtractor,
    BookExtractor,
    WeaponExtractor,
    ReliquaryExtractor,
    QuestDialogueExtractor,
)

# 导出核心工具
from .core import (
    TextMapParser,
    StoryContentExtractor,
    load_json,
    save_json,
    get_data_path,
    setup_logger,
)

__all__ = [
    # 提取器
    'AvatarExtractor',
    'BookExtractor',
    'WeaponExtractor',
    'ReliquaryExtractor',
    'QuestDialogueExtractor',
    # 核心工具
    'TextMapParser',
    'StoryContentExtractor',
    'load_json',
    'save_json',
    'get_data_path',
    'setup_logger',
]
