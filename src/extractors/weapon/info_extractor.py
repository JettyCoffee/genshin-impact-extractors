"""
武器信息提取器
提取武器的基本属性和故事
"""

from typing import Any, Dict, Optional

from ...core import TextMapParser, StoryContentExtractor, setup_logger
from ...models import IDOffsets


class WeaponInfoExtractor:
    """武器信息提取器"""
    
    def __init__(self, text_parser: TextMapParser, story_extractor: StoryContentExtractor):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
            story_extractor: 故事内容提取器
        """
        self.text_parser = text_parser
        self.story_extractor = story_extractor
        self.logger = setup_logger(__name__)
    
    def extract_info(self, weapon_data: Dict) -> Optional[Dict[str, Any]]:
        """
        提取单个武器的信息
        
        参数:
            weapon_data: 武器原始数据
        
        返回:
            结构化的武器信息，如果武器无效则返回 None
        """
        weapon_id = weapon_data.get('id')
        
        # 获取武器名称
        name = self.text_parser.get_text(weapon_data.get('nameTextMapHash', 0))
        
        # 如果没有名称，跳过该武器（可能是测试数据）
        if not name:
            return None
        
        # 提取基础信息
        info = {
            'id': weapon_id,
            'name': name,
            'description': self.text_parser.get_text(weapon_data.get('descTextMapHash', 0)),
            'weapon_type': weapon_data.get('weaponType', ''),
            'rank_level': weapon_data.get('rankLevel', 0),
            'icon': weapon_data.get('icon', ''),
        }
        
        # 提取属性数据
        self._extract_stats(info, weapon_data)
        
        # 提取故事内容
        self._extract_story(info, weapon_id, weapon_data)
        
        return info
    
    def _extract_stats(self, info: Dict, weapon_data: Dict) -> None:
        """
        提取武器属性数据
        
        参数:
            info: 武器信息字典（会被修改）
            weapon_data: 武器原始数据
        """
        weapon_props = weapon_data.get('weaponProp', [])
        if not weapon_props:
            return
        
        # 主属性（通常是攻击力）
        if len(weapon_props) > 0:
            main_prop = weapon_props[0]
            info['main_stat'] = {
                'type': main_prop.get('propType', ''),
                'init_value': main_prop.get('initValue', 0),
                'curve': main_prop.get('type', '')
            }
        
        # 副属性
        if len(weapon_props) > 1:
            sub_prop = weapon_props[1]
            if sub_prop.get('propType') != 'FIGHT_PROP_NONE':
                info['sub_stat'] = {
                    'type': sub_prop.get('propType', ''),
                    'init_value': sub_prop.get('initValue', 0),
                    'curve': sub_prop.get('type', '')
                }
    
    def _extract_story(self, info: Dict, weapon_id: int, weapon_data: Dict) -> None:
        """
        提取武器故事
        
        参数:
            info: 武器信息字典（会被修改）
            weapon_id: 武器 ID
            weapon_data: 武器原始数据
        """
        story_id = weapon_data.get('storyId', 0)
        
        if not story_id:
            info['has_story'] = False
            return
        
        # 验证 ID 映射规律
        expected_story_id = weapon_id + IDOffsets.WEAPON_STORY
        if story_id != expected_story_id:
            self.logger.warning(
                f"武器 {weapon_id} 的 storyId {story_id} 不符合映射规律 "
                f"(预期: {expected_story_id})"
            )
        
        # 提取故事内容
        story_content = self.story_extractor.get_story_content(story_id)
        if story_content:
            info['story'] = story_content
            info['has_story'] = True
        else:
            info['has_story'] = False
