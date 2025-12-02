"""
圣遗物提取器主类
"""

from typing import Any, Dict, List, Optional

from ..base import BaseExtractor
from ...core import StoryContentExtractor
from .data_loader import ReliquaryDataLoader
from .info_extractor import ReliquaryInfoExtractor
from .set_extractor import ReliquarySetExtractor


class ReliquaryExtractor(BaseExtractor):
    """圣遗物信息提取器"""
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化圣遗物提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP 等)
        """
        super().__init__(language)
        
        # 初始化故事提取器
        self.story_extractor = StoryContentExtractor(language)
        
        # 初始化子模块
        self.data_loader = ReliquaryDataLoader()
        self.info_extractor = ReliquaryInfoExtractor(self.text_parser, self.story_extractor)
        self.set_extractor = ReliquarySetExtractor()
        
        # 加载数据
        self.logger.info("加载圣遗物数据...")
        self.reliquaries = self.data_loader.load_reliquaries()
        self.relic_sets = self.data_loader.load_relic_sets()
        self.logger.info(
            f"成功加载 {len(self.reliquaries)} 个圣遗物数据, "
            f"{len(self.relic_sets)} 个套装"
        )
    
    def extract_reliquary_info(self, relic_data: Dict) -> Optional[Dict[str, Any]]:
        """
        提取单个圣遗物的信息
        
        参数:
            relic_data: 圣遗物原始数据
        
        返回:
            结构化的圣遗物信息
        """
        return self.info_extractor.extract_info(relic_data)
    
    def extract_all(self) -> List[Dict[str, Any]]:
        """
        提取所有圣遗物的完整信息
        
        返回:
            完整的圣遗物信息列表
        """
        self.logger.info("开始提取所有圣遗物信息...")
        
        all_relics = []
        relics_with_story = 0
        
        for relic_data in self.reliquaries:
            relic_id = relic_data.get('id')
            
            if not relic_id:
                continue
            
            relic_info = self.extract_reliquary_info(relic_data)
            if relic_info:
                all_relics.append(relic_info)
                
                if relic_info.get('has_story'):
                    relics_with_story += 1
        
        self.logger.info(f"成功提取 {len(all_relics)} 个圣遗物信息")
        self.logger.info(f"其中 {relics_with_story} 个圣遗物包含故事")
        
        return all_relics
    
    def extract_sets(self) -> List[Dict[str, Any]]:
        """
        按套装组织提取圣遗物信息
        
        返回:
            套装信息列表，每个套装包含其所有部位
        """
        self.logger.info("开始按套装提取圣遗物信息...")
        
        # 首先提取所有圣遗物
        all_relics = self.extract_all()
        
        # 按套装组织
        all_sets = self.set_extractor.extract_sets(all_relics, self.relic_sets)
        
        self.logger.info(f"成功提取 {len(all_sets)} 个圣遗物套装")
        sets_with_full_story = sum(1 for s in all_sets if s.get('has_full_story'))
        self.logger.info(f"其中 {sets_with_full_story} 个套装包含完整故事")
        
        return all_sets
    
    def save_to_file(self, output_file: str, data: Optional[List[Dict]] = None,
                     organize_by_set: bool = True) -> None:
        """
        保存圣遗物数据到文件
        
        参数:
            output_file: 输出文件路径
            data: 圣遗物数据列表，如果为 None 则提取所有
            organize_by_set: 是否按套装组织数据
        """
        if data is None:
            data = self.extract_sets() if organize_by_set else self.extract_all()
        
        super().save_to_file(output_file, data)
    
    def get_relics_by_set(self, set_id: int) -> List[Dict]:
        """
        获取指定套装的所有圣遗物
        
        参数:
            set_id: 套装 ID
        
        返回:
            该套装的所有圣遗物
        """
        all_relics = self.extract_all()
        return [r for r in all_relics if r.get('set_id') == set_id]
    
    def get_relics_by_rarity(self, rank_level: int) -> List[Dict]:
        """
        按稀有度筛选圣遗物
        
        参数:
            rank_level: 稀有度等级 (1-5 星)
        
        返回:
            该稀有度的所有圣遗物
        """
        all_relics = self.extract_all()
        return [r for r in all_relics if r.get('rank_level') == rank_level]
