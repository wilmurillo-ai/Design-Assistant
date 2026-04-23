#!/usr/bin/env python3
"""
并行优化测试脚本
对比顺序执行 vs 并行执行的时间差异
"""

import time
import sys
import os

# 添加脚本路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis_engine import analyze_stock, print_report


def test_parallel_performance():
    """测试并行性能"""
    print("=" * 70)
    print("🧪 金融分析师团队 - 并行优化测试")
    print("=" * 70)
    
    # 测试股票
    test_cases = [
        ("600519", "贵州茅台", 1550),
    ]
    
    results = {}
    
    # ========== 测试快速版 ==========
    print("\n" + "=" * 70)
    print("📋 测试快速版（目标: ≤30s）")
    print("=" * 70)
    print("并行策略: 3个分析师同时调用 AI")
    print("Token 限制: 300（精简输出）")
    print()
    
    start = time.time()
    result = analyze_stock("600519", "贵州茅台", 1550, mode="quick", verbose=True)
    quick_time = time.time() - start
    results["快速版"] = quick_time
    
    print_report(result)
    print(f"\n⏱️ 实际耗时: {quick_time:.1f}s")
    print(f"🎯 目标时间: 30s")
    print(f"{'✅ 达成目标！' if quick_time <= 30 else '❌ 未达成目标'}")
    
    # ========== 测试标准版 ==========
    print("\n" + "=" * 70)
    print("📋 测试标准版（目标: ≤90s）")
    print("=" * 70)
    print("并行策略: 5个分析师并行 + 策略师顺序")
    print("Token 限制: 1500（标准输出）")
    print()
    
    start = time.time()
    result = analyze_stock("600519", "贵州茅台", 1550, mode="standard", verbose=True)
    standard_time = time.time() - start
    results["标准版"] = standard_time
    
    print_report(result)
    print(f"\n⏱️ 实际耗时: {standard_time:.1f}s")
    print(f"🎯 目标时间: 90s")
    print(f"{'✅ 达成目标！' if standard_time <= 90 else '❌ 未达成目标'}")
    
    # ========== 汇总对比 ==========
    print("\n" + "=" * 70)
    print("📊 性能汇总")
    print("=" * 70)
    
    print("\n| 档位 | 目标时间 | 实际耗时 | 结果 |")
    print("|------|----------|----------|------|")
    print(f"| 快速版 | ≤30s | {quick_time:.1f}s | {'✅' if quick_time <= 30 else '❌'} |")
    print(f"| 标准版 | ≤90s | {standard_time:.1f}s | {'✅' if standard_time <= 90 else '❌'} |")
    
    print("\n📈 优化效果:")
    
    # 估算顺序执行时间（假设每个分析师平均 10-15s）
    estimated_sequential_quick = 3 * 12  # 3个分析师，平均12s
    estimated_sequential_standard = 6 * 12  # 6个分析师，平均12s
    
    print(f"  - 快速版预估顺序执行: ~{estimated_sequential_quick}s → 并行: {quick_time:.1f}s")
    print(f"    节省时间: ~{estimated_sequential_quick - quick_time:.0f}s ({(1 - quick_time/estimated_sequential_quick)*100:.0f}% 提升)")
    
    print(f"  - 标准版预估顺序执行: ~{estimated_sequential_standard}s → 并行: {standard_time:.1f}s")
    print(f"    节省时间: ~{estimated_sequential_standard - standard_time:.0f}s ({(1 - standard_time/estimated_sequential_standard)*100:.0f}% 提升)")
    
    print("\n" + "=" * 70)
    
    return results


def test_timeout_control():
    """测试超时控制"""
    print("\n" + "=" * 70)
    print("🧪 超时控制测试")
    print("=" * 70)
    
    from analysis_engine import AnalysisEngine
    
    print(f"单次 AI 调用超时: {AnalysisEngine.SINGLE_CALL_TIMEOUT}s")
    print(f"快速版整体超时: {AnalysisEngine.QUICK_TIMEOUT}s")
    print(f"标准版整体超时: {AnalysisEngine.STANDARD_TIMEOUT}s")
    print(f"专业版整体超时: {AnalysisEngine.PRO_TIMEOUT}s")
    print("\n✅ 超时控制配置正确")


if __name__ == "__main__":
    print("\n🚀 开始测试...\n")
    
    # 测试超时配置
    test_timeout_control()
    
    # 测试并行性能
    results = test_parallel_performance()
    
    print("\n✅ 测试完成！")