"""
角色提取器主类
整合各个子模块，提供统一的角色数据提取接口
"""

from typing import Any, Dict, List, Optional

from ..base import BaseExtractor
from .data_loader import AvatarDataLoader
from .info_extractor import AvatarInfoExtractor, AvatarProfileExtractor
from .story_extractor import AvatarStoryExtractor
from .voice_extractor import AvatarVoiceExtractor


class AvatarExtractor(BaseExtractor):
    """角色信息提取器"""
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化角色提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP 等)
        """
        super().__init__(language)
        
        # 初始化数据加载器
        self.data_loader = AvatarDataLoader()
        
        # 初始化各子提取器
        self.info_extractor = AvatarInfoExtractor(self.text_parser)
        self.profile_extractor = AvatarProfileExtractor(self.text_parser)
        self.story_extractor = AvatarStoryExtractor(self.text_parser)
        self.voice_extractor = AvatarVoiceExtractor(self.text_parser, language)
        
        # 加载数据
        self.logger.info("加载角色数据...")
        self.avatars = self.data_loader.load_avatars()
        self.fetter_info = self.data_loader.load_fetter_info()
        self.fetter_stories = self.data_loader.load_fetter_stories()
        self.fetters = self.data_loader.load_fetters()
        
        self.logger.info(
            f"成功加载 {len(self.avatars)} 个角色配置, "
            f"{len(self.fetter_info)} 个角色资料, "
            f"{len(self.fetter_stories)} 个角色故事, "
            f"{len(self.fetters)} 个语音"
        )
    
    def extract_avatar_info(self, avatar_id: int) -> Optional[Dict[str, Any]]:
        """
        提取单个角色的完整信息
        
        参数:
            avatar_id: 角色 ID
        
        返回:
            结构化的角色信息，如果角色无效则返回 None
        """
        if avatar_id not in self.avatars:
            self.logger.debug(f"角色 ID {avatar_id} 不存在")
            return None
        
        avatar_data = self.avatars[avatar_id]
        
        # 提取基础信息
        info = self.info_extractor.extract_basic_info(avatar_id, avatar_data)
        if not info:
            return None
        
        # 提取个人资料
        info['profile'] = self.profile_extractor.extract_profile(avatar_id, self.fetter_info)
        
        # 提取故事
        stories = self.story_extractor.extract_stories(avatar_id, self.fetter_stories)
        info['stories'] = stories
        info['story_count'] = len(stories)
        
        # 提取语音
        voice_overs = self.voice_extractor.extract_voices(avatar_id, self.fetters)
        info['voice_overs'] = voice_overs
        info['voice_count'] = len(voice_overs)
        
        return info
    
    def extract_all(self, skip_test_avatars: bool = True) -> List[Dict[str, Any]]:
        """
        提取所有角色的完整信息
        
        参数:
            skip_test_avatars: 是否跳过测试角色（ID >= 11000000 的角色）
        
        返回:
            完整的角色信息列表
        """
        self.logger.info("开始提取所有角色信息...")
        
        all_avatars = []
        
        for avatar_id in self.avatars.keys():
            # 跳过测试角色
            if skip_test_avatars and avatar_id >= 11000000:
                continue
            
            # 提取角色信息
            avatar_info = self.extract_avatar_info(avatar_id)
            if avatar_info:
                all_avatars.append(avatar_info)
                self.logger.debug(
                    f"已提取角色: {avatar_info['name']} (ID: {avatar_id}, "
                    f"故事: {avatar_info['story_count']}, 语音: {avatar_info['voice_count']})"
                )
        
        self.logger.info(f"成功提取 {len(all_avatars)} 个角色信息")
        avatars_with_stories = sum(1 for a in all_avatars if a.get('story_count', 0) > 0)
        avatars_with_voices = sum(1 for a in all_avatars if a.get('voice_count', 0) > 0)
        self.logger.info(f"其中 {avatars_with_stories} 个角色有故事, {avatars_with_voices} 个角色有语音")
        
        return all_avatars
    
    def get_avatars_by_weapon_type(self, weapon_type: str) -> List[Dict]:
        """
        按武器类型筛选角色
        
        参数:
            weapon_type: 武器类型
        
        返回:
            该武器类型的所有角色
        """
        all_avatars = self.extract_all()
        return [a for a in all_avatars if a.get('weapon_type') == weapon_type]
    
    def get_avatars_by_body_type(self, body_type: str) -> List[Dict]:
        """
        按身体类型筛选角色
        
        参数:
            body_type: 身体类型
        
        返回:
            该身体类型的所有角色
        """
        all_avatars = self.extract_all()
        return [a for a in all_avatars if a.get('body_type') == body_type]
