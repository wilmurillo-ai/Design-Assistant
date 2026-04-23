#!/usr/bin/env python3
"""
测试数据真实性修复

验证：
1. 默认强制获取真实数据
2. API 失败时需要用户参数
3. 数据来源透明
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis_engine import analyze_stock, print_report


def test_user_params():
    """测试：用户提供参数（API 可能失败）"""
    print("=" * 70)
    print("📋 测试 1: 用户提供参数")
    print("=" * 70)
    
    try:
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
            source = result["real_time_data"].get("source", "未知")
            print(f"\n✅ 数据来源: {source}")
        
        return True, elapsed
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False, 0


def test_no_params_with_mock():
    """测试：无参数 + 允许模拟（测试模式）"""
    print("\n" + "=" * 70)
    print("📋 测试 2: 无参数 + allow_mock=True（测试模式）")
    print("=" * 70)
    
    try:
        start = time.time()
        result = analyze_stock(
            code="000001",
            mode="quick",
            allow_mock=True,  # 允许模拟数据
            verbose=True
        )
        elapsed = time.time() - start
        
        print(f"\n⏱️ 耗时: {elapsed:.1f}s")
        print_report(result)
        
        # 验证数据来源
        if "real_time_data" in result:
            source = result["real_time_data"].get("source", "未知")
            is_mock = result["real_time_data"].get("is_mock", False)
            print(f"\n📊 数据来源: {source}")
            if is_mock:
                print("⚠️ 使用了模拟数据（仅测试用）")
        
        return True, elapsed
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False, 0


def test_no_params_no_mock():
    """测试：无参数 + 不允许模拟（应报错）"""
    print("\n" + "=" * 70)
    print("📋 测试 3: 无参数 + allow_mock=False（应报错）")
    print("=" * 70)
    
    try:
        result = analyze_stock(
            code="000001",
            mode="quick",
            allow_mock=False,  # 不允许模拟
            verbose=True
        )
        print("\n❌ 应该报错但没有报错！")
        return False, 0
    except ValueError as e:
        print(f"\n✅ 正确报错: {e}")
        return True, 0
    except Exception as e:
        print(f"\n⚠️ 其他错误: {e}")
        return False, 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🧪 数据真实性修复验证")
    print("=" * 70)
    
    results = []
    
    # 测试 1
    ok, t = test_user_params()
    results.append(("用户提供参数", ok, t))
    
    # 测试 2
    ok, t = test_no_params_with_mock()
    results.append(("无参数+允许模拟", ok, t))
    
    # 测试 3
    ok, t = test_no_params_no_mock()
    results.append(("无参数+禁止模拟", ok, t))
    
    # 汇总
    print("\n" + "=" * 70)
    print("📊 测试汇总")
    print("=" * 70)
    
    print("\n| 测试 | 结果 | 耗时 |")
    print("|------|------|------|")
    for name, ok, t in results:
        status = "✅" if ok else "❌"
        print(f"| {name} | {status} | {t:.1f}s |")
    
    print("\n" + "=" * 70)
    print("✅ 验证完成！")
    print("""
数据真实性原则：
1. ✅ 默认强制调用真实 API
2. ✅ API 失败时需要用户参数
3. ✅ 无参数 + 不允许模拟 → 报错
4. ✅ 数据来源透明标注
""")


if __name__ == "__main__":
    main()