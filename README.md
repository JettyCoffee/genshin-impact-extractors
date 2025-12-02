# Genshin Extractors

原神游戏数据提取工具集，用于从 [AnimeGameData](https://github.com/Dimbreath/AnimeGameData) 提取结构化的游戏文本数据。

## 📋 功能概述

本工具集提供多个专用提取器，用于从原神游戏数据中提取：

| 提取器 | 描述 | 输出 |
|--------|------|------|
| `weapon_extractor.py` | 武器信息及故事 | `weapons.json` |
| `reliquary_extractor.py` | 圣遗物套装及故事 | `reliquary_sets.json` |
| `book_extractor.py` | 书籍、信件等文档 | `books.json`, `book_series.json` |
| `avatar_extractor.py` | 角色信息、故事、语音 | `avatars.json` |
| `quest_dialogue_extractor.py` | 任务对话（按类型分类） | `quests/` 目录 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- [AnimeGameData](https://github.com/Dimbreath/AnimeGameData) 数据目录

### 目录结构

```
project_root/
├── AnimeGameData/           # 游戏数据（需要单独获取）
│   ├── BinOutput/
│   ├── ExcelBinOutput/
│   ├── Readable/
│   └── TextMap/
└── genshin-extractors/      # 本项目
    ├── extract_all.py
    ├── utils.py
    ├── weapon_extractor.py
    ├── reliquary_extractor.py
    ├── book_extractor.py
    ├── avatar_extractor.py
    ├── quest_dialogue_extractor.py
    └── output/              # 提取结果输出目录
```

### 运行方式

#### 方式一：提取全部数据（推荐）

```bash
cd genshin-extractors
python extract_all.py
```

这将依次运行所有提取器并生成汇总报告。

#### 方式二：单独运行提取器

```bash
# 提取武器数据
python weapon_extractor.py

# 提取圣遗物数据
python reliquary_extractor.py

# 提取书籍数据
python book_extractor.py

# 提取角色数据
python avatar_extractor.py

# 提取任务对话
python quest_dialogue_extractor.py
```

## 📦 提取器详解

### 1. 武器提取器 (`weapon_extractor.py`)

提取所有武器的基础信息和故事文本。

**提取内容：**
- 武器名称、描述
- 星级、武器类型
- 武器故事（基于 Document ID 映射：`story_id = weapon_id + 180000`）

**输出示例：**
```json
{
  "id": 11501,
  "name": "风鹰剑",
  "description": "...",
  "weapon_type": "WEAPON_SWORD_ONE_HAND",
  "rank_level": 5,
  "has_story": true,
  "story": "..."
}
```

### 2. 圣遗物提取器 (`reliquary_extractor.py`)

按套装提取圣遗物信息，每个套装包含5个部位的故事。

**提取内容：**
- 套装名称、套装效果
- 五个部位（生之花、死之羽、时之沙、空之杯、理之冠）
- 每个部位的独立故事

**输出示例：**
```json
{
  "set_id": 15001,
  "name": "角斗士的终幕礼",
  "pieces": [
    {
      "equip_type": "生之花",
      "name": "角斗士的留恋",
      "story": "..."
    }
  ],
  "has_full_story": true
}
```

### 3. 书籍提取器 (`book_extractor.py`)

提取游戏中的纯书籍内容（不包括武器/圣遗物故事）。

**提取内容：**
- 书籍、信件、分页文档
- 书籍系列组织
- 内容分类

**文档类型：**
- `Book` - 书籍
- `Letter` - 信件
- `Paged` - 分页文档
- `Video` - 视频

### 4. 角色提取器 (`avatar_extractor.py`)

提取可玩角色的完整信息。

**提取内容：**
- 基础信息（名称、元素、武器类型、星级）
- 个人资料（生日、星座、所属）
- 角色故事（按解锁条件排序）
- 角色语音

**输出示例：**
```json
{
  "id": 10000002,
  "name": "神里绫华",
  "element": "冰",
  "weapon_type": "单手剑",
  "quality": 5,
  "profile": {
    "birthday": "9月28日",
    "constellation": "簪缨座",
    "affiliation": "社奉行"
  },
  "stories": [...],
  "voices": [...]
}
```

### 5. 任务对话提取器 (`quest_dialogue_extractor.py`)

从 BinOutput 提取完整的任务对话树。

**数据源：**
- `BinOutput/Quest/{id}.json` - 主任务数据
- `BinOutput/Talk/Quest/{talkId}.json` - 对话详细数据

**任务类型：**
| 代码 | 类型 | 说明 |
|------|------|------|
| AQ | 魔神任务 | Archon Quest |
| LQ | 传说任务 | Legend Quest |
| WQ | 世界任务 | World Quest |
| EQ | 活动任务 | Event Quest |
| IQ | 委托任务 | Commission Quest |

**输出结构：**
```
output/quests/
├── 魔神任务/
│   └── {chapter_id}-{region}-{chapter_title}/
│       └── {quest_id}-{quest_title}.json
├── 传说任务/
├── 世界任务/
├── 活动任务/
├── 委托任务/
└── extraction_stats.json
```

**对话树结构：**
```json
{
  "id": 306,
  "title": "昔日的风",
  "type": "AQ",
  "type_name": "魔神任务",
  "talks": [
    {
      "talk_id": 30610,
      "dialogues": [
        {
          "id": 3061001,
          "role": "安柏",
          "text": "呼…真累人。",
          "next": [...]
        }
      ]
    }
  ]
}
```

## 🛠️ 核心模块

### utils.py

提供公共功能：

- `TextMapParser` - 文本哈希到文本的映射解析
- `StoryContentExtractor` - 故事内容提取（从 Readable 目录）
- `load_json()` / `save_json()` - JSON 读写
- `get_data_path()` - 数据路径解析
- `setup_logger()` - 日志配置

### 多语言支持

所有提取器支持多语言，通过 `language` 参数指定：

```python
# 中文（默认）
extractor = WeaponExtractor(language='CHS')

# 英文
extractor = WeaponExtractor(language='EN')

# 日文
extractor = WeaponExtractor(language='JP')
```

## 📊 输出示例

运行 `extract_all.py` 后的输出：

```
================================================================================
原神游戏数据提取工具
================================================================================

1. 提取武器数据...
✓ 武器提取完成:
  - 总数: 150
  - 有故事: 85

2. 提取圣遗物数据...
✓ 圣遗物提取完成:
  - 总套装数: 45
  - 有完整故事的套装: 40

3. 提取书籍数据...
✓ 书籍提取完成:
  - 总数: 500
  - 有内容: 480
  - 系列数: 50

4. 提取角色数据...
✓ 角色提取完成:
  - 总数: 80
  - 有故事: 78
  - 有语音: 78

================================================================================
✓ 所有提取任务完成！
================================================================================
```

## 📁 输出文件说明

| 文件 | 说明 |
|------|------|
| `weapons.json` | 所有武器数据 |
| `reliquary_sets.json` | 圣遗物套装数据 |
| `books.json` | 所有书籍数据 |
| `book_series.json` | 书籍系列组织 |
| `avatars.json` | 所有角色数据 |
| `quests/` | 任务对话（按类型/章节组织） |
| `extraction_summary.json` | 提取汇总统计 |

## 🔧 扩展开发

### 添加新提取器

1. 创建新的提取器文件（如 `xxx_extractor.py`）
2. 继承或使用 `utils.py` 中的工具类
3. 实现 `extract_all()` 方法和 `save_to_file()` 方法
4. 在 `extract_all.py` 中集成

### 数据结构参考

游戏数据主要来源：
- `ExcelBinOutput/` - 配置表（JSON格式）
- `BinOutput/` - 二进制配置（已解析为JSON）
- `TextMap/` - 多语言文本映射
- `Readable/` - 可读文本内容

## 📝 许可证

本项目仅用于学习和研究目的。游戏数据版权归 miHoYo/HoYoverse 所有。

## 🙏 致谢

- [AnimeGameData](https://github.com/Dimbreath/AnimeGameData) - 游戏数据来源
- [Genshin Impact](https://genshin.hoyoverse.com/) - 原神
