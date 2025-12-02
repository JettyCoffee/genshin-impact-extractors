"""
IO 模块
提供 JSON 文件读写功能
"""

import json
import os
from typing import Any


def load_json(file_path: str) -> Any:
    """
    加载 JSON 文件
    
    参数:
        file_path: JSON 文件路径
    
    返回:
        解析后的数据
    
    异常:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON 解析失败
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, file_path: str, indent: int = 2) -> None:
    """
    保存数据为 JSON 文件
    
    参数:
        data: 要保存的数据
        file_path: 保存路径
        indent: 缩进空格数
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
