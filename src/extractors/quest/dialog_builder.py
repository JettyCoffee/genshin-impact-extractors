"""
对话树构建器
从 dialogList 构建对话树结构
"""

from typing import Any, Dict, List, Optional, Set

from ...core import TextMapParser
from ...models import DialogFieldMap, TalkFieldMap
from .role_resolver import RoleNameResolver


class DialogTreeBuilder:
    """对话树构建器"""
    
    def __init__(self, text_parser: TextMapParser, role_resolver: RoleNameResolver):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
            role_resolver: 角色名称解析器
        """
        self.text_parser = text_parser
        self.role_resolver = role_resolver
    
    def build_tree(self, dialog_list: List[Dict], visited: Optional[Set[int]] = None) -> List[Dict]:
        """
        从 dialogList 构建对话树
        
        参数:
            dialog_list: 对话列表（来自 Talk 文件的 dialogList）
            visited: 已访问的对话 ID 集合
        
        返回:
            对话树列表
        """
        if not dialog_list:
            return []
        
        if visited is None:
            visited = set()
        
        # 解码对话列表
        decoded_list = [DialogFieldMap.decode(d) for d in dialog_list]
        
        # 构建 ID 到对话数据的映射
        dialog_map = {d['id']: d for d in decoded_list}
        
        # 找出所有被引用的对话 ID（非根节点）
        referenced_ids = set()
        for dialog in decoded_list:
            for next_id in dialog.get('nextDialogs', []):
                referenced_ids.add(next_id)
        
        # 根节点是没有被引用的对话
        root_ids = [d['id'] for d in decoded_list if d['id'] not in referenced_ids]
        
        # 如果没有找到根节点，使用第一个对话作为根
        if not root_ids and decoded_list:
            root_ids = [decoded_list[0]['id']]
        
        trees = []
        for root_id in root_ids:
            tree = self._build_node(root_id, dialog_map, visited.copy())
            if tree:
                trees.append(tree)
        
        return trees
    
    def _build_node(self, dialog_id: int, dialog_map: Dict[int, Dict],
                    visited: Set[int]) -> Optional[Dict[str, Any]]:
        """
        递归构建对话节点
        
        参数:
            dialog_id: 对话 ID
            dialog_map: 对话 ID 到数据的映射
            visited: 已访问的对话 ID 集合
        
        返回:
            对话节点字典
        """
        if dialog_id in visited:
            return None
        if dialog_id not in dialog_map:
            return None
        
        visited.add(dialog_id)
        dialog = dialog_map[dialog_id]
        
        # 提取角色信息
        role_info = dialog.get('talkRole', {})
        role_type = role_info.get('type', role_info.get('_type', ''))
        role_id = role_info.get('id', role_info.get('_id', ''))
        
        # 获取角色名
        role_name = self.role_resolver.get_role_name(role_type, role_id)
        
        # 获取文本
        text_hash = dialog.get('talkContentTextMapHash')
        text = self.text_parser.get_text(text_hash) if text_hash else ''
        
        node = {
            'id': dialog_id,
            'role': role_name,
            'role_type': role_type,
            'role_id': str(role_id),
            'text': text,
            'next': []
        }
        
        # 递归处理子节点
        for next_id in dialog.get('nextDialogs', []):
            child = self._build_node(next_id, dialog_map, visited.copy())
            if child:
                node['next'].append(child)
        
        return node
    
    def process_talk(self, talk_data: Dict) -> Optional[List[Dict]]:
        """
        处理一个 Talk（对话序列）
        
        参数:
            talk_data: Talk 原始数据
        
        返回:
            对话树列表
        """
        # 解码 Talk 数据
        decoded_talk = TalkFieldMap.decode(talk_data)
        
        # 获取对话列表
        dialog_list = decoded_talk.get('dialogList', [])
        if not dialog_list:
            return None
        
        return self.build_tree(dialog_list)
