"""
文本解析模块
提供文本哈希到文本的映射解析功能
"""

import json
from typing import Dict

from .config import get_data_path


class TextMapParser:
    """文本映射解析器"""
    
    # 支持的语言代码
    SUPPORTED_LANGUAGES = [
        'CHS',  # 简体中文
        'CHT',  # 繁体中文
        'EN',   # 英语
        'JP',   # 日语
        'KR',   # 韩语
        'DE',   # 德语
        'FR',   # 法语
        'ES',   # 西班牙语
        'PT',   # 葡萄牙语
        'RU',   # 俄语
        'ID',   # 印尼语
        'TH',   # 泰语
        'VI',   # 越南语
        'TR',   # 土耳其语
        'IT',   # 意大利语
    ]
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化文本映射解析器
        
        参数:
            language: 语言代码 (CHS, EN, JP 等)
        
        异常:
            ValueError: 不支持的语言代码
            FileNotFoundError: 文本映射文件不存在
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"不支持的语言代码: {language}，"
                f"支持的语言: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )
        
        self.language = language
        self.text_map = self._load_text_map()
    
    def _load_text_map(self) -> Dict[int, str]:
        """
        加载文本映射数据
        
        返回:
            哈希到文本的映射字典
        """
        text_map_file = get_data_path(f'TextMap/TextMap{self.language}.json')
        
        if not text_map_file.exists():
            raise FileNotFoundError(f"文本映射文件不存在: {text_map_file}")
        
        with open(text_map_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 将字符串 key 转换为整数
        return {int(k): v for k, v in data.items()}
    
    def get_text(self, text_hash: int) -> str:
        """
        根据哈希获取文本
        
        参数:
            text_hash: 文本哈希值
        
        返回:
            对应的文本，如果不存在则返回空字符串
        """
        return self.text_map.get(text_hash, '')
    
    def get_text_or_default(self, text_hash: int, default: str = '') -> str:
        """
        根据哈希获取文本，不存在时返回默认值
        
        参数:
            text_hash: 文本哈希值
            default: 默认值
        
        返回:
            对应的文本或默认值
        """
        return self.text_map.get(text_hash, default)
    
    def has_text(self, text_hash: int) -> bool:
        """
        检查是否存在指定哈希的文本
        
        参数:
            text_hash: 文本哈希值
        
        返回:
            是否存在
        """
        return text_hash in self.text_map
    
    @property
    def size(self) -> int:
        """返回文本映射的条目数"""
        return len(self.text_map)
