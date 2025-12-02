"""
圣遗物套装提取器
按套装组织圣遗物数据
"""

from typing import Any, Dict, List


class ReliquarySetExtractor:
    """圣遗物套装提取器"""
    
    def extract_sets(self, all_relics: List[Dict], relic_sets: List[Dict]) -> List[Dict[str, Any]]:
        """
        按套装组织圣遗物数据
        
        参数:
            all_relics: 所有圣遗物数据列表
            relic_sets: 套装配置数据列表
        
        返回:
            套装信息列表
        """
        # 按 ID 索引圣遗物
        relic_by_id = {r['id']: r for r in all_relics}
        
        all_sets = []
        
        for set_data in relic_sets:
            set_id = set_data.get('setId', 0)
            
            if set_id == 0:
                continue
            
            # 获取套装包含的圣遗物列表
            contains_list = set_data.get('containsList', [])
            
            # 获取套装名称（从第一个部位获取）
            set_name = self._get_set_name(contains_list, relic_by_id)
            
            # 获取套装效果
            set_effects = self._get_set_effects(set_data)
            
            # 收集套装的所有部位
            pieces = [relic_by_id[rid] for rid in contains_list if rid in relic_by_id]
            
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
        
        return all_sets
    
    def _get_set_name(self, contains_list: List[int], relic_by_id: Dict[int, Dict]) -> str:
        """
        从第一个部位获取套装名称
        
        参数:
            contains_list: 套装包含的圣遗物 ID 列表
            relic_by_id: 圣遗物 ID 到数据的映射
        
        返回:
            套装名称
        """
        if not contains_list:
            return ''
        
        first_id = contains_list[0]
        if first_id not in relic_by_id:
            return ''
        
        first_piece = relic_by_id[first_id]
        name = first_piece.get('name', '')
        
        # 套装名称通常是部位名称的前缀
        if '·' in name:
            return name.split('·')[0]
        
        return ''
    
    def _get_set_effects(self, set_data: Dict) -> List[Dict]:
        """
        获取套装效果
        
        参数:
            set_data: 套装配置数据
        
        返回:
            套装效果列表
        """
        set_effects = []
        equip_affixes = set_data.get('equipAffixId', 0)
        
        if equip_affixes:
            need_nums = set_data.get('setNeedNum', [])
            for need_num in need_nums:
                set_effects.append({
                    'piece_count': need_num,
                    'affix_id': equip_affixes
                })
        
        return set_effects
