"""
命令行入口
提供提取器的命令行接口
"""

import argparse
import logging
import sys
from pathlib import Path

from ..core import get_data_path, save_json
from ..extractors import (
    AvatarExtractor,
    BookExtractor,
    WeaponExtractor,
    ReliquaryExtractor,
    QuestDialogueExtractor,
)


def setup_logging(verbose: bool = False) -> None:
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('extraction.log', encoding='utf-8')
        ]
    )


def extract_weapons(output_dir: Path, language: str) -> dict:
    """提取武器数据"""
    print("\n" + "-" * 60)
    print("提取武器数据...")
    print("-" * 60)
    
    extractor = WeaponExtractor(language=language)
    weapons = extractor.extract_all()
    
    weapon_file = output_dir / 'weapons.json'
    extractor.save_to_file(str(weapon_file), weapons)
    
    stats = {
        'total': len(weapons),
        'with_story': sum(1 for w in weapons if w.get('has_story')),
        'file': 'weapons.json'
    }
    
    print(f"✓ 武器提取完成: 总数 {stats['total']}, 有故事 {stats['with_story']}")
    return stats


def extract_reliquaries(output_dir: Path, language: str) -> dict:
    """提取圣遗物数据"""
    print("\n" + "-" * 60)
    print("提取圣遗物数据...")
    print("-" * 60)
    
    extractor = ReliquaryExtractor(language=language)
    sets = extractor.extract_sets()
    
    set_file = output_dir / 'reliquary_sets.json'
    extractor.save_to_file(str(set_file), sets)
    
    stats = {
        'total_sets': len(sets),
        'sets_with_full_story': sum(1 for s in sets if s.get('has_full_story')),
        'file': 'reliquary_sets.json'
    }
    
    print(f"✓ 圣遗物提取完成: 套装数 {stats['total_sets']}, 完整故事 {stats['sets_with_full_story']}")
    return stats


def extract_books(output_dir: Path, language: str) -> dict:
    """提取书籍数据"""
    print("\n" + "-" * 60)
    print("提取书籍数据...")
    print("-" * 60)
    
    extractor = BookExtractor(language=language)
    
    # 提取普通书籍
    books = extractor.extract_all(include_all_types=True)
    book_file = output_dir / 'books.json'
    extractor.save_to_file(str(book_file), books)
    
    # 提取系列
    series = extractor.extract_series()
    series_file = output_dir / 'book_series.json'
    save_json(series, str(series_file))
    
    # 提取皮肤
    costumes = extractor.extract_costumes()
    costume_file = output_dir / 'costumes.json'
    save_json(costumes, str(costume_file))
    
    # 提取风之翼
    windgliders = extractor.extract_windgliders()
    windglider_file = output_dir / 'windgliders.json'
    save_json(windgliders, str(windglider_file))
    
    book_stats = extractor.get_statistics()
    
    stats = {
        'total': book_stats['total_count'],
        'with_content': book_stats['with_content_count'],
        'series_count': len(series),
        'costumes': len(costumes),
        'windgliders': len(windgliders),
        'type_distribution': book_stats['type_distribution'],
        'files': ['books.json', 'book_series.json', 'costumes.json', 'windgliders.json']
    }
    
    print(f"✓ 书籍提取完成: 总数 {stats['total']}, 有内容 {stats['with_content']}, 系列 {stats['series_count']}")
    return stats


def extract_avatars(output_dir: Path, language: str) -> dict:
    """提取角色数据"""
    print("\n" + "-" * 60)
    print("提取角色数据...")
    print("-" * 60)
    
    extractor = AvatarExtractor(language=language)
    avatars = extractor.extract_all(skip_test_avatars=True)
    
    avatar_file = output_dir / 'avatars.json'
    extractor.save_to_file(str(avatar_file), avatars)
    
    stats = {
        'total': len(avatars),
        'with_stories': sum(1 for a in avatars if a.get('story_count', 0) > 0),
        'with_voices': sum(1 for a in avatars if a.get('voice_count', 0) > 0),
        'file': 'avatars.json'
    }
    
    print(f"✓ 角色提取完成: 总数 {stats['total']}, 有故事 {stats['with_stories']}, 有语音 {stats['with_voices']}")
    return stats


def extract_quests(output_dir: Path, language: str) -> dict:
    """提取任务对话数据"""
    print("\n" + "-" * 60)
    print("提取任务对话数据...")
    print("-" * 60)
    
    extractor = QuestDialogueExtractor(language=language)
    quest_output_dir = output_dir / 'quests'
    extractor.extract_all_to_files(str(quest_output_dir))
    
    stats = {
        'total_quest_files': len(extractor.quest_files),
        'output_dir': 'quests/'
    }
    
    print(f"✓ 任务对话提取完成: {stats['total_quest_files']} 个任务文件")
    return stats


def extract_all(output_dir: Path, language: str) -> dict:
    """提取所有数据"""
    summary = {}
    
    summary['weapons'] = extract_weapons(output_dir, language)
    summary['reliquaries'] = extract_reliquaries(output_dir, language)
    summary['books'] = extract_books(output_dir, language)
    summary['avatars'] = extract_avatars(output_dir, language)
    summary['quests'] = extract_quests(output_dir, language)
    
    # 保存汇总信息
    summary_file = output_dir / 'extraction_summary.json'
    save_json(summary, str(summary_file))
    
    return summary


def print_summary(summary: dict) -> None:
    """打印汇总信息"""
    print("\n" + "=" * 60)
    print("提取汇总")
    print("=" * 60)
    
    if 'weapons' in summary:
        print(f"  • 武器: {summary['weapons']['total']} 个")
    if 'reliquaries' in summary:
        print(f"  • 圣遗物: {summary['reliquaries']['total_sets']} 个套装")
    if 'books' in summary:
        print(f"  • 书籍: {summary['books']['total']} 个 ({summary['books']['series_count']} 个系列)")
    if 'avatars' in summary:
        print(f"  • 角色: {summary['avatars']['total']} 个")
    if 'quests' in summary:
        print(f"  • 任务: {summary['quests']['total_quest_files']} 个")
    
    print("\n" + "=" * 60)
    print("✓ 所有提取任务完成！")
    print("=" * 60)


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(
        description='原神游戏数据提取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s                    # 提取所有数据
  %(prog)s --type weapon      # 仅提取武器数据
  %(prog)s --type avatar      # 仅提取角色数据
  %(prog)s --language EN      # 使用英文提取
        '''
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=['all', 'weapon', 'reliquary', 'book', 'avatar', 'quest'],
        default='all',
        help='要提取的数据类型 (默认: all)'
    )
    
    parser.add_argument(
        '--language', '-l',
        default='CHS',
        help='语言代码 (默认: CHS)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='输出目录 (默认: ./output)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    # 设置输出目录
    if args.output:
        output_dir = Path(args.output)
    else:
        # 默认输出到 genshin-extractors/output
        output_dir = Path(__file__).parent.parent.parent / 'output'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("原神游戏数据提取工具")
    print("=" * 60)
    print(f"语言: {args.language}")
    print(f"输出目录: {output_dir}")
    
    try:
        summary = {}
        
        if args.type == 'all':
            summary = extract_all(output_dir, args.language)
        elif args.type == 'weapon':
            summary['weapons'] = extract_weapons(output_dir, args.language)
        elif args.type == 'reliquary':
            summary['reliquaries'] = extract_reliquaries(output_dir, args.language)
        elif args.type == 'book':
            summary['books'] = extract_books(output_dir, args.language)
        elif args.type == 'avatar':
            summary['avatars'] = extract_avatars(output_dir, args.language)
        elif args.type == 'quest':
            summary['quests'] = extract_quests(output_dir, args.language)
        
        print_summary(summary)
        return 0
        
    except Exception as e:
        logging.error(f"提取过程中发生错误: {e}", exc_info=True)
        print(f"\n✗ 错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
