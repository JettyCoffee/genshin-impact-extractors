"""
任务数据加载器
"""

from pathlib import Path
from typing import Dict, List, Optional

from ...core import get_data_path, load_json, setup_logger


class QuestDataLoader:
    """任务数据加载器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def scan_quest_files(self) -> Dict[int, Path]:
        """
        扫描 BinOutput/Quest 目录，获取所有任务文件
        
        返回:
            任务 ID 到文件路径的映射
        """
        quest_dir = get_data_path('BinOutput/Quest')
        quest_files = {}
        
        if not quest_dir.exists():
            self.logger.warning(f"Quest 目录不存在: {quest_dir}")
            return quest_files
        
        for file_path in quest_dir.glob('*.json'):
            try:
                quest_id = int(file_path.stem)
                quest_files[quest_id] = file_path
            except ValueError:
                # 跳过非数字命名的文件
                continue
        
        return quest_files
    
    def load_chapter_map(self) -> Dict[int, Dict]:
        """
        加载章节配置
        
        返回:
            章节 ID 到数据的映射
        """
        try:
            chapter_file = get_data_path('ExcelBinOutput/ChapterExcelConfigData.json')
            chapters = load_json(str(chapter_file))
            return {c['id']: c for c in chapters if 'id' in c}
        except Exception as e:
            self.logger.warning(f"无法加载 ChapterExcelConfigData.json: {e}")
            return {}
    
    def load_npc_config(self) -> Dict[int, Dict]:
        """
        加载 NPC 配置
        
        返回:
            NPC ID 到数据的映射
        """
        try:
            npc_file = get_data_path('ExcelBinOutput/NpcExcelConfigData.json')
            npcs = load_json(str(npc_file))
            return {n['id']: n for n in npcs if 'id' in n}
        except Exception as e:
            self.logger.warning(f"无法加载 NpcExcelConfigData.json: {e}")
            return {}
    
    def load_avatar_config(self) -> Dict[int, Dict]:
        """
        加载角色配置
        
        返回:
            角色 ID 到数据的映射
        """
        try:
            avatar_file = get_data_path('ExcelBinOutput/AvatarExcelConfigData.json')
            avatars = load_json(str(avatar_file))
            return {a['id']: a for a in avatars if 'id' in a}
        except Exception as e:
            self.logger.warning(f"无法加载 AvatarExcelConfigData.json: {e}")
            return {}
    
    def load_quest_data(self, quest_id: int, quest_files: Dict[int, Path]) -> Optional[Dict]:
        """
        加载指定任务的数据
        
        参数:
            quest_id: 任务 ID
            quest_files: 任务文件映射
        
        返回:
            任务数据，如果不存在则返回 None
        """
        if quest_id not in quest_files:
            return None
        
        try:
            return load_json(str(quest_files[quest_id]))
        except Exception as e:
            self.logger.warning(f"加载任务文件失败 {quest_id}: {e}")
            return None
    
    def load_talk_data(self, talk_id: int) -> Optional[Dict]:
        """
        加载 Talk 对话数据
        
        参数:
            talk_id: Talk ID
        
        返回:
            Talk 数据，如果不存在则返回 None
        """
        talk_file = get_data_path(f'BinOutput/Talk/Quest/{talk_id}.json')
        if talk_file.exists():
            try:
                return load_json(str(talk_file))
            except Exception as e:
                self.logger.debug(f"加载 Talk 文件失败 {talk_id}: {e}")
        return None
