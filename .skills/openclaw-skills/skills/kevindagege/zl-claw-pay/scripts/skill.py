#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZLPay Skill 命令行入口（包装脚本）

此脚本负责设置正确的 Python 路径，然后调用 zlpay_skill 包。
"""

import sys
import os
from pathlib import Path

# 添加脚本目录到 Python 路径
script_dir = Path(__file__).parent
package_root = script_dir
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

# 导入并运行主模块
from zlpay_skill.skill import main

if __name__ == "__main__":
    main()
