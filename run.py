#!/usr/bin/env python
"""
便捷启动脚本
直接运行此文件即可启动提取工具
"""

import sys
from src.cli.main import main

if __name__ == '__main__':
    sys.exit(main())
