#!/usr/bin/env python3
"""Price Alerts System - 价格警报系统

支持价格阈值和百分比变化警报
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

ALERTS_FILE = Path(__file__).parent.parent / 'data' / 'alerts.json'


def load_alerts():
    """加载警报列表"""
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_alerts(alerts):
    """保存警报列表"""
    ALERTS_FILE.parent.mkdir(exist_ok=True)
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)


def add_alert(symbol, condition, value):
    """添加警报"""
    alerts = load_alerts()
    
    alert_id = f"{symbol}_{int(datetime.now().timestamp())}"
    
    alert = {
        'id': alert_id,
        'symbol': symbol,
        'condition': condition,  # above, below, up_percent, down_percent
        'value': float(value),
        'created_at': datetime.now().isoformat(),
        'triggered': False,
        'triggered_at': None
    }
    
    alerts.append(alert)
    save_alerts(alerts)
    
    return alert


def remove_alert(alert_id):
    """移除警报"""
    alerts = load_alerts()
    alerts = [a for a in alerts if a['id'] != alert_id]
    save_alerts(alerts)
    return True


def check_alerts():
    """检查所有警报"""
    from binance_api import get_current_price
    
    alerts = load_alerts()
    triggered = []
    still_monitoring = []
    
    for alert in alerts:
        if alert['triggered']:
            still_monitoring.append(alert)
            continue
        
        symbol = alert['symbol']
        condition = alert['condition']
        target_value = alert['value']
        
        current_price = get_current_price(symbol)
        if not current_price:
            still_monitoring.append(alert)
            continue
        
        # 检查触发条件
        should_trigger = False
        
        if condition == 'above':
            should_trigger = current_price > target_value
        elif condition == 'below':
            should_trigger = current_price < target_value
        elif condition == 'up_percent':
            # 需要基准价格，这里简化为检查绝对值
            should_trigger = False  # 需要更多数据
        elif condition == 'down_percent':
            should_trigger = False  # 需要更多数据
        
        if should_trigger:
            alert['triggered'] = True
            alert['triggered_at'] = datetime.now().isoformat()
            alert['triggered_price'] = current_price
            triggered.append(alert)
    
    # 保存更新后的状态
    save_alerts(alerts)
    
    return {
        'triggered': triggered,
        'monitoring': still_monitoring
    }


def format_alert_table(alerts):
    """格式化警报表格"""
    if not alerts:
        return "📭 暂无警报"
    
    header = "🔔 **价格警报**\n\n"
    header += "| ID | 交易对 | 条件 | 目标值 | 状态 |\n"
    header += "|----|---------|------|--------|------|\n"
    
    rows = []
    for alert in alerts:
        status = "✅ 已触发" if alert['triggered'] else "⏳ 监控中"
        status_icon = "✅" if alert['triggered'] else "⏳"
        
        if alert['condition'] == 'above':
            condition_text = f"> ${alert['value']:,.2f}"
        elif alert['condition'] == 'below':
            condition_text = f"< ${alert['value']:,.2f}"
        elif alert['condition'] == 'up_percent':
            condition_text = f"↑ {alert['value']}%"
        else:
            condition_text = f"↓ {alert['value']}%"
        
        rows.append(f"| {alert['id'][-12:]} | {alert['symbol']} | {condition_text} | {status_icon} |")
    
    return header + "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description='Price Alerts System')
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')
    
    # 添加警报
    add_parser = subparsers.add_parser('add', help='Add an alert')
    add_parser.add_argument('symbol', help='Trading pair (e.g., BTCUSDT)')
    add_parser.add_argument('condition', choices=['above', 'below', 'up_percent', 'down_percent'], help='Condition')
    add_parser.add_argument('value', type=float, help='Target value')
    
    # 列出警报
    subparsers.add_parser('list', help='List all alerts')
    
    # 检查警报
    subparsers.add_parser('check', help='Check and trigger alerts')
    
    # 移除警报
    remove_parser = subparsers.add_parser('remove', help='Remove an alert')
    remove_parser.add_argument('alert_id', help='Alert ID to remove')
    
    args = parser.parse_args()
    
    if args.action == 'add':
        alert = add_alert(args.symbol.upper(), args.condition, args.value)
        print(f"[OK] 警报已添加: {alert['id']}")
        print(json.dumps(alert, indent=2, ensure_ascii=False))
    
    elif args.action == 'list':
        alerts = load_alerts()
        print(format_alert_table(alerts))
        print(f"\n共 {len(alerts)} 个警报")
    
    elif args.action == 'check':
        result = check_alerts()
        if result['triggered']:
            print("🚨 **触发的警报:**")
            for alert in result['triggered']:
                print(f"  🚀 {alert['symbol']}: ${alert.get('triggered_price', 'N/A')} (条件: {alert['condition']} {alert['value']})")
        
        if result['monitoring']:
            print(f"\n⏳ 监控中: {len(result['monitoring'])} 个警报")
    
    elif args.action == 'remove':
        remove_alert(args.alert_id)
        print(f"[OK] 警报已移除: {args.alert_id}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
