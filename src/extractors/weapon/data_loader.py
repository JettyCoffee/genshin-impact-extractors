"""
武器数据加载器
"""

from typing import Dict, List

from ...core import get_data_path, load_json, setup_logger


class WeaponDataLoader:
    """武器数据加载器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def load_weapons(self) -> List[Dict]:
        """
        加载武器配置数据
        
        返回:
            武器数据列表
        """
        weapon_file = get_data_path('ExcelBinOutput/WeaponExcelConfigData.json')
        return load_json(str(weapon_file))
