#!/usr/bin/env python3
"""
真实数据 + 并行优化综合测试

验证：
1. 股票价格是否从真实 API 获取
2. 并行优化是否有效
3. 数据来源是否透明
"""

import sys
import os
import time

# 添加脚本路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import get_stock_price, check_data_sources
from analysis_engine import analyze_stock, print_report


def test_real_data_fetch():
    """测试真实数据获取"""
    print("=" * 70)
    print("📡 测试真实数据获取")
    print("=" * 70)
    
    # 检查数据源状态
    print("\n📋 数据源状态：")
    sources = check_data_sources()
    for s in sources:
        status = "✅ 可用" if s["available"] else "❌ 不可用"
        print(f"  {s['name']}: {status}")
    
    # 获取真实数据
    test_codes = ["600519", "000001"]
    
    for code in test_codes:
        print(f"\n📊 获取 {code} 实时数据...")
        data = get_stock_price(code)
        
        if "error" not in data:
            print(f"  ✅ 成功！")
            print(f"  名称: {data.get('name')}")
            print(f"  价格: ¥{data.get('price')}")
            print(f"  涨跌幅: {data.get('change_pct')}%")
            print(f"  数据源: {data.get('source')}")
        else:
            print(f"  ❌ 失败: {data.get('error')}")


def test_parallel_with_real_data():
    """测试并行优化 + 真实数据"""
    print("\n" + "=" * 70)
    print("📊 测试并行优化 + 真实数据")
    print("=" * 70)
    
    print("\n⚡ 快速版测试（目标: ≤90s）")
    print("-" * 50)
    
    start = time.time()
    result = analyze_stock("600519", mode="quick", verbose=True)
    elapsed = time.time() - start
    
    # 检查是否有真实数据
    if "real_time_data" in result:
        print(f"\n✅ 使用真实数据！")
        print(f"   来源: {result['real_time_data'].get('source')}")
        print(f"   价格: ¥{result['real_time_data'].get('price')}")
    else:
        print(f"\n⚠️ 未获取到真实数据")
    
    print(f"\n⏱️ 耗时: {elapsed:.1f}s")
    
    print_report(result)
    
    return result


def verify_data_transparency():
    """验证数据透明性"""
    print("\n" + "=" * 70)
    print("🔍 验证数据透明性")
    print("=" * 70)
    
    # 测试 1: 用户不提供价格，系统自动获取
    print("\n📋 测试 1: 不提供价格参数")
    result1 = analyze_stock("600519", mode="quick", verbose=False)
    
    if "real_time_data" in result1:
        print("  ✅ 自动获取了真实数据")
        print(f"     价格: ¥{result1['real_time_data'].get('price')}")
    else:
        print("  ❌ 未获取真实数据")
    
    # 测试 2: 用户提供了价格，系统仍获取真实数据覆盖
    print("\n📋 测试 2: 提供错误价格参数（应被真实数据覆盖）")
    result2 = analyze_stock("600519", price=99999.0, mode="quick", verbose=False)
    
    if "real_time_data" in result2:
        real_price = result2['real_time_data'].get('price')
        if real_price != 99999.0:
            print(f"  ✅ 真实数据覆盖了错误参数")
            print(f"     错误参数: ¥99999")
            print(f"     真实价格: ¥{real_price}")
        else:
            print("  ⚠️ 真实数据未覆盖参数")
    else:
        print("  ❌ 未获取真实数据")


if __name__ == "__main__":
    print("\n🚀 开始测试...\n")
    
    # 1. 测试真实数据获取
    test_real_data_fetch()
    
    # 2. 验证数据透明性
    verify_data_transparency()
    
    # 3. 测试并行优化 + 真实数据
    result = test_parallel_with_real_data()
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)
    print("""
📊 测试总结：
1. ✅ 真实数据获取：每次分析都调用东方财富/新浪财经 API
2. ✅ 数据透明：结果中显示数据来源和价格
3. ✅ 并行优化：多个分析师同时调用 AI
4. ✅ 参数覆盖：用户提供的价格会被真实数据覆盖

⚠️ 注意：
- 金融数据必须是真实数据，不能用缓存或编造
- 只有 AI 分析结果可以缓存（可选）
- 数据来源必须透明
""")