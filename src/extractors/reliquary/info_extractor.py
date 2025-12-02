"""
圣遗物信息提取器
提取单个圣遗物的基本属性和故事
"""

from typing import Any, Dict, Optional

from ...core import TextMapParser, StoryContentExtractor
from ...models import EquipTypes


class ReliquaryInfoExtractor:
    """圣遗物信息提取器"""
    
    def __init__(self, text_parser: TextMapParser, story_extractor: StoryContentExtractor):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
            story_extractor: 故事内容提取器
        """
        self.text_parser = text_parser
        self.story_extractor = story_extractor
    
    def extract_info(self, relic_data: Dict) -> Optional[Dict[str, Any]]:
        """
        提取单个圣遗物的信息
        
        参数:
            relic_data: 圣遗物原始数据
        
        返回:
            结构化的圣遗物信息，如果无效则返回 None
        """
        relic_id = relic_data.get('id')
        
        # 获取圣遗物名称
        name = self.text_parser.get_text(relic_data.get('nameTextMapHash', 0))
        
        # 如果没有名称，跳过
        if not name:
            return None
        
        equip_type = relic_data.get('equipType', '')
        
        info = {
            'id': relic_id,
            'name': name,
            'description': self.text_parser.get_text(relic_data.get('descTextMapHash', 0)),
            'set_id': relic_data.get('setId', 0),
            'equip_type': equip_type,
            'equip_type_name': EquipTypes.get_name(equip_type),
            'rank_level': relic_data.get('rankLevel', 0),
            'icon': relic_data.get('icon', ''),
            'max_level': relic_data.get('maxLevel', 0),
        }
        
        # 提取故事内容
        story_id = relic_data.get('storyId', 0)
        if story_id:
            story_content = self.story_extractor.get_story_content(story_id)
            if story_content:
                info['story'] = story_content
                info['has_story'] = True
            else:
                info['has_story'] = False
        else:
            info['has_story'] = False
        
        return info
