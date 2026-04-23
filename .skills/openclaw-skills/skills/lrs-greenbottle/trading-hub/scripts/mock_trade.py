#!/usr/bin/env python3
"""模拟交易系统 - Mock Trading System

功能：
- 虚拟钱包管理（默认 $10,000）
- 市价/限价模拟成交
- 持仓管理
- 交易历史记录
- 盈亏计算
- 支持现货/合约双模式
"""

import json
import time
import os
from datetime import datetime
from typing import Optional, Dict, List, Union

# 数据文件路径
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DATA_FILE = os.path.join(DATA_DIR, 'mock_wallet.json')
MOCK_HISTORY_FILE = os.path.join(DATA_DIR, 'mock_history.json')

class MockWallet:
    """模拟钱包"""
    
    def __init__(self, initial_balance: float = 1000.0, mode: str = 'spot'):
        """
        初始化钱包
        :param initial_balance: 初始USDT余额
        :param mode: 'spot' 现货模式 或 'futures' 合约模式
        """
        self.mode = mode
        self.initial_balance = initial_balance
        self.load()
    
    def load(self):
        """从文件加载钱包状态"""
        key = f"{self.mode}_balance"
        if os.path.exists(MOCK_DATA_FILE):
            with open(MOCK_DATA_FILE, 'r') as f:
                data = json.load(f)
                if key in data:
                    self.balance = data[key]['balance']
                    self.positions = data[key].get('positions', {})
                    self.orders = data[key].get('orders', [])
                    return
        
        # 默认初始化
        self.balance = self.initial_balance
        self.positions = {}  # {symbol: {qty, avg_price, side}}
        self.orders = []     # 订单历史
    
    def save(self):
        """保存钱包状态到文件"""
        key = f"{self.mode}_balance"
        data = {}
        if os.path.exists(MOCK_DATA_FILE):
            with open(MOCK_DATA_FILE, 'r') as f:
                data = json.load(f)
        
        data[key] = {
            'balance': self.balance,
            'positions': self.positions,
            'orders': self.orders[-100:]  # 只保留最近100条
        }
        
        with open(MOCK_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def reset(self, initial_balance: float = None):
        """重置钱包"""
        if initial_balance:
            self.initial_balance = initial_balance
        self.balance = self.initial_balance
        self.positions = {}
        self.orders = []
        self.save()
        return self.get_status()
    
    def get_status(self) -> dict:
        """获取钱包状态"""
        total_positions_value = 0
        positions_detail = {}
        
        for symbol, pos in self.positions.items():
            qty = pos['qty']
            avg_price = pos['avg_price']
            positions_detail[symbol] = {
                'qty': qty,
                'avg_price': avg_price,
                'value': qty * avg_price
            }
            total_positions_value += qty * avg_price
        
        return {
            'mode': self.mode,
            'balance': self.balance,
            'positions_value': total_positions_value,
            'total_assets': self.balance + total_positions_value,
            'positions': positions_detail
        }


class MockTrade:
    """模拟交易引擎"""
    
    def __init__(self, initial_balance: float = 1000.0, mode: str = 'spot'):
        """
        初始化交易引擎
        :param initial_balance: 初始USDT余额
        :param mode: 'spot' 现货模式 或 'futures' 合约模式
        """
        self.wallet = MockWallet(initial_balance, mode)
        self.current_price = {}  # 缓存当前价格
    
    def set_price(self, symbol: str, price: float):
        """设置当前价格（模拟撮合用）"""
        self.current_price[symbol] = price
    
    def get_market_price(self, symbol: str = 'BTCUSDT') -> float:
        """获取市场价（如果没有缓存则模拟）"""
        if symbol in self.current_price:
            return self.current_price[symbol]
        
        # 如果没有设置价格，返回模拟价格
        # 实际使用时应先通过 set_price 设置
        return self._get_simulated_price(symbol)
    
    def _get_simulated_price(self, symbol: str) -> float:
        """获取模拟价格（临时）"""
        import random
        # BTC 模拟价格 $70,000 附近
        if symbol == 'BTCUSDT':
            return 70000 + random.uniform(-500, 500)
        return 100.0
    
    def buy_market(self, symbol: str, amount: float, current_price: float = None) -> dict:
        """
        市价买入
        :param symbol: 交易对如 BTCUSDT
        :param amount: 买入金额(USDT)
        :param current_price: 当前价格（可选）
        :return: 成交结果
        """
        if current_price is None:
            current_price = self.get_market_price(symbol)
        
        qty = amount / current_price  # 买入数量
        
        # 检查余额
        if self.wallet.balance < amount:
            return {
                'success': False,
                'error': f'余额不足。需要 ${amount:.2f}，只有 ${self.wallet.balance:.2f}'
            }
        
        # 扣除USDT
        self.wallet.balance -= amount
        
        # 更新持仓
        if symbol in self.wallet.positions:
            old = self.wallet.positions[symbol]
            total_qty = old['qty'] + qty
            old['avg_price'] = (old['qty'] * old['avg_price'] + qty * current_price) / total_qty
            old['qty'] = total_qty
        else:
            self.wallet.positions[symbol] = {
                'qty': qty,
                'avg_price': current_price,
                'side': 'long'
            }
        
        # 记录订单
        order = {
            'id': f"Mock_{int(time.time() * 1000)}",
            'time': datetime.now().isoformat(),
            'symbol': symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'price': current_price,
            'qty': qty,
            'amount': amount,
            'status': 'FILLED'
        }
        self.wallet.orders.append(order)
        self.wallet.save()
        
        return {
            'success': True,
            'order': order,
            'remaining_balance': self.wallet.balance
        }
    
    def sell_market(self, symbol: str, qty: float = None, percent: float = None, current_price: float = None) -> dict:
        """
        市价卖出
        :param symbol: 交易对
        :param qty: 卖出数量（可选）
        :param percent: 卖出持仓比例0-1（可选）
        :param current_price: 当前价格（可选）
        :return: 成交结果
        """
        if current_price is None:
            current_price = self.get_market_price(symbol)
        
        if symbol not in self.wallet.positions:
            return {
                'success': False,
                'error': f'没有 {symbol} 持仓'
            }
        
        pos = self.wallet.positions[symbol]
        
        # 计算卖出数量
        if percent is not None:
            sell_qty = pos['qty'] * percent
        elif qty is not None:
            sell_qty = qty
        else:
            sell_qty = pos['qty']  # 全部卖出
        
        if sell_qty > pos['qty']:
            return {
                'success': False,
                'error': f'持仓不足。持有 {pos["qty"]:.8f}，尝试卖出 {sell_qty:.8f}'
            }
        
        # 计算收益
        sell_value = sell_qty * current_price
        cost = sell_qty * pos['avg_price']
        profit = sell_value - cost
        profit_pct = (current_price - pos['avg_price']) / pos['avg_price'] * 100
        
        # 增加USDT
        self.wallet.balance += sell_value
        
        # 更新持仓
        pos['qty'] -= sell_qty
        if pos['qty'] <= 0.00000001:
            del self.wallet.positions[symbol]
        
        # 记录订单
        order = {
            'id': f"Mock_{int(time.time() * 1000)}",
            'time': datetime.now().isoformat(),
            'symbol': symbol,
            'side': 'SELL',
            'type': 'MARKET',
            'price': current_price,
            'qty': sell_qty,
            'amount': sell_value,
            'cost': cost,
            'profit': profit,
            'profit_pct': profit_pct,
            'status': 'FILLED'
        }
        self.wallet.orders.append(order)
        self.wallet.save()
        
        return {
            'success': True,
            'order': order,
            'remaining_balance': self.wallet.balance
        }
    
    def buy_limit(self, symbol: str, price: float, amount: float) -> dict:
        """
        限价买入挂单（模拟，会立即以指定价格成交）
        :return: 成交结果
        """
        # 模拟撮合：立即以挂单价成交
        return self.buy_market(symbol, amount, price)
    
    def sell_limit(self, symbol: str, price: float, qty: float = None, percent: float = None) -> dict:
        """
        限价卖出挂单（模拟，会立即以指定价格成交）
        :return: 成交结果
        """
        return self.sell_market(symbol, qty, percent, price)
    
    def get_position(self, symbol: str = 'BTCUSDT') -> dict:
        """获取持仓"""
        if symbol in self.wallet.positions:
            pos = self.wallet.positions[symbol]
            current = self.get_market_price(symbol)
            return {
                'symbol': symbol,
                'qty': pos['qty'],
                'avg_price': pos['avg_price'],
                'current_price': current,
                'value': pos['qty'] * current,
                'profit': pos['qty'] * (current - pos['avg_price']),
                'profit_pct': (current - pos['avg_price']) / pos['avg_price'] * 100
            }
        return None
    
    def get_history(self, limit: int = 20) -> list:
        """获取交易历史"""
        return self.wallet.orders[-limit:]
    
    def get_profit_summary(self) -> dict:
        """获取盈亏汇总"""
        orders = self.wallet.orders
        total_profit = 0
        buy_count = 0
        sell_count = 0
        winning_trades = 0
        losing_trades = 0
        
        for o in orders:
            if o['side'] == 'SELL' and 'profit' in o:
                total_profit += o['profit']
                sell_count += 1
                if o['profit'] > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
            elif o['side'] == 'BUY':
                buy_count += 1
        
        return {
            'total_trades': len(orders),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'total_profit': total_profit,
            'win_rate': winning_trades / sell_count * 100 if sell_count > 0 else 0
        }


def print_status(trade: MockTrade):
    """打印交易状态"""
    status = trade.wallet.get_status()
    print(f"""
=== 模拟交易账户状态 ===
模式: {status['mode'].upper()}
可用余额: ${status['balance']:.2f}
持仓价值: ${status['positions_value']:.2f}
总资产: ${status['total_assets']:.2f}
""")
    
    if status['positions']:
        print('持仓明细:')
        for symbol, pos in status['positions'].items():
            current = trade.get_market_price(symbol)
            profit = pos['qty'] * (current - pos['avg_price'])
            profit_pct = (current - pos['avg_price']) / pos['avg_price'] * 100
            print(f"  {symbol}: {pos['qty']:.8f} @ ${pos['avg_price']:.2f} = ${pos['value']:.2f} (浮盈: ${profit:.2f} {profit_pct:+.2f}%)")
    
    summary = trade.get_profit_summary()
    print(f"""
=== 交易统计 ===
交易次数: {summary['total_trades']}
买入: {summary['buy_count']} | 卖出: {summary['sell_count']}
盈利交易: {summary['winning_trades']} | 亏损交易: {summary['losing_trades']}
总盈亏: ${summary['total_profit']:.2f}
胜率: {summary['win_rate']:.1f}%
""")


# ========== CLI ==========
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='模拟交易系统')
    parser.add_argument('action', choices=['status', 'buy', 'sell', 'reset', 'history', 'profit'], help='操作')
    parser.add_argument('--symbol', default='BTCUSDT', help='交易对')

    parser.add_argument('--amount', type=float, help='买入金额(USDT)')
    parser.add_argument('--qty', type=float, help='卖出数量')
    parser.add_argument('--percent', type=float, help='卖出比例(0-1)')
    parser.add_argument('--price', type=float, help='限价')
    parser.add_argument('--balance', type=float, default=1000, help='初始资金')
    parser.add_argument('--mode', default='spot', choices=['spot', 'futures'], help='交易模式')
    parser.add_argument('--current-price', type=float, help='当前价格')
    
    args = parser.parse_args()
    
    trade = MockTrade(initial_balance=args.balance, mode=args.mode)
    
    if args.action == 'status':
        print_status(trade)
    
    elif args.action == 'buy':
        if not args.amount:
            print('错误: 需要 --amount 参数')
        else:
            result = trade.buy_market(args.symbol, args.amount, args.current_price)
            if result['success']:
                print(f"✅ 买入成功!")
                print(f"数量: {result['order']['qty']:.8f} {args.symbol}")
                print(f"价格: ${result['order']['price']:.2f}")
                print(f"金额: ${result['order']['amount']:.2f}")
                print(f"剩余余额: ${result['remaining_balance']:.2f}")
            else:
                print(f"❌ 买入失败: {result['error']}")
    
    elif args.action == 'sell':
        result = trade.sell_market(args.symbol, args.qty, args.percent, args.current_price)
        if result['success']:
            print(f"✅ 卖出成功!")
            print(f"数量: {result['order']['qty']:.8f} {args.symbol}")
            print(f"价格: ${result['order']['price']:.2f}")
            print(f"金额: ${result['order']['amount']:.2f}")
            print(f"盈亏: ${result['order']['profit']:.2f} ({result['order']['profit_pct']:+.2f}%)")
            print(f"剩余余额: ${result['remaining_balance']:.2f}")
        else:
            print(f"❌ 卖出失败: {result['error']}")
    
    elif args.action == 'reset':
        status = trade.wallet.reset(args.balance)
        print(f"✅ 钱包已重置")
        print(f"初始资金: ${status['balance']:.2f}")
    
    elif args.action == 'history':
        history = trade.get_history(20)
        if history:
            print('=== 最近交易 ===')
            for o in history:
                pnl = f" 盈亏:${o.get('profit', 0):.2f}" if o['side'] == 'SELL' else ''
                print(f"{o['time'][:19]} {o['side']} {o['qty']:.6f}@${o['price']:.2f} = ${o['amount']:.2f}{pnl}")
        else:
            print('暂无交易记录')
    
    elif args.action == 'profit':
        summary = trade.get_profit_summary()
        print('=== 盈亏统计 ===')
        print(f"总交易次数: {summary['total_trades']}")
        print(f"买入次数: {summary['buy_count']}")
        print(f"卖出次数: {summary['sell_count']}")
        print(f"盈利交易: {summary['winning_trades']}")
        print(f"亏损交易: {summary['losing_trades']}")
        print(f"总盈亏: ${summary['total_profit']:.2f}")
        print(f"胜率: {summary['win_rate']:.1f}%")
