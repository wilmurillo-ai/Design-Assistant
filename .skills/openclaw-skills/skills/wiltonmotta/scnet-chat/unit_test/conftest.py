#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest 配置文件
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试模式配置
TEST_MODE = os.environ.get('SCNET_TEST_MODE', 'mock').lower()
MOCK_MODE = TEST_MODE == 'mock'
REAL_MODE = TEST_MODE == 'real'
