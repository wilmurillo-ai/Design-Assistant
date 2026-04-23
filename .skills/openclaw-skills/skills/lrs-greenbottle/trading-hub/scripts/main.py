#!/usr/bin/env python3
"""Trading Hub Main Entry - 交易助手主入口

整合所有交易功能
"""

import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, __file__.rsplit('/', 3)[0])

from binance_api import get_balance, get_position, get_current_price, get_all_positions
from btc_analyzer import main as analyze_btc
from btc_monitor import main as monitor_btc
from astock import get_position_suggestion, check_ice_point
from sentiment import analyze_sentiment, format_sentiment_report
from alerts import load_alerts, check_alerts
from position_manager import get_total_exposure, calculate_position_suggestion


def cmd_status():
    """状态总览"""
    print("[状态] 获取交易状态...")
    
    # 获取所有持仓
    all_positions = get_all_positions()
    balance = get_balance()
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'paper' if __import__('os').getenv('CRYPTO_DEMO', 'true').lower() == 'true' else 'live',
        'balance': balance,
        'positions': all_positions,
        'total_positions': len(all_positions)
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 格式化输出
    print("\n📊 **交易状态**")
    print(f"⏰ 更新时间: {result['timestamp']}")
    print(f"🔧 模式: {'📝 模拟交易' if result['mode'] == 'paper' else '💰 实盘交易'}")
    
    if balance:
        print(f"💰 余额: ${balance.get('available', 0):.2f} USDT")
    
    if all_positions:
        print(f"\n📂 持仓数量: {len(all_positions)}")
        for pos in all_positions:
            direction = "多" if float(pos.get('positionAmt', 0)) > 0 else "空"
            print(f"  • {pos['symbol']}: {direction} {abs(float(pos.get('positionAmt', 0)))}")
    else:
        print("\n📭 无持仓")


def cmd_balance():
    """查询余额"""
    balance = get_balance()
    if balance:
        print(json.dumps(balance, indent=2, ensure_ascii=False))
        print(f"\n💰 {balance['asset']} 余额: ${balance['balance']}")
        print(f"📝 可用: ${balance['available']}")
    else:
        print("[ERROR] 无法获取余额")


def cmd_position(symbol='BTCUSDT'):
    """查询持仓"""
    position = get_position(symbol)
    if position:
        print(json.dumps(position, indent=2, ensure_ascii=False))
        current = get_current_price(symbol)
        if current:
            entry = float(position.get('entryPrice', 1))
            amt = abs(float(position.get('positionAmt', 1)))
            pnl = float(position.get('unRealizedProfit', 0))
            pnl_pct = (pnl / (entry * amt)) * 100 if entry * amt > 0 else 0
            print(f"\n📊 {symbol} 持仓")
            print(f"  方向: {'多' if float(position.get('positionAmt', 0)) > 0 else '空'}")
            print(f"  数量: {abs(float(position.get('positionAmt', 0)))}")
            print(f"  均价: ${float(position.get('entryPrice', 0))}")
            print(f"  当前: ${current}")
            print(f"  PnL: ${float(position.get('unRealizedProfit', 0)):.2f} ({pnl_pct:.2f}%)")
    else:
        print(f"[INFO] {symbol} 无持仓")


def cmd_analyze(symbol='BTCUSDT'):
    """技术分析"""
    print(f"[分析] {symbol} 技术分析...")
    # 调用 BTC analyzer
    import btc_analyzer
    sys.argv = ['btc_analyzer.py']
    btc_analyzer.main()


def cmd_sentiment(symbol='BTC'):
    """情绪分析"""
    print(f"[情绪] {symbol} 市场情绪分析...")
    result = analyze_sentiment(symbol)
    print(format_sentiment_report(result))


def cmd_ice():
    """冰点检查"""
    print("[冰点] 检查市场冰点状态...")
    result = check_ice_point()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result['is_super_ice']:
        print(f"\n🚨 **极度冰点！** 涨停仅 {result['zt_count']} 家")
    elif result['is_ice']:
        print(f"\n🔴 **市场冰点** 涨停 {result['zt_count']} 家，建议仓位 ≤15%")
    else:
        print(f"\n🟡 市场未冰点（涨停 {result['zt_count']} 家）")


def cmd_position_suggestion():
    """仓位建议"""
    print("[仓位] 计算仓位建议...")
    exposure = get_total_exposure()
    suggestion = calculate_position_suggestion(exposure)
    print(json.dumps(suggestion, indent=2, ensure_ascii=False))
    
    status_emoji = {
        "强势": "🟢", "偏强": "🟢", "震荡": "🟡",
        "偏弱": "🟠", "冰点": "🔴"
    }.get(suggestion['market_status'], "⚪")
    
    print(f"\n{status_emoji} 市场状态: {suggestion['market_status']}")
    print(f"💼 建议仓位: {int(suggestion['market_ratio']*100)}%")


def cmd_alerts():
    """查看警报"""
    alerts = load_alerts()
    print(f"\n🔔 **价格警报** ({len(alerts)} 个)")
    
    if not alerts:
        print("📭 暂无警报")
        return
    
    for alert in alerts:
        status = "✅" if alert['triggered'] else "⏳"
        if alert['condition'] == 'above':
            cond = f"> ${alert['value']:,.2f}"
        elif alert['condition'] == 'below':
            cond = f"< ${alert['value']:,.2f}"
        else:
            cond = f"{alert['condition']} {alert['value']}%"
        
        print(f"  {status} {alert['symbol']}: {cond}")


def cmd_check_alerts():
    """检查警报触发"""
    print("[警报] 检查所有警报...")
    result = check_alerts()
    
    if result['triggered']:
        print("\n🚨 **触发的警报:**")
        for alert in result['triggered']:
            print(f"  🚀 {alert['symbol']}: ${alert.get('triggered_price', 'N/A')} 触发 {alert['condition']}")
    
    print(f"\n⏳ 监控中: {len(result['monitoring'])} 个")


def cmd_exposure():
    """风险敞口"""
    exposure = get_total_exposure()
    print(json.dumps(exposure, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description='Trading Hub - 统一交易助手')
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # 状态
    status_parser = subparsers.add_parser('status', help='Portfolio and strategy overview')
    
    # 余额
    balance_parser = subparsers.add_parser('balance', help='Check exchange balances')
    balance_parser.add_argument('--exchange', '-e', default='binance', help='Exchange name')
    
    # 持仓
    position_parser = subparsers.add_parser('position', help='Check position')
    position_parser.add_argument('symbol', nargs='?', default='BTCUSDT', help='Trading pair')
    
    # 分析
    analyze_parser = subparsers.add_parser('analyze', help='Technical analysis')
    analyze_parser.add_argument('symbol', nargs='?', default='BTCUSDT', help='Trading pair')
    
    # 情绪
    sentiment_parser = subparsers.add_parser('sentiment', help='Market sentiment analysis')
    sentiment_parser.add_argument('--symbol', '-s', default='BTC', help='Symbol to analyze')
    
    # 冰点
    subparsers.add_parser('ice', help='Check market ice point')
    
    # 仓位建议
    subparsers.add_parser('suggestion', help='Position suggestion')
    
    # 警报
    alerts_parser = subparsers.add_parser('alerts', help='View price alerts')
    check_parser = subparsers.add_parser('check', help='Check alert triggers')
    
    # 敞口
    subparsers.add_parser('exposure', help='Risk exposure')
    
    args = parser.parse_args()
    
    if args.mode == 'status':
        cmd_status()
    elif args.mode == 'balance':
        cmd_balance()
    elif args.mode == 'position':
        cmd_position(args.symbol)
    elif args.mode == 'analyze':
        cmd_analyze(args.symbol)
    elif args.mode == 'sentiment':
        cmd_sentiment(args.symbol)
    elif args.mode == 'ice':
        cmd_ice()
    elif args.mode == 'suggestion':
        cmd_position_suggestion()
    elif args.mode == 'alerts':
        cmd_alerts()
    elif args.mode == 'check':
        cmd_check_alerts()
    elif args.mode == 'exposure':
        cmd_exposure()
    else:
        # 默认显示状态
        cmd_status()


if __name__ == "__main__":
    main()
