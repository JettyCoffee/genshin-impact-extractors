"""
书籍提取器
提取纯书籍内容（不包括武器和圣遗物的故事）
"""

from typing import Dict, List, Any, Optional, Set

# 支持作为模块导入和直接运行
try:
    from .utils import (
        load_json, save_json, get_data_path,
        setup_logger, TextMapParser, StoryContentExtractor
    )
except ImportError:
    from utils import (
        load_json, save_json, get_data_path,
        setup_logger, TextMapParser, StoryContentExtractor
    )


class BookExtractor:
    """书籍信息提取器"""
    
    # Document类型
    DOC_TYPES = {
        'Book': '书籍',
        'Letter': '信件',
        'Paged': '分页文档',
        'Video': '视频'
    }
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化书籍提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP等)
        """
        self.language = language
        self.logger = setup_logger(__name__)
        
        # 初始化文本解析器和故事提取器
        self.text_parser = TextMapParser(language)
        self.story_extractor = StoryContentExtractor(language)
        
        # 加载数据
        self.logger.info("加载书籍、武器和圣遗物数据...")
        self.documents = self._load_documents()
        self.books_codex = self._load_books_codex()
        self.weapon_story_ids = self._get_weapon_story_ids()
        self.relic_story_ids = self._get_relic_story_ids()
        
        total_docs = len(self.documents)
        pure_books = total_docs - len(self.weapon_story_ids) - len(self.relic_story_ids)
        self.logger.info(
            f"成功加载 {total_docs} 个Documents "
            f"(武器故事: {len(self.weapon_story_ids)}, "
            f"圣遗物故事: {len(self.relic_story_ids)}, "
            f"纯书籍: {pure_books})"
        )
    
    def _load_documents(self) -> List[Dict]:
        """加载Document配置数据"""
        doc_file = get_data_path('ExcelBinOutput/DocumentExcelConfigData.json')
        return load_json(str(doc_file))
    
    def _load_books_codex(self) -> List[Dict]:
        """加载书籍分类配置数据"""
        try:
            codex_file = get_data_path('ExcelBinOutput/BooksCodexExcelConfigData.json')
            return load_json(str(codex_file))
        except:
            self.logger.warning("无法加载BooksCodexExcelConfigData.json")
            return []
    
    def _get_weapon_story_ids(self) -> Set[int]:
        """获取所有武器故事的Document ID集合"""
        weapon_file = get_data_path('ExcelBinOutput/WeaponExcelConfigData.json')
        weapons = load_json(str(weapon_file))
        return {w.get('storyId') for w in weapons if w.get('storyId', 0) > 0}
    
    def _get_relic_story_ids(self) -> Set[int]:
        """获取所有圣遗物故事的Document ID集合"""
        relic_file = get_data_path('ExcelBinOutput/ReliquaryExcelConfigData.json')
        relics = load_json(str(relic_file))
        return {r.get('storyId') for r in relics if r.get('storyId', 0) > 0}
    
    def is_pure_book(self, doc_id: int) -> bool:
        """
        判断是否是纯书籍（不是武器或圣遗物的故事）
        
        参数:
            doc_id: Document ID
        
        返回:
            True表示是纯书籍
        """
        return (doc_id not in self.weapon_story_ids and 
                doc_id not in self.relic_story_ids)
    
    def is_costume_doc(self, doc_id: int) -> bool:
        """
        判断是否是皮肤文档
        
        参数:
            doc_id: Document ID
        
        返回:
            True表示是皮肤文档
        """
        return 340000 <= doc_id < 350000
    
    def is_windglider_doc(self, doc_id: int) -> bool:
        """
        判断是否是风之翼文档
        
        参数:
            doc_id: Document ID
        
        返回:
            True表示是风之翼文档
        """
        return 140000 <= doc_id < 150000
    
    def is_regular_book(self, doc_id: int) -> bool:
        """
        判断是否是普通书籍（排除武器、圣遗物、皮肤、风之翼）
        
        参数:
            doc_id: Document ID
        
        返回:
            True表示是普通书籍
        """
        return (self.is_pure_book(doc_id) and 
                not self.is_costume_doc(doc_id) and 
                not self.is_windglider_doc(doc_id))
    
    def _extract_series_name(self, title: str) -> Optional[str]:
        """
        从标题中提取系列名称
        
        参数:
            title: 书籍标题
        
        返回:
            系列名称，如果不是系列书则返回None
        """
        # 检查是否包含卷数标记
        volume_markers = ['·卷', '·第', '篇', '（上）', '（下）', '（中）']
        
        for marker in volume_markers:
            if marker in title:
                # 提取系列名称（标记之前的部分）
                series_name = title.split(marker)[0].strip()
                if '·' in series_name:
                    # 如果系列名称中还有·，保留第一部分
                    return series_name .split('·')[0].strip()
                return series_name
        
        # 检查是否符合"XXX·YYY"的模式
        if '·' in title:
            parts = title.split('·')
            if len(parts) >= 2:
                series_name = parts[0].strip()
                # 如果第二部分看起来像是分册名而不是副标题
                second_part = parts[1].strip()
                if any(keyword in second_part for keyword in ['卷', '篇', '章', '上', '下', '中']):
                    return series_name
        
        return None
    
    def _get_book_codex_info(self, doc_id: int) -> Optional[Dict]:
        """
        从BooksCodexExcelConfigData获取书籍的分类信息
        
        参数:
            doc_id: Document ID
        
        返回:
            分类信息字典，如果不存在则返回None
        """
        for codex in self.books_codex:
            if codex.get('materialId') == doc_id:
                return codex
        return None
    
    def extract_book_info(self, doc_data: Dict, book_type: str = 'regular') -> Optional[Dict[str, Any]]:
        """
        提取单个书籍的信息
        
        参数:
            doc_data: Document原始数据
            book_type: 书籍类型 ('regular', 'costume', 'windglider', 'all')
        
        返回:
            结构化的书籍信息，如果无效则返回None
        """
        doc_id = doc_data.get('id')
        
        # 根据book_type过滤
        if book_type == 'regular':
            if not self.is_regular_book(doc_id):
                return None
        elif book_type == 'costume':
            if not self.is_costume_doc(doc_id):
                return None
        elif book_type == 'windglider':
            if not self.is_windglider_doc(doc_id):
                return None
        elif book_type == 'all':
            if not self.is_pure_book(doc_id):
                return None
        else:
            return None
        
        # 获取书籍标题
        title = self.text_parser.get_text(doc_data.get('titleTextMapHash', 0))
        
        # 如果没有标题，跳过
        if not title:
            return None
        
        # 提取基础信息
        doc_type = doc_data.get('documentType', 'Book')
        info = {
            'id': doc_id,
            'title': title,
            'document_type': doc_type,
            'document_type_name': self.DOC_TYPES.get(doc_type, doc_type),
            'preview_path': doc_data.get('previewPath', ''),
        }
        
        # 标记特殊类型
        if  self.is_costume_doc(doc_id):
            info['special_type'] = 'costume'
        elif self.is_windglider_doc(doc_id):
            info['special_type'] = 'windglider'
        
        # 提取系列信息（仅对普通书籍）
        if book_type == 'regular':
            series_name = self._extract_series_name(title)
            if series_name:
                info['series_name'] = series_name
                info['is_series'] = True
            else:
                info['is_series'] = False
        
        # 从BooksCodexExcelConfigData获取分类信息
        codex_info = self._get_book_codex_info(doc_id)
        if codex_info:
            info['sort_order'] = codex_info.get('sortOrder', 0)
        
        # 提取内容
        quest_id_list = doc_data.get('questIDList', [])
        if quest_id_list:
            # 通常书籍只有一个questID
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
    
    def extract_all(self, include_all_types: bool = True, book_type: str = 'regular') -> List[Dict[str, Any]]:
        """
        提取所有书籍的完整信息
        
        参数:
            include_all_types: 是否包括所有类型（Letter, Paged, Video等），
                             False则只包括Book类型
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
            
            # 跳过无效ID
            if not doc_id:
                continue
            
            # 如果只要Book类型，过滤其他类型
            if not include_all_types:
                if doc_data.get('documentType') != 'Book':
                    continue
            
            # 提取书籍信息
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
            doc_type: Document类型 (Book, Letter, Paged, Video)
        
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
            书籍系列列表，每个系列包含其所有分册
        """
        self.logger.info("开始按系列组织书籍...")
        
        # 首先提取所有书籍
        all_books = self.extract_all(include_all_types=True)
        
        # 按系列名称分组
        from collections import defaultdict
        series_dict = defaultdict(list)
        standalone_books = []
        
        for book in all_books:
            if book.get('is_series'):
                series_name = book.get('series_name')
                series_dict[series_name].append(book)
            else:
                standalone_books.append(book)
        
        # 组织系列数据
        all_series = []
        for series_name, volumes in series_dict.items():
            # 按sort_order排序
            volumes.sort(key=lambda x: x.get('sort_order', 0))
            
            # 检查preview_path是否一致
            preview_paths = {v.get('preview_path') for v in volumes}
            main_preview_path = volumes[0].get('preview_path') if volumes else ''
            
            series_info = {
                'series_name': series_name,
                'volume_count': len(volumes),
                'volumes': volumes,
                'preview_path': main_preview_path,
                'has_consistent_icon': len(preview_paths) == 1,
                'has_full_content': all(v.get('has_content', False) for v in volumes)
            }
            
            all_series.append(series_info)
        
        # 按系列名称排序
        all_series.sort(key=lambda x: x['series_name'])
        
        self.logger.info(f"成功组织 {len(all_series)} 个书籍系列")
        self.logger.info(f"独立书籍: {len(standalone_books)} 本")
        series_with_full_content = sum(1 for s in all_series if s.get('has_full_content'))
        self.logger.info(f"有完整内容的系列: {series_with_full_content} 个")
        
        return all_series
    
    def extract_costumes(self) -> List[Dict[str, Any]]:
        """
        提取所有皮肤信息
        
        返回:
            皮肤信息列表
        """
        return self.extract_all(include_all_types=True, book_type='costume')
    
    def extract_windgliders(self) -> List[Dict[str, Any]]:
        """
        提取所有风之翼信息
        
        返回:
            风之翼信息列表
        """
        return self.extract_all(include_all_types=True, book_type='windglider')

    
    def save_to_file(self, output_file: str, books: Optional[List[Dict]] = None):
        """
        保存书籍数据到文件
        
        参数:
            output_file: 输出文件路径
            books: 书籍数据列表，如果为None则提取所有
        """
        if books is None:
            books = self.extract_all()
        
        save_json(books, output_file)
        self.logger.info(f"书籍数据已保存到: {output_file}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取书籍统计信息
        
        返回:
            统计信息字典
        """
        all_books = self.extract_all(include_all_types=True)
        
        # 按类型统计
        type_stats = {}
        for book in all_books:
            doc_type = book.get('document_type', 'Unknown')
            type_stats[doc_type] = type_stats.get(doc_type, 0) + 1
        
        # 内容统计
        has_content = sum(1 for b in all_books if b.get('has_content'))
        
        return {
            'total_count': len(all_books),
            'with_content_count': has_content,
            'without_content_count': len(all_books) - has_content,
            'type_distribution': type_stats
        }


def main():
    """测试函数"""
    import sys
    
    # 设置日志级别
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 创建提取器
    extractor = BookExtractor(language='CHS')
    
    # 保存到输出目录
    output_dir = get_data_path('../genshin-extractors/output')
    output_dir.mkdir(exist_ok=True)
    
    # 1. 提取普通书籍
    all_books = extractor.extract_all(include_all_types=True, book_type='regular')
    output_file = output_dir / 'books.json'
    extractor.save_to_file(str(output_file), all_books)
    
    # 2. 提取并保存系列书籍
    series = extractor.extract_series()
    series_file = output_dir / 'book_series.json'
    save_json(series, str(series_file))
    print(f"书籍系列数据已保存到: {series_file}")
    
    # 3. 提取皮肤
    costumes = extractor.extract_costumes()
    costume_file = output_dir / 'costumes.json'
    save_json(costumes, str(costume_file))
    print(f"皮肤数据已保存到: {costume_file}")
    
    # 4. 提取风之翼
    windgliders = extractor.extract_windgliders()
    windglider_file = output_dir / 'windgliders.json'
    save_json(windgliders, str(windglider_file))
    print(f"风之翼数据已保存到: {windglider_file}")
    
    # 获取并显示统计信息
    stats = extractor.get_statistics()
    
    print("\n" + "=" * 60)
    print("数据提取统计")
    print("=" * 60)
    print(f"普通书籍数: {stats['total_count']}")
    print(f"有内容的书籍: {stats['with_content_count']}")
    print(f"书籍系列数: {len(series)}")
    print(f"皮肤数: {len(costumes)}")
    print(f"风之翼数: {len(windgliders)}")
    
    print("\n按类型统计:")
    for doc_type, count in sorted(stats['type_distribution'].items()):
        type_name = BookExtractor.DOC_TYPES.get(doc_type, doc_type)
        print(f"  {type_name} ({doc_type}): {count} 个")
    
    # 显示系列示例
    print("\n书籍系列示例（前3个）:")
    for s in series[:3]:
        print(f"\n  系列: {s['series_name']}")
        print(f"    分册数: {s['volume_count']}, 完整内容: {s['has_full_content']}")
    
    # 显示皮肤示例
    if costumes:
        print("\n皮肤示例（前3个）:")
        for c in costumes[:3]:
            has_content = "✓" if c.get('has_content') else "✗"
            print(f"  {has_content} {c['title']} (ID: {c['id']})")
    
    # 显示风之翼示例
    if windgliders:
        print("\n风之翼示例（前3个）:")
        for w in windgliders[:3]:
            has_content = "✓" if w.get('has_content') else "✗"
            print(f"  {has_content} {w['title']} (ID: {w['id']})")


if __name__ == '__main__':
    main()
