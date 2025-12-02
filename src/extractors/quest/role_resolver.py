"""
角色名称解析器
解析对话中的角色名称
"""

from typing import Any, Dict

from ...core import TextMapParser
from ...models import TalkRoleTypes


class RoleNameResolver:
    """角色名称解析器"""
    
    def __init__(
        self,
        text_parser: TextMapParser,
        npc_config: Dict[int, Dict],
        avatar_config: Dict[int, Dict]
    ):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
            npc_config: NPC 配置映射
            avatar_config: 角色配置映射
        """
        self.text_parser = text_parser
        self.npc_config = npc_config
        self.avatar_config = avatar_config
    
    def get_role_name(self, role_type: str, role_id: Any) -> str:
        """
        解析角色名称
        
        参数:
            role_type: 角色类型
            role_id: 角色 ID
        
        返回:
            角色名称
        """
        if role_type == TalkRoleTypes.PLAYER:
            return '旅行者'
        
        # 尝试转换 ID 为整数
        try:
            role_id_int = int(role_id)
        except (ValueError, TypeError):
            return 'Unknown'
        
        # 尝试从 NPC 配置获取
        if role_type in [TalkRoleTypes.NPC, TalkRoleTypes.GADGET]:
            if role_id_int in self.npc_config:
                name_hash = self.npc_config[role_id_int].get('nameTextMapHash')
                if name_hash:
                    name = self.text_parser.get_text(name_hash)
                    if name:
                        return name
        
        # 尝试从 Avatar 配置获取
        if role_id_int in self.avatar_config:
            name_hash = self.avatar_config[role_id_int].get('nameTextMapHash')
            if name_hash:
                name = self.text_parser.get_text(name_hash)
                if name:
                    return name
        
        return 'Unknown'
