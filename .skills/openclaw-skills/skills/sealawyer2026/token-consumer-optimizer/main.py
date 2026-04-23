#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token消费优选师 - CLI入口
Token Consumer Optimizer

帮助用户选择最经济的AI模型消费方案
"""

import argparse
import json
import sys
from typing import Optional

from optimizer import (
    TokenConsumerOptimizer, 
    BudgetLevel, 
    get_optimizer,
    recommend_model
)


def print_header():
    """打印标题"""
    print("""
╔══════════════════════════════════════════════╗
║     Token消费优选师 v1.0.0                   ║
║     Token Consumer Optimizer                 ║
╚══════════════════════════════════════════════╝
""")


def cmd_recommend(args):
    """推荐命令"""
    optimizer = get_optimizer()
    
    budget_level = BudgetLevel(args.budget) if args.budget else BudgetLevel.BALANCED
    
    # 估算token数
    if args.tokens:
        input_tokens = args.tokens
    elif args.text:
        input_tokens = len(args.text)
    else:
        input_tokens = 1000  # 默认值
    
    output_tokens = args.output_tokens or (input_tokens // 2)
    
    print(f"📊 任务分析")
    print(f"   任务类型: {args.task}")
    print(f"   输入Token: {input_tokens:,}")
    print(f"   输出Token: {output_tokens:,}")
    print(f"   预算级别: {budget_level.value}")
    print()
    
    recommendations = optimizer.recommend(
        task_type=args.task,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        budget_level=budget_level
    )
    
    if not recommendations:
        print("❌ 无法生成推荐，请检查任务类型")
        return
    
    print("💡 推荐方案 (按性价比排序):")
    print("-" * 80)
    
    for i, rec in enumerate(recommendations[:5], 1):
        badge = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{badge} #{i} {rec.model.name} ({rec.model.provider})")
        print(f"    💰 预估成本: ¥{rec.total_cost_cny:.4f} (${rec.total_cost_usd:.4f})")
        print(f"    📉 可节省: {rec.savings_percent:.1f}% (对比最贵方案)")
        print(f"    ✅ 推荐理由: {rec.reason}")
        print(f"    📊 综合评分: {rec.score:.1f}/100")
        print()
    
    # 输出JSON格式
    if args.json:
        result = {
            "task_type": args.task,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "recommendations": [
                {
                    "rank": i+1,
                    "model": rec.model.name,
                    "provider": rec.model.provider,
                    "cost_cny": rec.total_cost_cny,
                    "cost_usd": rec.total_cost_usd,
                    "savings_percent": rec.savings_percent,
                    "reason": rec.reason,
                    "score": rec.score
                }
                for i, rec in enumerate(recommendations[:5])
            ]
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_compare(args):
    """对比命令"""
    optimizer = get_optimizer()
    
    input_tokens = args.tokens or 1000
    output_tokens = args.output_tokens or (input_tokens // 2)
    
    print(f"📊 全平台价格对比 ({input_tokens:,} tokens)")
    print("-" * 80)
    print(f"{'排名':<4} {'模型':<20} {'厂商':<12} {'人民币':<10} {'美元':<10} {'上下文':<10}")
    print("-" * 80)
    
    results = optimizer.compare_all(input_tokens, output_tokens)
    
    for i, r in enumerate(results, 1):
        context = f"{r['context_length']//1000}K" if r['context_length'] < 1000000 else f"{r['context_length']//1000000}M"
        print(f"#{i:<3} {r['model_name']:<20} {r['provider']:<12} ¥{r['cost_cny']:<9.4f} ${r['cost_usd']:<9.4f} {context:<10}")
    
    print("-" * 80)
    
    # 计算节省
    cheapest = results[0]
    most_expensive = results[-1]
    savings = ((most_expensive['cost_cny'] - cheapest['cost_cny']) / most_expensive['cost_cny'] * 100)
    
    print(f"\n💡 省钱提示: 使用 {cheapest['model_name']} 比 {most_expensive['model_name']} 节省 {savings:.1f}%")
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))


def cmd_budget(args):
    """预算分析命令"""
    optimizer = get_optimizer()
    
    analysis = optimizer.analyze_budget(
        monthly_budget_cny=args.budget,
        daily_calls=args.daily_calls,
        avg_input_tokens=args.tokens or 1000
    )
    
    print(f"📊 预算分析报告")
    print(f"   月度预算: ¥{analysis['budget_cny']:.2f}")
    print(f"   预估月调用: {analysis['estimated_monthly_calls']:,} 次")
    print()
    
    print("💰 各模型月度成本:")
    print("-" * 80)
    print(f"{'模型':<20} {'单次成本':<12} {'月度成本':<12} {'可调用':<12} {'状态':<10}")
    print("-" * 80)
    
    for opt in analysis['model_options'][:10]:
        status = "✅ 支持" if opt['within_budget'] else "❌ 超预算"
        calls = f"{opt['affordable_calls']:,}次" if opt['within_budget'] else "-"
        print(f"{opt['model_name']:<20} ¥{opt['cost_per_call_cny']:<11.4f} ¥{opt['monthly_cost_cny']:<11.2f} {calls:<12} {status:<10}")
    
    print("-" * 80)
    
    recommended = analysis.get('recommended', {})
    if recommended:
        print(f"\n🎯 推荐方案: {recommended.get('model_name', 'N/A')}")
        print(f"   单次成本: ¥{recommended.get('cost_per_call_cny', 0):.4f}")
        if recommended.get('within_budget'):
            print(f"   ✅ 在预算范围内")
        else:
            print(f"   ⚠️ 建议增加预算或降低调用频率")
    
    if args.json:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))


def cmd_calculate(args):
    """成本计算命令"""
    optimizer = get_optimizer()
    
    model_id = args.model
    input_tokens = args.tokens or 1000
    output_tokens = args.output_tokens or (input_tokens // 2)
    
    try:
        cost_cny, cost_usd = optimizer.calculate_cost(model_id, input_tokens, output_tokens)
        model = optimizer.models.get(model_id)
        
        print(f"📊 成本计算结果")
        print(f"   模型: {model.name if model else model_id}")
        print(f"   输入Token: {input_tokens:,}")
        print(f"   输出Token: {output_tokens:,}")
        print()
        print(f"   💰 预估成本:")
        print(f"      人民币: ¥{cost_cny:.4f}")
        print(f"      美元: ${cost_usd:.4f}")
        
        if args.json:
            print(json.dumps({
                "model": model_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_cny": cost_cny,
                "cost_usd": cost_usd
            }, ensure_ascii=False, indent=2))
            
    except ValueError as e:
        print(f"❌ 错误: {e}")
        print(f"可用模型: {', '.join(optimizer.models.keys())}")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="Token消费优选师 - 帮你选择最经济的AI模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 推荐最优模型
  python main.py recommend --task code_generation --tokens 2000
  
  # 对比所有模型价格
  python main.py compare --tokens 5000
  
  # 预算分析
  python main.py budget --budget 1000 --daily-calls 50
  
  # 计算特定模型成本
  python main.py calculate --model kimi-k2 --tokens 10000

任务类型:
  - simple_qa: 简单问答
  - code_generation: 代码生成
  - document_processing: 长文档处理
  - creative_writing: 创意写作
  - analysis: 数据分析
  - translation: 翻译任务
        """
    )
    
    parser.add_argument('--version', action='version', version='Token消费优选师 v1.0.0')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # recommend 命令
    recommend_parser = subparsers.add_parser('recommend', help='推荐最优模型')
    recommend_parser.add_argument('--task', required=True, help='任务类型')
    recommend_parser.add_argument('--tokens', type=int, help='输入token数')
    recommend_parser.add_argument('--output-tokens', type=int, help='输出token数')
    recommend_parser.add_argument('--text', help='输入文本(自动估算token)')
    recommend_parser.add_argument('--budget', default='balanced', 
                                 choices=['ultra_cheap', 'cheap', 'balanced', 'performance', 'ultra_performance'],
                                 help='预算级别')
    
    # compare 命令
    compare_parser = subparsers.add_parser('compare', help='对比所有模型')
    compare_parser.add_argument('--tokens', type=int, default=1000, help='输入token数')
    compare_parser.add_argument('--output-tokens', type=int, help='输出token数')
    
    # budget 命令
    budget_parser = subparsers.add_parser('budget', help='预算分析')
    budget_parser.add_argument('--budget', type=float, required=True, help='月度预算(人民币)')
    budget_parser.add_argument('--daily-calls', type=int, default=100, help='日均调用次数')
    budget_parser.add_argument('--tokens', type=int, default=1000, help='平均输入token数')
    
    # calculate 命令
    calculate_parser = subparsers.add_parser('calculate', help='计算特定模型成本')
    calculate_parser.add_argument('--model', required=True, help='模型ID')
    calculate_parser.add_argument('--tokens', type=int, required=True, help='输入token数')
    calculate_parser.add_argument('--output-tokens', type=int, help='输出token数')
    
    args = parser.parse_args()
    
    if not args.command:
        print_header()
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == 'recommend':
            cmd_recommend(args)
        elif args.command == 'compare':
            cmd_compare(args)
        elif args.command == 'budget':
            cmd_budget(args)
        elif args.command == 'calculate':
            cmd_calculate(args)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
