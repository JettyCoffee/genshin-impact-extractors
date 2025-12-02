"""
配置模块
提供路径配置和日志设置等基础功能
"""

import logging
from pathlib import Path


def setup_logger(name: str) -> logging.Logger:
    """
    设置日志记录器
    
    参数:
        name: 日志记录器名称
    
    返回:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_data_path(relative_path: str = '') -> Path:
    """
    获取数据文件的绝对路径
    
    参数:
        relative_path: 相对于 AnimeGameData 的路径
    
    返回:
        绝对路径
    """
    # 获取项目根目录（genshin-extractors 的父目录）
    current_file = Path(__file__).resolve()
    # src/core/config.py -> genshin-extractors -> paimon
    project_root = current_file.parent.parent.parent.parent
    data_dir = project_root / 'AnimeGameData'
    
    if relative_path:
        return data_dir / relative_path
    return data_dir


def get_output_path(relative_path: str = '') -> Path:
    """
    获取输出文件的绝对路径
    
    参数:
        relative_path: 相对于 output 目录的路径
    
    返回:
        绝对路径
    """
    # 获取 genshin-extractors 目录
    current_file = Path(__file__).resolve()
    extractors_dir = current_file.parent.parent.parent
    output_dir = extractors_dir / 'output'
    
    if relative_path:
        return output_dir / relative_path
    return output_dir
