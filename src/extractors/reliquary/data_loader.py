"""
圣遗物数据加载器
"""

from typing import Dict, List

from ...core import get_data_path, load_json, setup_logger


class ReliquaryDataLoader:
    """圣遗物数据加载器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def load_reliquaries(self) -> List[Dict]:
        """
        加载圣遗物配置数据
        
        返回:
            圣遗物数据列表
        """
        relic_file = get_data_path('ExcelBinOutput/ReliquaryExcelConfigData.json')
        return load_json(str(relic_file))
    
    def load_relic_sets(self) -> List[Dict]:
        """
        加载圣遗物套装配置数据
        
        返回:
            套装数据列表
        """
        set_file = get_data_path('ExcelBinOutput/ReliquarySetExcelConfigData.json')
        return load_json(str(set_file))
