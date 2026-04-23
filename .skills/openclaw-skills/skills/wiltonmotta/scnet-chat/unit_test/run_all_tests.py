#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet Chat Skill 测试运行脚本

使用方法:
    # Mock 模式（默认，安全）
    python3 unit_test/run_all_tests.py
    
    # 真实模式（会产生费用！）
    export SCNET_TEST_MODE=real
    python3 unit_test/run_all_tests.py

测试套件:
    1. test_auth.py      - 认证测试
    2. test_job.py       - 作业管理
    3. test_file.py      - 文件管理
    4. test_notebook.py  - Notebook管理（付费）
    5. test_container.py - 容器管理（付费）
    6. test_advanced.py  - 高级功能
"""

import sys
import os
import subprocess
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 获取测试模式
TEST_MODE = os.environ.get('SCNET_TEST_MODE', 'mock').lower()
MOCK_MODE = TEST_MODE == 'mock'


def print_header():
    """打印测试头"""
    print("="*70)
    print("SCNet Chat Skill 单元测试")
    print("="*70)
    print(f"测试模式: {'MOCK (模拟)' if MOCK_MODE else 'REAL (真实API)'}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print()


def print_summary(results):
    """打印测试摘要"""
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    
    print()
    print("="*70)
    print("测试摘要")
    print("="*70)
    print(f"总用例数: {total}")
    print(f"通过:     {passed} ✅")
    print(f"失败:     {failed} ❌")
    print(f"跳过:     {skipped} ⏸️")
    print(f"通过率:   {passed/total*100:.1f}%" if total > 0 else "0%")
    print("="*70)
    
    # 失败详情
    if failed > 0:
        print("\n失败的测试:")
        for r in results:
            if r['status'] == 'failed':
                print(f"  - {r['name']}: {r.get('message', '')}")


def save_report(results):
    """保存测试报告"""
    report_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(
        report_dir,
        f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    report = {
        "test_mode": "mock" if MOCK_MODE else "real",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 测试报告已保存: {report_file}")


def run_test_suite(test_file):
    """运行单个测试套件"""
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    
    print(f"\n运行: {test_file}...")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', test_path, '-v', '--tb=short'],
        capture_output=True,
        text=True
    )
    
    # 解析结果
    output = result.stdout + result.stderr
    
    # 简单解析通过/失败
    passed = result.returncode == 0
    
    # 提取测试数量
    import re
    match = re.search(r'(\d+) passed', output)
    passed_count = int(match.group(1)) if match else 0
    
    match = re.search(r'(\d+) failed', output)
    failed_count = int(match.group(1)) if match else 0
    
    match = re.search(r'(\d+) skipped', output)
    skipped_count = int(match.group(1)) if match else 0
    
    status = "passed" if passed else "failed"
    
    print(f"  结果: {status.upper()}")
    print(f"  通过: {passed_count}, 失败: {failed_count}, 跳过: {skipped_count}")
    
    return {
        "name": test_file,
        "status": status,
        "passed": passed_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "output": output[-500:] if len(output) > 500 else output  # 保存最后500字符
    }


def main():
    """主函数"""
    print_header()
    
    if not MOCK_MODE:
        print("⚠️  WARNING: 真实测试模式已启用！")
        print("   这将连接真实的 SCNet 平台并产生费用。")
        print("   测试将创建实际的 Notebook 和容器资源。")
        print()
        response = input("确认继续? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("\n测试已取消")
            return 1
        print()
    
    # 测试套件列表
    test_suites = [
        ('test_auth.py', '认证测试'),
        ('test_job.py', '作业管理'),
        ('test_file.py', '文件管理'),
        ('test_notebook.py', 'Notebook管理 ⚠️'),
        ('test_container.py', '容器管理 ⚠️'),
        ('test_advanced.py', '高级功能'),
    ]
    
    results = []
    
    for test_file, desc in test_suites:
        result = run_test_suite(test_file)
        result['description'] = desc
        results.append(result)
    
    # 打印摘要
    print_summary(results)
    
    # 保存报告
    save_report(results)
    
    # 返回退出码
    failed = sum(1 for r in results if r['status'] == 'failed')
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
