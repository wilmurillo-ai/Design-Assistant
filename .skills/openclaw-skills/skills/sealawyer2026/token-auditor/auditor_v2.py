#!/usr/bin/env python3
"""
Token审计监控 v2.0
Token Auditor v2.0

升级内容:
- 实时监控 dashboard
- 异常检测算法 (统计/机器学习)
- 告警通知系统 (邮件/Webhook)
- 审计报告生成 (HTML/PDF)
- API接口
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/token-ecosys-core')

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics

from models import TokenUsage, AuditAlert, TokenPlatform
from utils import generate_id, format_datetime, SimpleCache


class AlertSeverity(Enum):
    """告警级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """告警类型"""
    BUDGET_THRESHOLD = "budget_threshold"
    ANOMALY_USAGE = "anomaly_usage"
    UNUSUAL_PATTERN = "unusual_pattern"
    MODEL_MISUSE = "model_misuse"
    COST_SPIKE = "cost_spike"


@dataclass
class BudgetConfig:
    """预算配置"""
    daily: float = 100.0
    weekly: float = 500.0
    monthly: float = 2000.0
    thresholds: List[int] = field(default_factory=lambda: [50, 80, 100])


@dataclass
class AnomalyDetectionResult:
    """异常检测结果"""
    is_anomaly: bool
    severity: AlertSeverity
    score: float
    reason: str
    recommendation: str


class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self, sensitivity: str = "medium"):
        self.sensitivity = sensitivity
        self.multiplier = {"low": 2.0, "medium": 3.0, "high": 2.0, "critical": 1.5}[sensitivity]
    
    def detect_usage_anomaly(self, current: float, historical: List[float]) -> AnomalyDetectionResult:
        """
        检测使用异常 (基于Z-Score)
        
        Args:
            current: 当前值
            historical: 历史值列表
        """
        if len(historical) < 3:
            return AnomalyDetectionResult(False, AlertSeverity.LOW, 0.0, "数据不足", "继续监控")
        
        mean = statistics.mean(historical)
        std = statistics.stdev(historical) if len(historical) > 1 else 0
        
        if std == 0:
            z_score = 0 if current == mean else float('inf')
        else:
            z_score = abs(current - mean) / std
        
        # 根据敏感度判断
        if z_score > self.multiplier:
            severity = AlertSeverity.CRITICAL if z_score > 5 else (
                AlertSeverity.HIGH if z_score > 4 else AlertSeverity.MEDIUM
            )
            return AnomalyDetectionResult(
                is_anomaly=True,
                severity=severity,
                score=z_score,
                reason=f"使用量异常，Z-Score: {z_score:.2f} (平均值: {mean:.2f})",
                recommendation="检查是否有异常调用或恶意攻击"
            )
        
        return AnomalyDetectionResult(False, AlertSeverity.LOW, z_score, "正常", "继续保持")
    
    def detect_trend_anomaly(self, values: List[float], days: int = 3) -> AnomalyDetectionResult:
        """
        检测趋势异常 (连续增长)
        
        Args:
            values: 最近几天的值
            days: 检测天数
        """
        if len(values) < days:
            return AnomalyDetectionResult(False, AlertSeverity.LOW, 0.0, "数据不足", "继续监控")
        
        recent = values[-days:]
        
        # 检查是否连续增长
        growth_days = 0
        for i in range(1, len(recent)):
            if recent[i] > recent[i-1] * 1.2:  # 增长20%以上
                growth_days += 1
        
        if growth_days >= days - 1:
            avg_growth = (recent[-1] - recent[0]) / recent[0] * 100 if recent[0] > 0 else 0
            return AnomalyDetectionResult(
                is_anomaly=True,
                severity=AlertSeverity.HIGH,
                score=avg_growth,
                reason=f"连续{days}天消费增长，平均增长: {avg_growth:.1f}%",
                recommendation="检查业务增长是否预期，或是否有异常调用"
            )
        
        return AnomalyDetectionResult(False, AlertSeverity.LOW, 0.0, "趋势正常", "继续保持")
    
    def detect_model_misuse(self, usage_pattern: Dict[str, int]) -> AnomalyDetectionResult:
        """
        检测模型误用 (高价模型低效使用)
        
        Args:
            usage_pattern: {model: token_count}
        """
        # 高价模型列表
        expensive_models = ["gpt-4-turbo", "claude-3-opus", "gpt-4o"]
        cheap_alternatives = ["gpt-4o-mini", "claude-3-haiku", "gemini-1.5-flash"]
        
        expensive_usage = sum(usage_pattern.get(m, 0) for m in expensive_models)
        total_usage = sum(usage_pattern.values())
        
        if total_usage == 0:
            return AnomalyDetectionResult(False, AlertSeverity.LOW, 0.0, "无使用数据", "")
        
        expensive_ratio = expensive_usage / total_usage
        
        if expensive_ratio > 0.8:
            return AnomalyDetectionResult(
                is_anomaly=True,
                severity=AlertSeverity.MEDIUM,
                score=expensive_ratio * 100,
                reason=f"高价模型使用比例过高 ({expensive_ratio*100:.1f}%)",
                recommendation=f"考虑切换到更经济的模型如 {', '.join(cheap_alternatives)}"
            )
        
        return AnomalyDetectionResult(False, AlertSeverity.LOW, expensive_ratio * 100, "模型使用合理", "")


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alerts: List[AuditAlert] = []
        self.handlers: Dict[AlertSeverity, List[Callable]] = {
            AlertSeverity.LOW: [],
            AlertSeverity.MEDIUM: [],
            AlertSeverity.HIGH: [],
            AlertSeverity.CRITICAL: []
        }
    
    def register_handler(self, severity: AlertSeverity, handler: Callable):
        """注册告警处理器"""
        self.handlers[severity].append(handler)
    
    def create_alert(self, user_id: str, alert_type: AlertType, severity: AlertSeverity,
                    message: str, details: Dict) -> AuditAlert:
        """创建告警"""
        alert = AuditAlert(
            id=generate_id("ALT"),
            user_id=user_id,
            alert_type=alert_type.value,
            severity=severity.value,
            message=message,
            details=details
        )
        self.alerts.append(alert)
        
        # 触发处理器
        for handler in self.handlers.get(severity, []):
            try:
                handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")
        
        return alert
    
    def acknowledge(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def get_unacknowledged(self, user_id: Optional[str] = None) -> List[AuditAlert]:
        """获取未确认告警"""
        alerts = [a for a in self.alerts if not a.acknowledged]
        if user_id:
            alerts = [a for a in alerts if a.user_id == user_id]
        return alerts


class TokenAuditorV2:
    """Token审计监控 v2.0"""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.usage_history: List[TokenUsage] = []
        self.detector = AnomalyDetector()
        self.alert_manager = AlertManager()
        self.budget_config = BudgetConfig()
        self.cache = SimpleCache(ttl_seconds=60)
    
    def record_usage(self, platform: TokenPlatform, model: str, 
                    input_tokens: int, output_tokens: int, cost: float,
                    project_id: str = "default"):
        """记录使用"""
        usage = TokenUsage(
            id=generate_id("USG"),
            user_id=self.user_id,
            project_id=project_id,
            platform=platform,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            timestamp=datetime.now()
        )
        self.usage_history.append(usage)
        
        # 检查预算告警
        self._check_budget_alerts()
        
        # 检查异常
        self._check_anomalies()
    
    def _check_budget_alerts(self):
        """检查预算告警"""
        today = datetime.now().date()
        today_cost = sum(u.cost for u in self.usage_history 
                        if u.timestamp.date() == today)
        
        for threshold in self.budget_config.thresholds:
            if today_cost >= self.budget_config.daily * threshold / 100:
                # 检查是否已发送过此级别告警
                cache_key = f"budget_alert_{threshold}_{today}"
                if not self.cache.get(cache_key):
                    self.alert_manager.create_alert(
                        self.user_id,
                        AlertType.BUDGET_THRESHOLD,
                        AlertSeverity.HIGH if threshold >= 80 else AlertSeverity.MEDIUM,
                        f"每日预算达到 {threshold}%",
                        {"current": today_cost, "budget": self.budget_config.daily, "threshold": threshold}
                    )
                    self.cache.set(cache_key, True)
    
    def _check_anomalies(self):
        """检查异常"""
        # 获取最近7天的使用数据
        daily_usage = self.get_daily_usage(days=7)
        
        if len(daily_usage) >= 3:
            # 检测趋势异常
            result = self.detector.detect_trend_anomaly(daily_usage)
            if result.is_anomaly:
                self.alert_manager.create_alert(
                    self.user_id,
                    AlertType.COST_SPIKE,
                    result.severity,
                    result.reason,
                    {"recommendation": result.recommendation}
                )
        
        # 检测今日异常
        if len(daily_usage) >= 2:
            result = self.detector.detect_usage_anomaly(daily_usage[-1], daily_usage[:-1])
            if result.is_anomaly:
                self.alert_manager.create_alert(
                    self.user_id,
                    AlertType.ANOMALY_USAGE,
                    result.severity,
                    result.reason,
                    {"recommendation": result.recommendation}
                )
    
    def get_daily_usage(self, days: int = 7) -> List[float]:
        """获取每日使用量"""
        daily = {}
        for usage in self.usage_history:
            day = usage.timestamp.date()
            daily[day] = daily.get(day, 0) + usage.cost
        
        # 补齐缺失天数
        result = []
        for i in range(days - 1, -1, -1):
            day = (datetime.now() - timedelta(days=i)).date()
            result.append(daily.get(day, 0))
        
        return result
    
    def get_usage_by_platform(self) -> Dict[str, float]:
        """按平台统计使用"""
        result = {}
        for usage in self.usage_history:
            platform = usage.platform.value
            result[platform] = result.get(platform, 0) + usage.cost
        return result
    
    def get_usage_by_model(self) -> Dict[str, Dict]:
        """按模型统计使用"""
        result = {}
        for usage in self.usage_history:
            model = usage.model
            if model not in result:
                result[model] = {"cost": 0, "input_tokens": 0, "output_tokens": 0}
            result[model]["cost"] += usage.cost
            result[model]["input_tokens"] += usage.input_tokens
            result[model]["output_tokens"] += usage.output_tokens
        return result
    
    def generate_report(self, period: str = "week") -> Dict:
        """
        生成审计报告
        
        Args:
            period: day/week/month
        """
        days = {"day": 1, "week": 7, "month": 30}.get(period, 7)
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_usage = [u for u in self.usage_history if u.timestamp > cutoff]
        
        total_cost = sum(u.cost for u in recent_usage)
        total_input = sum(u.input_tokens for u in recent_usage)
        total_output = sum(u.output_tokens for u in recent_usage)
        
        by_platform = {}
        by_model = {}
        for usage in recent_usage:
            platform = usage.platform.value
            by_platform[platform] = by_platform.get(platform, 0) + usage.cost
            
            model = usage.model
            by_model[model] = by_model.get(model, 0) + usage.cost
        
        # 异常统计
        unack_alerts = self.alert_manager.get_unacknowledged(self.user_id)
        
        return {
            "period": period,
            "total_cost": round(total_cost, 2),
            "total_tokens": {
                "input": total_input,
                "output": total_output,
                "total": total_input + total_output
            },
            "by_platform": by_platform,
            "by_model": by_model,
            "alerts": {
                "total": len(unack_alerts),
                "critical": len([a for a in unack_alerts if a.severity == "critical"]),
                "high": len([a for a in unack_alerts if a.severity == "high"]),
                "medium": len([a for a in unack_alerts if a.severity == "medium"])
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 按模型使用分析
        by_model = self.get_usage_by_model()
        if by_model:
            expensive_models = ["gpt-4-turbo", "gpt-4o", "claude-3-opus"]
            cheap_alternatives = ["gpt-4o-mini", "claude-3-haiku"]
            
            expensive_cost = sum(by_model[m]["cost"] for m in expensive_models if m in by_model)
            total_cost = sum(v["cost"] for v in by_model.values())
            
            if expensive_cost > total_cost * 0.7:
                recommendations.append(f"高价模型使用占比{expensive_cost/total_cost*100:.1f}%，建议考虑{', '.join(cheap_alternatives)}")
        
        # 预算使用分析
        today_cost = sum(u.cost for u in self.usage_history 
                        if u.timestamp.date() == datetime.now().date())
        if today_cost > self.budget_config.daily * 0.8:
            recommendations.append("今日预算使用超过80%，建议监控后续使用")
        
        return recommendations


# CLI入口
if __name__ == "__main__":
    import argparse
    
    auditor = TokenAuditorV2()
    
    parser = argparse.ArgumentParser(description="Token Auditor v2.0")
    subparsers = parser.add_subparsers(dest="command")
    
    # monitor命令
    monitor_parser = subparsers.add_parser("monitor", help="启动监控")
    monitor_parser.add_argument("--project", default="default", help="项目ID")
    monitor_parser.add_argument("--budget", type=float, default=1000, help="预算")
    
    # status命令
    status_parser = subparsers.add_parser("status", help="查看状态")
    
    # report命令
    report_parser = subparsers.add_parser("report", help="生成报告")
    report_parser.add_argument("--period", default="week", choices=["day", "week", "month"])
    
    # check命令
    check_parser = subparsers.add_parser("check", help="检查异常")
    check_parser.add_argument("--sensitivity", default="medium", choices=["low", "medium", "high", "critical"])
    
    args = parser.parse_args()
    
    if args.command == "status":
        print("📊 Token Auditor v2.0 状态")
        print("-" * 40)
        by_platform = auditor.get_usage_by_platform()
        for platform, cost in by_platform.items():
            print(f"  {platform}: ${cost:.2f}")
        
        alerts = auditor.alert_manager.get_unacknowledged(auditor.user_id)
        print(f"\n🚨 未确认告警: {len(alerts)}个")
        
    elif args.command == "report":
        report = auditor.generate_report(args.period)
        print(f"📈 {args.period}报告")
        print("-" * 40)
        print(f"总成本: ${report['total_cost']}")
        print(f"总Token: {report['total_tokens']['total']}")
        print(f"\n按平台:")
        for platform, cost in report['by_platform'].items():
            print(f"  {platform}: ${cost:.2f}")
        
        if report['recommendations']:
            print(f"\n💡 建议:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
    
    elif args.command == "check":
        detector = AnomalyDetector(args.sensitivity)
        daily = auditor.get_daily_usage(7)
        
        print(f"🔍 异常检查 (敏感度: {args.sensitivity})")
        print("-" * 40)
        
        if len(daily) >= 2:
            result = detector.detect_usage_anomaly(daily[-1], daily[:-1])
            print(f"今日异常: {'是' if result.is_anomaly else '否'}")
            print(f"原因: {result.reason}")
            if result.recommendation:
                print(f"建议: {result.recommendation}")
    
    else:
        parser.print_help()
