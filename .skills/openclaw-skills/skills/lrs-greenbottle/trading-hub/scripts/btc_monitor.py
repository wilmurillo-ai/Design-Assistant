#!/usr/bin/env python3
"""BTC Position Monitor - 持仓监控

检查当前持仓状态，判断是否触发止损/止盈
"""

import requests
import json
import sys
import time
import datetime
import hmac
import hashlib

# 导入配置
sys.path.insert(0, __file__.rsplit('/', 2)[0])
from config import load_config, get_signature, save_positions, load_positions


FUTURES_URL = "https://fapi.binance.com"
SPOT_URL = "https://api.binance.com"


def get_position(symbol="BTCUSDT"):
    """获取持仓信息"""
    config = load_config()
    if not config or not config['binance'].get('api_key'):
        return None

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']

    timestamp = int(time.time() * 1000)
    query = f"symbol={symbol}&timestamp={timestamp}"
    signature = get_signature(query, secret_key)

    try:
        resp = requests.get(
            f"{FUTURES_URL}/fapi/v2/positionRisk",
            params={"symbol": symbol, "timestamp": timestamp, "signature": signature},
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        data = resp.json()
        # 检查API错误响应（如451/429等）
        if not isinstance(data, list):
            return None
        positions = data
        
        for pos in positions:
            if pos['symbol'] == symbol and float(pos.get('positionAmt', 0)) != 0:
                return {
                    "symbol": pos['symbol'],
                    "quantity": float(pos['positionAmt']),
                    "entry_price": float(pos['entryPrice']),
                    "unrealized_pnl": float(pos['unRealizedProfit']),
                    "leverage": int(pos['leverage']),
                    "margin": float(pos.get('isolatedWallet', 0)),
                    "positionSide": pos.get('positionSide', 'BOTH'),
                }
        return None
    except Exception as e:
        return None


def get_current_price(symbol="BTCUSDT"):
    """获取当前价格"""
    try:
        resp = requests.get(
            f"{FUTURES_URL}/fapi/v1/ticker/price",
            params={"symbol": symbol},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and 'price' in data:
                return float(data['price'])
    except:
        pass
    return None


def get_balance():
    """获取账户余额"""
    config = load_config()
    if not config or not config['binance'].get('api_key'):
        return None

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']

    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = get_signature(query, secret_key)

    try:
        resp = requests.get(
            f"{FUTURES_URL}/fapi/v2/balance",
            params={"timestamp": timestamp, "signature": signature},
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        data = resp.json()
        # 检查API错误响应（如451/429等）
        if not isinstance(data, list):
            return None
        balances = data
        
        for b in balances:
            if b['asset'] == 'USDT':
                return {
                    "asset": "USDT",
                    "balance": float(b['balance']),
                    "available": float(b['availableBalance']),
                }
        return None
    except Exception as e:
        return None


def check_triggers(position, current_price, config_stop=None, config_profit=None):
    """检查是否触发止损/止盈"""
    quantity = abs(position['quantity'])
    entry = position['entry_price']
    leverage = position['leverage']
    direction = "多" if position['quantity'] > 0 else "空"
    
    # 理论止损价（杠杆倒数）
    if direction == "多":
        theoretical_stop = entry * (1 - 1 / leverage)
        theoretical_profit = entry * (1 + 2 / leverage)  # 2倍杠杆止盈
        stop_triggered = current_price <= theoretical_stop
        profit_triggered = current_price >= theoretical_profit
    else:
        theoretical_stop = entry * (1 + 1 / leverage)
        theoretical_profit = entry * (1 - 2 / leverage)
        stop_triggered = current_price >= theoretical_stop
        profit_triggered = current_price <= theoretical_profit
    
    # 自定义止损/止盈
    if config_stop:
        if direction == "多":
            stop_triggered = stop_triggered or (current_price <= config_stop)
        else:
            stop_triggered = stop_triggered or (current_price >= config_stop)
    
    if config_profit:
        if direction == "多":
            profit_triggered = profit_triggered or (current_price >= config_profit)
        else:
            profit_triggered = profit_triggered or (current_price <= config_profit)
    
    return {
        "direction": direction,
        "theoretical_stop": round(theoretical_stop, 2),
        "theoretical_profit": round(theoretical_profit, 2),
        "config_stop": config_stop,
        "config_profit": config_profit,
        "stop_triggered": stop_triggered,
        "profit_triggered": profit_triggered
    }


def format_position_status(position, current_price, balance=None, triggers=None):
    """格式化持仓状态"""
    quantity = abs(position['quantity'])
    entry = position['entry_price']
    leverage = position['leverage']
    direction = "多仓" if position['quantity'] > 0 else "空仓"
    pnl = position['unrealized_pnl']
    pnl_pct = (pnl / (entry * quantity)) * 100 if quantity > 0 else 0
    
    # 计算距离
    if position['quantity'] > 0:  # 多仓
        stop_distance_pct = (entry - triggers['theoretical_stop'] if triggers else (entry * (1 - 1/leverage))) / entry * 100
        profit_distance_pct = (triggers['theoretical_profit'] if triggers else (entry * (1 + 2/leverage)) - entry) / entry * 100
        distance_to_entry = (current_price - entry) / entry * 100
    else:  # 空仓
        stop_distance_pct = (triggers['theoretical_stop'] if triggers else (entry * (1 + 1/leverage)) - entry) / entry * 100
        profit_distance_pct = (entry - (triggers['theoretical_profit'] if triggers else (entry * (1 - 2/leverage)))) / entry * 100
        distance_to_entry = (entry - current_price) / entry * 100
    
    return {
        "has_position": True,
        "symbol": position['symbol'],
        "direction": direction,
        "quantity": round(quantity, 6),
        "entry_price": round(entry, 2),
        "current_price": round(current_price, 2),
        "leverage": leverage,
        "pnl": round(pnl, 4),
        "pnl_pct": round(pnl_pct, 2),
        "distance_to_entry_pct": round(distance_to_entry, 2),
        "stop_distance_pct": round(abs(stop_distance_pct), 2),
        "profit_distance_pct": round(abs(profit_distance_pct), 2),
        "margin": round(position.get('margin', 0), 2),
        "balance": round(balance['available'], 2) if balance else 0,
        "triggers": triggers,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def format_no_position(current_price, balance=None):
    """格式化无持仓状态"""
    return {
        "has_position": False,
        "current_price": round(current_price, 2) if current_price else 0,
        "balance": round(balance['available'], 2) if balance and 'available' in balance else (round(balance['balance'], 2) if balance else 0),
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def main():
    # 加载本地配置的止损止盈
    positions_config = load_positions()
    btc_config = positions_config.get('binance', {}).get('BTCUSDT', {})
    config_stop = btc_config.get('stop_loss')
    config_profit = btc_config.get('take_profit')

    # 获取持仓
    position = get_position()
    current_price = get_current_price()
    balance = get_balance()

    if current_price is None:
        # 价格获取失败，静默退出
        return

    # 无持仓 → 静默退出，不推送任何消息
    if not position:
        return

    # 检查触发
    triggers = check_triggers(position, current_price, config_stop, config_profit)

    # 无触发 → 静默退出，不推送任何消息
    if not triggers['stop_triggered'] and not triggers['profit_triggered']:
        return

    # 格式化状态
    status = format_position_status(position, current_price, balance, triggers)

    # 保存状态
    save_positions({
        'binance': {
            'BTCUSDT': {
                'entry_price': position['entry_price'],
                'quantity': position['quantity'],
                'leverage': position['leverage'],
                'stop_loss': config_stop,
                'take_profit': config_profit,
                'last_update': status['timestamp']
            }
        }
    })

    print(json.dumps(status, ensure_ascii=False))

    # 打印易读格式
    emoji = "🟢" if status['pnl_pct'] >= 0 else "🔴"
    print(f"\n📊 **BTC仓位状态**")
    print(f"{emoji} 方向: {status['direction']}")
    print(f"💰 当前价格: ${status['current_price']:,.2f}")
    print(f"📈 入场价格: ${status['entry_price']:,.2f} (距离: {'+' if status['distance_to_entry_pct'] >= 0 else ''}{status['distance_to_entry_pct']}%)")
    print(f"📉 数量: {status['quantity']} BTC")
    print(f"⚖️ 杠杆: {status['leverage']}x")
    print(f"{emoji} PnL: ${status['pnl']:,.4f} ({'+' if status['pnl_pct'] >= 0 else ''}{status['pnl_pct']}%)")
    print(f"💳 可用余额: ${status['balance']:,.2f}")

    print(f"\n📍 距离止损: {status['stop_distance_pct']}% (理论: ${triggers['theoretical_stop']:,.2f})")
    print(f"🎯 距离止盈: {status['profit_distance_pct']}% (理论: ${triggers['theoretical_profit']:,.2f})")

    if config_stop:
        print(f"⚙️ 自定义止损: ${config_stop:,.2f}")
    if config_profit:
        print(f"⚙️ 自定义止盈: ${config_profit:,.2f}")

    # 触发警告
    if triggers['stop_triggered']:
        print(f"\n🚨 **警告：触发止损条件！**")
        print(f"   当前价 ${current_price:,.2f} {'<=' if triggers['direction'] == '多' else '>='} 止损价 ${triggers['theoretical_stop']:,.2f}")

    if triggers['profit_triggered']:
        print(f"\n🎯 **提示：触发止盈条件！**")
        print(f"   当前价 ${current_price:,.2f} {'>=' if triggers['direction'] == '多' else '<='} 止盈价 ${triggers['theoretical_profit']:,.2f}")


if __name__ == "__main__":
    main()
