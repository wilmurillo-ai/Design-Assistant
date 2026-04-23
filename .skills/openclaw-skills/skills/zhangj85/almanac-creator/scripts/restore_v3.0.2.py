#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复黄历脚本到 V3.0.2 版本
"""

import shutil
import os

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'
backup_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py.bak20260418'
v302_backup = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py.v3.0.2.backup'

# 1. 备份当前版本
if os.path.exists(script_path):
    shutil.copy(script_path, v302_backup)
    print(f"Backed up current version to {v302_backup}")

# 2. 恢复 4 月 18 日备份（V3.0.3，最接近 V3.0.2）
if os.path.exists(backup_path):
    shutil.copy(backup_path, script_path)
    print(f"Restored from {backup_path}")
    print("Script restored to V3.0.3 (closest to V3.0.2)")
else:
    print("ERROR: Backup file not found!")

print("\nOK! Script restored.")
