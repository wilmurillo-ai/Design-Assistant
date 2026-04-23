#!/usr/bin/env python3
"""Grid Trading Strategy - 网格交易策略

在价格区间内均匀布置买卖单，价格上涨卖出，下跌买入
"""

import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, __file__.rsplit('/', 3)[0])
from config import load_config, get_signature, log_trade


def calculate_grid_levels(price_low, price_high, num_grids):
    """计算网格价格 levels"""
    step = (price_high - price_low) / (num_grids + 1)
    levels = []
    for i in range(1, num_grids + 1):
        price = price_low + step * i
        # 买单价格（略低于网格线）
        buy_price = price * 0.998
        # 卖单价格（略高于网格线）
        sell_price = price * 1.002
        levels.append({
            'grid_num': i,
            'price': round(price, 2),
            'buy_price': round(buy_price, 2),
            'sell_price': round(sell_price, 2)
        })
    return levels


def simulate_grid_trading(symbol, price_low, price_high, num_grids, investment_per_grid):
    """模拟网格交易"""
    levels = calculate_grid_levels(price_low, price_high, num_grids)
    
    # 模拟交易
    trades = []
    total_invested = 0
    total_bought = 0
    total_sold = 0
    
    # 模拟价格从低价开始上涨
    price_range = price_high - price_low
    simulated_prices = [
        price_low * 0.98,  # 开盘略低
        price_low * 0.99,
        price_low,
        *[(price_low + price_range * i / num_grids) for i in range(1, num_grids + 1)],
        price_high * 1.01,
        price_high * 1.02  # 收盘略高
    ]
    
    for price in simulated_prices:
        for level in levels:
            if price <= level['buy_price'] and total_invested < investment_per_grid * num_grids * 10:
                # 买入
                qty = investment_per_grid / level['buy_price']
                trades.append({
                    'type': 'BUY',
                    'price': level['buy_price'],
                    'qty': qty,
                    'grid': level['grid_num']
                })
                total_invested += investment_per_grid
                total_bought += qty
            
            elif price >= level['sell_price'] and total_bought > 0:
                # 卖出
                qty = min(total_bought * 0.1, investment_per_grid / level['sell_price'])
                trades.append({
                    'type': 'SELL',
                    'price': level['sell_price'],
                    'qty': qty,
                    'grid': level['grid_num']
                })
                total_sold += qty
    
    # 计算收益
    final_price = simulated_prices[-1]
    remaining_bought = total_bought - total_sold
    final_value = remaining_bought * final_price
    total_profit = total_sold * final_price - (total_invested - final_value)
    
    return {
        'strategy': 'grid_trading',
        'symbol': symbol,
        'levels': levels,
        'num_grids': num_grids,
        'price_range': [price_low, price_high],
        'total_trades': len(trades),
        'total_invested': round(total_invested, 2),
        'total_bought': round(total_bought, 6),
        'total_sold': round(total_sold, 6),
        'remaining': round(remaining_bought, 6),
        'final_value': round(final_value, 2),
        'profit': round(total_profit, 2),
        'profit_pct': round((total_profit / total_invested) * 100, 2) if total_invested > 0 else 0,
        'simulated_prices': len(simulated_prices)
    }


def main():
    parser = argparse.ArgumentParser(description='Grid Trading Strategy')
    parser.add_argument('--symbol', default='BTCUSDT', help='Trading pair')
    parser.add_argument('--price-low', type=float, help='Lower price bound')
    parser.add_argument('--price-high', type=float, help='Upper price bound')
    parser.add_argument('--num-grids', type=int, default=10, help='Number of grid levels')
    parser.add_argument('--investment', type=float, default=100, help='Investment per grid in USDT')
    parser.add_argument('--simulate', action='store_true', help='Run simulation')
    
    args = parser.parse_args()
    
    if not args.price_low or not args.price_high:
        # 使用当前价格估算
        from binance_api import get_current_price
        current = get_current_price(args.symbol)
        if current:
            args.price_low = current * 0.9
            args.price_high = current * 1.1
            print(f"[INFO] Using price range: ${args.price_low:,.2f} - ${args.price_high:,.2f}")
        else:
            print("[ERROR] Cannot get current price, please specify --price-low and --price-high")
            sys.exit(1)
    
    print(f"[网格交易] {args.symbol}")
    print(f"  价格区间: ${args.price_low:,.2f} - ${args.price_high:,.2f}")
    print(f"  网格层数: {args.num_grids}")
    print(f"  每层投入: ${args.investment}")
    
    if args.simulate:
        result = simulate_grid_trading(args.symbol, args.price_low, args.price_high, args.num_grids, args.investment)
        print(f"\n[模拟结果]")
        print(f"  总交易次数: {result['total_trades']}")
        print(f"  总投入: ${result['total_invested']}")
        print(f"  盈利: ${result['profit']} ({result['profit_pct']}%)")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        levels = calculate_grid_levels(args.price_low, args.price_high, args.num_grids)
        print(f"\n[网格配置]")
        for level in levels:
            print(f"  Grid {level['grid_num']}: ${level['buy_price']:,.2f} (买) / ${level['sell_price']:,.2f} (卖)")
        
        print(f"\n[提示] 使用 --simulate 运行模拟回测")


if __name__ == "__main__":
    main()
