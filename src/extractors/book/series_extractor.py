"""
书籍系列提取器
按系列组织书籍数据
"""

from collections import defaultdict
from typing import Any, Dict, List


class BookSeriesExtractor:
    """书籍系列提取器"""
    
    def extract_series(self, all_books: List[Dict]) -> List[Dict[str, Any]]:
        """
        按系列组织书籍
        
        参数:
            all_books: 所有书籍数据列表
        
        返回:
            书籍系列列表
        """
        # 按系列名称分组
        series_dict = defaultdict(list)
        
        for book in all_books:
            if book.get('is_series'):
                series_name = book.get('series_name')
                series_dict[series_name].append(book)
        
        # 组织系列数据
        all_series = []
        for series_name, volumes in series_dict.items():
            # 按 sort_order 排序
            volumes.sort(key=lambda x: x.get('sort_order', 0))
            
            # 检查 preview_path 是否一致
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
        
        return all_series
    
    def get_standalone_books(self, all_books: List[Dict]) -> List[Dict]:
        """
        获取独立书籍（非系列）
        
        参数:
            all_books: 所有书籍数据列表
        
        返回:
            独立书籍列表
        """
        return [book for book in all_books if not book.get('is_series')]
