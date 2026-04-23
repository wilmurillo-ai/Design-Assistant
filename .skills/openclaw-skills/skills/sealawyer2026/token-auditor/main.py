#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token审计员 - CLI入口
Token Auditor CLI

Token消费诊断与优化专家
"""

import argparse
import json
import sys
import os
from datetime import datetime, timedelta

from auditor import TokenAuditor, ConsumptionRecord, get_auditor


def print_header():
    """打印标题"""
    print("""
╔══════════════════════════════════════════════╗
║     Token审计员 v1.0.0                       ║
║     消费诊断与优化专家                       ║
╚══════════════════════════════════════════════╝
""")


def generate_sample_data(auditor: TokenAuditor, days: int = 30):
    """生成示例数据"""
    import random
    
    models = ["gpt-4o", "gpt-4o-mini", "kimi-k2", "doubao-pro", "claude-3-5"]
    task_types = ["code", "simple", "long_context", "qa"]
    
    for i in range(days * 10):  # 每天10条记录
        day_offset = random.randint(0, days - 1)
        timestamp = (datetime.now() - timedelta(days=day_offset)).isoformat()
        
        model = random.choice(models)
        task_type = random.choice(task_types)
        
        # 模拟一些浪费情况
        prompt_length = random.randint(100, 3000) if random.random() > 0.8 else random.randint(100, 500)
        tokens_input = prompt_length + random.randint(0, 500)
        tokens_output = random.randint(100, 1000)
        
        # 成本计算 (简化)
        cost_per_1k = {"gpt-4o": 0.005, "gpt-4o-mini": 0.00015, "kimi-k2": 0.00015, 
                       "doubao-pro": 0.00008, "claude-3-5": 0.003}[model]
        cost = (tokens_input + tokens_output) / 1000 * cost_per_1k
        
        # 某天异常高消费
        if day_offset == 5:
            cost *= 3
        
        record = ConsumptionRecord(
            timestamp=timestamp,
            model=model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost=cost,
            task_type=task_type,
            prompt_length=prompt_length,
            response_length=tokens_output,
            latency_ms=random.randint(200, 2000)
        )
        auditor.add_record(record)


def cmd_audit(args):
    """执行审计"""
    auditor = get_auditor(args.config)
    
    # 如果有示例数据标志，生成示例
    if args.sample:
        print("🎲 生成示例数据...")
        generate_sample_data(auditor, args.days)
        print(f"   已生成 {len(auditor.records)} 条记录\n")
    
    if not auditor.records:
        print("❌ 暂无消费记录")
        print("   使用 --sample 生成示例数据进行测试")
        return
    
    print(f"🔍 正在审计最近 {args.days} 天的消费数据...")
    print()
    
    # 生成报告
    report = auditor.generate_report(args.days)
    
    # 显示概览
    print("📊 审计概览")
    print("-" * 60)
    print(f"   报告ID: {report.report_id}")
    print(f"   审计周期: {report.period_start[:10]} 至 {report.period_end[:10]}")
    print(f"   总调用次数: {report.total_records:,}")
    print(f"   总Token数: {report.total_tokens:,}")
    print(f"   总成本: ¥{report.total_cost:.2f}")
    
    health_icon = "🟢" if report.overall_health_score >= 80 else "🟡" if report.overall_health_score >= 60 else "🔴"
    print(f"   健康评分: {health_icon} {report.overall_health_score}/100")
    print()
    
    # 异常检测
    anomalies = auditor.detect_anomalies()
    if anomalies:
        print("⚠️ 发现消费异常")
        print("-" * 60)
        for a in anomalies[:5]:
            icon = "📈" if a["type"] == "spike" else "📉"
            print(f"   {icon} {a['date']}: ¥{a['cost']:.2f} (偏离{a['deviation']:+.1f}σ)")
        print()
    
    # 浪费分析
    if report.waste_items:
        print("💸 浪费分析")
        print("-" * 60)
        total_waste = sum(w.wasted_cost for w in report.waste_items)
        for w in report.waste_items[:5]:
            icon = "🔴" if w.severity.value == "critical" else "🟠" if w.severity.value == "high" else "🟡"
            print(f"   {icon} {w.type.value}")
            print(f"      {w.description}")
            print(f"      浪费: ¥{w.wasted_cost:.2f} | 建议: {w.suggestion}")
            print()
        print(f"   总浪费金额: ¥{total_waste:.2f}")
        print()
    
    # 优化机会
    if report.opportunities:
        print("💡 优化机会")
        print("-" * 60)
        print(f"{'类别':<15} {'当前成本':<12} {'优化后':<12} {'节省':<12} {'优先级':<8}")
        print("-" * 60)
        for o in report.opportunities[:5]:
            print(f"{o.category:<15} ¥{o.current_cost:<11.2f} ¥{o.optimized_cost:<11.2f} {o.savings_percentage:.0f}% ¥{o.savings:<11.2f} P{o.priority}")
        print()
        total_savings = sum(o.savings for o in report.opportunities)
        print(f"   💰 全部优化后可节省: ¥{total_savings:.2f}")
        print()
    
    # 行动建议
    print("🎯 行动建议")
    print("-" * 60)
    for i, rec in enumerate(report.recommendations, 1):
        print(f"   {i}. {rec}")
    print()
    
    # 导出报告
    if args.export:
        output_dir = os.path.dirname(args.export) or "."
        if output_dir != "." and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        format = "json" if args.export.endswith(".json") else "markdown"
        content = auditor.export_report(report, format)
        
        with open(args.export, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 报告已导出: {args.export}")


def cmd_simulate(args):
    """模拟数据并审计"""
    auditor = get_auditor(args.config)
    
    print("🎲 生成模拟数据...")
    generate_sample_data(auditor, args.days)
    print(f"   已生成 {len(auditor.records)} 条记录\n")
    
    # 执行审计
    args.sample = False  # 避免重复生成
    cmd_audit(args)


def cmd_export(args):
    """导出已有报告"""
    # 这里可以实现从历史记录加载报告
    print("📄 导出功能")
    print("   从模拟数据生成示例报告...")
    
    auditor = get_auditor(args.config)
    generate_sample_data(auditor, 30)
    report = auditor.generate_report(30)
    
    format = "json" if args.format == "json" else "markdown"
    content = auditor.export_report(report, format)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 报告已保存: {args.output}")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="Token审计员 - 消费诊断与优化专家",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用示例数据进行审计
  python main.py audit --sample --days 30
  
  # 审计并导出报告
  python main.py audit --sample --export report.md
  
  # 生成模拟数据并审计
  python main.py simulate --days 30
  
  # 导出JSON格式报告
  python main.py export --format json --output report.json

功能:
  - 消费模式分析
  - 异常检测 (突增/浪费)
  - 优化建议报告
  - ROI计算

检测的浪费类型:
  - 提示词过长 (可压缩)
  - 模型选择不当 (简单任务用大模型)
  - 重复请求 (未使用缓存)
  - 高温度参数 (输出冗余)
        """
    )
    
    parser.add_argument('--version', action='version', version='Token审计员 v1.0.0')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # audit 命令
    audit_parser = subparsers.add_parser('audit', help='执行审计')
    audit_parser.add_argument('--days', type=int, default=30, help='审计天数')
    audit_parser.add_argument('--sample', action='store_true', help='使用示例数据')
    audit_parser.add_argument('--export', help='导出报告路径')
    
    # simulate 命令
    simulate_parser = subparsers.add_parser('simulate', help='模拟数据并审计')
    simulate_parser.add_argument('--days', type=int, default=30, help='天数')
    simulate_parser.add_argument('--export', help='导出报告路径')
    
    # export 命令
    export_parser = subparsers.add_parser('export', help='导出报告')
    export_parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='格式')
    export_parser.add_argument('--output', default='report.md', help='输出文件')
    
    args = parser.parse_args()
    
    if not args.command:
        print_header()
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == 'audit':
            cmd_audit(args)
        elif args.command == 'simulate':
            cmd_simulate(args)
        elif args.command == 'export':
            cmd_export(args)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
