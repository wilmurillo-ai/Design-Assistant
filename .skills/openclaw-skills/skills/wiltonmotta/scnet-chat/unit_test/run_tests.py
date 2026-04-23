#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本

使用方法:
    # Mock 模式（默认，安全）
    python3 unit_test/run_tests.py
    
    # 真实模式（会产生费用！）
    export SCNET_TEST_MODE=real
    python3 unit_test/run_tests.py

测试套件执行顺序:
    1. test_01_auth.py    - 认证测试
    2. test_02_job.py     - 作业管理
    3. test_03_file.py    - 文件管理
    4. test_04_notebook.py - Notebook管理（付费）
    5. test_05_container.py - 容器管理（付费）
    6. test_06_advanced.py - 高级功能
"""

import sys
import os
import unittest
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unit_test import MOCK_MODE, REAL_MODE


def run_tests(test_pattern=None, verbose=True):
    """
    运行测试
    
    Args:
        test_pattern: 测试文件名模式，如 "test_01_*.py"
        verbose: 是否详细输出
    """
    loader = unittest.TestLoader()
    
    # 获取测试目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 选择测试模式
    if test_pattern:
        pattern = test_pattern
    else:
        pattern = "test_*.py"
    
    print("="*70)
    print("SCNet Chat Skill 单元测试")
    print("="*70)
    print(f"测试模式: {'MOCK (模拟)' if MOCK_MODE else 'REAL (真实API)'}")
    print(f"测试目录: {test_dir}")
    print(f"测试模式: {pattern}")
    print("="*70)
    
    if REAL_MODE:
        print("\n⚠️  WARNING: 真实测试模式已启用！")
        print("   这将连接真实的 SCNet 平台并产生费用。")
        print("   测试将创建实际的 Notebook 和容器资源。")
        print()
        response = input("   确认继续? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("\n测试已取消")
            return 1
    
    print()
    
    # 发现测试
    suite = loader.discover(test_dir, pattern=pattern)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # 返回退出码
    return 0 if result.wasSuccessful() else 1


def main():
    parser = argparse.ArgumentParser(description='SCNet Chat Skill 测试运行器')
    parser.add_argument(
        '--pattern', '-p',
        help='测试文件名模式，如 "test_01_*.py"',
        default=None
    )
    parser.add_argument(
        '--mode', '-m',
        choices=['mock', 'real'],
        help='测试模式（默认: mock）',
        default=None
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='静默模式'
    )
    
    args = parser.parse_args()
    
    # 设置模式
    if args.mode:
        os.environ['SCNET_TEST_MODE'] = args.mode
        # 重新导入以更新模式
        import importlib
        import unit_test
        importlib.reload(unit_test)
    
    # 运行测试
    exit_code = run_tests(args.pattern, not args.quiet)
    
    # 打印报告位置提示
    print("\n" + "="*70)
    print("测试报告已保存到 unit_test/reports/ 目录")
    print("="*70)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
