"""
故事内容提取模块
统一处理武器、圣遗物、书籍的故事文本提取
"""

import os
from typing import Dict

from .config import get_data_path, setup_logger
from .io import load_json


class StoryContentExtractor:
    """
    故事内容提取器
    统一处理武器、圣遗物、书籍的故事文本提取
    """
    
    # 语言代码到 Localization 字段名的映射
    LANGUAGE_PATH_FIELDS = {
        'CHS': ['DHHBMABKMMN', 'HKLGNINJMGG', 'chsPath'],
        'CHT': ['tcPath'],
        'EN': ['enPath'],
        'JP': ['jpPath'],
        'KR': ['krPath'],
        'DE': ['dePath'],
        'FR': ['frPath'],
        'ES': ['esPath'],
        'PT': ['ptPath'],
        'RU': ['ruPath'],
        'ID': ['idPath'],
        'TH': ['thPath'],
        'VI': ['viPath'],
        'TR': ['trPath'],
        'IT': ['itPath'],
    }
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化故事内容提取器
        
        参数:
            language: 语言代码
        """
        self.language = language
        self.logger = setup_logger(__name__)
        
        # 加载所需的数据文件
        self.logger.info("加载 Document 和 Localization 数据...")
        self.documents = self._load_documents()
        self.localization_map = self._build_localization_map()
        self.logger.info(
            f"加载完成: {len(self.documents)} 个 Documents, "
            f"{len(self.localization_map)} 个 Localization 映射"
        )
    
    def _load_documents(self) -> Dict[int, Dict]:
        """
        加载 Document 配置数据
        
        返回:
            ID 到 Document 数据的映射
        """
        doc_file = get_data_path('ExcelBinOutput/DocumentExcelConfigData.json')
        docs = load_json(str(doc_file))
        return {doc['id']: doc for doc in docs}
    
    def _build_localization_map(self) -> Dict[int, str]:
        """
        构建 Localization ID 到文件路径的映射
        
        返回:
            ID 到路径的映射
        """
        loc_file = get_data_path('ExcelBinOutput/LocalizationExcelConfigData.json')
        loc_data = load_json(str(loc_file))
        
        loc_map = {}
        path_fields = self.LANGUAGE_PATH_FIELDS.get(self.language, [])
        
        for entry in loc_data:
            # 尝试从多个可能的字段名获取路径
            path = ''
            for field in path_fields:
                if field in entry and entry[field]:
                    path = entry[field]
                    break
            
            if path and 'id' in entry:
                loc_map[entry['id']] = path
        
        return loc_map
    
    def get_story_content(self, story_id: int) -> str:
        """
        根据 story ID 获取故事内容
        
        参数:
            story_id: 故事 ID（Document ID）
        
        返回:
            故事文本内容，如果获取失败则返回空字符串
        """
        # 1. 从 Documents 获取 quest ID
        if story_id not in self.documents:
            self.logger.debug(f"Story ID {story_id} 不存在于 Documents 中")
            return ''
        
        document = self.documents[story_id]
        quest_id_list = document.get('questIDList', [])
        
        if not quest_id_list:
            self.logger.debug(f"Story ID {story_id} 没有 questIDList")
            return ''
        
        # 通常取第一个 quest ID
        quest_id = quest_id_list[0]
        
        # 2. 从 Localization 获取文件路径
        if quest_id not in self.localization_map:
            self.logger.debug(f"Quest ID {quest_id} 不存在于 Localization 映射中")
            return ''
        
        raw_path = self.localization_map[quest_id]
        
        # 3. 读取文本文件
        filename = os.path.basename(raw_path) + '.txt'
        readable_dir = get_data_path(f'Readable/{self.language}')
        file_path = readable_dir / filename
        
        if not file_path.exists():
            self.logger.debug(f"文本文件不存在: {file_path}")
            return ''
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            self.logger.error(f"读取故事文件失败 {file_path}: {e}")
            return ''
    
    def has_story(self, story_id: int) -> bool:
        """
        检查指定 ID 是否有对应的故事内容
        
        参数:
            story_id: 故事 ID
        
        返回:
            是否有故事内容
        """
        return bool(self.get_story_content(story_id))
