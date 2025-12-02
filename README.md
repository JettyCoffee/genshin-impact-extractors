# Genshin Extractors

原神游戏数据提取工具集，用于从 [AnimeGameData](https://github.com/Dimbreath/AnimeGameData) 提取结构化的游戏文本数据。

## 📋 功能概述

本工具集提供多个专用提取器，用于从原神游戏数据中提取：

| 提取器 | 描述 | 输出 |
|--------|------|------|
| `WeaponExtractor` | 武器信息及故事 | `weapons.json` |
| `ReliquaryExtractor` | 圣遗物套装及故事 | `reliquary_sets.json` |
| `BookExtractor` | 书籍、信件等文档 | `books.json`, `book_series.json` |
| `AvatarExtractor` | 角色信息、故事、语音 | `avatars.json` |
| `QuestDialogueExtractor` | 任务对话（按类型分类） | `quests/` 目录 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- [AnimeGameData](https://github.com/Dimbreath/AnimeGameData) 数据目录

### 安装

```bash
# 克隆项目
git clone https://github.com/JettyCoffee/genshin-impact-extractors.git
cd genshin-extractors

# 安装依赖（可选）
pip install -e .
```

### 目录结构

```
project_root/
├── AnimeGameData/           # 游戏数据（需要单独获取）
│   ├── BinOutput/
│   ├── ExcelBinOutput/
│   ├── Readable/
│   └── TextMap/
└── genshin-extractors/      # 本项目
    ├── src/                 # 源代码目录
    │   ├── core/            # 核心工具模块
    │   │   ├── config.py    # 配置和路径管理
    │   │   ├── io.py        # JSON 读写
    │   │   ├── text_parser.py    # 文本映射解析
    │   │   └── story_extractor.py # 故事内容提取
    │   ├── models/          # 数据模型和常量
    │   │   ├── constants.py # 常量定义
    │   │   └── field_maps.py # 加密字段映射
    │   ├── extractors/      # 提取器模块
    │   │   ├── base.py      # 提取器基类
    │   │   ├── avatar/      # 角色提取器
    │   │   ├── book/        # 书籍提取器
    │   │   ├── weapon/      # 武器提取器
    │   │   ├── reliquary/   # 圣遗物提取器
    │   │   └── quest/       # 任务对话提取器
    │   └── cli/             # 命令行接口
    │       └── main.py      # CLI 入口
    ├── output/              # 提取结果输出目录
    ├── pyproject.toml       # 项目配置
    └── README.md
```

### 运行方式

#### 方式一：命令行工具（推荐）

```bash
# 提取全部数据
genshin-extract --type all

# 仅提取武器数据
genshin-extract --type weapon

# 仅提取角色数据
genshin-extract --type avatar

# 指定语言和输出目录
genshin-extract --type all --language EN --output ./my_output
```

#### 方式二：Python 代码调用

```python
from src import AvatarExtractor, WeaponExtractor

# 创建提取器
extractor = AvatarExtractor(language='CHS')

# 提取所有数据
avatars = extractor.extract_all()

# 保存到文件
extractor.save_to_file('avatars.json', avatars)
```

#### 方式三：直接运行旧脚本

```bash
# 仍然保留了兼容的独立脚本
python extract_all.py
python weapon_extractor.py
python avatar_extractor.py
```

## 📦 项目架构

### 核心模块 (src/core/)

| 模块 | 功能 |
|------|------|
| `config.py` | 路径配置、日志设置 |
| `io.py` | JSON 文件读写 |
| `text_parser.py` | 文本哈希到文本的映射解析 |
| `story_extractor.py` | 故事内容提取（从 Readable 目录） |

### 数据模型 (src/models/)

| 模块 | 功能 |
|------|------|
| `constants.py` | 身体类型、武器类型、任务类型等常量映射 |
| `field_maps.py` | 游戏数据加密字段名到原始字段名的映射 |

### 提取器模块 (src/extractors/)

每个提取器都被拆分为多个子模块，便于维护：

```
extractors/
├── base.py              # 提取器基类
├── avatar/              # 角色提取器
│   ├── data_loader.py   # 数据加载
│   ├── info_extractor.py    # 基础信息提取
│   ├── story_extractor.py   # 故事提取
│   └── voice_extractor.py   # 语音提取
├── book/                # 书籍提取器
│   ├── data_loader.py
│   ├── info_extractor.py
│   ├── series_extractor.py  # 系列组织
│   └── type_checker.py      # 类型判断
├── weapon/              # 武器提取器
│   ├── data_loader.py
│   └── info_extractor.py
├── reliquary/           # 圣遗物提取器
│   ├── data_loader.py
│   ├── info_extractor.py
│   └── set_extractor.py     # 套装组织
└── quest/               # 任务对话提取器
    ├── data_loader.py
    ├── dialog_builder.py    # 对话树构建
    ├── quest_processor.py   # 任务处理
    └── role_resolver.py     # 角色名解析
```

## 📦 提取器详解

### 1. 武器提取器 (WeaponExtractor)

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

### 2. 圣遗物提取器 (ReliquaryExtractor)

按套装提取圣遗物信息，每个套装包含 5 个部位的故事。

**提取内容：**
- 套装名称、套装效果
- 五个部位（生之花、死之羽、时之沙、空之杯、理之冠）
- 每个部位的独立故事

**输出示例：**
```json
{
  "set_id": 15001,
  "set_name": "角斗士的终幕礼",
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

### 3. 书籍提取器 (BookExtractor)

提取游戏中的纯书籍内容（不包括武器/圣遗物故事）。

**提取内容：**
- 书籍、信件、分页文档
- 书籍系列组织
- 皮肤、风之翼文档

**文档类型：**
| 类型 | 说明 |
|------|------|
| `Book` | 书籍 |
| `Letter` | 信件 |
| `Paged` | 分页文档 |
| `Video` | 视频 |

### 4. 角色提取器 (AvatarExtractor)

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
  "weapon_type": "单手剑",
  "profile": {
    "birthday": "9/28",
    "constellation": "簪缨座"
  },
  "stories": [...],
  "voice_overs": [...]
}
```

### 5. 任务对话提取器 (QuestDialogueExtractor)

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
└── 委托任务/
```

## 🌍 多语言支持

所有提取器支持多语言，通过 `language` 参数指定：

```python
from src import WeaponExtractor

# 中文（默认）
extractor = WeaponExtractor(language='CHS')

# 英文
extractor = WeaponExtractor(language='EN')

# 日文
extractor = WeaponExtractor(language='JP')
```

支持的语言代码：
- `CHS` - 简体中文
- `CHT` - 繁体中文
- `EN` - 英语
- `JP` - 日语
- `KR` - 韩语
- 以及 DE, FR, ES, PT, RU, ID, TH, VI, TR, IT

## 📁 输出文件说明

| 文件 | 说明 |
|------|------|
| `weapons.json` | 所有武器数据 |
| `reliquary_sets.json` | 圣遗物套装数据 |
| `books.json` | 所有书籍数据 |
| `book_series.json` | 书籍系列组织 |
| `costumes.json` | 皮肤文档 |
| `windgliders.json` | 风之翼文档 |
| `avatars.json` | 所有角色数据 |
| `quests/` | 任务对话（按类型/章节组织） |
| `extraction_summary.json` | 提取汇总统计 |

## 🔧 扩展开发

### 添加新提取器

1. 在 `src/extractors/` 下创建新目录
2. 创建以下文件：
   - `__init__.py` - 导出主类
   - `data_loader.py` - 数据加载逻辑
   - `info_extractor.py` - 信息提取逻辑
   - `extractor.py` - 主提取器类（继承 `BaseExtractor`）
3. 在 `src/extractors/__init__.py` 中导出新提取器
4. 在 `src/cli/main.py` 中添加命令行支持

### 数据结构参考

游戏数据主要来源：
- `ExcelBinOutput/` - 配置表（JSON 格式）
- `BinOutput/` - 二进制配置（已解析为 JSON）
- `TextMap/` - 多语言文本映射
- `Readable/` - 可读文本内容

## 📝 许可证

本项目仅用于学习和研究目的。游戏数据版权归 miHoYo/HoYoverse 所有。

## 🙏 致谢

- [AnimeGameData](https://github.com/Dimbreath/AnimeGameData) - 游戏数据来源
- [Genshin Impact](https://genshin.hoyoverse.com/) - 原神
