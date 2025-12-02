"""
角色语音提取器
提取角色的语音文本
"""

from typing import Any, Dict, List

from ...core import TextMapParser


class AvatarVoiceExtractor:
    """角色语音提取器"""
    
    def __init__(self, text_parser: TextMapParser, language: str = 'CHS'):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
            language: 语言代码
        """
        self.text_parser = text_parser
        self.language = language
    
    def extract_voices(self, avatar_id: int, fetters: List[Dict]) -> List[Dict[str, Any]]:
        """
        提取角色语音
        
        参数:
            avatar_id: 角色 ID
            fetters: 所有角色的语音数据列表
        
        返回:
            该角色的语音列表
        """
        avatar_fetters = [f for f in fetters if f.get('avatarId') == avatar_id]
        
        voice_overs = []
        for fetter in avatar_fetters:
            title = self.text_parser.get_text(fetter.get('voiceTitleTextMapHash', 0))
            content = self.text_parser.get_text(fetter.get('voiceFileTextTextMapHash', 0))
            
            if title and content:
                vo_entry = {
                    'fetter_id': fetter.get('fetterId', 0),
                    'title': title,
                    'content': content,
                    'voice_file': fetter.get('voiceFile', '')
                }
                
                # 提取关系信息（如果标题是"关于..."）
                relation = self._extract_relation(title)
                if relation:
                    vo_entry['relation'] = relation
                
                voice_overs.append(vo_entry)
        
        return voice_overs
    
    def _extract_relation(self, title: str) -> str:
        """
        从标题中提取关系信息
        
        参数:
            title: 语音标题
        
        返回:
            关系描述，如果不是关系语音则返回空字符串
        """
        if self.language == 'CHS':
            if title.startswith('关于'):
                return title[2:]
        elif self.language == 'EN':
            if title.startswith('About '):
                return title[6:]
        
        return ''
