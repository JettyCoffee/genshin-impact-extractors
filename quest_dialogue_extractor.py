"""
任务对话提取器
提取任务的对话内容，按任务类型和章节组织

数据源：
- BinOutput/Quest/{id}.json - 主任务数据（包含子任务和talk列表）
- BinOutput/Talk/Quest/{talkId}.json - 对话详细数据
- ExcelBinOutput/ChapterExcelConfigData.json - 章节数据
- ExcelBinOutput/NpcExcelConfigData.json - NPC名称
- ExcelBinOutput/AvatarExcelConfigData.json - 角色名称
"""

from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import re
import os

# 支持作为模块导入和直接运行
try:
    from .utils import (
        load_json, save_json, get_data_path,
        setup_logger, TextMapParser
    )
except ImportError:
    from utils import (
        load_json, save_json, get_data_path,
        setup_logger, TextMapParser
    )


class QuestDialogueExtractor:
    """任务对话提取器 - 基于BinOutput数据源"""
    
    # 任务类型映射
    QUEST_TYPES = {
        'AQ': '魔神任务',  # Archon Quest
        'LQ': '传说任务',  # Legend Quest / Story Quest  
        'WQ': '世界任务',  # World Quest
        'EQ': '活动任务',  # Event Quest
        'IQ': '委托任务',  # Commission Quest
    }
    
    # 加密字段映射 - Quest字段
    QUEST_FIELD_MAP = {
        'FJIMHCGKKPJ': 'id',
        'DNIFJDIGILK': 'luaPath',
        'LINDNOIHPNE': 'chapterId',         # 章节ID (某些文件)
        'NKEKKINIKEB': 'chapterId',         # 章节系列ID - 正确的章节ID
        'ODOCBCAGDJA': 'mainQuestId',       # 主任务ID（不是章节ID！）
        'DCHHEHNNEOO': 'talks',
        'BMCONAJCMAK': 'subQuests',
        'AFKIEPNELHE': 'questType',         # 任务类型，如 "AQ"、"LQ"、"WQ" 等
        'DLPKBOPINEE': 'descTextMapHash',   # 任务描述文本Hash
        'HMPOGBDMBOK': 'titleTextMapHash',  # 任务标题文本Hash
    }
    
    # 加密字段映射 - Talk字段
    TALK_FIELD_MAP = {
        'FJIMHCGKKPJ': 'id',
        'FHNJHCFCADD': 'questId',
        'ELEPNLBFNOP': 'npcId',
        'OLCKDFIEGLI': 'initDialog',
        'IKCBIFLCCOH': 'dialogList',  # 对话列表
        'AFKIEPNELHE': 'talkType',    # 对话类型，如 "QUEST"
        'PDFCHAAMEHA': 'talkId',      # Talk ID
    }
    
    # 加密字段映射 - SubQuest字段
    SUBQUEST_FIELD_MAP = {
        'FKJCGCAMNEH': 'subId',
        'JDCNDABFDFP': 'order',
        'DLPKBOPINEE': 'descTextMapHash',
    }
    
    # 加密字段映射 - Dialog字段（对话条目内部的字段）
    DIALOG_FIELD_MAP = {
        'FJIMHCGKKPJ': 'id',                    # 对话ID
        'BCBFGKALICJ': 'talkRole',              # 角色信息
        'DBIHEJMJCMK': 'talkContentTextMapHash', # 对话文本hash
        'JLLIMLALADN': 'nextDialogs',           # 下一个对话ID列表
    }
    
    # 加密字段映射 - TalkRole内部字段
    TALK_ROLE_FIELD_MAP = {
        'FGFJOGEKHOK': 'type',                  # 角色类型，如 "TALK_ROLE_NPC"
        '_type': 'type',                        # 有些文件直接用 _type
        '_id': 'id',                            # 有些文件直接用 _id
    }
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化任务对话提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP等)
        """
        self.language = language
        self.logger = setup_logger(__name__)
        
        # 初始化文本解析器
        self.text_parser = TextMapParser(language)
        
        # 加载配置数据
        self.logger.info("加载任务和对话配置...")
        self._load_configs()
        self.logger.info("配置加载完成")
    
    def _decode_field(self, data: Dict, field_name: str, field_map: Dict[str, str], default=None):
        """
        从数据中获取字段值，支持加密字段名和原始字段名
        
        参数:
            data: 数据字典
            field_name: 原始字段名
            field_map: 加密字段映射表
            default: 默认值
        
        返回:
            字段值
        """
        # 首先尝试原始字段名
        if field_name in data:
            return data[field_name]
        
        # 尝试从加密字段映射中查找
        for encrypted_key, original_key in field_map.items():
            if original_key == field_name and encrypted_key in data:
                return data[encrypted_key]
        
        return default
    
    def _decode_quest_data(self, data: Dict) -> Dict:
        """
        解码Quest数据，将加密字段名转换为原始字段名
        
        参数:
            data: 原始数据字典
        
        返回:
            解码后的数据字典
        """
        decoded = {}
        
        # 复制所有原始字段
        for key, value in data.items():
            # 检查是否是加密字段
            if key in self.QUEST_FIELD_MAP:
                decoded[self.QUEST_FIELD_MAP[key]] = value
            else:
                decoded[key] = value
        
        return decoded
    
    def _decode_talk_data(self, data: Dict) -> Dict:
        """
        解码Talk数据，将加密字段名转换为原始字段名
        
        参数:
            data: 原始数据字典
        
        返回:
            解码后的数据字典
        """
        decoded = {}
        
        for key, value in data.items():
            if key in self.TALK_FIELD_MAP:
                decoded[self.TALK_FIELD_MAP[key]] = value
            else:
                decoded[key] = value
        
        return decoded
    
    def _decode_subquest_data(self, data: Dict) -> Dict:
        """
        解码SubQuest数据，将加密字段名转换为原始字段名
        
        参数:
            data: 原始数据字典
        
        返回:
            解码后的数据字典
        """
        decoded = {}
        
        for key, value in data.items():
            if key in self.SUBQUEST_FIELD_MAP:
                decoded[self.SUBQUEST_FIELD_MAP[key]] = value
            else:
                decoded[key] = value
        
        return decoded
    
    def _decode_dialog_data(self, data: Dict) -> Dict:
        """
        解码单个Dialog对话条目数据
        
        参数:
            data: 原始对话数据字典
        
        返回:
            解码后的数据字典
        """
        decoded = {}
        
        for key, value in data.items():
            if key in self.DIALOG_FIELD_MAP:
                decoded[self.DIALOG_FIELD_MAP[key]] = value
            else:
                decoded[key] = value
        
        # 解码 talkRole 内部字段
        if 'talkRole' in decoded and isinstance(decoded['talkRole'], dict):
            role_data = decoded['talkRole']
            decoded_role = {}
            for key, value in role_data.items():
                if key in self.TALK_ROLE_FIELD_MAP:
                    decoded_role[self.TALK_ROLE_FIELD_MAP[key]] = value
                else:
                    decoded_role[key] = value
            decoded['talkRole'] = decoded_role
        
        return decoded
    
    def _decode_dialog_list(self, dialog_list: List[Dict]) -> List[Dict]:
        """
        解码对话列表中的所有对话条目
        
        参数:
            dialog_list: 原始对话列表
        
        返回:
            解码后的对话列表
        """
        return [self._decode_dialog_data(dialog) for dialog in dialog_list]
    
    def _load_configs(self):
        """加载所有需要的配置文件"""
        # 加载章节配置
        self.chapter_map = self._load_chapter_map()
        
        # 加载角色配置（用于解析对话中的角色名）
        self.npc_config = self._load_npc_config()
        self.avatar_config = self._load_avatar_config()
        
        # 扫描所有Quest文件并构建索引
        self.quest_files = self._scan_quest_files()
        
        self.logger.info(
            f"已加载: {len(self.quest_files)} 个任务文件, "
            f"{len(self.chapter_map)} 个章节, "
            f"{len(self.npc_config)} 个NPC, "
            f"{len(self.avatar_config)} 个角色"
        )
    
    def _scan_quest_files(self) -> Dict[int, Path]:
        """扫描BinOutput/Quest目录，获取所有任务文件"""
        quest_dir = get_data_path('BinOutput/Quest')
        quest_files = {}
        
        if not quest_dir.exists():
            self.logger.warning(f"Quest目录不存在: {quest_dir}")
            return quest_files
        
        for file_path in quest_dir.glob('*.json'):
            # 尝试从文件名提取ID（跳过hash命名的文件）
            try:
                quest_id = int(file_path.stem)
                quest_files[quest_id] = file_path
            except ValueError:
                # 跳过非数字命名的文件（如hash命名）
                continue
        
        return quest_files
    
    def _load_chapter_map(self) -> Dict[int, Dict]:
        """加载章节配置"""
        try:
            chapter_file = get_data_path('ExcelBinOutput/ChapterExcelConfigData.json')
            chapters = load_json(str(chapter_file))
            return {c['id']: c for c in chapters if 'id' in c}
        except:
            self.logger.warning("无法加载ChapterExcelConfigData.json")
            return {}
    
    def _load_npc_config(self) -> Dict[int, Dict]:
        """加载NPC配置"""
        try:
            npc_file = get_data_path('ExcelBinOutput/NpcExcelConfigData.json')
            npcs = load_json(str(npc_file))
            return {n['id']: n for n in npcs if 'id' in n}
        except:
            self.logger.warning("无法加载NpcExcelConfigData.json")
            return {}
    
    def _load_avatar_config(self) -> Dict[int, Dict]:
        """加载角色配置"""
        try:
            avatar_file = get_data_path('ExcelBinOutput/AvatarExcelConfigData.json')
            avatars = load_json(str(avatar_file))
            return {a['id']: a for a in avatars if 'id' in a}
        except:
            self.logger.warning("无法加载AvatarExcelConfigData.json")
            return {}
    
    def _load_talk_data(self, talk_id: int) -> Optional[Dict]:
        """
        加载Talk对话数据
        
        参数:
            talk_id: Talk ID
            
        返回:
            Talk数据字典，如果文件不存在则返回None
        """
        talk_file = get_data_path(f'BinOutput/Talk/Quest/{talk_id}.json')
        if talk_file.exists():
            try:
                return load_json(str(talk_file))
            except Exception as e:
                self.logger.debug(f"加载Talk文件失败 {talk_id}: {e}")
        return None

    def get_role_name(self, role_type: str, role_id: Any) -> str:
        """
        解析角色名称
        
        参数:
            role_type: 角色类型
            role_id: 角色ID
        
        返回:
            角色名称
        """
        if role_type == 'TALK_ROLE_PLAYER':
            return '旅行者'
        
        # 尝试转换ID为整数
        try:
            role_id_int = int(role_id)
        except (ValueError, TypeError):
            return 'Unknown'
        
        # 尝试从NPC配置获取
        if role_type in ['TALK_ROLE_NPC', 'TALK_ROLE_GADGET']:
            if role_id_int in self.npc_config:
                name_hash = self.npc_config[role_id_int].get('nameTextMapHash')
                if name_hash:
                    name = self.text_parser.get_text(name_hash)
                    if name:
                        return name
        
        # 尝试从Avatar配置获取
        if role_id_int in self.avatar_config:
            name_hash = self.avatar_config[role_id_int].get('nameTextMapHash')
            if name_hash:
                name = self.text_parser.get_text(name_hash)
                if name:
                    return name
        
        return 'Unknown'
    
    def _build_dialog_tree(self, dialog_list: List[Dict], visited: Optional[Set[int]] = None) -> List[Dict]:
        """
        从dialogList构建对话树
        
        参数:
            dialog_list: 对话列表（来自Talk文件的dialogList）
            visited: 已访问的对话ID集合
            
        返回:
            对话树列表
        """
        if not dialog_list:
            return []
        
        if visited is None:
            visited = set()
        
        # 构建ID到对话数据的映射
        dialog_map = {d['id']: d for d in dialog_list}
        
        # 找出所有被引用的对话ID（非根节点）
        referenced_ids = set()
        for dialog in dialog_list:
            for next_id in dialog.get('nextDialogs', []):
                referenced_ids.add(next_id)
        
        # 根节点是没有被引用的对话
        root_ids = [d['id'] for d in dialog_list if d['id'] not in referenced_ids]
        
        # 如果没有找到根节点，使用第一个对话作为根
        if not root_ids and dialog_list:
            root_ids = [dialog_list[0]['id']]
        
        def build_node(dialog_id: int, current_visited: Set[int]) -> Optional[Dict]:
            """递归构建节点"""
            if dialog_id in current_visited:
                return None
            if dialog_id not in dialog_map:
                return None
            
            current_visited.add(dialog_id)
            dialog = dialog_map[dialog_id]
            
            # 提取角色信息（已解码）
            role_info = dialog.get('talkRole', {})
            # 支持解码后的字段名 'type' 和原始字段名 '_type'
            role_type = role_info.get('type', role_info.get('_type', ''))
            # 支持解码后的字段名 'id' 和原始字段名 '_id'
            role_id = role_info.get('id', role_info.get('_id', ''))
            
            # 获取角色名
            role_name = self.get_role_name(role_type, role_id)
            
            # 获取文本
            text_hash = dialog.get('talkContentTextMapHash')
            text = self.text_parser.get_text(text_hash) if text_hash else ''
            
            node = {
                'id': dialog_id,
                'role': role_name,
                'role_type': role_type,
                'role_id': str(role_id),
                'text': text,
                'next': []
            }
            
            # 递归处理子节点
            for next_id in dialog.get('nextDialogs', []):
                child = build_node(next_id, current_visited.copy())
                if child:
                    node['next'].append(child)
            
            return node
        
        trees = []
        for root_id in root_ids:
            tree = build_node(root_id, visited.copy())
            if tree:
                trees.append(tree)
        
        return trees
    
    def process_talk(self, talk_id: int) -> Optional[List[Dict]]:
        """
        处理一个Talk（对话序列）
        
        参数:
            talk_id: Talk ID
        
        返回:
            对话树列表
        """
        talk_data = self._load_talk_data(talk_id)
        if not talk_data:
            return None
        
        # 先解码Talk数据
        decoded_talk = self._decode_talk_data(talk_data)
        
        # 获取对话列表（使用解码后的字段名）
        dialog_list = decoded_talk.get('dialogList', [])
        if not dialog_list:
            return None
        
        # 解码对话列表中的每个条目
        decoded_dialog_list = self._decode_dialog_list(dialog_list)
        
        return self._build_dialog_tree(decoded_dialog_list)
    
    def _sanitize_filename(self, name: str) -> str:
        """
        清理文件名，移除非法字符
        
        参数:
            name: 原始名称
        
        返回:
            清理后的名称
        """
        if not name:
            return ''
        # 移除或替换非法字符
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # 移除前后空格
        name = name.strip()
        # 限制长度
        if len(name) > 100:
            name = name[:100]
        return name
    
    def _extract_icon_suffix(self, icon_path: str) -> str:
        """
        从icon路径提取后缀部分
        例如: "UI_ChapterIcon_Sumeru" -> "Sumeru"
        
        参数:
            icon_path: icon路径
        
        返回:
            后缀部分
        """
        if not icon_path:
            return 'Unknown'
        
        # 移除前缀 "UI_ChapterIcon_"
        if '_' in icon_path:
            parts = icon_path.split('_')
            return parts[-1] if parts else 'Unknown'
        
        return icon_path
    
    def _get_chapter_info(self, chapter_id: int) -> Dict[str, Any]:
        """
        获取章节信息
        
        参数:
            chapter_id: 章节ID
        
        返回:
            章节信息字典
        """
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
    
    def _extract_quest_type(self, quest_data: Dict) -> str:
        """
        从任务数据中提取任务类型
        
        优先从questType字段（解码后）直接获取，然后尝试luaPath，最后从chapterId推断
        
        参数:
            quest_data: 任务数据字典（已解码）
        
        返回:
            任务类型代码（AQ/LQ/WQ/EQ/IQ等）
        """
        # 方法1: 直接从 questType 字段获取（解码后的AFKIEPNELHE字段）
        quest_type = quest_data.get('questType', '')
        if quest_type and quest_type in ['AQ', 'LQ', 'WQ', 'EQ', 'IQ']:
            return quest_type
        
        # 方法2: 从luaPath提取（支持解码后的字段名）
        lua_path = quest_data.get('luaPath', '')
        if lua_path:
            # 格式如: "Actor/Quest/AQ306" 或 "Actor/Quest/LQ/LQ11110"
            # 提取Quest/后面的类型前缀
            if '/Quest/' in lua_path:
                after_quest = lua_path.split('/Quest/')[-1]
                # 提取前两个字母作为类型
                for prefix in ['AQ', 'LQ', 'WQ', 'EQ', 'IQ']:
                    if after_quest.startswith(prefix):
                        return prefix
        
        # 方法3: 从chapterId推断（备用）
        chapter_id = quest_data.get('chapterId', 0)
        if chapter_id:
            # 1000-1999: 魔神任务章节
            if 1000 <= chapter_id < 2000:
                return 'AQ'
            # 其他范围可以根据需要添加
        
        return 'Unknown'
    
    def extract_quest(self, main_quest_id: int) -> Optional[Dict[str, Any]]:
        """
        提取单个主任务的完整信息（包含子任务和对话）
        
        参数:
            main_quest_id: 主任务ID
        
        返回:
            任务数据
        """
        if main_quest_id not in self.quest_files:
            return None
        
        # 从BinOutput/Quest/{id}.json加载任务数据
        quest_file = self.quest_files[main_quest_id]
        try:
            raw_quest = load_json(str(quest_file))
            # 解码加密字段
            main_quest = self._decode_quest_data(raw_quest)
        except Exception as e:
            self.logger.warning(f"加载任务文件失败 {main_quest_id}: {e}")
            return None
        
        # 获取标题和描述
        title = self.text_parser.get_text(main_quest.get('titleTextMapHash', 0))
        description = self.text_parser.get_text(main_quest.get('descTextMapHash', 0))
        
        if not title:
            title = f'Quest_{main_quest_id}'
        
        # 获取任务类型（从luaPath字段提取，如 "Actor/Quest/AQ306" -> "AQ"）
        quest_type = self._extract_quest_type(main_quest)
        quest_type_name = self.QUEST_TYPES.get(quest_type, quest_type)
        
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
        
        # 根据任务类型重命名 icon_suffix 字段
        if quest_type == 'LQ':
            quest_data['role'] = icon_suffix
        elif quest_type == 'EQ':
            quest_data['festival'] = icon_suffix
        elif quest_type == 'AQ':
            quest_data['chapter'] = icon_suffix
        elif quest_type in ['WQ', 'IQ']:
            quest_data['region'] = icon_suffix
        else:
            quest_data['chapter_icon_suffix'] = icon_suffix
        
        # 处理子任务（subQuests）
        sub_quests = main_quest.get('subQuests', [])
        # 解码每个子任务的字段
        decoded_sub_quests = [self._decode_subquest_data(sub) for sub in sub_quests]
        decoded_sub_quests.sort(key=lambda x: x.get('order', 0))
        
        for sub in decoded_sub_quests:
            sub_id = sub.get('subId')
            sub_data = {
                'id': sub_id,
                'order': sub.get('order', 0),
                'description': self.text_parser.get_text(sub.get('descTextMapHash', 0)),
            }
            quest_data['sub_quests'].append(sub_data)
        
        # 处理对话（talks）
        talks = main_quest.get('talks', [])
        
        for talk_info in talks:
            # 解码talk信息
            decoded_talk_info = self._decode_talk_data(talk_info)
            talk_id = decoded_talk_info.get('id')
            if not talk_id:
                continue
            
            # 获取talk的额外信息
            npc_id = decoded_talk_info.get('npcId', [])
            
            # 从BinOutput/Talk/Quest/{talkId}.json加载对话数据
            dialogue_tree = self.process_talk(talk_id)
            
            talk_data = {
                'talk_id': talk_id,
                'npc_ids': npc_id if isinstance(npc_id, list) else [npc_id] if npc_id else [],
                'dialogues': dialogue_tree if dialogue_tree else []
            }
            
            quest_data['talks'].append(talk_data)
        
        return quest_data
    
    def extract_all_quests(self, output_dir: str):
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
            
            # 提取任务数据
            quest_data = self.extract_quest(main_quest_id)
            if not quest_data:
                continue
            
            # 获取元数据
            quest_type = quest_data.get('type', 'Unknown')
            quest_type_name = quest_data['type_name']
            chapter_id = quest_data['chapter_id']
            chapter_title = quest_data['chapter_title']
            
            # 确定中间字段名 (role/festival/chapter/region)
            middle_name = 'Unknown'
            if 'role' in quest_data:
                middle_name = quest_data['role']
            elif 'festival' in quest_data:
                middle_name = quest_data['festival']
            elif 'chapter' in quest_data:
                middle_name = quest_data['chapter']
            elif 'region' in quest_data:
                middle_name = quest_data['region']
            elif 'chapter_icon_suffix' in quest_data:
                middle_name = quest_data['chapter_icon_suffix']
            
            # 构建第一层文件夹: chapter_id-middle-chapter_title
            # 需要清理文件名
            safe_chapter_title = self._sanitize_filename(chapter_title)
            safe_middle = self._sanitize_filename(middle_name)
            
            folder_name = f"{chapter_id}-{safe_middle}-{safe_chapter_title}"
            
            type_dir = output_path / quest_type_name / folder_name
            type_dir.mkdir(parents=True, exist_ok=True)
            
            # 构建第二层文件名: id-title.json
            safe_title = self._sanitize_filename(quest_data['title'])
            if not safe_title:
                safe_title = f"Quest_{main_quest_id}"
            
            file_name = f"{quest_data['id']}-{safe_title}.json"
            output_file = type_dir / file_name
            
            # 保存
            save_json(quest_data, str(output_file))
            success_count += 1
            
            if count % 100 == 0:
                self.logger.info(f"已处理 {count}/{len(self.quest_files)} 个任务（成功 {success_count} 个）...")
        
        self.logger.info(f"任务提取完成，共处理 {count} 个任务，成功 {success_count} 个")
        
        # 生成统计信息
        stats = self._generate_statistics(output_path)
        stats_file = output_path / 'extraction_stats.json'
        save_json(stats, str(stats_file))
        self.logger.info(f"统计信息已保存到: {stats_file}")
    
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


def main():
    """测试函数"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 创建提取器
    extractor = QuestDialogueExtractor(language='CHS')
    
    # 设置输出目录
    output_dir = get_data_path('../genshin-extractors/output/quests')
    
    # 提取所有任务
    extractor.extract_all_quests(str(output_dir))
    
    print("\n" + "=" * 60)
    print("任务对话提取完成")
    print("=" * 60)
    print(f"输出目录: {output_dir}")


if __name__ == '__main__':
    main()
