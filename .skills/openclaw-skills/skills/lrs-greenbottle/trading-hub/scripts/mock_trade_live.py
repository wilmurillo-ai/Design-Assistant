#!/usr/bin/env python3
"""模拟交易系统 - 实时价格版

与真实Binance价格联动，模拟交易更真实
"""

import requests
import json
import time
from datetime import datetime
from mock_trade import MockTrade, print_status, MOCK_DATA_FILE

def get_btc_price() -> float:
    """获取BTC实时价格"""
    try:
        resp = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
        return float(resp.json()['price'])
    except:
        return 70000.0

def get_eth_price() -> float:
    """获取ETH实时价格"""
    try:
        resp = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT', timeout=10)
        return float(resp.json()['price'])
    except:
        return 2500.0

# 预定义交易对
PRICES = {
    'BTCUSDT': get_btc_price,
    'ETHUSDT': get_eth_price,
}

def get_price(symbol: str) -> float:
    """获取交易对价格"""
    if symbol in PRICES:
        return PRICES[symbol]()
    return 100.0

# ========== 交互式菜单 ==========
def main():
    print("""
🫙 模拟交易系统 v1.0
==================
模式: 现货 | 资金: $10,000
""")
    
    trade = MockTrade(initial_balance=10000, mode='spot')
    
    while True:
        btc_price = get_price('BTCUSDT')
        status = trade.wallet.get_status()
        
        print(f"""
当前BTC价格: ${btc_price:,.2f}
可用余额: ${status['balance']:.2f}
总资产: ${status['total_assets']:.2f}
""")
        
        if status['positions']:
            for symbol, pos in status['positions'].items():
                current = get_price(symbol)
                profit = pos['qty'] * (current - pos['avg_price'])
                profit_pct = (current - pos['avg_price']) / pos['avg_price'] * 100
                print(f"持仓: {pos['qty']:.6f} {symbol} @ ${pos['avg_price']:.2f} | 现在${current:.2f} | 浮盈${profit:.2f} ({profit_pct:+.2f}%)")
        
        print("""
操作选项:
1. 买入BTC
2. 卖出BTC
3. 查看持仓
4. 交易历史
5. 盈亏统计
6. 重置账户
0. 退出
""")
        
        choice = input("选择: ").strip()
        
        if choice == '1':
            amount = float(input("买入金额(USDT): "))
            price = get_price('BTCUSDT')
            result = trade.buy_market('BTCUSDT', amount, price)
            if result['success']:
                print(f"\n✅ 买入成功!")
                print(f"数量: {result['order']['qty']:.8f} BTC")
                print(f"均价: ${result['order']['price']:,.2f}")
            else:
                print(f"\n❌ {result['error']}")
        
        elif choice == '2':
            qty = float(input("卖出数量(BTC): "))
            price = get_price('BTCUSDT')
            result = trade.sell_market('BTCUSDT', qty=qty, current_price=price)
            if result['success']:
                print(f"\n✅ 卖出成功!")
                print(f"数量: {result['order']['qty']:.8f} BTC")
                print(f"价格: ${result['order']['price']:,.2f}")
                print(f"盈亏: ${result['order']['profit']:.2f} ({result['order']['profit_pct']:+.2f}%)")
            else:
                print(f"\n❌ {result['error']}")
        
        elif choice == '3':
            print_status(trade)
        
        elif choice == '4':
            history = trade.get_history(10)
            print("\n=== 最近交易 ===")
            for o in history:
                pnl = f" 盈亏:${o.get('profit', 0):.2f}" if o['side'] == 'SELL' else ''
                print(f"{o['time'][:19]} {o['side']} {o['qty']:.6f} @ ${o['price']:,.2f}{pnl}")
        
        elif choice == '5':
            summary = trade.get_profit_summary()
            print(f"""
=== 盈亏统计 ===
总交易: {summary['total_trades']}次
盈利: {summary['winning_trades']} | 亏损: {summary['losing_trades']}
总盈亏: ${summary['total_profit']:.2f}
胜率: {summary['win_rate']:.1f}%
""")
        
        elif choice == '6':
            confirm = input("确认重置? (y/n): ")
            if confirm.lower() == 'y':
                trade.wallet.reset(10000)
                print("✅ 已重置")
        
        elif choice == '0':
            print("Bye~ 🫙")
            break
        
        input("\n按回车继续...")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # 命令行模式
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('action', choices=['buy', 'sell', 'status', 'history'])
        parser.add_argument('--amount', type=float)
        parser.add_argument('--qty', type=float)
        parser.add_argument('--price', type=float)
        args = parser.parse_args()
        
        trade = MockTrade(mode='spot')
        btc_price = get_price('BTCUSDT')
        
        if args.action == 'buy':
            amount = args.amount or float(input("买入金额: "))
            result = trade.buy_market('BTCUSDT', amount, btc_price)
            if result['success']:
                print(f"✅ 买入 {result['order']['qty']:.8f} BTC @ ${btc_price:,.2f}")
            else:
                print(f"❌ {result['error']}")
        elif args.action == 'sell':
            qty = args.qty or float(input("卖出数量: "))
            result = trade.sell_market('BTCUSDT', qty=qty, current_price=btc_price)
            if result['success']:
                print(f"✅ 卖出 {result['order']['qty']:.8f} BTC @ ${btc_price:,.2f}, 盈亏: ${result['order']['profit']:.2f}")
            else:
                print(f"❌ {result['error']}")
        elif args.action == 'status':
            print_status(trade)
        elif args.action == 'history':
            for o in trade.get_history():
                print(f"{o['time'][:19]} {o['side']} {o['qty']:.6f} @ ${o['price']:,.2f}")
    else:
        main()
