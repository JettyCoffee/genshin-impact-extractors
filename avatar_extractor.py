"""
角色(Avatar)提取器
提取角色的基础信息、个人资料、角色故事和语音
参考 odl/persona_builder.py 实现，但集中存储所有角色
"""

from typing import Dict, List, Any, Optional

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


class AvatarExtractor:
    """角色信息提取器"""
    
    # 身体类型映射
    BODY_TYPES = {
        'BODY_BOY': '少年',
        'BODY_GIRL': '少女',
        'BODY_MALE': '成年男性',
        'BODY_LADY': '成年女性',
        'BODY_LOLI': '萝莉'
    }
    
    # 武器类型映射
    WEAPON_TYPES = {
        'WEAPON_SWORD_ONE_HAND': '单手剑',
        'WEAPON_CLAYMORE': '双手剑',
        'WEAPON_BOW': '弓',
        'WEAPON_CATALYST': '法器',
        'WEAPON_POLE': '长柄武器'
    }
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化角色提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP等)
        """
        self.language = language
        self.logger = setup_logger(__name__)
        
        # 初始化文本解析器
        self.text_parser = TextMapParser(language)
        
        # 加载角色相关数据
        self.logger.info("加载角色数据...")
        self.avatars = self._load_avatars()
        self.fetter_info = self._load_fetter_info()
        self.fetter_stories = self._load_fetter_stories()
        self.fetters = self._load_fetters()
        
        self.logger.info(
            f"成功加载 {len(self.avatars)} 个角色配置, "
            f"{len(self.fetter_info)} 个角色资料, "
            f"{len(self.fetter_stories)} 个角色故事, "
            f"{len(self.fetters)} 个语音"
        )
    
    def _load_avatars(self) -> Dict[int, Dict]:
        """加载角色配置数据"""
        avatar_file = get_data_path('ExcelBinOutput/AvatarExcelConfigData.json')
        avatars = load_json(str(avatar_file))
        # 转换为字典，以ID为键
        return {avatar['id']: avatar for avatar in avatars if 'id' in avatar}
    
    def _load_fetter_info(self) -> Dict[int, Dict]:
        """加载角色资料配置数据"""
        try:
            fetter_file = get_data_path('ExcelBinOutput/FetterInfoExcelConfigData.json')
            fetter_list = load_json(str(fetter_file))
            # 以avatarId为键
            return {item['avatarId']: item for item in fetter_list if 'avatarId' in item}
        except:
            self.logger.warning("无法加载FetterInfoExcelConfigData.json")
            return {}
    
    def _load_fetter_stories(self) -> List[Dict]:
        """加载角色故事配置数据"""
        try:
            story_file = get_data_path('ExcelBinOutput/FetterStoryExcelConfigData.json')
            return load_json(str(story_file))
        except:
            self.logger.warning("无法加载FetterStoryExcelConfigData.json")
            return []
    
    def _load_fetters(self) -> List[Dict]:
        """加载语音配置数据"""
        try:
            fetter_file = get_data_path('ExcelBinOutput/FettersExcelConfigData.json')
            return load_json(str(fetter_file))
        except:
            self.logger.warning("无法加载FettersExcelConfigData.json")
            return []
    
    def extract_avatar_info(self, avatar_id: int) -> Optional[Dict[str, Any]]:
        """
        提取单个角色的完整信息
        
        参数:
            avatar_id: 角色ID
        
        返回:
            结构化的角色信息，如果角色无效则返回None
        """
        if avatar_id not in self.avatars:
            self.logger.debug(f"角色ID {avatar_id} 不存在")
            return None
        
        avatar_data = self.avatars[avatar_id]
        
        # 获取角色名称
        name = self.text_parser.get_text(avatar_data.get('nameTextMapHash', 0))
        
        # 如果没有名称，跳过（可能是测试数据）
        if not name:
            return None
        
        # 提取基础信息
        info = {
            'id': avatar_id,
            'name': name,
            'description': self.text_parser.get_text(avatar_data.get('descTextMapHash', 0)),
            'body_type': avatar_data.get('bodyType', ''),
            'body_type_name': self.BODY_TYPES.get(avatar_data.get('bodyType', ''), ''),
            'weapon_type': avatar_data.get('weaponType', ''),
            'weapon_type_name': self.WEAPON_TYPES.get(avatar_data.get('weaponType', ''), ''),
            'icon': avatar_data.get('iconName', ''),
            'quality_type': avatar_data.get('qualityType', ''),  # 星级相关
        }
        
        # 提取个人资料信息
        if avatar_id in self.fetter_info:
            fetter_info = self.fetter_info[avatar_id]
            info['profile'] = {
                'title': self.text_parser.get_text(fetter_info.get('avatarTitleTextMapHash', 0)),
                'detail': self.text_parser.get_text(fetter_info.get('avatarDetailTextMapHash', 0)),
                'constellation': self.text_parser.get_text(fetter_info.get('avatarConstellationBeforTextMapHash', 0)),
                'native': self.text_parser.get_text(fetter_info.get('avatarNativeTextMapHash', 0)),
                'vision': self.text_parser.get_text(fetter_info.get('avatarVisionBeforTextMapHash', 0)),
                'cv': {
                    'chinese': self.text_parser.get_text(fetter_info.get('cvChineseTextMapHash', 0)),
                    'japanese': self.text_parser.get_text(fetter_info.get('cvJapaneseTextMapHash', 0)),
                    'english': self.text_parser.get_text(fetter_info.get('cvEnglishTextMapHash', 0)),
                    'korean': self.text_parser.get_text(fetter_info.get('cvKoreanTextMapHash', 0))
                },
                'birthday': f"{fetter_info.get('infoBirthMonth', 0)}/{fetter_info.get('infoBirthDay', 0)}"
            }
        else:
            info['profile'] = {}
        
        # 提取角色故事
        avatar_stories = [s for s in self.fetter_stories if s.get('avatarId') == avatar_id]
        stories = []
        for story in avatar_stories:
            title = self.text_parser.get_text(story.get('storyTitleTextMapHash', 0))
            content = self.text_parser.get_text(story.get('storyContextTextMapHash', 0))
            if title and content:
                stories.append({
                    'fetter_id': story.get('fetterId', 0),
                    'title': title,
                    'content': content
                })
        
        info['stories'] = stories
        info['story_count'] = len(stories)
        
        # 提取语音
        avatar_fetters = [f for f in self.fetters if f.get('avatarId') == avatar_id]
        voice_overs = []
        for fetter in avatar_fetters:
            title = self.text_parser.get_text(fetter.get('voiceTitleTextMapHash', 0))
            content = self.text_parser.get_text(fetter.get('voiceFileTextTextMapHash', 0))
            if title and content:
                # 提取关系信息（如果标题是"关于..."）
                relation = None
                if self.language == 'CHS':
                    if title.startswith('关于'):
                        relation = title[2:]
                elif self.language == 'EN':
                    if title.startswith('About '):
                        relation = title[6:]
                
                vo_entry = {
                    'fetter_id': fetter.get('fetterId', 0),
                    'title': title,
                    'content': content,
                    'voice_file': fetter.get('voiceFile', '')
                }
                if relation:
                    vo_entry['relation'] = relation
                
                voice_overs.append(vo_entry)
        
        info['voice_overs'] = voice_overs
        info['voice_count'] = len(voice_overs)
        
        return info
    
    def extract_all(self, skip_test_avatars: bool = True) -> List[Dict[str, Any]]:
        """
        提取所有角色的完整信息
        
        参数:
            skip_test_avatars: 是否跳过测试角色（ID >= 11000000的角色）
        
        返回:
            完整的角色信息列表
        """
        self.logger.info("开始提取所有角色信息...")
        
        all_avatars = []
        
        for avatar_id in self.avatars.keys():
            # 跳过测试角色
            if skip_test_avatars and avatar_id >= 11000000:
                continue
            
            # 提取角色信息
            avatar_info = self.extract_avatar_info(avatar_id)
            if avatar_info:
                all_avatars.append(avatar_info)
                self.logger.debug(
                    f"已提取角色: {avatar_info['name']} (ID: {avatar_id}, "
                    f"故事: {avatar_info['story_count']}, 语音: {avatar_info['voice_count']})"
                )
        
        self.logger.info(f"成功提取 {len(all_avatars)} 个角色信息")
        avatars_with_stories = sum(1 for a in all_avatars if a.get('story_count', 0) > 0)
        avatars_with_voices = sum(1 for a in all_avatars if a.get('voice_count', 0) > 0)
        self.logger.info(f"其中 {avatars_with_stories} 个角色有故事, {avatars_with_voices} 个角色有语音")
        
        return all_avatars
    
    def save_to_file(self, output_file: str, avatars: Optional[List[Dict]] = None):
        """
        保存角色数据到文件（集中存储）
        
        参数:
            output_file: 输出文件路径
            avatars: 角色数据列表，如果为None则提取所有
        """
        if avatars is None:
            avatars = self.extract_all()
        
        save_json(avatars, output_file)
        self.logger.info(f"角色数据已保存到: {output_file}")
    
    def get_avatars_by_weapon_type(self, weapon_type: str) -> List[Dict]:
        """
        按武器类型筛选角色
        
        参数:
            weapon_type: 武器类型
        
        返回:
            该武器类型的所有角色
        """
        all_avatars = self.extract_all()
        return [a for a in all_avatars if a.get('weapon_type') == weapon_type]
    
    def get_avatars_by_body_type(self, body_type: str) -> List[Dict]:
        """
        按身体类型筛选角色
        
        参数:
            body_type: 身体类型
        
        返回:
            该身体类型的所有角色
        """
        all_avatars = self.extract_all()
        return [a for a in all_avatars if a.get('body_type') == body_type]


def main():
    """测试函数"""
    import sys
    
    # 设置日志级别
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 创建提取器
    extractor = AvatarExtractor(language='CHS')
    
    # 提取所有角色
    avatars = extractor.extract_all(skip_test_avatars=True)
    
    # 保存到输出目录
    output_dir = get_data_path('../genshin_extractors/output')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'avatars.json'
    
    extractor.save_to_file(str(output_file), avatars)
    
    # 显示统计信息
    print("\n" + "=" * 60)
    print("角色提取统计")
    print("=" * 60)
    print(f"总角色数: {len(avatars)}")
    print(f"有故事的角色: {sum(1 for a in avatars if a.get('story_count', 0) > 0)}")
    print(f"有语音的角色: {sum(1 for a in avatars if a.get('voice_count', 0) > 0)}")
    
    # 按武器类型统计
    weapon_stats = {}
    for avatar in avatars:
        wtype = avatar.get('weapon_type_name', 'Unknown')
        weapon_stats[wtype] = weapon_stats.get(wtype, 0) + 1
    
    print("\n按武器类型统计:")
    for wtype, count in sorted(weapon_stats.items()):
        if count > 0:
            print(f"  {wtype}: {count} 个")
    
    # 按身体类型统计
    body_stats = {}
    for avatar in avatars:
        btype = avatar.get('body_type_name', 'Unknown')
        body_stats[btype] = body_stats.get(btype, 0) + 1
    
    print("\n按身体类型统计:")
    for btype, count in sorted(body_stats.items()):
        if count > 0:
            print(f"  {btype}: {count} 个")
    
    # 显示一些角色示例
    print("\n角色示例（前5个）:")
    for avatar in avatars[:5]:
        print(f"\n  {avatar['name']} (ID: {avatar['id']})")
        print(f"    武器: {avatar['weapon_type_name']}")
        if avatar.get('profile'):
            print(f"    称号: {avatar['profile'].get('title', 'N/A')}")
            print(f"    生日: {avatar['profile'].get('birthday', 'N/A')}")
        print(f"    故事数: {avatar['story_count']}, 语音数: {avatar['voice_count']}")


if __name__ == '__main__':
    main()
