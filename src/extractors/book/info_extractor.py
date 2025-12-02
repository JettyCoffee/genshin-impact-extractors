"""
书籍信息提取器
提取单个书籍的基本属性和内容
"""

from typing import Any, Dict, List, Optional

from ...core import TextMapParser, StoryContentExtractor
from ...models import DocumentTypes
from .type_checker import BookTypeChecker


class BookInfoExtractor:
    """书籍信息提取器"""
    
    def __init__(
        self,
        text_parser: TextMapParser,
        story_extractor: StoryContentExtractor,
        type_checker: BookTypeChecker,
        books_codex: List[Dict]
    ):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
            story_extractor: 故事内容提取器
            type_checker: 书籍类型判断器
            books_codex: 书籍分类数据
        """
        self.text_parser = text_parser
        self.story_extractor = story_extractor
        self.type_checker = type_checker
        self.books_codex = books_codex
    
    def extract_info(self, doc_data: Dict, book_type: str = 'regular') -> Optional[Dict[str, Any]]:
        """
        提取单个书籍的信息
        
        参数:
            doc_data: Document 原始数据
            book_type: 书籍类型 ('regular', 'costume', 'windglider', 'all')
        
        返回:
            结构化的书籍信息，如果无效则返回 None
        """
        doc_id = doc_data.get('id')
        
        # 根据 book_type 过滤
        if not self._should_include(doc_id, book_type):
            return None
        
        # 获取书籍标题
        title = self.text_parser.get_text(doc_data.get('titleTextMapHash', 0))
        if not title:
            return None
        
        # 提取基础信息
        doc_type = doc_data.get('documentType', 'Book')
        info = {
            'id': doc_id,
            'title': title,
            'document_type': doc_type,
            'document_type_name': DocumentTypes.get_name(doc_type),
            'preview_path': doc_data.get('previewPath', ''),
        }
        
        # 标记特殊类型
        if self.type_checker.is_costume_doc(doc_id):
            info['special_type'] = 'costume'
        elif self.type_checker.is_windglider_doc(doc_id):
            info['special_type'] = 'windglider'
        
        # 提取系列信息（仅对普通书籍）
        if book_type == 'regular':
            series_name = self._extract_series_name(title)
            if series_name:
                info['series_name'] = series_name
                info['is_series'] = True
            else:
                info['is_series'] = False
        
        # 从 BooksCodexExcelConfigData 获取分类信息
        codex_info = self._get_book_codex_info(doc_id)
        if codex_info:
            info['sort_order'] = codex_info.get('sortOrder', 0)
        
        # 提取内容
        quest_id_list = doc_data.get('questIDList', [])
        if quest_id_list:
            content = self.story_extractor.get_story_content(doc_id)
            if content:
                info['content'] = content
                info['has_content'] = True
            else:
                info['has_content'] = False
        else:
            info['has_content'] = False
        
        # 其他元数据
        info['subtitle_id'] = doc_data.get('subtitleID', 0)
        info['split_type'] = doc_data.get('splitType', '')
        
        return info
    
    def _should_include(self, doc_id: int, book_type: str) -> bool:
        """判断是否应该包含此文档"""
        if book_type == 'regular':
            return self.type_checker.is_regular_book(doc_id)
        elif book_type == 'costume':
            return self.type_checker.is_costume_doc(doc_id)
        elif book_type == 'windglider':
            return self.type_checker.is_windglider_doc(doc_id)
        elif book_type == 'all':
            return self.type_checker.is_pure_book(doc_id)
        return False
    
    def _extract_series_name(self, title: str) -> Optional[str]:
        """从标题中提取系列名称"""
        volume_markers = ['·卷', '·第', '篇', '（上）', '（下）', '（中）']
        
        for marker in volume_markers:
            if marker in title:
                series_name = title.split(marker)[0].strip()
                if '·' in series_name:
                    return series_name.split('·')[0].strip()
                return series_name
        
        if '·' in title:
            parts = title.split('·')
            if len(parts) >= 2:
                series_name = parts[0].strip()
                second_part = parts[1].strip()
                if any(keyword in second_part for keyword in ['卷', '篇', '章', '上', '下', '中']):
                    return series_name
        
        return None
    
    def _get_book_codex_info(self, doc_id: int) -> Optional[Dict]:
        """从 BooksCodexExcelConfigData 获取书籍的分类信息"""
        for codex in self.books_codex:
            if codex.get('materialId') == doc_id:
                return codex
        return None
