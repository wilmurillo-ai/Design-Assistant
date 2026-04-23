#!/usr/bin/env python3
"""
快速测试：只测试数据获取逻辑，不调用 AI
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🧪 快速测试：数据获取逻辑")
print("=" * 70)

# 测试 1: 数据获取模块
print("\n📋 测试 1: 检查数据获取模块")
print("-" * 50)

try:
    from data_fetcher import get_stock_price, check_data_sources
    
    sources = check_data_sources()
    print("数据源状态：")
    for s in sources:
        status = "✅" if s["available"] else "❌"
        print(f"  {s['name']}: {status}")
    
    print("\n尝试获取 600519 数据...")
    data = get_stock_price("600519")
    
    if "error" in data:
        print(f"❌ 获取失败: {data['error']}")
    else:
        print(f"✅ 获取成功！")
        print(f"   名称: {data.get('name')}")
        print(f"   价格: ¥{data.get('price')}")
        print(f"   来源: {data.get('source')}")

except Exception as e:
    print(f"❌ 异常: {e}")


# 测试 2: analyze_stock 数据逻辑（不调用 AI）
print("\n" + "=" * 70)
print("📋 测试 2: analyze_stock 数据逻辑")
print("-" * 50)

# 模拟 analyze_stock 的数据逻辑
def test_data_logic(code, name=None, price=None, allow_mock=False):
    """测试数据获取逻辑（不调用 AI）"""
    real_time_data = {}
    
    try:
        from data_fetcher import get_stock_price
        real_time_data = get_stock_price(code)
        
        if "error" not in real_time_data:
            name = real_time_data.get("name", name or code)
            price = real_time_data.get("price", price or 0)
            source = real_time_data.get("source", "API")
            print(f"✅ 从 API 获取: {name} ¥{price}")
            return True, source
    except Exception as e:
        print(f"⚠️ API 失败: {e}")
        real_time_data = {}
    
    # 降级逻辑
    if price is not None and name is not None:
        print(f"ℹ️ 使用用户参数: {name} ¥{price}")
        return True, "用户参数"
    
    if allow_mock:
        print(f"⚠️ 使用模拟数据（仅测试）")
        return True, "模拟数据"
    
    print(f"❌ 报错：无法获取数据且无用户参数")
    return False, "错误"


# 测试场景
print("\n场景 A: 用户提供参数")
ok, source = test_data_logic("600519", name="贵州茅台", price=1550)
print(f"   结果: {'✅' if ok else '❌'}, 来源: {source}")

print("\n场景 B: 无参数 + 允许模拟")
ok, source = test_data_logic("600519", allow_mock=True)
print(f"   结果: {'✅' if ok else '❌'}, 来源: {source}")

print("\n场景 C: 无参数 + 不允许模拟")
ok, source = test_data_logic("600519", allow_mock=False)
print(f"   结果: {'✅' if ok else '❌'}, 来源: {source}")


print("\n" + "=" * 70)
print("✅ 测试完成！")
print("=" * 70)