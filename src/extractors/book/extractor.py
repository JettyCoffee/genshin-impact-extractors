"""
书籍提取器主类
"""

from typing import Any, Dict, List, Optional

from ..base import BaseExtractor
from ...core import StoryContentExtractor
from ...models import DocumentTypes
from .data_loader import BookDataLoader
from .type_checker import BookTypeChecker
from .info_extractor import BookInfoExtractor
from .series_extractor import BookSeriesExtractor


class BookExtractor(BaseExtractor):
    """书籍信息提取器"""
    
    # 导出 DOC_TYPES 以保持向后兼容
    DOC_TYPES = DocumentTypes.NAMES
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化书籍提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP 等)
        """
        super().__init__(language)
        
        # 初始化故事提取器
        self.story_extractor = StoryContentExtractor(language)
        
        # 初始化数据加载器
        self.data_loader = BookDataLoader()
        
        # 加载数据
        self.logger.info("加载书籍、武器和圣遗物数据...")
        self.documents = self.data_loader.load_documents()
        self.books_codex = self.data_loader.load_books_codex()
        weapon_story_ids = self.data_loader.get_weapon_story_ids()
        relic_story_ids = self.data_loader.get_relic_story_ids()
        
        # 初始化类型判断器
        self.type_checker = BookTypeChecker(weapon_story_ids, relic_story_ids)
        
        # 初始化子模块
        self.info_extractor = BookInfoExtractor(
            self.text_parser,
            self.story_extractor,
            self.type_checker,
            self.books_codex
        )
        self.series_extractor = BookSeriesExtractor()
        
        total_docs = len(self.documents)
        pure_books = total_docs - len(weapon_story_ids) - len(relic_story_ids)
        self.logger.info(
            f"成功加载 {total_docs} 个 Documents "
            f"(武器故事: {len(weapon_story_ids)}, "
            f"圣遗物故事: {len(relic_story_ids)}, "
            f"纯书籍: {pure_books})"
        )
    
    def extract_book_info(self, doc_data: Dict, book_type: str = 'regular') -> Optional[Dict[str, Any]]:
        """
        提取单个书籍的信息
        
        参数:
            doc_data: Document 原始数据
            book_type: 书籍类型
        
        返回:
            结构化的书籍信息
        """
        return self.info_extractor.extract_info(doc_data, book_type)
    
    def extract_all(self, include_all_types: bool = True, book_type: str = 'regular') -> List[Dict[str, Any]]:
        """
        提取所有书籍的完整信息
        
        参数:
            include_all_types: 是否包括所有类型（Letter, Paged, Video 等）
            book_type: 书籍类型 ('regular', 'costume', 'windglider', 'all')
        
        返回:
            完整的书籍信息列表
        """
        type_name = {
            'regular': '普通书籍',
            'costume': '皮肤',
            'windglider': '风之翼',
            'all': '所有文档'
        }.get(book_type, book_type)
        
        self.logger.info(f"开始提取{type_name}信息...")
        
        all_books = []
        books_with_content = 0
        
        for doc_data in self.documents:
            doc_id = doc_data.get('id')
            
            if not doc_id:
                continue
            
            # 如果只要 Book 类型，过滤其他类型
            if not include_all_types:
                if doc_data.get('documentType') != 'Book':
                    continue
            
            book_info = self.extract_book_info(doc_data, book_type=book_type)
            if book_info:
                all_books.append(book_info)
                
                if book_info.get('has_content'):
                    books_with_content += 1
        
        self.logger.info(f"成功提取 {len(all_books)} 个{type_name}信息")
        self.logger.info(f"其中 {books_with_content} 个包含内容")
        
        return all_books
    
    def extract_by_type(self, doc_type: str) -> List[Dict[str, Any]]:
        """
        按类型提取书籍
        
        参数:
            doc_type: Document 类型 (Book, Letter, Paged, Video)
        
        返回:
            该类型的所有书籍
        """
        self.logger.info(f"提取类型为 {doc_type} 的书籍...")
        
        books = []
        for doc_data in self.documents:
            if doc_data.get('documentType') == doc_type:
                book_info = self.extract_book_info(doc_data)
                if book_info:
                    books.append(book_info)
        
        self.logger.info(f"成功提取 {len(books)} 个 {doc_type} 类型的书籍")
        return books
    
    def extract_series(self) -> List[Dict[str, Any]]:
        """
        按系列组织书籍
        
        返回:
            书籍系列列表
        """
        self.logger.info("开始按系列组织书籍...")
        
        all_books = self.extract_all(include_all_types=True)
        all_series = self.series_extractor.extract_series(all_books)
        standalone_books = self.series_extractor.get_standalone_books(all_books)
        
        self.logger.info(f"成功组织 {len(all_series)} 个书籍系列")
        self.logger.info(f"独立书籍: {len(standalone_books)} 本")
        series_with_full_content = sum(1 for s in all_series if s.get('has_full_content'))
        self.logger.info(f"有完整内容的系列: {series_with_full_content} 个")
        
        return all_series
    
    def extract_costumes(self) -> List[Dict[str, Any]]:
        """提取所有皮肤信息"""
        return self.extract_all(include_all_types=True, book_type='costume')
    
    def extract_windgliders(self) -> List[Dict[str, Any]]:
        """提取所有风之翼信息"""
        return self.extract_all(include_all_types=True, book_type='windglider')
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取书籍统计信息"""
        all_books = self.extract_all(include_all_types=True)
        
        type_stats = {}
        for book in all_books:
            doc_type = book.get('document_type', 'Unknown')
            type_stats[doc_type] = type_stats.get(doc_type, 0) + 1
        
        has_content = sum(1 for b in all_books if b.get('has_content'))
        
        return {
            'total_count': len(all_books),
            'with_content_count': has_content,
            'without_content_count': len(all_books) - has_content,
            'type_distribution': type_stats
        }
