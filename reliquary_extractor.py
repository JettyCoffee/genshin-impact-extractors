"""
圣遗物提取器
圣遗物按套装组织，每个套装5个部位，每个部位有独立的故事
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict

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


class ReliquaryExtractor:
    """圣遗物信息提取器"""
    
    # 部位类型映射
    EQUIP_TYPES = {
        'EQUIP_BRACER': '生之花',
        'EQUIP_NECKLACE': '死之羽',
        'EQUIP_SHOES': '时之沙',
        'EQUIP_RING': '空之杯',
        'EQUIP_DRESS': '理之冠'
    }
    
    def __init__(self, language: str = 'CHS'):
        """
        初始化圣遗物提取器
        
        参数:
            language: 语言代码 (CHS, EN, JP等)
        """
        self.language = language
        self.logger = setup_logger(__name__)
        
        # 初始化文本解析器和故事提取器
        self.text_parser = TextMapParser(language)
        self.story_extractor = StoryContentExtractor(language)
        
        # 加载圣遗物数据
        self.logger.info("加载圣遗物数据...")
        self.reliquaries = self._load_reliquaries()
        self.relic_sets = self._load_relic_sets()
        self.logger.info(
            f"成功加载 {len(self.reliquaries)} 个圣遗物数据, "
            f"{len(self.relic_sets)} 个套装"
        )
    
    def _load_reliquaries(self) -> List[Dict]:
        """加载圣遗物配置数据"""
        relic_file = get_data_path('ExcelBinOutput/ReliquaryExcelConfigData.json')
        return load_json(str(relic_file))
    
    def _load_relic_sets(self) -> List[Dict]:
        """加载圣遗物套装配置数据"""
        set_file = get_data_path('ExcelBinOutput/ReliquarySetExcelConfigData.json')
        return load_json(str(set_file))
    
    def extract_reliquary_info(self, relic_data: Dict) -> Optional[Dict[str, Any]]:
        """
        提取单个圣遗物的信息
        
        参数:
            relic_data: 圣遗物原始数据
        
        返回:
            结构化的圣遗物信息，如果无效则返回None
        """
        relic_id = relic_data.get('id')
        
        # 获取圣遗物名称
        name = self.text_parser.get_text(relic_data.get('nameTextMapHash', 0))
        
        # 如果没有名称，跳过
        if not name:
            return None
        
        # 提取基础信息
        equip_type = relic_data.get('equipType', '')
        info = {
            'id': relic_id,
            'name': name,
            'description': self.text_parser.get_text(relic_data.get('descTextMapHash', 0)),
            'set_id': relic_data.get('setId', 0),
            'equip_type': equip_type,
            'equip_type_name': self.EQUIP_TYPES.get(equip_type, equip_type),
            'rank_level': relic_data.get('rankLevel', 0),  # 星级
            'icon': relic_data.get('icon', ''),
            'max_level': relic_data.get('maxLevel', 0),
        }
        
        # 提取故事内容
        story_id = relic_data.get('storyId', 0)
        if story_id:
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
        提取所有圣遗物的完整信息
        
        返回:
            完整的圣遗物信息列表
        """
        self.logger.info("开始提取所有圣遗物信息...")
        
        all_relics = []
        relics_with_story = 0
        
        for relic_data in self.reliquaries:
            relic_id = relic_data.get('id')
            
            # 跳过无效ID
            if not relic_id:
                continue
            
            # 提取圣遗物信息
            relic_info = self.extract_reliquary_info(relic_data)
            if relic_info:
                all_relics.append(relic_info)
                
                if relic_info.get('has_story'):
                    relics_with_story += 1
        
        self.logger.info(f"成功提取 {len(all_relics)} 个圣遗物信息")
        self.logger.info(f"其中 {relics_with_story} 个圣遗物包含故事")
        
        return all_relics
    
    def extract_sets(self) -> List[Dict[str, Any]]:
        """
        按套装组织提取圣遗物信息
        
        返回:
            套装信息列表，每个套装包含其所有部位
        """
        self.logger.info("开始按套装提取圣遗物信息...")
        
        # 首先提取所有圣遗物
        all_relics = self.extract_all()
        
        # 按ID索引
        relic_by_id = {r['id']: r for r in all_relics}
        
        # 组织套装数据
        all_sets = []
        
        for set_data in self.relic_sets:
            set_id = set_data.get('setId', 0)
            
            if set_id == 0:
                continue
            
            # 获取套装名称（从第一个部位获取，因为套装本身没有nameTextMapHash）
            contains_list = set_data.get('containsList', [])
            
            set_name = ''
            if contains_list and contains_list[0] in relic_by_id:
                first_piece = relic_by_id[contains_list[0]]
                # 套装名称通常是部位名称的前缀
                set_name = first_piece.get('name', '').split('·')[0] if '·' in first_piece.get('name', '') else ''
            
            # 获取套装效果描述
            set_effects = []
            equip_affixes = set_data.get('equipAffixId', 0)
            if equip_affixes:
                # 2件套效果
                if set_data.get('setNeedNum', []):
                    need_nums = set_data.get('setNeedNum', [])
                    for need_num in need_nums:
                        set_effects.append({
                            'piece_count': need_num,
                            'affix_id': equip_affixes
                        })
            
            # 收集套装的所有部位
            pieces = []
            for relic_id in contains_list:
                if relic_id in relic_by_id:
                    pieces.append(relic_by_id[relic_id])
            
            if not pieces:
                continue
            
            set_info = {
                'set_id': set_id,
                'set_name': set_name or f'圣遗物套装 {set_id}',
                'piece_count': len(pieces),
                'max_rarity': max(p.get('rank_level', 0) for p in pieces) if pieces else 0,
                'pieces': pieces,
                'set_effects': set_effects,
                'has_full_story': all(p.get('has_story', False) for p in pieces)
            }
            
            all_sets.append(set_info)
        
        self.logger.info(f"成功提取 {len(all_sets)} 个圣遗物套装")
        sets_with_full_story = sum(1 for s in all_sets if s.get('has_full_story'))
        self.logger.info(f"其中 {sets_with_full_story} 个套装包含完整故事")
        
        return all_sets
    
    def save_to_file(self, output_file: str, data: Optional[List[Dict]] = None, 
                     organize_by_set: bool = True):
        """
        保存圣遗物数据到文件
        
        参数:
            output_file: 输出文件路径
            data: 圣遗物数据列表，如果为None则提取所有
            organize_by_set: 是否按套装组织数据
        """
        if data is None:
            data = self.extract_sets() if organize_by_set else self.extract_all()
        
        save_json(data, output_file)
        self.logger.info(f"圣遗物数据已保存到: {output_file}")
    
    def get_relics_by_set(self, set_id: int) -> List[Dict]:
        """
        获取指定套装的所有圣遗物
        
        参数:
            set_id: 套装ID
        
        返回:
            该套装的所有圣遗物
        """
        all_relics = self.extract_all()
        return [r for r in all_relics if r.get('set_id') == set_id]
    
    def get_relics_by_rarity(self, rank_level: int) -> List[Dict]:
        """
        按稀有度筛选圣遗物
        
        参数:
            rank_level: 稀有度等级 (1-5星)
        
        返回:
            该稀有度的所有圣遗物
        """
        all_relics = self.extract_all()
        return [r for r in all_relics if r.get('rank_level') == rank_level]


def main():
    """测试函数"""
    import sys
    
    # 设置日志级别
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 创建提取器
    extractor = ReliquaryExtractor(language='CHS')
    
    # 按套装提取
    sets = extractor.extract_sets()
    
    # 保存到输出目录
    output_dir = get_data_path('../genshin-extractors/output')
    output_dir.mkdir(exist_ok=True)
    
    # 保存套装组织的数据
    set_file = output_dir / 'reliquary_sets.json'
    extractor.save_to_file(str(set_file), sets, organize_by_set=True)
    
    # 保存单个圣遗物数据
    all_relics = extractor.extract_all()
    relic_file = output_dir / 'reliquaries.json'
    extractor.save_to_file(str(relic_file), all_relics, organize_by_set=False)
    
    # 显示统计信息
    print("\n" + "=" * 60)
    print("圣遗物提取统计")
    print("=" * 60)
    print(f"总圣遗物数: {len(all_relics)}")
    print(f"总套装数: {len(sets)}")
    print(f"有故事的圣遗物: {sum(1 for r in all_relics if r.get('has_story'))}")
    print(f"有完整故事的套装: {sum(1 for s in sets if s.get('has_full_story'))}")
    
    # 显示一些套装示例
    print("\n套装示例（前5个）:")
    for s in sets[:5]:
        print(f"  {s['set_name']} (ID: {s['set_id']}): {s['piece_count']} 件, "
              f"{s['max_rarity']} 星, 完整故事: {s['has_full_story']}")


if __name__ == '__main__':
    main()
