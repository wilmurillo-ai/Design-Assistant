#!/usr/bin/env python3
"""Backtesting Engine - 回测引擎

回测各种交易策略的历史表现
"""

import sys
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, __file__.rsplit('/', 3)[0])


def get_historical_data(symbol, start_date, end_date, timeframe='1h'):
    """获取历史数据（模拟）"""
    # 实际使用时应该从API获取，这里用模拟数据演示
    import random
    
    # 模拟价格数据
    days = (end_date - start_date).days
    if timeframe == '1h':
        periods = days * 24
    elif timeframe == '4h':
        periods = days * 6
    else:  # 1d
        periods = days
    
    periods = min(periods, 500)  # 限制数据量
    
    # 从一个合理的价格开始
    base_price = 65000 if 'BTC' in symbol else 3500
    prices = [base_price]
    
    for i in range(periods):
        # 随机游走
        change = random.uniform(-0.03, 0.035)  # ±3% 波动
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    return prices


def backtest_grid_strategy(prices, price_low, price_high, num_grids, investment_per_grid):
    """回测网格策略"""
    trades = []
    cash = investment_per_grid * num_grids
    position = 0
    grid_step = (price_high - price_low) / num_grids
    
    buy_count = 0
    sell_count = 0
    
    for i, price in enumerate(prices):
        # 计算当前在哪个网格
        grid_index = int((price - price_low) / grid_step) if price > price_low else 0
        grid_index = max(0, min(num_grids - 1, grid_index))
        
        # 买入条件：价格触及网格线且有钱
        if price <= price_low + grid_step * (grid_index + 0.5) and cash >= investment_per_grid:
            qty = investment_per_grid / price
            trades.append({
                'type': 'BUY',
                'price': price,
                'qty': qty,
                'grid': grid_index,
                'index': i
            })
            cash -= investment_per_grid
            position += qty
            buy_count += 1
        
        # 卖出条件：价格上涨到网格上方且有持仓
        elif price >= price_low + grid_step * (grid_index + 1.5) and position > 0.001:
            qty = position * 0.1  # 卖10%
            trades.append({
                'type': 'SELL',
                'price': price,
                'qty': qty,
                'grid': grid_index,
                'index': i
            })
            cash += qty * price
            position -= qty
            sell_count += 1
    
    # 计算结果
    final_price = prices[-1]
    final_value = cash + position * final_price
    total_invested = investment_per_grid * num_grids
    profit = final_value - total_invested
    profit_pct = (profit / total_invested) * 100
    
    # 买入持有对比
    buy_hold_qty = total_invested / prices[0]
    buy_hold_value = buy_hold_qty * final_price
    buy_hold_profit_pct = ((buy_hold_value - total_invested) / total_invested) * 100
    
    return {
        'strategy': 'grid_trading',
        'periods': len(prices),
        'total_trades': len(trades),
        'buy_count': buy_count,
        'sell_count': sell_count,
        'total_invested': round(total_invested, 2),
        'final_value': round(final_value, 2),
        'profit': round(profit, 2),
        'profit_pct': round(profit_pct, 2),
        'buy_hold_profit_pct': round(buy_hold_profit_pct, 2),
        'outperformance': round(profit_pct - buy_hold_profit_pct, 2),
        'final_price': round(final_price, 2),
        'start_price': round(prices[0], 2)
    }


def backtest_dca_strategy(prices, investment_per_period, num_periods):
    """回测DCA策略（定投）"""
    total_invested = 0
    total_qty = 0
    trades = []
    
    period_step = len(prices) // num_periods if num_periods > 0 else len(prices)
    
    for i in range(0, len(prices), max(1, period_step)):
        price = prices[i]
        qty = investment_per_period / price
        trades.append({
            'type': 'BUY',
            'price': price,
            'qty': qty,
            'index': i
        })
        total_invested += investment_per_period
        total_qty += qty
    
    final_price = prices[-1]
    final_value = total_qty * final_price
    profit = final_value - total_invested
    profit_pct = (profit / total_invested) * 100 if total_invested > 0 else 0
    
    # 买入持有对比
    buy_hold_qty = total_invested / prices[0]
    buy_hold_value = buy_hold_qty * final_price
    buy_hold_profit_pct = ((buy_hold_value - total_invested) / total_invested) * 100
    
    return {
        'strategy': 'dca',
        'total_trades': len(trades),
        'total_invested': round(total_invested, 2),
        'total_qty': round(total_qty, 6),
        'avg_buy_price': round(total_invested / total_qty, 2) if total_qty > 0 else 0,
        'final_value': round(final_value, 2),
        'profit': round(profit, 2),
        'profit_pct': round(profit_pct, 2),
        'buy_hold_profit_pct': round(buy_hold_profit_pct, 2),
        'outperformance': round(profit_pct - buy_hold_profit_pct, 2),
        'final_price': round(final_price, 2),
        'start_price': round(prices[0], 2)
    }


def calculate_max_drawdown(prices):
    """计算最大回撤"""
    peak = prices[0]
    max_dd = 0
    
    for price in prices:
        if price > peak:
            peak = price
        dd = (peak - price) / peak
        if dd > max_dd:
            max_dd = dd
    
    return max_dd * 100


def format_backtest_report(result):
    """格式化回测报告"""
    return f"""
📊 **回测报告** - {result.get('strategy', 'unknown').upper()}

**收益对比:**
| 策略 | 收益率 |
|------|--------|
| 本策略 | {result['profit_pct']:+.2f}% |
| 买入持有 | {result.get('buy_hold_profit_pct', 0):+.2f}% |
| 超额收益 | {result.get('outperformance', 0):+.2f}% |

**交易统计:**
| 指标 | 数值 |
|------|------|
| 总交易次数 | {result['total_trades']} |
| 买入次数 | {result.get('buy_count', '-')} |
| 卖出次数 | {result.get('sell_count', '-')} |
| 最大回撤 | {result.get('max_drawdown', 'N/A')} |

**资金情况:**
| 指标 | 数值 |
|------|------|
| 总投入 | ${result['total_invested']} |
| 最终价值 | ${result['final_value']} |
| 盈利 | ${result['profit']} |

**价格变化:**
| 项目 | 价格 |
|------|------|
| 起始价格 | ${result['start_price']:,.2f} |
| 最终价格 | ${result['final_price']:,.2f} |
"""


def main():
    parser = argparse.ArgumentParser(description='Backtesting Engine')
    parser.add_argument('--strategy', '-s', required=True, 
                        choices=['grid', 'dca', 'trend'],
                        help='Strategy to backtest')
    parser.add_argument('--symbol', default='BTCUSDT', help='Trading pair')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--price-low', type=float, help='Grid lower bound')
    parser.add_argument('--price-high', type=float, help='Grid upper bound')
    parser.add_argument('--num-grids', type=int, default=10, help='Number of grids')
    parser.add_argument('--investment', type=float, default=100, help='Investment amount')
    parser.add_argument('--periods', type=int, default=12, help='Number of periods (for DCA)')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    # 解析日期
    if args.start:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
    else:
        start_date = datetime.now() - timedelta(days=30)
    
    if args.end:
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    print(f"[回测] {args.strategy} 策略 {args.symbol}")
    print(f"  时间范围: {start_date.date()} - {end_date.date()}")
    
    # 获取历史数据
    prices = get_historical_data(args.symbol, start_date, end_date)
    
    # 运行回测
    if args.strategy == 'grid':
        if not args.price_low or not args.price_high:
            # 自动估算价格范围
            args.price_low = min(prices) * 0.9
            args.price_high = max(prices) * 1.1
        
        result = backtest_grid_strategy(
            prices, args.price_low, args.price_high, 
            args.num_grids, args.investment
        )
    elif args.strategy == 'dca':
        result = backtest_dca_strategy(prices, args.investment, args.periods)
    else:
        print("[ERROR] Strategy not implemented")
        sys.exit(1)
    
    # 添加最大回撤
    result['max_drawdown'] = f"{calculate_max_drawdown(prices):.2f}%"
    
    if args.format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_backtest_report(result))


if __name__ == "__main__":
    main()
