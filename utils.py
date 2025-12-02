"""
通用工具模块
提供数据加载、文本映射等公共功能
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


def setup_logger(name: str) -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_data_path(relative_path: str = '') -> Path:
    """
    获取数据文件的绝对路径
    
    参数:
        relative_path: 相对于AnimeGameData的路径
    
    返回:
        绝对路径
    """
    # 获取项目根目录
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    data_dir = project_root / 'AnimeGameData'
    
    if relative_path:
        return data_dir / relative_path
    return data_dir


def load_json(file_path: str) -> Any:
    """
    加载JSON文件
    
    参数:
        file_path: JSON文件路径
    
    返回:
        解析后的数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, file_path: str, indent: int = 2):
    """
    保存数据为JSON文件
    
    参数:
        data: 要保存的数据
        file_path: 保存路径
        indent: 缩进空格数
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


class TextMapParser:
    """文本映射解析器"""
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化文本映射解析器
        
        参数:
            language: 语言代码 (CHS, EN, JP等)
        """
        self.language = language
        self.text_map = self._load_text_map()
    
    def _load_text_map(self) -> Dict[int, str]:
        """加载文本映射数据"""
        text_map_file = get_data_path(f'TextMap/TextMap{self.language}.json')
        
        if not text_map_file.exists():
            raise FileNotFoundError(f"文本映射文件不存在: {text_map_file}")
        
        with open(text_map_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 将字符串key转换为整数
        return {int(k): v for k, v in data.items()}
    
    def get_text(self, text_hash: int) -> str:
        """
        根据hash获取文本
        
        参数:
            text_hash: 文本哈希值
        
        返回:
            对应的文本，如果不存在则返回空字符串
        """
        return self.text_map.get(text_hash, '')


class StoryContentExtractor:
    """
    故事内容提取器
    统一处理武器、圣遗物、书籍的故事文本提取
    """
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化故事内容提取器
        
        参数:
            language: 语言代码
        """
        self.language = language
        self.logger = setup_logger(__name__)
        
        # 加载所需的数据文件
        self.logger.info("加载Document和Localization数据...")
        self.documents = self._load_documents()
        self.localization_map = self._build_localization_map()
        self.logger.info(f"加载完成: {len(self.documents)} 个Documents, {len(self.localization_map)} 个Localization映射")
    
    def _load_documents(self) -> Dict[int, Dict]:
        """加载Document配置数据"""
        doc_file = get_data_path('ExcelBinOutput/DocumentExcelConfigData.json')
        docs = load_json(str(doc_file))
        # 转换为字典方便查询
        return {doc['id']: doc for doc in docs}
    
    def _build_localization_map(self) -> Dict[int, str]:
        """构建Localization ID到文件路径的映射"""
        loc_file = get_data_path('ExcelBinOutput/LocalizationExcelConfigData.json')
        loc_data = load_json(str(loc_file))
        
        loc_map = {}
        for entry in loc_data:
            # 根据语言选择对应的路径字段
            # 注意：部分字段名被加密，需要同时尝试原始名和加密名
            path = ''
            if self.language == 'CHS':
                # DHHBMABKMMN 和 HKLGNINJMGG 都指向中文简体路径
                path = entry.get('DHHBMABKMMN') or entry.get('HKLGNINJMGG') or entry.get('chsPath')
            elif self.language == 'CHT':
                path = entry.get('tcPath')
            elif self.language == 'EN':
                path = entry.get('enPath')
            elif self.language == 'JP':
                path = entry.get('jpPath')
            elif self.language == 'KR':
                path = entry.get('krPath')
            elif self.language == 'DE':
                path = entry.get('dePath')
            elif self.language == 'FR':
                path = entry.get('frPath')
            elif self.language == 'ES':
                path = entry.get('esPath')
            elif self.language == 'PT':
                path = entry.get('ptPath')
            elif self.language == 'RU':
                path = entry.get('ruPath')
            elif self.language == 'ID':
                path = entry.get('idPath')
            elif self.language == 'TH':
                path = entry.get('thPath')
            elif self.language == 'VI':
                path = entry.get('viPath')
            elif self.language == 'TR':
                path = entry.get('trPath')
            elif self.language == 'IT':
                path = entry.get('itPath')
            
            if path and 'id' in entry:
                loc_map[entry['id']] = path
        
        return loc_map
    
    def get_story_content(self, story_id: int) -> str:
        """
        根据story ID获取故事内容
        
        参数:
            story_id: 故事ID（Document ID）
        
        返回:
            故事文本内容，如果获取失败则返回空字符串
        """
        # 1. 从Documents获取quest ID
        if story_id not in self.documents:
            self.logger.debug(f"Story ID {story_id} 不存在于Documents中")
            return ''
        
        document = self.documents[story_id]
        quest_id_list = document.get('questIDList', [])
        
        if not quest_id_list:
            self.logger.debug(f"Story ID {story_id} 没有questIDList")
            return ''
        
        # 通常取第一个quest ID
        quest_id = quest_id_list[0]
        
        # 2. 从Localization获取文件路径
        if quest_id not in self.localization_map:
            self.logger.debug(f"Quest ID {quest_id} 不存在于Localization映射中")
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
