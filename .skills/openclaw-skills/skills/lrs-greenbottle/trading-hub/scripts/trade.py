#!/usr/bin/env python3
"""统一交易接口 - Trade Hub

支持:
- mock模式: 模拟交易，无真实资金
- real模式: 真实交易

用法:
  python3 trade.py status [--mode mock|real]
  python3 trade.py buy BTC 1000 [--mode mock]
  python3 trade.py sell BTC 0.01 [--mode mock]
  python3 trade.py reset [--mode mock]
"""

import sys
import os

# 添加scripts路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mock_trade import MockTrade
import requests

# ============ 配置 ============
MODE_FILE = os.path.join(os.path.dirname(__file__), 'trade_mode.json')

def get_current_mode():
    """获取当前模式"""
    if os.path.exists(MODE_FILE):
        with open(MODE_FILE, 'r') as f:
            return json.load(f).get('mode', 'mock')
    return 'mock'

def set_mode(mode: str):
    """设置交易模式"""
    with open(MODE_FILE, 'w') as f:
        json.dump({'mode': mode}, f)
    print(f"✅ 已切换到 {mode.upper()} 模式")

def get_btc_price() -> float:
    """获取BTC实时价格"""
    try:
        resp = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
        return float(resp.json()['price'])
    except:
        return 70000.0

# ============ 命令 ============
def cmd_status(mode: str):
    """显示状态"""
    if mode == 'real':
        from binance_api import get_balance, get_position
        btc = get_balance('BTC')
        usdt = get_balance('USDT')
        btc_price = get_btc_price()
        
        print(f"""
=== 真实账户状态 ===
USDT余额: ${usdt['available']:.2f}
BTC数量: {btc['balance']:.8f}
BTC价值: ${btc['balance'] * btc_price:.2f}
BTC现价: ${btc_price:,.2f}
""")
    else:
        trade = MockTrade(mode='spot')
        status = trade.wallet.get_status()
        btc_price = get_btc_price()
        
        print(f"""
=== 模拟账户状态 (Mock) ===
可用余额: ${status['balance']:.2f}
持仓价值: ${status['positions_value']:.2f}
总资产: ${status['total_assets']:.2f}
BTC现价: ${btc_price:,.2f}
""")
        
        if status['positions']:
            for symbol, pos in status['positions'].items():
                current = get_btc_price() if symbol == 'BTCUSDT' else pos['avg_price']
                profit = pos['qty'] * (current - pos['avg_price'])
                profit_pct = (current - pos['avg_price']) / pos['avg_price'] * 100
                print(f"持仓: {pos['qty']:.6f} {symbol} @ ${pos['avg_price']:.2f} | 浮盈${profit:.2f} ({profit_pct:+.2f}%)")

def cmd_buy(symbol: str, amount: float, mode: str):
    """买入"""
    btc_price = get_btc_price()
    
    if mode == 'real':
        print("⚠️ 真实交易模式待实现，请稍候...")
        # TODO: 实现真实买入
    else:
        trade = MockTrade(mode='spot')
        result = trade.buy_market(symbol, amount, btc_price)
        if result['success']:
            print(f"✅ 模拟买入成功!")
            print(f"数量: {result['order']['qty']:.8f} BTC")
            print(f"价格: ${btc_price:,.2f}")
            print(f"金额: ${result['order']['amount']:.2f}")
            print(f"剩余余额: ${result['remaining_balance']:.2f}")
        else:
            print(f"❌ {result['error']}")

def cmd_sell(symbol: str, qty: float, mode: str):
    """卖出"""
    btc_price = get_btc_price()
    
    if mode == 'real':
        print("⚠️ 真实交易模式待实现，请稍候...")
        # TODO: 实现真实卖出
    else:
        trade = MockTrade(mode='spot')
        result = trade.sell_market(symbol, qty=qty, current_price=btc_price)
        if result['success']:
            print(f"✅ 模拟卖出成功!")
            print(f"数量: {result['order']['qty']:.8f} BTC")
            print(f"价格: ${btc_price:,.2f}")
            print(f"金额: ${result['order']['amount']:.2f}")
            print(f"盈亏: ${result['order']['profit']:.2f} ({result['order']['profit_pct']:+.2f}%)")
            print(f"剩余余额: ${result['remaining_balance']:.2f}")
        else:
            print(f"❌ {result['error']}")

def cmd_reset(mode: str):
    """重置"""
    if mode == 'real':
        print("⚠️ 真实账户无法重置!")
    else:
        trade = MockTrade(mode='spot')
        trade.wallet.reset(1000)
        print("✅ 模拟账户已重置 (余额: $1,000)")

def cmd_mode(args_mode: str = None):
    """切换/查看模式"""
    if args_mode:
        set_mode(args_mode)
    else:
        current = get_current_mode()
        print(f"当前模式: {current.upper()}")

def cmd_history(mode: str, limit: int = 10):
    """交易历史"""
    if mode == 'real':
        # TODO: 从真实账户获取
        pass
    else:
        trade = MockTrade(mode='spot')
        history = trade.get_history(limit)
        if history:
            print(f"\n=== 最近{len(history)}笔交易 ===")
            for o in history:
                pnl = f" | 盈亏:${o.get('profit', 0):.2f}" if o['side'] == 'SELL' else ''
                print(f"{o['time'][:19]} {o['side']} {o['qty']:.6f} @ ${o['price']:,.2f}{pnl}")
        else:
            print("暂无交易记录")

def cmd_profit(mode: str):
    """盈亏统计"""
    if mode == 'real':
        # TODO: 从真实账户计算
        pass
    else:
        trade = MockTrade(mode='spot')
        summary = trade.get_profit_summary()
        print(f"""
=== 盈亏统计 ===
总交易: {summary['total_trades']}次
买入: {summary['buy_count']} | 卖出: {summary['sell_count']}
盈利: {summary['winning_trades']} | 亏损: {summary['losing_trades']}
总盈亏: ${summary['total_profit']:.2f}
胜率: {summary['win_rate']:.1f}%
""")

# ============ 主程序 ============
if __name__ == '__main__':
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Trade Hub - 统一交易接口')
    parser.add_argument('action', choices=['status', 'buy', 'sell', 'reset', 'mode', 'history', 'profit', 'help'], help='操作')
    parser.add_argument('symbol', nargs='?', default='BTCUSDT', help='交易对')
    parser.add_argument('amount', nargs='?', type=float, help='金额/数量')
    parser.add_argument('--mode', '-m', choices=['mock', 'real'], help='交易模式')
    parser.add_argument('--limit', '-n', type=int, default=10, help='历史记录数量')
    
    args = parser.parse_args()
    
    # 确定模式
    mode = args.mode or get_current_mode()
    
    if args.action == 'status':
        cmd_status(mode)
    elif args.action == 'buy':
        if not args.amount:
            print("错误: 需要金额参数")
            print("用法: python3 trade.py buy BTC 1000")
        else:
            cmd_buy(args.symbol, args.amount, mode)
    elif args.action == 'sell':
        if not args.amount:
            print("错误: 需要数量参数")
            print("用法: python3 trade.py sell BTC 0.01")
        else:
            cmd_sell(args.symbol, args.amount, mode)
    elif args.action == 'reset':
        cmd_reset(mode)
    elif args.action == 'mode':
        cmd_mode(args.mode)
    elif args.action == 'history':
        cmd_history(mode, args.limit)
    elif args.action == 'profit':
        cmd_profit(mode)
    elif args.action == 'help':
        print("""
🫙 Trade Hub 帮助
================

模式切换:
  python3 trade.py mode mock    # 切换到模拟模式
  python3 trade.py mode real    # 切换到真实模式

交易操作:
  python3 trade.py status       # 查看账户状态
  python3 trade.py buy BTC 1000 # 买入1000U的BTC
  python3 trade.py sell BTC 0.01 # 卖出0.01个BTC
  python3 trade.py history       # 查看交易历史
  python3 trade.py profit        # 查看盈亏统计
  python3 trade.py reset         # 重置模拟账户

示例:
  # 模拟交易
  python3 trade.py mode mock
  python3 trade.py buy BTC 1000
  python3 trade.py status
  
  # 真实交易(待实现)
  python3 trade.py mode real
  python3 trade.py buy BTC 100
""")