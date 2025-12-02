"""
Quest 相关的加密字段映射
这些字段名在游戏数据中被加密，需要映射回原始名称
"""


class QuestFieldMap:
    """Quest 主任务字段映射"""
    
    ENCRYPTED_FIELDS = {
        'FJIMHCGKKPJ': 'id',
        'DNIFJDIGILK': 'luaPath',
        'LINDNOIHPNE': 'chapterId',         # 章节 ID (某些文件)
        'NKEKKINIKEB': 'chapterId',         # 章节系列 ID - 正确的章节 ID
        'ODOCBCAGDJA': 'mainQuestId',       # 主任务 ID（不是章节 ID！）
        'DCHHEHNNEOO': 'talks',
        'BMCONAJCMAK': 'subQuests',
        'AFKIEPNELHE': 'questType',         # 任务类型
        'DLPKBOPINEE': 'descTextMapHash',   # 任务描述文本 Hash
        'HMPOGBDMBOK': 'titleTextMapHash',  # 任务标题文本 Hash
    }
    
    @classmethod
    def decode(cls, data: dict) -> dict:
        """解码 Quest 数据"""
        decoded = {}
        for key, value in data.items():
            if key in cls.ENCRYPTED_FIELDS:
                decoded[cls.ENCRYPTED_FIELDS[key]] = value
            else:
                decoded[key] = value
        return decoded


class TalkFieldMap:
    """Talk 对话字段映射"""
    
    ENCRYPTED_FIELDS = {
        'FJIMHCGKKPJ': 'id',
        'FHNJHCFCADD': 'questId',
        'ELEPNLBFNOP': 'npcId',
        'OLCKDFIEGLI': 'initDialog',
        'IKCBIFLCCOH': 'dialogList',
        'AFKIEPNELHE': 'talkType',
        'PDFCHAAMEHA': 'talkId',
    }
    
    @classmethod
    def decode(cls, data: dict) -> dict:
        """解码 Talk 数据"""
        decoded = {}
        for key, value in data.items():
            if key in cls.ENCRYPTED_FIELDS:
                decoded[cls.ENCRYPTED_FIELDS[key]] = value
            else:
                decoded[key] = value
        return decoded


class SubQuestFieldMap:
    """SubQuest 子任务字段映射"""
    
    ENCRYPTED_FIELDS = {
        'FKJCGCAMNEH': 'subId',
        'JDCNDABFDFP': 'order',
        'DLPKBOPINEE': 'descTextMapHash',
    }
    
    @classmethod
    def decode(cls, data: dict) -> dict:
        """解码 SubQuest 数据"""
        decoded = {}
        for key, value in data.items():
            if key in cls.ENCRYPTED_FIELDS:
                decoded[cls.ENCRYPTED_FIELDS[key]] = value
            else:
                decoded[key] = value
        return decoded


class DialogFieldMap:
    """Dialog 对话条目字段映射"""
    
    ENCRYPTED_FIELDS = {
        'FJIMHCGKKPJ': 'id',
        'BCBFGKALICJ': 'talkRole',
        'DBIHEJMJCMK': 'talkContentTextMapHash',
        'JLLIMLALADN': 'nextDialogs',
    }
    
    @classmethod
    def decode(cls, data: dict) -> dict:
        """解码 Dialog 数据"""
        decoded = {}
        for key, value in data.items():
            if key in cls.ENCRYPTED_FIELDS:
                decoded[cls.ENCRYPTED_FIELDS[key]] = value
            else:
                decoded[key] = value
        
        # 解码 talkRole 内部字段
        if 'talkRole' in decoded and isinstance(decoded['talkRole'], dict):
            decoded['talkRole'] = TalkRoleFieldMap.decode(decoded['talkRole'])
        
        return decoded


class TalkRoleFieldMap:
    """TalkRole 角色信息字段映射"""
    
    ENCRYPTED_FIELDS = {
        'FGFJOGEKHOK': 'type',
        '_type': 'type',
        '_id': 'id',
    }
    
    @classmethod
    def decode(cls, data: dict) -> dict:
        """解码 TalkRole 数据"""
        decoded = {}
        for key, value in data.items():
            if key in cls.ENCRYPTED_FIELDS:
                decoded[cls.ENCRYPTED_FIELDS[key]] = value
            else:
                decoded[key] = value
        return decoded
