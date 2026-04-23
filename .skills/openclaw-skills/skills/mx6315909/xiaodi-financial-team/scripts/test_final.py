#!/usr/bin/env python3
"""
并行优化测试（支持离线模式）

测试场景：
1. 用户提供参数 → 使用用户数据
2. API 可用 → 使用真实数据
3. 都不可用 → 降级到模拟数据（明确标注）
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis_engine import analyze_stock, print_report


def test_user_provided_data():
    """测试用户提供数据的情况"""
    print("=" * 70)
    print("📋 测试 1: 用户提供数据")
    print("=" * 70)
    
    start = time.time()
    result = analyze_stock(
        code="600519",
        name="贵州茅台",
        price=1550.0,
        mode="quick",
        verbose=True
    )
    elapsed = time.time() - start
    
    print(f"\n⏱️ 耗时: {elapsed:.1f}s")
    print_report(result)
    
    # 验证数据来源
    if "real_time_data" in result:
        print(f"\n📊 数据来源: {result['real_time_data'].get('source', '未知')}")
    else:
        print(f"\n📊 使用用户参数数据")
    
    return result, elapsed


def test_quick_mode():
    """测试快速版"""
    print("\n" + "=" * 70)
    print("📋 测试 2: 快速版（用户提供数据）")
    print("=" * 70)
    
    start = time.time()
    result = analyze_stock(
        code="000001",
        name="平安银行",
        price=10.5,
        mode="quick",
        verbose=True
    )
    elapsed = time.time() - start
    
    print(f"\n⏱️ 耗时: {elapsed:.1f}s")
    print(f"🎯 目标: ≤90s")
    print(f"{'✅ 达标' if elapsed <= 90 else '❌ 未达标'}")
    
    return result, elapsed


def test_standard_mode():
    """测试标准版"""
    print("\n" + "=" * 70)
    print("📋 测试 3: 标准版（用户提供数据）")
    print("=" * 70)
    
    start = time.time()
    result = analyze_stock(
        code="601318",
        name="中国平安",
        price=45.0,
        mode="standard",
        verbose=True
    )
    elapsed = time.time() - start
    
    print(f"\n⏱️ 耗时: {elapsed:.1f}s")
    print(f"🎯 目标: ≤180s")
    print(f"{'✅ 达标' if elapsed <= 180 else '❌ 未达标'}")
    
    return result, elapsed


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🧪 金融分析师团队 - 并行优化测试")
    print("=" * 70)
    print("""
⚠️ 注意：
- 当前环境可能无法访问东方财富 API
- 测试使用用户提供的数据参数
- 当 API 可用时，会自动获取真实数据覆盖参数
""")
    
    results = {}
    
    # 测试 1: 用户提供数据
    try:
        r1, t1 = test_user_provided_data()
        results["用户提供数据"] = {"time": t1, "ok": True}
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results["用户提供数据"] = {"time": 0, "ok": False, "error": str(e)}
    
    # 测试 2: 快速版
    try:
        r2, t2 = test_quick_mode()
        results["快速版"] = {"time": t2, "ok": t2 <= 90}
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results["快速版"] = {"time": 0, "ok": False, "error": str(e)}
    
    # 测试 3: 标准版
    try:
        r3, t3 = test_standard_mode()
        results["标准版"] = {"time": t3, "ok": t3 <= 180}
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results["标准版"] = {"time": 0, "ok": False, "error": str(e)}
    
    # 汇总
    print("\n" + "=" * 70)
    print("📊 测试汇总")
    print("=" * 70)
    
    print("\n| 测试 | 耗时 | 目标 | 结果 |")
    print("|------|------|------|------|")
    for name, r in results.items():
        if r.get("ok") is not None:
            status = "✅" if r["ok"] else "❌"
            print(f"| {name} | {r['time']:.1f}s | - | {status} |")
        else:
            print(f"| {name} | - | - | ❌ {r.get('error', '失败')} |")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    run_all_tests()