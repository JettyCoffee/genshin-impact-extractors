"""
角色数据加载器
负责加载角色相关的配置数据
"""

from typing import Dict, List

from ...core import get_data_path, load_json, setup_logger


class AvatarDataLoader:
    """角色数据加载器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def load_avatars(self) -> Dict[int, Dict]:
        """
        加载角色配置数据
        
        返回:
            以角色 ID 为键的字典
        """
        avatar_file = get_data_path('ExcelBinOutput/AvatarExcelConfigData.json')
        avatars = load_json(str(avatar_file))
        return {avatar['id']: avatar for avatar in avatars if 'id' in avatar}
    
    def load_fetter_info(self) -> Dict[int, Dict]:
        """
        加载角色资料配置数据
        
        返回:
            以 avatarId 为键的字典
        """
        try:
            fetter_file = get_data_path('ExcelBinOutput/FetterInfoExcelConfigData.json')
            fetter_list = load_json(str(fetter_file))
            return {item['avatarId']: item for item in fetter_list if 'avatarId' in item}
        except Exception as e:
            self.logger.warning(f"无法加载 FetterInfoExcelConfigData.json: {e}")
            return {}
    
    def load_fetter_stories(self) -> List[Dict]:
        """
        加载角色故事配置数据
        
        返回:
            故事数据列表
        """
        try:
            story_file = get_data_path('ExcelBinOutput/FetterStoryExcelConfigData.json')
            return load_json(str(story_file))
        except Exception as e:
            self.logger.warning(f"无法加载 FetterStoryExcelConfigData.json: {e}")
            return []
    
    def load_fetters(self) -> List[Dict]:
        """
        加载语音配置数据
        
        返回:
            语音数据列表
        """
        try:
            fetter_file = get_data_path('ExcelBinOutput/FettersExcelConfigData.json')
            return load_json(str(fetter_file))
        except Exception as e:
            self.logger.warning(f"无法加载 FettersExcelConfigData.json: {e}")
            return []
