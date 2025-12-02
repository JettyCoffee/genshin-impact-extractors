"""
角色基础信息提取器
提取角色的基本属性（名称、武器类型、身体类型等）
"""

from typing import Any, Dict, Optional

from ...core import TextMapParser
from ...models import BodyTypes, WeaponTypes


class AvatarInfoExtractor:
    """角色基础信息提取器"""
    
    def __init__(self, text_parser: TextMapParser):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
        """
        self.text_parser = text_parser
    
    def extract_basic_info(self, avatar_id: int, avatar_data: Dict) -> Optional[Dict[str, Any]]:
        """
        提取角色基础信息
        
        参数:
            avatar_id: 角色 ID
            avatar_data: 角色原始数据
        
        返回:
            角色基础信息字典，如果无效则返回 None
        """
        # 获取角色名称
        name = self.text_parser.get_text(avatar_data.get('nameTextMapHash', 0))
        
        # 如果没有名称，跳过（可能是测试数据）
        if not name:
            return None
        
        body_type = avatar_data.get('bodyType', '')
        weapon_type = avatar_data.get('weaponType', '')
        
        return {
            'id': avatar_id,
            'name': name,
            'description': self.text_parser.get_text(avatar_data.get('descTextMapHash', 0)),
            'body_type': body_type,
            'body_type_name': BodyTypes.get_name(body_type),
            'weapon_type': weapon_type,
            'weapon_type_name': WeaponTypes.get_name(weapon_type),
            'icon': avatar_data.get('iconName', ''),
            'quality_type': avatar_data.get('qualityType', ''),
        }


class AvatarProfileExtractor:
    """角色个人资料提取器"""
    
    def __init__(self, text_parser: TextMapParser):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
        """
        self.text_parser = text_parser
    
    def extract_profile(self, avatar_id: int, fetter_info: Dict[int, Dict]) -> Dict[str, Any]:
        """
        提取角色个人资料
        
        参数:
            avatar_id: 角色 ID
            fetter_info: 角色资料数据映射
        
        返回:
            角色资料字典
        """
        if avatar_id not in fetter_info:
            return {}
        
        info = fetter_info[avatar_id]
        
        return {
            'title': self.text_parser.get_text(info.get('avatarTitleTextMapHash', 0)),
            'detail': self.text_parser.get_text(info.get('avatarDetailTextMapHash', 0)),
            'constellation': self.text_parser.get_text(info.get('avatarConstellationBeforTextMapHash', 0)),
            'native': self.text_parser.get_text(info.get('avatarNativeTextMapHash', 0)),
            'vision': self.text_parser.get_text(info.get('avatarVisionBeforTextMapHash', 0)),
            'cv': {
                'chinese': self.text_parser.get_text(info.get('cvChineseTextMapHash', 0)),
                'japanese': self.text_parser.get_text(info.get('cvJapaneseTextMapHash', 0)),
                'english': self.text_parser.get_text(info.get('cvEnglishTextMapHash', 0)),
                'korean': self.text_parser.get_text(info.get('cvKoreanTextMapHash', 0))
            },
            'birthday': f"{info.get('infoBirthMonth', 0)}/{info.get('infoBirthDay', 0)}"
        }
