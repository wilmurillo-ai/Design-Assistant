#!/usr/bin/env python3
"""
Token消费优选技能 (Token Consumer Optimizer)
智能AI模型消费决策助手
"""

import json
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    CODE = "code"
    WRITING = "writing"
    ANALYSIS = "analysis"
    CHAT = "chat"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"

@dataclass
class Model:
    id: str
    name: str
    provider: str
    input_price: float
    output_price: float
    currency: str
    unit: str
    strengths: List[str]
    weaknesses: List[str]
    speed: str
    quality: str
    context_window: int

def load_models() -> List[Model]:
    """加载模型数据库"""
    try:
        with open('models.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        models = []
        for m in data['models']:
            # 统一转换为USD per million
            if m['currency'] == 'CNY':
                rate = data['exchange_rate']['CNY_TO_USD']
                input_price = m['input_price_cny'] * 1000 * rate  # per 1k -> per million
                output_price = m['output_price_cny'] * 1000 * rate
            else:
                input_price = m['input_price_usd']
                output_price = m['output_price_usd']
            
            models.append(Model(
                id=m['id'],
                name=m['name'],
                provider=m['provider'],
                input_price=input_price,
                output_price=output_price,
                currency='USD',
                unit='per_million',
                strengths=m.get('strengths', []),
                weaknesses=m.get('weaknesses', []),
                speed=m.get('speed', 'medium'),
                quality=m.get('quality', 'medium'),
                context_window=m.get('context_window', 8000)
            ))
        return models
    except Exception as e:
        print(f"❌ 加载模型数据失败: {e}")
        return []

def calculate_cost(model: Model, input_tokens: int, output_tokens: int) -> float:
    """计算调用成本 (USD)"""
    input_cost = (input_tokens / 1_000_000) * model.input_price
    output_cost = (output_tokens / 1_000_000) * model.output_price
    return input_cost + output_cost

def format_currency(amount: float) -> str:
    """格式化货币显示"""
    if amount < 0.01:
        return f"${amount*100:.2f}¢"
    return f"${amount:.4f}"

def cmd_recommend(args):
    """智能推荐模型"""
    models = load_models()
    if not models:
        return
    
    task = args.task or "通用任务"
    budget = args.budget or 10  # USD
    quality = args.quality or "medium"
    
    print(f"🎯 Token消费优选推荐")
    print(f"=" * 60)
    print(f"任务类型: {task}")
    print(f"预算范围: ${budget}")
    print(f"质量要求: {quality}")
    print("")
    
    # 根据质量和预算筛选
    filtered = []
    for m in models:
        score = 0
        
        # 质量匹配
        if quality == "high" and m.quality in ["high"]:
            score += 3
        elif quality == "medium" and m.quality in ["medium", "high"]:
            score += 2
        elif quality == "low":
            score += 1
        
        # 成本效益 (价格越低越好)
        avg_price = (m.input_price + m.output_price) / 2
        if avg_price < 1:  # per million
            score += 3
        elif avg_price < 5:
            score += 2
        else:
            score += 1
        
        filtered.append((m, score, avg_price))
    
    # 排序: 分数降序，价格升序
    filtered.sort(key=lambda x: (-x[1], x[2]))
    
    print("📊 推荐方案 (Top 3):")
    print("")
    
    for i, (model, score, _) in enumerate(filtered[:3], 1):
        cost_1m = calculate_cost(model, 500000, 500000)  # 估算100万token成本
        
        print(f"{i}. 🏆 {model.name}")
        print(f"   提供商: {model.provider}")
        print(f"   输入价格: ${model.input_price}/M tokens")
        print(f"   输出价格: ${model.output_price}/M tokens")
        print(f"   估算成本: {format_currency(cost_1m)} (1M tokens)")
        print(f"   优势: {', '.join(model.strengths[:3])}")
        print(f"   上下文: {model.context_window:,} tokens")
        print("")
    
    # 最优推荐
    best = filtered[0][0]
    print(f"💡 最优推荐: {best.name}")
    print(f"   理由: 性价比最优，满足{quality}质量要求")
    print(f"   预估每月成本(100万tokens): {format_currency(calculate_cost(best, 500000, 500000) * 10)}")

def cmd_compare(args):
    """比价查询"""
    models = load_models()
    if not models:
        return
    
    input_tokens = args.input_tokens or 1000
    output_tokens = args.output_tokens or 500
    
    print(f"💰 Token消费比价")
    print(f"=" * 70)
    print(f"输入: {input_tokens:,} tokens | 输出: {output_tokens:,} tokens")
    print("")
    
    results = []
    for m in models:
        cost = calculate_cost(m, input_tokens, output_tokens)
        results.append((m, cost))
    
    # 按价格排序
    results.sort(key=lambda x: x[1])
    
    print(f"{'排名':<4} {'模型':<20} {'提供商':<12} {'成本':<12} {'性价比'}")
    print("-" * 70)
    
    cheapest = results[0][1]
    for i, (model, cost) in enumerate(results[:10], 1):
        savings = ((cost - cheapest) / cheapest * 100) if cheapest > 0 else 0
        savings_str = f"+{savings:.0f}%" if savings > 0 else "最优"
        print(f"{i:<4} {model.name:<20} {model.provider:<12} {format_currency(cost):<12} {savings_str}")
    
    print("")
    print(f"💡 最便宜: {results[0][0].name} ({format_currency(results[0][1])})")
    print(f"💡 最贵: {results[-1][0].name} ({format_currency(results[-1][1])})")
    print(f"💡 差价: {format_currency(results[-1][1] - results[0][1])} ({(results[-1][1]/results[0][1]-1)*100:.0f}%)")

def cmd_estimate(args):
    """成本估算"""
    models = load_models()
    if not models:
        return
    
    model_id = args.model
    input_tokens = args.input or 10000
    output_tokens = args.output or 3000
    
    # 查找模型
    model = None
    for m in models:
        if m.id == model_id or m.name.lower() == model_id.lower():
            model = m
            break
    
    if not model:
        print(f"❌ 未找到模型: {model_id}")
        print(f"可用模型: {', '.join([m.id for m in models])}")
        return
    
    cost = calculate_cost(model, input_tokens, output_tokens)
    
    print(f"🧮 成本估算")
    print(f"=" * 50)
    print(f"模型: {model.name}")
    print(f"提供商: {model.provider}")
    print("")
    print(f"输入Token: {input_tokens:,}")
    print(f"输出Token: {output_tokens:,}")
    print(f"总计Token: {input_tokens + output_tokens:,}")
    print("")
    print(f"输入成本: ${(input_tokens/1_000_000)*model.input_price:.6f}")
    print(f"输出成本: ${(output_tokens/1_000_000)*model.output_price:.6f}")
    print(f"总成本: {format_currency(cost)}")
    print("")
    
    # 换算人民币
    cny_cost = cost * 7.2
    print(f"约等于: ¥{cny_cost:.4f}")

def cmd_budget(args):
    """预算规划"""
    monthly_budget = args.monthly or 1000
    usage = args.usage or "daily"
    
    models = load_models()
    if not models:
        return
    
    print(f"📊 Token消费预算规划")
    print(f"=" * 60)
    print(f"月度预算: ${monthly_budget}")
    print(f"使用频率: {usage}")
    print("")
    
    # 计算可用Token数
    print("不同模型下的可用Token量:")
    print("")
    print(f"{'模型':<20} {'提供商':<12} {'可用Token':<15} {'日均Token'}")
    print("-" * 70)
    
    for m in models:
        avg_price = (m.input_price + m.output_price) / 2
        tokens_per_month = (monthly_budget / avg_price) * 1_000_000
        tokens_per_day = tokens_per_month / 30
        
        print(f"{m.name:<20} {m.provider:<12} {tokens_per_month:>12,.0f} {tokens_per_day:>12,.0f}")
    
    print("")
    print("💡 建议:")
    print("   - 高频调用: 选择低价模型 (Gemini Flash, GPT-4o-mini)")
    print("   - 关键任务: 混合策略 (简单任务用低价模型，复杂任务用高价模型)")
    print("   - 预留20%预算用于突发需求")

def cmd_report(args):
    """生成消费报告"""
    print(f"📈 Token消费报告")
    print(f"=" * 60)
    print("")
    print("功能开发中...")
    print("")
    print("计划功能:")
    print("- 历史消费数据分析")
    print("- 成本趋势预测")
    print("- 优化建议")
    print("- 节省金额统计")
    print("")
    print("💡 当前可使用 compare/estimate 命令进行即时分析")

def main():
    parser = argparse.ArgumentParser(
        description="Token消费优选 - 智能AI模型消费决策助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  token-consumer-optimizer recommend --task "代码审查"
  token-consumer-optimizer compare --input 1000 --output 500
  token-consumer-optimizer estimate --model gpt-4o --input 10000
  token-consumer-optimizer budget --monthly 500

Token经济生态:
  - Token Master: Token压缩
  - Compute Market: 算力市场  
  - Token Consumer Optimizer: 消费优选 (本工具)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # recommend命令
    recommend_parser = subparsers.add_parser('recommend', help='智能推荐最优模型')
    recommend_parser.add_argument('--task', '-t', help='任务描述')
    recommend_parser.add_argument('--budget', '-b', type=float, help='预算(USD)')
    recommend_parser.add_argument('--quality', '-q', choices=['low', 'medium', 'high'], 
                                  default='medium', help='质量要求')
    
    # compare命令
    compare_parser = subparsers.add_parser('compare', help='比价查询')
    compare_parser.add_argument('--input-tokens', '-i', type=int, default=1000)
    compare_parser.add_argument('--output-tokens', '-o', type=int, default=500)
    
    # estimate命令
    estimate_parser = subparsers.add_parser('estimate', help='成本估算')
    estimate_parser.add_argument('--model', '-m', required=True, help='模型ID')
    estimate_parser.add_argument('--input', '-i', type=int, default=10000)
    estimate_parser.add_argument('--output', type=int, default=3000)
    
    # budget命令
    budget_parser = subparsers.add_parser('budget', help='预算规划')
    budget_parser.add_argument('--monthly', '-m', type=float, default=1000)
    budget_parser.add_argument('--usage', '-u', choices=['daily', 'weekly', 'monthly'],
                               default='daily', help='使用频率')
    
    # report命令
    report_parser = subparsers.add_parser('report', help='消费报告')
    report_parser.add_argument('--period', '-p', choices=['day', 'week', 'month'],
                               default='week', help='报告周期')
    
    args = parser.parse_args()
    
    if args.command == 'recommend':
        cmd_recommend(args)
    elif args.command == 'compare':
        cmd_compare(args)
    elif args.command == 'estimate':
        cmd_estimate(args)
    elif args.command == 'budget':
        cmd_budget(args)
    elif args.command == 'report':
        cmd_report(args)
    else:
        parser.print_help()
        print("\n💡 Token经济生态:")
        print("   - Token Master: Token压缩 (已发布)")
        print("   - Compute Market: 算力市场 (已发布)")
        print("   - Token Consumer Optimizer: 消费优选 (本工具)")
        print("\n   访问: http://token-master.cn/shop/")

if __name__ == '__main__':
    main()
