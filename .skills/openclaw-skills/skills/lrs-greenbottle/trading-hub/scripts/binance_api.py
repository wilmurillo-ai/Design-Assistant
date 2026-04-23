#!/usr/bin/env python3
"""Binance API - 统一币安API封装

支持：现货交易、合约交易、杠杆操作
"""

import sys
import time
import json
import hmac
import hashlib
import requests
from config import load_config, get_signature, log_trade

# 现货和合约分别使用不同的域名
SPOT_URL = "https://api.binance.com"
FUTURES_URL = "https://fapi.binance.com"


def get_balance(asset='USDT'):
    """获取现货或合约账户余额"""
    config = load_config()
    if not config or not config['binance'].get('api_key'):
        return None

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = get_signature(query, secret_key)

    # 合约账户余额
    try:
        resp = requests.get(
            f"{FUTURES_URL}/fapi/v2/balance",
            params={"timestamp": timestamp, "signature": signature},
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        if resp.status_code == 200:
            balances = resp.json()
            for b in balances:
                if b['asset'] == asset:
                    return {
                        'asset': asset,
                        'balance': float(b['balance']),
                        'available': float(b['availableBalance']),
                        'accountType': 'futures'
                    }
    except Exception as e:
        print(f"[WARN] Futures balance error: {e}")

    # 现货账户余额
    try:
        query = f"timestamp={timestamp}"
        signature = get_signature(query, secret_key)
        resp = requests.get(
            f"{SPOT_URL}/api/v3/account",
            params={"timestamp": timestamp, "signature": signature},
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        if resp.status_code == 200:
            balances = resp.json().get('balances', [])
            for b in balances:
                if b['asset'] == asset and float(b['free']) > 0:
                    return {
                        'asset': asset,
                        'balance': float(b['free']) + float(b['locked']),
                        'available': float(b['free']),
                        'accountType': 'spot'
                    }
    except Exception as e:
        print(f"[WARN] Spot balance error: {e}")

    return None


def get_position(symbol='BTCUSDT', account_type='futures'):
    """获取持仓信息"""
    config = load_config()
    if not config or not config['binance'].get('api_key'):
        return None

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']
    timestamp = int(time.time() * 1000)

    if account_type == 'futures':
        query = f"timestamp={timestamp}"
        signature = get_signature(query, secret_key)

        try:
            resp = requests.get(
                f"{FUTURES_URL}/fapi/v2/positionRisk",
                params={"timestamp": timestamp, "signature": signature},
                headers={"X-MBX-APIKEY": api_key},
                timeout=10
            )
            if resp.status_code == 200:
                positions = resp.json()
                for pos in positions:
                    if pos['symbol'] == symbol and float(pos.get('positionAmt', 0)) != 0:
                        return {
                            'symbol': pos['symbol'],
                            'quantity': float(pos['positionAmt']),
                            'entry_price': float(pos['entryPrice']),
                            'unrealized_pnl': float(pos['unRealizedProfit']),
                            'leverage': int(pos['leverage']),
                            'margin': float(pos['isolatedWallet']) if pos.get('isolated') else 0,
                            'position_side': pos.get('positionSide', 'BOTH'),
                            'accountType': 'futures'
                        }
                return None
        except Exception as e:
            print(f"[ERROR] Get position error: {e}")

    return None


def get_current_price(symbol='BTCUSDT'):
    """获取当前价格"""
    try:
        resp = requests.get(
            f"{FUTURES_URL}/fapi/v1/ticker/price",
            params={"symbol": symbol},
            timeout=5
        )
        if resp.status_code == 200:
            return float(resp.json()['price'])
    except:
        pass
    # fallback 到现货行情
    try:
        resp = requests.get(
            f"{SPOT_URL}/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=5
        )
        if resp.status_code == 200:
            return float(resp.json()['price'])
    except:
        pass
    return None


def set_leverage(symbol, leverage):
    """设置杠杆"""
    config = load_config()
    if not config:
        return {'code': -1, 'msg': '配置错误'}

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']
    timestamp = int(time.time() * 1000)
    query = f"symbol={symbol}&leverage={leverage}&timestamp={timestamp}"
    signature = get_signature(query, secret_key)

    try:
        resp = requests.post(
            f"{FUTURES_URL}/fapi/v1/leverage",
            data={**dict(p.split('=') for p in query.split('&')), 'signature': signature},
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        return resp.json()
    except Exception as e:
        return {'code': -1, 'msg': str(e)}


def open_position(symbol, side, quantity, leverage=5):
    """开仓（市价单）"""
    config = load_config()
    if not config:
        return {'code': -1, 'msg': '配置错误'}

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']

    # 先设置杠杆
    set_leverage(symbol, leverage)

    timestamp = int(time.time() * 1000)

    # 市价开仓
    params = {
        'symbol': symbol,
        'side': side.upper(),
        'type': 'MARKET',
        'quantity': quantity,
        'timestamp': timestamp
    }

    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = get_signature(query, secret_key)
    params['signature'] = signature

    try:
        resp = requests.post(
            f"{FUTURES_URL}/fapi/v1/order",
            data=params,
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        result = resp.json()

        # 记录交易
        if 'orderId' in result:
            log_trade({
                'type': 'open',
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'leverage': leverage,
                'orderId': result.get('orderId'),
                'price': result.get('avgPrice', 'MARKET')
            })

        return result
    except Exception as e:
        return {'code': -1, 'msg': str(e)}


def close_position(symbol, quantity=None, position_side='BOTH'):
    """平仓（市价单）"""
    config = load_config()
    if not config:
        return {'code': -1, 'msg': '配置错误'}

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']

    # 获取当前持仓
    position = get_position(symbol)
    if not position:
        return {'code': -1, 'msg': '无持仓'}

    if quantity is None:
        quantity = abs(position['quantity'])

    # 确定平仓方向
    if position['quantity'] > 0:
        close_side = 'SELL'
    else:
        close_side = 'BUY'

    timestamp = int(time.time() * 1000)

    params = {
        'symbol': symbol,
        'side': close_side,
        'type': 'MARKET',
        'quantity': quantity,
        'timestamp': timestamp
    }

    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = get_signature(query, secret_key)
    params['signature'] = signature

    try:
        resp = requests.post(
            f"{FUTURES_URL}/fapi/v1/order",
            data=params,
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        result = resp.json()

        # 记录交易
        if 'orderId' in result:
            log_trade({
                'type': 'close',
                'symbol': symbol,
                'side': close_side,
                'quantity': quantity,
                'orderId': result.get('orderId'),
                'price': result.get('avgPrice', 'MARKET'),
                'pnl': position.get('unrealized_pnl', 0)
            })

        return result
    except Exception as e:
        return {'code': -1, 'msg': str(e)}


def set_stop_loss(symbol, stop_price, quantity=None):
    """设置止损（市价止损）"""
    config = load_config()
    if not config:
        return {'code': -1, 'msg': '配置错误'}

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']

    # 获取当前持仓确定方向
    position = get_position(symbol)
    if not position:
        return {'code': -1, 'msg': '无持仓'}

    if quantity is None:
        quantity = abs(position['quantity'])

    close_side = 'SELL' if position['quantity'] > 0 else 'BUY'

    timestamp = int(time.time() * 1000)

    params = {
        'symbol': symbol,
        'side': close_side,
        'type': 'STOP_MARKET',
        'stopPrice': stop_price,
        'closePosition': 'true',
        'timestamp': timestamp
    }

    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = get_signature(query, secret_key)
    params['signature'] = signature

    try:
        resp = requests.post(
            f"{FUTURES_URL}/fapi/v1/order",
            data=params,
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        result = resp.json()

        if 'orderId' in result:
            log_trade({
                'type': 'set_stop_loss',
                'symbol': symbol,
                'stop_price': stop_price,
                'orderId': result.get('orderId')
            })

        return result
    except Exception as e:
        return {'code': -1, 'msg': str(e)}


def set_take_profit(symbol, take_price, quantity=None):
    """设置止盈（市价止盈）"""
    config = load_config()
    if not config:
        return {'code': -1, 'msg': '配置错误'}

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']

    position = get_position(symbol)
    if not position:
        return {'code': -1, 'msg': '无持仓'}

    if quantity is None:
        quantity = abs(position['quantity'])

    close_side = 'SELL' if position['quantity'] > 0 else 'BUY'

    timestamp = int(time.time() * 1000)

    params = {
        'symbol': symbol,
        'side': close_side,
        'type': 'TAKE_PROFIT_MARKET',
        'stopPrice': take_price,
        'closePosition': 'true',
        'timestamp': timestamp
    }

    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = get_signature(query, secret_key)
    params['signature'] = signature

    try:
        resp = requests.post(
            f"{FUTURES_URL}/fapi/v1/order",
            data=params,
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        result = resp.json()

        if 'orderId' in result:
            log_trade({
                'type': 'set_take_profit',
                'symbol': symbol,
                'take_price': take_price,
                'orderId': result.get('orderId')
            })

        return result
    except Exception as e:
        return {'code': -1, 'msg': str(e)}


def close_all_positions():
    """平所有持仓"""
    config = load_config()
    if not config:
        return [{'code': -1, 'msg': '配置错误'}]

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = get_signature(query, secret_key)

    try:
        resp = requests.get(
            f"{FUTURES_URL}/fapi/v2/positionRisk",
            params={"timestamp": timestamp, "signature": signature},
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        positions = resp.json()

        results = []
        for pos in positions:
            if float(pos.get('positionAmt', 0)) != 0:
                quantity = abs(float(pos['positionAmt']))
                close_side = 'SELL' if float(pos['positionAmt']) > 0 else 'BUY'

                params = {
                    'symbol': pos['symbol'],
                    'side': close_side,
                    'type': 'MARKET',
                    'quantity': quantity,
                    'timestamp': timestamp
                }
                query = '&'.join([f"{k}={v}" for k, v in params.items()])
                signature = get_signature(query, secret_key)
                params['signature'] = signature

                close_resp = requests.post(
                    f"{FUTURES_URL}/fapi/v1/order",
                    data=params,
                    headers={"X-MBX-APIKEY": api_key},
                    timeout=10
                )
                results.append(close_resp.json())

        if results:
            log_trade({
                'type': 'close_all',
                'results': len(results)
            })

        return results
    except Exception as e:
        return [{'code': -1, 'msg': str(e)}]


def get_all_positions():
    """获取所有持仓"""
    config = load_config()
    if not config or not config['binance'].get('api_key'):
        return []

    api_key = config['binance']['api_key']
    secret_key = config['binance']['secret_key']
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = get_signature(query, secret_key)

    try:
        resp = requests.get(
            f"{FUTURES_URL}/fapi/v2/positionRisk",
            params={"timestamp": timestamp, "signature": signature},
            headers={"X-MBX-APIKEY": api_key},
            timeout=10
        )
        if resp.status_code == 200:
            positions = resp.json()
            return [p for p in positions if float(p.get('positionAmt', 0)) != 0]
    except Exception as e:
        print(f"[ERROR] {e}")

    return []


def format_position_status(position, current_price):
    """格式化持仓状态"""
    quantity = abs(position['quantity'])
    entry = position['entry_price']
    leverage = position['leverage']
    direction = "多" if position['quantity'] > 0 else "空"
    pnl = position.get('unrealized_pnl', 0)
    pnl_pct = (pnl / (entry * quantity)) * 100 if quantity > 0 else 0

    return {
        'has_position': True,
        'symbol': position['symbol'],
        'direction': direction,
        'quantity': round(quantity, 6),
        'entry_price': round(entry, 2),
        'current_price': round(current_price, 2),
        'leverage': leverage,
        'pnl': round(pnl, 4),
        'pnl_pct': round(pnl_pct, 2),
        'margin': round(position.get('margin', 0), 2)
    }


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 binance_api.py balance [asset]")
        print("  python3 binance_api.py position <symbol>")
        print("  python3 binance_api.py price <symbol>")
        print("  python3 binance_api.py open_long <symbol> <quantity> [leverage]")
        print("  python3 binance_api.py open_short <symbol> <quantity> [leverage]")
        print("  python3 binance_api.py close <symbol> [quantity]")
        print("  python3 binance_api.py close_all")
        print("  python3 binance_api.py stop_loss <symbol> <price>")
        print("  python3 binance_api.py take_profit <symbol> <price>")
        print("  python3 binance_api.py all_positions")
        sys.exit(1)

    action = sys.argv[1].lower()
    symbol = sys.argv[2].upper() if len(sys.argv) > 2 else 'BTCUSDT'

    if action == 'balance':
        asset = sys.argv[3] if len(sys.argv) > 3 else 'USDT'
        balance = get_balance(asset)
        if balance:
            print(json.dumps(balance, indent=2, ensure_ascii=False))
        else:
            print('[INFO] 无法获取余额')

    elif action == 'position':
        position = get_position(symbol)
        if position:
            current_price = get_current_price(symbol)
            if current_price:
                status = format_position_status(position, current_price)
                print(json.dumps(status, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(position, indent=2, ensure_ascii=False))
        else:
            print(f'[INFO] {symbol} 无持仓')

    elif action == 'price':
        price = get_current_price(symbol)
        if price:
            print(f'{symbol}: ${price}')
        else:
            print('[ERROR] 无法获取价格')

    elif action == 'open_long':
        quantity = float(sys.argv[3]) if len(sys.argv) > 3 else 0.001
        leverage = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        print(f'[交易] 开多仓 {symbol} {quantity}, 杠杆{leverage}x')
        result = open_position(symbol, 'BUY', quantity, leverage)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif action == 'open_short':
        quantity = float(sys.argv[3]) if len(sys.argv) > 3 else 0.001
        leverage = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        print(f'[交易] 开空仓 {symbol} {quantity}, 杠杆{leverage}x')
        result = open_position(symbol, 'SELL', quantity, leverage)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif action == 'close':
        quantity = float(sys.argv[3]) if len(sys.argv) > 3 else None
        print(f'[交易] 平仓 {symbol} {quantity or "全部"}')
        result = close_position(symbol, quantity)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif action == 'close_all':
        print('[交易] 一键平所有仓')
        results = close_all_positions()
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif action == 'stop_loss':
        price = float(sys.argv[3]) if len(sys.argv) > 3 else None
        if not price:
            print('[ERROR] 请指定止损价格')
            sys.exit(1)
        print(f'[交易] 设置止损 {symbol} @ ${price}')
        result = set_stop_loss(symbol, price)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif action == 'take_profit':
        price = float(sys.argv[3]) if len(sys.argv) > 3 else None
        if not price:
            print('[ERROR] 请指定止盈价格')
            sys.exit(1)
        print(f'[交易] 设置止盈 {symbol} @ ${price}')
        result = set_take_profit(symbol, price)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif action == 'all_positions':
        positions = get_all_positions()
        print(json.dumps(positions, indent=2, ensure_ascii=False))

    else:
        print(f'[ERROR] 未知操作: {action}')


if __name__ == "__main__":
    main()
