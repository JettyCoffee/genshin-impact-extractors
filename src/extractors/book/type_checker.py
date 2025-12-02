"""
书籍类型判断器
判断文档是否为纯书籍、皮肤、风之翼等
"""

from typing import Set

from ...models import IDOffsets


class BookTypeChecker:
    """书籍类型判断器"""
    
    def __init__(self, weapon_story_ids: Set[int], relic_story_ids: Set[int]):
        """
        初始化
        
        参数:
            weapon_story_ids: 武器故事 ID 集合
            relic_story_ids: 圣遗物故事 ID 集合
        """
        self.weapon_story_ids = weapon_story_ids
        self.relic_story_ids = relic_story_ids
    
    def is_pure_book(self, doc_id: int) -> bool:
        """
        判断是否是纯书籍（不是武器或圣遗物的故事）
        
        参数:
            doc_id: Document ID
        
        返回:
            True 表示是纯书籍
        """
        return (doc_id not in self.weapon_story_ids and 
                doc_id not in self.relic_story_ids)
    
    def is_costume_doc(self, doc_id: int) -> bool:
        """
        判断是否是皮肤文档
        
        参数:
            doc_id: Document ID
        
        返回:
            True 表示是皮肤文档
        """
        return IDOffsets.COSTUME_MIN <= doc_id < IDOffsets.COSTUME_MAX
    
    def is_windglider_doc(self, doc_id: int) -> bool:
        """
        判断是否是风之翼文档
        
        参数:
            doc_id: Document ID
        
        返回:
            True 表示是风之翼文档
        """
        return IDOffsets.WINDGLIDER_MIN <= doc_id < IDOffsets.WINDGLIDER_MAX
    
    def is_regular_book(self, doc_id: int) -> bool:
        """
        判断是否是普通书籍（排除武器、圣遗物、皮肤、风之翼）
        
        参数:
            doc_id: Document ID
        
        返回:
            True 表示是普通书籍
        """
        return (self.is_pure_book(doc_id) and 
                not self.is_costume_doc(doc_id) and 
                not self.is_windglider_doc(doc_id))
    
    def get_book_type(self, doc_id: int) -> str:
        """
        获取书籍类型
        
        参数:
            doc_id: Document ID
        
        返回:
            书籍类型字符串
        """
        if not self.is_pure_book(doc_id):
            return 'other'
        if self.is_costume_doc(doc_id):
            return 'costume'
        if self.is_windglider_doc(doc_id):
            return 'windglider'
        return 'regular'
