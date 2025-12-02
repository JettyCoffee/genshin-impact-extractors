"""
提取器基类
定义所有提取器的公共接口和方法
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..core import (
    setup_logger,
    load_json,
    save_json,
    get_data_path,
    TextMapParser,
)


class BaseExtractor(ABC):
    """提取器基类"""
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP 等)
        """
        self.language = language
        self.logger = setup_logger(self.__class__.__name__)
        self.text_parser = TextMapParser(language)
    
    @abstractmethod
    def extract_all(self) -> List[Dict[str, Any]]:
        """
        提取所有数据
        
        返回:
            提取的数据列表
        """
        pass
    
    def save_to_file(self, output_file: str, data: Optional[List[Dict]] = None) -> None:
        """
        保存数据到文件
        
        参数:
            output_file: 输出文件路径
            data: 要保存的数据，如果为 None 则调用 extract_all()
        """
        if data is None:
            data = self.extract_all()
        
        save_json(data, output_file)
        self.logger.info(f"数据已保存到: {output_file}")
    
    def _load_excel_data(self, filename: str) -> List[Dict]:
        """
        加载 ExcelBinOutput 数据
        
        参数:
            filename: 文件名（不含路径）
        
        返回:
            数据列表
        """
        file_path = get_data_path(f'ExcelBinOutput/{filename}')
        return load_json(str(file_path))
    
    def _load_excel_data_as_dict(self, filename: str, key_field: str = 'id') -> Dict[int, Dict]:
        """
        加载 ExcelBinOutput 数据并转换为字典
        
        参数:
            filename: 文件名（不含路径）
            key_field: 作为字典键的字段名
        
        返回:
            以指定字段为键的字典
        """
        data = self._load_excel_data(filename)
        return {item[key_field]: item for item in data if key_field in item}
    
    def get_text(self, text_hash: int) -> str:
        """
        获取文本映射
        
        参数:
            text_hash: 文本哈希值
        
        返回:
            对应的文本
        """
        return self.text_parser.get_text(text_hash)
