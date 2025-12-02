"""
主提取脚本
运行所有提取器并生成完整的游戏数据
"""

import sys
import logging
from pathlib import Path
from weapon_extractor import WeaponExtractor
from reliquary_extractor import ReliquaryExtractor
from book_extractor import BookExtractor
from avatar_extractor import AvatarExtractor
from utils import get_data_path


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('extraction.log', encoding='utf-8')
        ]
    )


def main():
    """主函数"""
    print("=" * 80)
    print("原神游戏数据提取工具")
    print("基于ID映射规律分析")
    print("=" * 80)
    print()
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 创建输出目录
    output_dir = get_data_path('../genshin_extractors/output')
    output_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"输出目录: {output_dir}")
    
    try:
        # 1. 提取武器数据
        print("\n" + "-" * 80)
        print("1. 提取武器数据...")
        print("-" * 80)
        weapon_extractor = WeaponExtractor(language='CHS')
        weapons = weapon_extractor.extract_all()
        weapon_file = output_dir / 'weapons.json'
        weapon_extractor.save_to_file(str(weapon_file), weapons)
        
        print(f"\n✓ 武器提取完成:")
        print(f"  - 总数: {len(weapons)}")
        print(f"  - 有故事: {sum(1 for w in weapons if w.get('has_story'))}")
        
        # 2. 提取圣遗物数据
        print("\n" + "-" * 80)
        print("2. 提取圣遗物数据...")
        print("-" * 80)
        relic_extractor = ReliquaryExtractor(language='CHS')
        
        # 提取套装数据
        sets = relic_extractor.extract_sets()
        set_file = output_dir / 'reliquary_sets.json'
        relic_extractor.save_to_file(str(set_file), sets, organize_by_set=True)
        
        print(f"\n✓ 圣遗物提取完成:")
        print(f"  - 总套装数: {len(sets)}")
        print(f"  - 有完整故事的套装: {sum(1 for s in sets if s.get('has_full_story'))}")
        
        # 3. 提取书籍数据
        print("\n" + "-" * 80)
        print("3. 提取书籍数据...")
        print("-" * 80)
        book_extractor = BookExtractor(language='CHS')
        books = book_extractor.extract_all(include_all_types=True)
        book_file = output_dir / 'books.json'
        book_extractor.save_to_file(str(book_file), books)
        
        stats = book_extractor.get_statistics()
        series = book_extractor.extract_series()
        series_file = output_dir / 'book_series.json'
        book_extractor.save_to_file(str(series_file), series)
        
        print(f"\n✓ 书籍提取完成:")
        print(f"  - 总数: {stats['total_count']}")
        print(f"  - 有内容: {stats['with_content_count']}")
        print(f"  - 系列数: {len(series)}")
        print(f"  - 类型分布:")
        for doc_type, count in sorted(stats['type_distribution'].items()):
            type_name = BookExtractor.DOC_TYPES.get(doc_type, doc_type)
            print(f"    • {type_name}: {count} 个")
        
        # 4. 提取角色数据
        print("\n" + "-" * 80)
        print("4. 提取角色数据...")
        print("-" * 80)
        avatar_extractor = AvatarExtractor(language='CHS')
        avatars = avatar_extractor.extract_all(skip_test_avatars=True)
        avatar_file = output_dir / 'avatars.json'
        avatar_extractor.save_to_file(str(avatar_file), avatars)
        
        print(f"\n✓ 角色提取完成:")
        print(f"  - 总数: {len(avatars)}")
        print(f"  - 有故事: {sum(1 for a in avatars if a.get('story_count', 0) > 0)}")
        print(f"  - 有语音: {sum(1 for a in avatars if a.get('voice_count', 0) > 0)}")
        
        # 5. 生成汇总报告
        print("\n" + "=" * 80)
        print("提取汇总")
        print("=" * 80)
        print(f"\n总计提取:")
        print(f"  • 武器: {len(weapons)} 个")
        print(f"  • 圣遗物: {len(sets)} 个套装")
        print(f"  • 书籍: {stats['total_count']} 个 ({len(series)} 个系列)")
        print(f"  • 角色: {len(avatars)} 个")
        print(f"\n故事与内容:")
        print(f"  • 武器故事: {sum(1 for w in weapons if w.get('has_story'))} 个")
        print(f"  • 圣遗物完整故事套装: {sum(1 for s in sets if s.get('has_full_story'))} 个")
        print(f"  • 书籍内容: {stats['with_content_count']} 个")
        print(f"  • 角色故事: {sum(1 for a in avatars if a.get('story_count', 0) > 0)} 个")
        print(f"  • 角色语音: {sum(1 for a in avatars if a.get('voice_count', 0) > 0)} 个")
        print(f"\n所有数据已保存到: {output_dir}")
        
        # 保存汇总信息
        summary = {
            'weapons': {
                'total': len(weapons),
                'with_story': sum(1 for w in weapons if w.get('has_story')),
                'file': 'weapons.json'
            },
            'reliquaries': {
                'total_sets': len(sets),
                'sets_with_full_story': sum(1 for s in sets if s.get('has_full_story')),
                'file': 'reliquary_sets.json'
            },
            'books': {
                'total': stats['total_count'],
                'with_content': stats['with_content_count'],
                'series_count': len(series),
                'type_distribution': stats['type_distribution'],
                'files': ['books.json', 'book_series.json']
            },
            'avatars': {
                'total': len(avatars),
                'with_stories': sum(1 for a in avatars if a.get('story_count', 0) > 0),
                'with_voices': sum(1 for a in avatars if a.get('voice_count', 0) > 0),
                'file': 'avatars.json'
            }
        }
        
        from utils import save_json
        summary_file = output_dir / 'extraction_summary.json'
        save_json(summary, str(summary_file))
        print(f"\n汇总信息已保存到: {summary_file}")
        
        print("\n" + "=" * 80)
        print("✓ 所有提取任务完成！")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        logger.error(f"提取过程中发生错误: {e}", exc_info=True)
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
