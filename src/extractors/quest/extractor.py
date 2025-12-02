"""
任务对话提取器主类
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import BaseExtractor
from ...core import save_json
from .data_loader import QuestDataLoader
from .role_resolver import RoleNameResolver
from .dialog_builder import DialogTreeBuilder
from .quest_processor import QuestProcessor


class QuestDialogueExtractor(BaseExtractor):
    """任务对话提取器"""
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化任务对话提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP 等)
        """
        super().__init__(language)
        
        # 初始化数据加载器
        self.data_loader = QuestDataLoader()
        
        # 加载配置数据
        self.logger.info("加载任务和对话配置...")
        self.quest_files = self.data_loader.scan_quest_files()
        self.chapter_map = self.data_loader.load_chapter_map()
        self.npc_config = self.data_loader.load_npc_config()
        self.avatar_config = self.data_loader.load_avatar_config()
        
        # 初始化子模块
        self.role_resolver = RoleNameResolver(self.text_parser, self.npc_config, self.avatar_config)
        self.dialog_builder = DialogTreeBuilder(self.text_parser, self.role_resolver)
        self.quest_processor = QuestProcessor(
            self.text_parser,
            self.data_loader,
            self.dialog_builder,
            self.chapter_map
        )
        
        self.logger.info(
            f"已加载: {len(self.quest_files)} 个任务文件, "
            f"{len(self.chapter_map)} 个章节, "
            f"{len(self.npc_config)} 个 NPC, "
            f"{len(self.avatar_config)} 个角色"
        )
    
    def extract_quest(self, main_quest_id: int) -> Optional[Dict[str, Any]]:
        """
        提取单个主任务的完整信息
        
        参数:
            main_quest_id: 主任务 ID
        
        返回:
            任务数据
        """
        return self.quest_processor.extract_quest(main_quest_id, self.quest_files)
    
    def extract_all(self) -> List[Dict[str, Any]]:
        """
        提取所有任务
        
        返回:
            所有任务数据列表
        """
        self.logger.info(f"开始提取所有任务，共 {len(self.quest_files)} 个...")
        
        all_quests = []
        for quest_id in self.quest_files.keys():
            quest_data = self.extract_quest(quest_id)
            if quest_data:
                all_quests.append(quest_data)
        
        self.logger.info(f"成功提取 {len(all_quests)} 个任务")
        return all_quests
    
    def extract_all_to_files(self, output_dir: str) -> None:
        """
        提取所有任务并保存到文件
        按任务类型和章节组织文件结构
        
        参数:
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"开始提取所有任务，共 {len(self.quest_files)} 个...")
        
        count = 0
        success_count = 0
        
        for main_quest_id in self.quest_files.keys():
            count += 1
            
            quest_data = self.extract_quest(main_quest_id)
            if not quest_data:
                continue
            
            # 保存到文件
            self._save_quest_to_file(output_path, quest_data)
            success_count += 1
            
            if count % 100 == 0:
                self.logger.info(f"已处理 {count}/{len(self.quest_files)} 个任务（成功 {success_count} 个）...")
        
        self.logger.info(f"任务提取完成，共处理 {count} 个任务，成功 {success_count} 个")
        
        # 生成统计信息
        stats = self._generate_statistics(output_path)
        stats_file = output_path / 'extraction_stats.json'
        save_json(stats, str(stats_file))
        self.logger.info(f"统计信息已保存到: {stats_file}")
    
    def _save_quest_to_file(self, output_path: Path, quest_data: Dict) -> None:
        """保存单个任务到文件"""
        quest_type_name = quest_data['type_name']
        chapter_id = quest_data['chapter_id']
        chapter_title = quest_data['chapter_title']
        
        # 确定中间字段名
        middle_name = 'Unknown'
        for field in ['role', 'festival', 'chapter', 'region', 'chapter_icon_suffix']:
            if field in quest_data:
                middle_name = quest_data[field]
                break
        
        # 构建文件夹名
        safe_chapter_title = QuestProcessor.sanitize_filename(chapter_title)
        safe_middle = QuestProcessor.sanitize_filename(middle_name)
        folder_name = f"{chapter_id}-{safe_middle}-{safe_chapter_title}"
        
        type_dir = output_path / quest_type_name / folder_name
        type_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建文件名
        safe_title = QuestProcessor.sanitize_filename(quest_data['title'])
        if not safe_title:
            safe_title = f"Quest_{quest_data['id']}"
        
        file_name = f"{quest_data['id']}-{safe_title}.json"
        output_file = type_dir / file_name
        
        save_json(quest_data, str(output_file))
    
    def _generate_statistics(self, output_dir: Path) -> Dict[str, Any]:
        """生成提取统计信息"""
        stats = {
            'total_quest_files': len(self.quest_files),
            'total_chapters': len(self.chapter_map),
            'total_npcs': len(self.npc_config),
            'total_avatars': len(self.avatar_config),
            'by_type': {},
        }
        
        # 扫描输出目录统计
        for type_dir in output_dir.iterdir():
            if type_dir.is_dir() and type_dir.name != 'extraction_stats.json':
                quest_count = 0
                for chapter_dir in type_dir.iterdir():
                    if chapter_dir.is_dir():
                        quest_count += len(list(chapter_dir.glob('*.json')))
                stats['by_type'][type_dir.name] = quest_count
        
        return stats
