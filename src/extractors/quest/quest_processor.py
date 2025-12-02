"""
任务处理器
处理单个任务的提取和组织
"""

import re
from typing import Any, Dict, List, Optional

from ...core import TextMapParser, setup_logger
from ...models import QuestTypes, QuestFieldMap, SubQuestFieldMap, TalkFieldMap
from .data_loader import QuestDataLoader
from .dialog_builder import DialogTreeBuilder


class QuestProcessor:
    """任务处理器"""
    
    def __init__(
        self,
        text_parser: TextMapParser,
        data_loader: QuestDataLoader,
        dialog_builder: DialogTreeBuilder,
        chapter_map: Dict[int, Dict]
    ):
        """
        初始化
        
        参数:
            text_parser: 文本解析器
            data_loader: 数据加载器
            dialog_builder: 对话树构建器
            chapter_map: 章节配置映射
        """
        self.text_parser = text_parser
        self.data_loader = data_loader
        self.dialog_builder = dialog_builder
        self.chapter_map = chapter_map
        self.logger = setup_logger(__name__)
    
    def extract_quest(self, main_quest_id: int, quest_files: Dict) -> Optional[Dict[str, Any]]:
        """
        提取单个主任务的完整信息
        
        参数:
            main_quest_id: 主任务 ID
            quest_files: 任务文件映射
        
        返回:
            任务数据
        """
        # 加载任务数据
        raw_quest = self.data_loader.load_quest_data(main_quest_id, quest_files)
        if not raw_quest:
            return None
        
        # 解码加密字段
        main_quest = QuestFieldMap.decode(raw_quest)
        
        # 获取标题和描述
        title = self.text_parser.get_text(main_quest.get('titleTextMapHash', 0))
        description = self.text_parser.get_text(main_quest.get('descTextMapHash', 0))
        
        if not title:
            title = f'Quest_{main_quest_id}'
        
        # 获取任务类型
        quest_type = self._extract_quest_type(main_quest)
        quest_type_name = QuestTypes.get_name(quest_type)
        
        # 获取章节信息
        chapter_id = main_quest.get('chapterId', 0)
        chapter_info = self._get_chapter_info(chapter_id)
        icon_suffix = chapter_info['icon_suffix']
        
        quest_data = {
            'id': main_quest_id,
            'title': title,
            'description': description,
            'type': quest_type,
            'type_name': quest_type_name,
            'chapter_id': chapter_id,
            'chapter_title': chapter_info['title'],
            'sub_quests': [],
            'talks': []
        }
        
        # 根据任务类型设置额外字段
        self._set_type_specific_field(quest_data, quest_type, icon_suffix)
        
        # 处理子任务
        self._process_sub_quests(quest_data, main_quest)
        
        # 处理对话
        self._process_talks(quest_data, main_quest)
        
        return quest_data
    
    def _extract_quest_type(self, quest_data: Dict) -> str:
        """从任务数据中提取任务类型"""
        # 方法1: 直接从 questType 字段获取
        quest_type = quest_data.get('questType', '')
        if quest_type in ['AQ', 'LQ', 'WQ', 'EQ', 'IQ']:
            return quest_type
        
        # 方法2: 从 luaPath 提取
        lua_path = quest_data.get('luaPath', '')
        if lua_path and '/Quest/' in lua_path:
            after_quest = lua_path.split('/Quest/')[-1]
            for prefix in ['AQ', 'LQ', 'WQ', 'EQ', 'IQ']:
                if after_quest.startswith(prefix):
                    return prefix
        
        # 方法3: 从 chapterId 推断
        chapter_id = quest_data.get('chapterId', 0)
        if chapter_id and 1000 <= chapter_id < 2000:
            return 'AQ'
        
        return 'Unknown'
    
    def _get_chapter_info(self, chapter_id: int) -> Dict[str, Any]:
        """获取章节信息"""
        if chapter_id not in self.chapter_map:
            return {
                'id': chapter_id,
                'title': f'Chapter_{chapter_id}',
                'icon_suffix': 'Unknown',
                'quest_type': 'Unknown'
            }
        
        chapter_data = self.chapter_map[chapter_id]
        
        title_hash = chapter_data.get('chapterTitleTextMapHash')
        title = self.text_parser.get_text(title_hash) if title_hash else f'Chapter_{chapter_id}'
        
        icon = chapter_data.get('chapterIcon', '')
        icon_suffix = self._extract_icon_suffix(icon)
        
        return {
            'id': chapter_id,
            'title': title,
            'icon': icon,
            'icon_suffix': icon_suffix,
            'quest_type': chapter_data.get('questType', 'Unknown'),
            'begin_quest_id': chapter_data.get('beginQuestId'),
            'end_quest_id': chapter_data.get('endQuestId')
        }
    
    def _extract_icon_suffix(self, icon_path: str) -> str:
        """从 icon 路径提取后缀部分"""
        if not icon_path:
            return 'Unknown'
        
        if '_' in icon_path:
            parts = icon_path.split('_')
            return parts[-1] if parts else 'Unknown'
        
        return icon_path
    
    def _set_type_specific_field(self, quest_data: Dict, quest_type: str, icon_suffix: str) -> None:
        """根据任务类型设置特定字段"""
        field_map = {
            'LQ': 'role',
            'EQ': 'festival',
            'AQ': 'chapter',
            'WQ': 'region',
            'IQ': 'region',
        }
        
        field_name = field_map.get(quest_type, 'chapter_icon_suffix')
        quest_data[field_name] = icon_suffix
    
    def _process_sub_quests(self, quest_data: Dict, main_quest: Dict) -> None:
        """处理子任务"""
        sub_quests = main_quest.get('subQuests', [])
        decoded_subs = [SubQuestFieldMap.decode(sub) for sub in sub_quests]
        decoded_subs.sort(key=lambda x: x.get('order', 0))
        
        for sub in decoded_subs:
            sub_data = {
                'id': sub.get('subId'),
                'order': sub.get('order', 0),
                'description': self.text_parser.get_text(sub.get('descTextMapHash', 0)),
            }
            quest_data['sub_quests'].append(sub_data)
    
    def _process_talks(self, quest_data: Dict, main_quest: Dict) -> None:
        """处理对话"""
        talks = main_quest.get('talks', [])
        
        for talk_info in talks:
            decoded_talk_info = TalkFieldMap.decode(talk_info)
            talk_id = decoded_talk_info.get('id')
            if not talk_id:
                continue
            
            npc_id = decoded_talk_info.get('npcId', [])
            
            # 加载并处理对话数据
            talk_data = self.data_loader.load_talk_data(talk_id)
            dialogue_tree = None
            if talk_data:
                dialogue_tree = self.dialog_builder.process_talk(talk_data)
            
            talk_entry = {
                'talk_id': talk_id,
                'npc_ids': npc_id if isinstance(npc_id, list) else [npc_id] if npc_id else [],
                'dialogues': dialogue_tree if dialogue_tree else []
            }
            
            quest_data['talks'].append(talk_entry)
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """清理文件名，移除非法字符"""
        if not name:
            return ''
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name.strip()
        if len(name) > 100:
            name = name[:100]
        return name
