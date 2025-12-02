"""
角色故事提取器
提取角色的故事文本
"""

from typing import Any, Dict, List

from ...core import TextMapParser


class AvatarStoryExtractor:
    """角色故事提取器"""
    
    def __init__(self, text_parser: TextMapParser):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
        """
        self.text_parser = text_parser
    
    def extract_stories(self, avatar_id: int, fetter_stories: List[Dict]) -> List[Dict[str, Any]]:
        """
        提取角色故事
        
        参数:
            avatar_id: 角色 ID
            fetter_stories: 所有角色的故事数据列表
        
        返回:
            该角色的故事列表
        """
        avatar_stories = [s for s in fetter_stories if s.get('avatarId') == avatar_id]
        
        stories = []
        for story in avatar_stories:
            title = self.text_parser.get_text(story.get('storyTitleTextMapHash', 0))
            content = self.text_parser.get_text(story.get('storyContextTextMapHash', 0))
            
            if title and content:
                stories.append({
                    'fetter_id': story.get('fetterId', 0),
                    'title': title,
                    'content': content
                })
        
        return stories
