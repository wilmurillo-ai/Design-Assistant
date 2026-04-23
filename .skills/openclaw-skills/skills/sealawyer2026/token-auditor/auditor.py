#!/usr/bin/env python3
"""
Token审计监控技能 (Token Auditor)
全方位Token使用审计与监控系统
"""

import json
import argparse
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# 数据存储路径
DATA_DIR = Path.home() / ".token-auditor"
DATA_DIR.mkdir(exist_ok=True)

@dataclass
class UsageRecord:
    timestamp: str
    project: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    user: str = "default"

@dataclass
class BudgetConfig:
    project: str
    monthly_budget: float
    thresholds: List[int]  # 告警阈值百分比
    alerts_triggered: List[str] = None
    
    def __post_init__(self):
        if self.alerts_triggered is None:
            self.alerts_triggered = []

class TokenAuditor:
    def __init__(self):
        self.usage_file = DATA_DIR / "usage.jsonl"
        self.config_file = DATA_DIR / "config.json"
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"projects": {}, "alert_enabled": True}
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def record_usage(self, project: str, model: str, input_tokens: int, 
                     output_tokens: int, cost: float, user: str = "default"):
        """记录Token使用情况"""
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            project=project,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            user=user
        )
        
        with open(self.usage_file, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
    
    def load_usage(self, days: int = 30) -> List[UsageRecord]:
        """加载使用记录"""
        records = []
        cutoff = datetime.now() - timedelta(days=days)
        
        if not self.usage_file.exists():
            return records
        
        with open(self.usage_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    record_time = datetime.fromisoformat(data['timestamp'])
                    if record_time >= cutoff:
                        records.append(UsageRecord(**data))
                except:
                    continue
        
        return records
    
    def get_project_stats(self, project: str = None, days: int = 7) -> Dict:
        """获取项目统计"""
        records = self.load_usage(days)
        
        if project:
            records = [r for r in records if r.project == project]
        
        if not records:
            return {
                "total_calls": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0,
                "avg_daily_cost": 0
            }
        
        stats = {
            "total_calls": len(records),
            "total_input_tokens": sum(r.input_tokens for r in records),
            "total_output_tokens": sum(r.output_tokens for r in records),
            "total_cost": sum(r.cost for r in records),
            "avg_daily_cost": sum(r.cost for r in records) / days
        }
        
        # 按模型分组
        model_stats = {}
        for r in records:
            if r.model not in model_stats:
                model_stats[r.model] = {"calls": 0, "cost": 0}
            model_stats[r.model]["calls"] += 1
            model_stats[r.model]["cost"] += r.cost
        
        stats["by_model"] = model_stats
        
        # 按天分组的消费趋势
        daily_cost = {}
        for r in records:
            day = r.timestamp[:10]
            daily_cost[day] = daily_cost.get(day, 0) + r.cost
        
        stats["daily_trend"] = daily_cost
        
        return stats
    
    def check_anomalies(self, sensitivity: str = "medium") -> List[Dict]:
        """检测异常"""
        records = self.load_usage(7)  # 最近7天
        anomalies = []
        
        if len(records) < 24:  # 需要足够数据
            return anomalies
        
        # 计算平均每小时消费
        hourly_cost = {}
        for r in records:
            hour = r.timestamp[:13]  # 精确到小时
            hourly_cost[hour] = hourly_cost.get(hour, 0) + r.cost
        
        if not hourly_cost:
            return anomalies
        
        avg_hourly = sum(hourly_cost.values()) / len(hourly_cost)
        
        # 异常阈值
        if sensitivity == "high":
            threshold = 2.0
        elif sensitivity == "medium":
            threshold = 3.0
        else:
            threshold = 5.0
        
        # 检测异常小时
        for hour, cost in hourly_cost.items():
            if cost > avg_hourly * threshold:
                anomalies.append({
                    "type": "spike",
                    "time": hour,
                    "cost": cost,
                    "avg": avg_hourly,
                    "multiplier": cost / avg_hourly
                })
        
        # 检测连续增长趋势
        daily_totals = []
        for r in records:
            day = r.timestamp[:10]
            daily_totals.append((day, r.cost))
        
        if len(daily_totals) >= 3:
            # 简化：检测最后3天是否持续增长超过20%
            pass  # 实际实现会更复杂
        
        return anomalies
    
    def check_budget_alerts(self, project: str) -> List[Dict]:
        """检查预算告警"""
        alerts = []
        
        if project not in self.config.get("projects", {}):
            return alerts
        
        config = self.config["projects"][project]
        budget = config.get("monthly_budget", 0)
        thresholds = config.get("thresholds", [50, 80, 100])
        triggered = config.get("alerts_triggered", [])
        
        if budget <= 0:
            return alerts
        
        # 获取本月消费
        stats = self.get_project_stats(project, days=30)
        spent = stats["total_cost"]
        percentage = (spent / budget) * 100
        
        for threshold in thresholds:
            if percentage >= threshold and threshold not in triggered:
                alerts.append({
                    "threshold": threshold,
                    "percentage": percentage,
                    "spent": spent,
                    "budget": budget,
                    "message": f"预算告警: 已使用 {percentage:.1f}% (${spent:.2f}/${budget:.2f})"
                })
                triggered.append(threshold)
        
        # 更新已触发告警
        self.config["projects"][project]["alerts_triggered"] = triggered
        self.save_config()
        
        return alerts

def cmd_monitor(args):
    """启动监控"""
    auditor = TokenAuditor()
    
    project = args.project or "default"
    budget = args.budget or 0
    
    # 保存项目配置
    if project not in auditor.config.get("projects", {}):
        auditor.config["projects"][project] = {}
    
    auditor.config["projects"][project]["monthly_budget"] = budget
    auditor.config["projects"][project]["thresholds"] = [50, 80, 100]
    auditor.config["projects"][project]["alerts_triggered"] = []
    auditor.save_config()
    
    print(f"🔍 Token审计监控已启动")
    print(f"=" * 50)
    print(f"项目: {project}")
    print(f"月度预算: ${budget}" if budget > 0 else "月度预算: 未设置")
    print(f"数据存储: {DATA_DIR}")
    print("")
    print("💡 提示:")
    print("  - 使用 'token-auditor status' 查看实时状态")
    print("  - 使用 'token-auditor check' 检测异常")
    print("  - 使用 'token-auditor report' 生成报告")

def cmd_status(args):
    """查看状态"""
    auditor = TokenAuditor()
    project = args.project
    
    print(f"📊 Token使用状态")
    print(f"=" * 50)
    
    # 今日统计
    today = datetime.now().strftime("%Y-%m-%d")
    today_records = [r for r in auditor.load_usage(1) if r.timestamp.startswith(today)]
    
    today_cost = sum(r.cost for r in today_records)
    today_calls = len(today_records)
    
    print(f"今日 ({today}):")
    print(f"  调用次数: {today_calls}")
    print(f"  消费金额: ${today_cost:.4f}")
    print("")
    
    # 项目统计
    stats = auditor.get_project_stats(project, days=7)
    
    print(f"最近7天统计:")
    print(f"  总调用次数: {stats['total_calls']}")
    print(f"  输入Token: {stats['total_input_tokens']:,}")
    print(f"  输出Token: {stats['total_output_tokens']:,}")
    print(f"  总消费: ${stats['total_cost']:.4f}")
    print(f"  日均消费: ${stats['avg_daily_cost']:.4f}")
    print("")
    
    # 按模型分组
    if stats.get("by_model"):
        print("按模型统计:")
        for model, data in sorted(stats["by_model"].items(), 
                                  key=lambda x: x[1]["cost"], reverse=True)[:5]:
            print(f"  {model}: {data['calls']}次, ${data['cost']:.4f}")
    
    # 预算状态
    if project and project in auditor.config.get("projects", {}):
        config = auditor.config["projects"][project]
        budget = config.get("monthly_budget", 0)
        if budget > 0:
            month_stats = auditor.get_project_stats(project, days=30)
            spent = month_stats["total_cost"]
            percentage = (spent / budget) * 100
            print("")
            print(f"预算状态: ${spent:.2f} / ${budget:.2f} ({percentage:.1f}%)")
            
            # 进度条
            bar_length = 20
            filled = int(bar_length * min(percentage, 100) / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"[{bar}]")

def cmd_check(args):
    """检查异常"""
    auditor = TokenAuditor()
    sensitivity = args.sensitivity or "medium"
    
    print(f"🔍 异常检测 (敏感度: {sensitivity})")
    print(f"=" * 50)
    
    anomalies = auditor.check_anomalies(sensitivity)
    
    if not anomalies:
        print("✅ 未发现异常消费模式")
    else:
        print(f"⚠️ 发现 {len(anomalies)} 个异常:")
        print("")
        for a in anomalies:
            print(f"  [{a['type'].upper()}] {a['time']}")
            print(f"    消费: ${a['cost']:.4f} (平均: ${a['avg']:.4f})")
            print(f"    倍数: {a['multiplier']:.1f}x")
            print("")
    
    # 检查预算告警
    for project in auditor.config.get("projects", {}):
        alerts = auditor.check_budget_alerts(project)
        if alerts:
            print(f"📢 预算告警 [{project}]:")
            for alert in alerts:
                print(f"  ⚠️ {alert['message']}")

def cmd_report(args):
    """生成报告"""
    auditor = TokenAuditor()
    period = args.period or "week"
    
    days = {"day": 1, "week": 7, "month": 30}.get(period, 7)
    
    print(f"📈 Token消费报告 ({period})")
    print(f"=" * 60)
    
    stats = auditor.get_project_stats(days=days)
    
    print(f"统计周期: 最近{days}天")
    print(f"总调用次数: {stats['total_calls']:,}")
    print(f"输入Token: {stats['total_input_tokens']:,}")
    print(f"输出Token: {stats['total_output_tokens']:,}")
    print(f"总消费: ${stats['total_cost']:.4f}")
    print(f"日均消费: ${stats['avg_daily_cost']:.4f}")
    print("")
    
    # 消费趋势
    if stats.get("daily_trend"):
        print("消费趋势 (最近7天):")
        for day in sorted(stats["daily_trend"].keys())[-7:]:
            cost = stats["daily_trend"][day]
            bar = "█" * int(cost * 50 / max(stats["daily_trend"].values()))
            print(f"  {day}: ${cost:.2f} {bar}")
    
    # 优化建议
    print("")
    print("💡 优化建议:")
    
    if stats["total_calls"] == 0:
        print("  - 暂无使用数据，开始记录后生成建议")
    else:
        # 简单建议逻辑
        by_model = stats.get("by_model", {})
        if by_model:
            most_expensive = max(by_model.items(), key=lambda x: x[1]["cost"])
            if most_expensive[1]["cost"] > stats["total_cost"] * 0.5:
                print(f"  - {most_expensive[0]} 占总消费50%以上，考虑优化使用策略")
        
        input_ratio = stats["total_input_tokens"] / max(stats["total_output_tokens"], 1)
        if input_ratio > 5:
            print("  - 输入/输出Token比例偏高，考虑使用token-consumer-optimizer优化")
        
        if stats["avg_daily_cost"] > 50:
            print("  - 日均消费较高，建议设置预算告警")

def cmd_alert(args):
    """设置告警"""
    auditor = TokenAuditor()
    
    project = args.project or "default"
    budget = args.budget or 0
    thresholds_str = args.thresholds or "50,80,100"
    thresholds = [int(t) for t in thresholds_str.split(",")]
    
    if project not in auditor.config.get("projects", {}):
        auditor.config["projects"][project] = {}
    
    auditor.config["projects"][project]["monthly_budget"] = budget
    auditor.config["projects"][project]["thresholds"] = thresholds
    auditor.config["projects"][project]["alerts_triggered"] = []
    auditor.save_config()
    
    print(f"✅ 告警设置已保存")
    print(f"=" * 50)
    print(f"项目: {project}")
    print(f"月度预算: ${budget}")
    print(f"告警阈值: {thresholds}%")
    print("")
    print("当消费达到阈值时将触发告警")

def cmd_record(args):
    """手动记录使用"""
    auditor = TokenAuditor()
    
    auditor.record_usage(
        project=args.project or "default",
        model=args.model or "unknown",
        input_tokens=args.input or 0,
        output_tokens=args.output or 0,
        cost=args.cost or 0,
        user=args.user or "default"
    )
    
    print(f"✅ 使用记录已保存")

def main():
    parser = argparse.ArgumentParser(
        description="Token审计监控 - 全方位Token使用审计与监控",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  token-auditor monitor --project myapp --budget 1000
  token-auditor status --project myapp
  token-auditor check --sensitivity high
  token-auditor report --period week
  token-auditor alert --budget 500 --thresholds 50,80,100

Token经济生态:
  - Token Master: Token压缩
  - Compute Market: 算力市场
  - Token Consumer Optimizer: 消费优选
  - Token Auditor: 审计监控 (本工具)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # monitor命令
    monitor_parser = subparsers.add_parser('monitor', help='启动监控')
    monitor_parser.add_argument('--project', '-p', help='项目名称')
    monitor_parser.add_argument('--budget', '-b', type=float, help='月度预算')
    
    # status命令
    status_parser = subparsers.add_parser('status', help='查看状态')
    status_parser.add_argument('--project', '-p', help='项目名称')
    
    # check命令
    check_parser = subparsers.add_parser('check', help='检查异常')
    check_parser.add_argument('--sensitivity', '-s', choices=['low', 'medium', 'high'],
                              default='medium', help='检测敏感度')
    
    # report命令
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('--period', '-p', choices=['day', 'week', 'month'],
                               default='week', help='报告周期')
    report_parser.add_argument('--format', '-f', choices=['text', 'html', 'json'],
                               default='text', help='输出格式')
    
    # alert命令
    alert_parser = subparsers.add_parser('alert', help='设置告警')
    alert_parser.add_argument('--project', '-p', help='项目名称')
    alert_parser.add_argument('--budget', '-b', type=float, required=True, help='月度预算')
    alert_parser.add_argument('--thresholds', '-t', help='告警阈值(逗号分隔，如50,80,100)')
    
    # record命令
    record_parser = subparsers.add_parser('record', help='手动记录使用')
    record_parser.add_argument('--project', '-p', required=True, help='项目名称')
    record_parser.add_argument('--model', '-m', required=True, help='模型名称')
    record_parser.add_argument('--input', '-i', type=int, required=True, help='输入Token数')
    record_parser.add_argument('--output', '-o', type=int, required=True, help='输出Token数')
    record_parser.add_argument('--cost', '-c', type=float, required=True, help='成本(USD)')
    record_parser.add_argument('--user', '-u', help='用户')
    
    args = parser.parse_args()
    
    if args.command == 'monitor':
        cmd_monitor(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'check':
        cmd_check(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'alert':
        cmd_alert(args)
    elif args.command == 'record':
        cmd_record(args)
    else:
        parser.print_help()
        print("\n💡 Token经济生态:")
        print("   - Token Master: Token压缩")
        print("   - Compute Market: 算力市场")
        print("   - Token Consumer Optimizer: 消费优选")
        print("   - Token Auditor: 审计监控 (本工具)")

if __name__ == '__main__':
    main()
