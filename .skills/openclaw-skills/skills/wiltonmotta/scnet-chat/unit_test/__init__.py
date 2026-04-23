#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet Chat Skill 单元测试套件

测试模式：
1. MOCK_MODE (默认): 使用模拟数据，不连接真实API
2. REAL_MODE: 连接真实SCNet平台，会产生实际费用

使用方法：
    # Mock模式（默认，安全）
    python3 -m pytest unit_test/ -v
    
    # 真实模式（需要配置，会产生费用）
    export SCNET_TEST_MODE=real
    python3 -m pytest unit_test/ -v

注意事项：
    - 真实模式会实际创建/删除资源，产生费用
    - 真实模式需要有效的 ~/.scnet-chat.env 配置
    - 所有测试用例必须确保资源清理
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试模式
TEST_MODE = os.environ.get('SCNET_TEST_MODE', 'mock').lower()
MOCK_MODE = TEST_MODE == 'mock'
REAL_MODE = TEST_MODE == 'real'

if REAL_MODE:
    print("⚠️  WARNING: 真实测试模式已启用！")
    print("   这将连接真实的 SCNet 平台并可能产生费用。")
    print("   5秒后继续...")
    import time
    time.sleep(5)
