"""
武器提取器主类
"""

from typing import Any, Dict, List, Optional

from ..base import BaseExtractor
from ...core import StoryContentExtractor
from .data_loader import WeaponDataLoader
from .info_extractor import WeaponInfoExtractor


class WeaponExtractor(BaseExtractor):
    """武器信息提取器"""
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化武器提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP 等)
        """
        super().__init__(language)
        
        # 初始化故事提取器
        self.story_extractor = StoryContentExtractor(language)
        
        # 初始化数据加载器和信息提取器
        self.data_loader = WeaponDataLoader()
        self.info_extractor = WeaponInfoExtractor(self.text_parser, self.story_extractor)
        
        # 加载数据
        self.logger.info("加载武器数据...")
        self.weapons = self.data_loader.load_weapons()
        self.logger.info(f"成功加载 {len(self.weapons)} 个武器数据")
    
    def extract_weapon_info(self, weapon_data: Dict) -> Optional[Dict[str, Any]]:
        """
        提取单个武器的信息
        
        参数:
            weapon_data: 武器原始数据
        
        返回:
            结构化的武器信息
        """
        return self.info_extractor.extract_info(weapon_data)
    
    def extract_all(self) -> List[Dict[str, Any]]:
        """
        提取所有武器的完整信息
        
        返回:
            完整的武器信息列表
        """
        self.logger.info("开始提取所有武器信息...")
        
        all_weapons = []
        weapons_with_story = 0
        
        for weapon_data in self.weapons:
            weapon_id = weapon_data.get('id')
            
            if not weapon_id:
                continue
            
            weapon_info = self.extract_weapon_info(weapon_data)
            if weapon_info:
                all_weapons.append(weapon_info)
                
                if weapon_info.get('has_story'):
                    weapons_with_story += 1
                    self.logger.debug(
                        f"已提取武器(含故事): {weapon_info['name']} (ID: {weapon_id})"
                    )
        
        self.logger.info(f"成功提取 {len(all_weapons)} 个武器信息")
        self.logger.info(f"其中 {weapons_with_story} 个武器包含故事")
        
        return all_weapons
    
    def get_weapons_by_type(self, weapon_type: str) -> List[Dict]:
        """
        按类型筛选武器
        
        参数:
            weapon_type: 武器类型
        
        返回:
            该类型的所有武器
        """
        all_weapons = self.extract_all()
        return [w for w in all_weapons if w.get('weapon_type') == weapon_type]
    
    def get_weapons_by_rarity(self, rank_level: int) -> List[Dict]:
        """
        按稀有度筛选武器
        
        参数:
            rank_level: 稀有度等级 (1-5 星)
        
        返回:
            该稀有度的所有武器
        """
        all_weapons = self.extract_all()
        return [w for w in all_weapons if w.get('rank_level') == rank_level]
