"""
书籍数据加载器
"""

from typing import Dict, List, Set

from ...core import get_data_path, load_json, setup_logger


class BookDataLoader:
    """书籍数据加载器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def load_documents(self) -> List[Dict]:
        """
        加载 Document 配置数据
        
        返回:
            文档数据列表
        """
        doc_file = get_data_path('ExcelBinOutput/DocumentExcelConfigData.json')
        return load_json(str(doc_file))
    
    def load_books_codex(self) -> List[Dict]:
        """
        加载书籍分类配置数据
        
        返回:
            书籍分类数据列表
        """
        try:
            codex_file = get_data_path('ExcelBinOutput/BooksCodexExcelConfigData.json')
            return load_json(str(codex_file))
        except Exception as e:
            self.logger.warning(f"无法加载 BooksCodexExcelConfigData.json: {e}")
            return []
    
    def get_weapon_story_ids(self) -> Set[int]:
        """
        获取所有武器故事的 Document ID 集合
        
        返回:
            武器故事 ID 集合
        """
        weapon_file = get_data_path('ExcelBinOutput/WeaponExcelConfigData.json')
        weapons = load_json(str(weapon_file))
        return {w.get('storyId') for w in weapons if w.get('storyId', 0) > 0}
    
    def get_relic_story_ids(self) -> Set[int]:
        """
        获取所有圣遗物故事的 Document ID 集合
        
        返回:
            圣遗物故事 ID 集合
        """
        relic_file = get_data_path('ExcelBinOutput/ReliquaryExcelConfigData.json')
        relics = load_json(str(relic_file))
        return {r.get('storyId') for r in relics if r.get('storyId', 0) > 0}
