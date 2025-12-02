"""
常量定义模块
集中管理各类映射和常量
"""


class BodyTypes:
    """角色身体类型"""
    
    BODY_BOY = 'BODY_BOY'
    BODY_GIRL = 'BODY_GIRL'
    BODY_MALE = 'BODY_MALE'
    BODY_LADY = 'BODY_LADY'
    BODY_LOLI = 'BODY_LOLI'
    
    # 身体类型到中文名的映射
    NAMES = {
        'BODY_BOY': '少年',
        'BODY_GIRL': '少女',
        'BODY_MALE': '成年男性',
        'BODY_LADY': '成年女性',
        'BODY_LOLI': '萝莉'
    }
    
    @classmethod
    def get_name(cls, body_type: str) -> str:
        """获取身体类型的中文名"""
        return cls.NAMES.get(body_type, '')


class WeaponTypes:
    """武器类型"""
    
    SWORD = 'WEAPON_SWORD_ONE_HAND'
    CLAYMORE = 'WEAPON_CLAYMORE'
    BOW = 'WEAPON_BOW'
    CATALYST = 'WEAPON_CATALYST'
    POLEARM = 'WEAPON_POLE'
    
    # 武器类型到中文名的映射
    NAMES = {
        'WEAPON_SWORD_ONE_HAND': '单手剑',
        'WEAPON_CLAYMORE': '双手剑',
        'WEAPON_BOW': '弓',
        'WEAPON_CATALYST': '法器',
        'WEAPON_POLE': '长柄武器'
    }
    
    @classmethod
    def get_name(cls, weapon_type: str) -> str:
        """获取武器类型的中文名"""
        return cls.NAMES.get(weapon_type, '')


class EquipTypes:
    """圣遗物部位类型"""
    
    FLOWER = 'EQUIP_BRACER'
    FEATHER = 'EQUIP_NECKLACE'
    SANDS = 'EQUIP_SHOES'
    GOBLET = 'EQUIP_RING'
    CIRCLET = 'EQUIP_DRESS'
    
    # 部位类型到中文名的映射
    NAMES = {
        'EQUIP_BRACER': '生之花',
        'EQUIP_NECKLACE': '死之羽',
        'EQUIP_SHOES': '时之沙',
        'EQUIP_RING': '空之杯',
        'EQUIP_DRESS': '理之冠'
    }
    
    @classmethod
    def get_name(cls, equip_type: str) -> str:
        """获取圣遗物部位的中文名"""
        return cls.NAMES.get(equip_type, equip_type)


class DocumentTypes:
    """文档类型"""
    
    BOOK = 'Book'
    LETTER = 'Letter'
    PAGED = 'Paged'
    VIDEO = 'Video'
    
    # 文档类型到中文名的映射
    NAMES = {
        'Book': '书籍',
        'Letter': '信件',
        'Paged': '分页文档',
        'Video': '视频'
    }
    
    @classmethod
    def get_name(cls, doc_type: str) -> str:
        """获取文档类型的中文名"""
        return cls.NAMES.get(doc_type, doc_type)


class QuestTypes:
    """任务类型"""
    
    ARCHON = 'AQ'      # 魔神任务
    LEGEND = 'LQ'      # 传说任务
    WORLD = 'WQ'       # 世界任务
    EVENT = 'EQ'       # 活动任务
    COMMISSION = 'IQ'  # 委托任务
    
    # 任务类型到中文名的映射
    NAMES = {
        'AQ': '魔神任务',
        'LQ': '传说任务',
        'WQ': '世界任务',
        'EQ': '活动任务',
        'IQ': '委托任务',
    }
    
    @classmethod
    def get_name(cls, quest_type: str) -> str:
        """获取任务类型的中文名"""
        return cls.NAMES.get(quest_type, quest_type)


class TalkRoleTypes:
    """对话角色类型"""
    
    PLAYER = 'TALK_ROLE_PLAYER'
    NPC = 'TALK_ROLE_NPC'
    GADGET = 'TALK_ROLE_GADGET'


class IDOffsets:
    """ID 偏移量常量"""
    
    # 武器 ID 到 Document ID 的映射偏移量
    WEAPON_STORY = 180000
    
    # 皮肤文档 ID 范围
    COSTUME_MIN = 340000
    COSTUME_MAX = 350000
    
    # 风之翼文档 ID 范围
    WINDGLIDER_MIN = 140000
    WINDGLIDER_MAX = 150000
