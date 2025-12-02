"""
武器提取器
基于ID映射规律：Document ID = Weapon ID + 180000
"""

from typing import Dict, List, Any, Optional

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


class WeaponExtractor:
    """武器信息提取器"""
    
    # 武器ID到Document ID的映射偏移量
    STORY_ID_OFFSET = 180000
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化武器提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP等)
        """
        self.language = language
        self.logger = setup_logger(__name__)
        
        # 初始化文本解析器和故事提取器
        self.text_parser = TextMapParser(language)
        self.story_extractor = StoryContentExtractor(language)
        
        # 加载武器数据
        self.logger.info("加载武器数据...")
        self.weapons = self._load_weapons()
        self.logger.info(f"成功加载 {len(self.weapons)} 个武器数据")
    
    def _load_weapons(self) -> List[Dict]:
        """加载武器配置数据"""
        weapon_file = get_data_path('ExcelBinOutput/WeaponExcelConfigData.json')
        return load_json(str(weapon_file))
    
    def extract_weapon_info(self, weapon_data: Dict) -> Optional[Dict[str, Any]]:
        """
        提取单个武器的信息
        
        参数:
            weapon_data: 武器原始数据
        
        返回:
            结构化的武器信息，如果武器无效则返回None
        """
        weapon_id = weapon_data.get('id')
        
        # 获取武器名称
        name = self.text_parser.get_text(weapon_data.get('nameTextMapHash', 0))
        
        # 如果没有名称，跳过该武器（可能是测试数据）
        if not name:
            return None
        
        # 提取基础信息
        info = {
            'id': weapon_id,
            'name': name,
            'description': self.text_parser.get_text(weapon_data.get('descTextMapHash', 0)),
            'weapon_type': weapon_data.get('weaponType', ''),
            'rank_level': weapon_data.get('rankLevel', 0),  # 星级
            'icon': weapon_data.get('icon', ''),
        }
        
        # 提取属性数据
        weapon_props = weapon_data.get('weaponProp', [])
        if weapon_props:
            # 主属性（通常是攻击力）
            main_prop = weapon_props[0] if len(weapon_props) > 0 else {}
            info['main_stat'] = {
                'type': main_prop.get('propType', ''),
                'init_value': main_prop.get('initValue', 0),
                'curve': main_prop.get('type', '')
            }
            
            # 副属性
            if len(weapon_props) > 1:
                sub_prop = weapon_props[1]
                if sub_prop.get('propType') != 'FIGHT_PROP_NONE':
                    info['sub_stat'] = {
                        'type': sub_prop.get('propType', ''),
                        'init_value': sub_prop.get('initValue', 0),
                        'curve': sub_prop.get('type', '')
                    }
        
        # 提取故事内容
        story_id = weapon_data.get('storyId', 0)
        if story_id:
            # 验证ID映射规律
            expected_story_id = weapon_id + self.STORY_ID_OFFSET
            if story_id != expected_story_id:
                self.logger.warning(
                    f"武器 {weapon_id} 的storyId {story_id} 不符合映射规律 "
                    f"(预期: {expected_story_id})"
                )
            
            # 提取故事内容
            story_content = self.story_extractor.get_story_content(story_id)
            if story_content:
                info['story'] = story_content
                info['has_story'] = True
            else:
                info['has_story'] = False
        else:
            info['has_story'] = False
        
        return info
    
    def extract_all(self) -> List[Dict[str, Any]]:
        """
        提取所有武器的完整信息
        
        返回:
            完整的武器信息列表
        """
        self.logger.info("开始提取所有武器信息...")
        
        all_weapons = []
        weapons_with_story = 0
        
        for weapon_data in self.weapons:
            weapon_id = weapon_data.get('id')
            
            # 跳过无效ID
            if not weapon_id:
                continue
            
            # 提取武器信息
            weapon_info = self.extract_weapon_info(weapon_data)
            if weapon_info:
                all_weapons.append(weapon_info)
                
                if weapon_info.get('has_story'):
                    weapons_with_story += 1
                    self.logger.debug(
                        f"已提取武器(含故事): {weapon_info['name']} (ID: {weapon_id})"
                    )
        
        self.logger.info(f"成功提取 {len(all_weapons)} 个武器信息")
        self.logger.info(f"其中 {weapons_with_story} 个武器包含故事")
        
        return all_weapons
    
    def save_to_file(self, output_file: str, weapons: Optional[List[Dict]] = None):
        """
        保存武器数据到文件
        
        参数:
            output_file: 输出文件路径
            weapons: 武器数据列表，如果为None则提取所有
        """
        if weapons is None:
            weapons = self.extract_all()
        
        save_json(weapons, output_file)
        self.logger.info(f"武器数据已保存到: {output_file}")
    
    def get_weapons_by_type(self, weapon_type: str) -> List[Dict]:
        """
        按类型筛选武器
        
        参数:
            weapon_type: 武器类型 (如: WEAPON_SWORD_ONE_HAND, WEAPON_CLAYMORE等)
        
        返回:
            该类型的所有武器
        """
        all_weapons = self.extract_all()
        return [w for w in all_weapons if w.get('weapon_type') == weapon_type]
    
    def get_weapons_by_rarity(self, rank_level: int) -> List[Dict]:
        """
        按稀有度筛选武器
        
        参数:
            rank_level: 稀有度等级 (1-5星)
        
        返回:
            该稀有度的所有武器
        """
        all_weapons = self.extract_all()
        return [w for w in all_weapons if w.get('rank_level') == rank_level]


def main():
    """测试函数"""
    import sys
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    # 创建提取器
    extractor = WeaponExtractor(language='CHS')
    
    # 提取所有武器
    weapons = extractor.extract_all()
    
    # 保存到输出目录
    output_dir = get_data_path('../genshin_extractors/output')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'weapons.json'
    
    extractor.save_to_file(str(output_file), weapons)
    
    # 显示统计信息
    print("\n" + "=" * 60)
    print("武器提取统计")
    print("=" * 60)
    print(f"总武器数: {len(weapons)}")
    print(f"有故事的武器: {sum(1 for w in weapons if w.get('has_story'))}")
    
    # 按类型统计
    weapon_types = {}
    for w in weapons:
        wtype = w.get('weapon_type', 'Unknown')
        weapon_types[wtype] = weapon_types.get(wtype, 0) + 1
    
    print("\n按类型统计:")
    for wtype, count in sorted(weapon_types.items()):
        print(f"  {wtype}: {count} 个")
    
    # 按稀有度统计
    print("\n按稀有度统计:")
    for rarity in range(1, 6):
        count = sum(1 for w in weapons if w.get('rank_level') == rarity)
        if count > 0:
            print(f"  {rarity} 星: {count} 个")


if __name__ == '__main__':
    import logging
    main()
