#!/usr/bin/env python3
"""自动交易引擎 - 扫描+模拟下单一体化

功能：
- 自动扫描市场发现机会
- 根据策略自动模拟下单
- 记录交易原因
- 追踪持仓和盈亏
- 学习总结
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional

BINANCE_API = "https://api.binance.com"
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TRADE_LOG = os.path.join(DATA_DIR, 'auto_trades.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'auto_config.json')

# 扫描币种
COINS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
    'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
    'MATICUSDT', 'LTCUSDT', 'ATOMUSDT', 'UNIUSDT', 'XLMUSDT',
    'NEARUSDT', 'APTUSDT', 'ARBUSDT', 'OPUSDT', 'INJUSDT'
]

# 风险配置
MAX_POSITIONS = 3  # 最多持仓数
MAX_POSITION_PCT = 0.25  # 单笔不超过25%资金
MIN_CONFIDENCE = 2  # 最小信心度

def get_ticker(symbol: str) -> Optional[dict]:
    try:
        resp = requests.get(f"{BINANCE_API}/api/v3/ticker/24hr", params={'symbol': symbol}, timeout=10)
        if resp.status_code == 200:
            d = resp.json()
            return {
                'symbol': symbol.replace('USDT', ''),
                'price': float(d['lastPrice']),
                'change_24h': float(d['priceChangePercent']),
                'high_24h': float(d['highPrice']),
                'low_24h': float(d['lowPrice']),
                'volume': float(d['quoteVolume'])
            }
    except:
        pass
    return None

def get_klines(symbol: str, interval: str = '1h', limit: int = 200) -> Optional[List]:
    try:
        resp = requests.get(f"{BINANCE_API}/api/v3/klines",
            params={'symbol': symbol, 'interval': interval, 'limit': limit}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

def calc_ema(prices: List[float], period: int) -> float:
    if len(prices) < period:
        return prices[-1] if prices else 0
    k = 2 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema

def calc_rsi(prices: List[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(diff if diff > 0 else 0)
        losses.append(abs(diff) if diff < 0 else 0)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    return 100 - (100 / (1 + avg_gain / avg_loss))

def calc_macd(prices: List[float]):
    if len(prices) < 26:
        return 0, 0, 0
    ema12 = calc_ema(prices, 12)
    ema26 = calc_ema(prices, 26)
    macd = ema12 - ema26
    signal = macd  # simplified
    hist = macd - signal
    return macd, signal, hist

def analyze_coin(symbol: str) -> Optional[dict]:
    ticker = get_ticker(symbol)
    if not ticker:
        return None
    
    klines_h = get_klines(symbol, '1h', 200)
    klines_d = get_klines(symbol, '1d', 50)
    
    closes_h = [float(k[4]) for k in klines_h] if klines_h else []
    closes_d = [float(k[4]) for k in klines_d] if klines_d else closes_h[-50:] if closes_h else []
    
    price = ticker['price']
    change = ticker['change_24h']
    high, low = ticker['high_24h'], ticker['low_24h']
    
    ema20_d = calc_ema(closes_d, 20)
    ema60_d = calc_ema(closes_d, 60)
    rsi_d = calc_rsi(closes_d)
    rsi_h = calc_rsi(closes_h)
    
    trend = '震荡'
    trend_dir = 0
    if ema20_d > ema60_d and price > ema20_d:
        trend = '多头'
        trend_dir = 1
    elif ema20_d < ema60_d and price < ema20_d:
        trend = '空头'
        trend_dir = -1
    
    signals = []
    action = '无信号'
    confidence = 0
    stop_loss = 0
    take_profit = 0
    
    # 超跌反弹
    if rsi_d < 35 and change > -3:
        signals.append('超跌反弹')
        if confidence < 4:
            action = '买涨'
            confidence = 4
            stop_loss = low * 0.98
            take_profit = price * 1.06
    
    # 回踩支撑
    if abs(price - ema20_d) / price < 0.03 and rsi_d > 40:
        signals.append('回踩支撑')
        if confidence < 3:
            action = '买涨'
            confidence = 3
            stop_loss = ema20_d * 0.97
            take_profit = price * 1.08
    
    # MACD金叉
    if len(closes_h) > 26:
        ema12_h = calc_ema(closes_h, 12)
        ema26_h = calc_ema(closes_h, 26)
        macd_h = ema12_h - ema26_h
        prev_macd = calc_ema(closes_h[:-1], 12) - calc_ema(closes_h[:-1], 26)
        if macd_h > 0 and prev_macd <= 0:
            signals.append('MACD金叉')
            if confidence < 2:
                action = '买涨'
                confidence = 3
                stop_loss = price * 0.97
                take_profit = price * 1.06
    
    # 强势突破
    if rsi_d > 60 and change > 3:
        signals.append('强势突破')
        if confidence < 2:
            action = '买涨'
            confidence = 2
            stop_loss = price * 0.96
            take_profit = price * 1.10
    
    # 空头反弹做空
    if trend == '空头' and rsi_h > 60:
        signals.append('反弹做空')
        if confidence < 2:
            action = '买跌'
            confidence = 2
            stop_loss = high * 1.02
            take_profit = price * 0.95
    
    return {
        'symbol': ticker['symbol'],
        'price': price,
        'change_24h': change,
        'trend': trend,
        'rsi_d': rsi_d,
        'rsi_h': rsi_h,
        'signals': signals,
        'action': action,
        'confidence': confidence,
        'stop_loss': stop_loss,
        'take_profit': take_profit
    }

def load_trade_log() -> dict:
    if os.path.exists(TRADE_LOG):
        with open(TRADE_LOG, 'r') as f:
            return json.load(f)
    return {'trades': [], 'positions': {}}

def save_trade_log(log: dict):
    with open(TRADE_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'enabled': True,
        'auto_trade': False,  # 默认只提醒，不自动下单
        'min_confidence': MIN_CONFIDENCE,
        'max_positions': MAX_POSITIONS
    }

def scan_and_decide() -> List[dict]:
    """扫描市场并返回可交易信号"""
    print("🔍 扫描市场...")
    results = []
    
    for symbol in COINS:
        result = analyze_coin(symbol)
        if result and result['confidence'] >= MIN_CONFIDENCE and result['action'] != '无信号':
            results.append(result)
        time.sleep(0.1)
    
    # 按信心度排序
    results.sort(key=lambda x: x['confidence'], reverse=True)
    return results[:5]

def execute_trade(signal: dict, amount_usdt: float = 100):
    """执行模拟交易"""
    from mock_trade import MockTrade
    
    trade = MockTrade(mode='spot')
    symbol = signal['symbol'] + 'USDT'
    
    if signal['action'] == '买涨':
        result = trade.buy_market(symbol, amount_usdt, signal['price'])
    elif signal['action'] == '买跌':
        # 模拟做空（实际买入后再卖出类似逻辑）
        result = trade.buy_market(symbol, amount_usdt, signal['price'])
    
    if result['success']:
        # 记录交易
        log = load_trade_log()
        trade_id = f"Auto_{int(time.time())}"
        log['trades'].append({
            'id': trade_id,
            'time': datetime.now().isoformat(),
            'symbol': signal['symbol'],
            'action': signal['action'],
            'price': signal['price'],
            'amount': amount_usdt,
            'qty': result['order']['qty'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'confidence': signal['confidence'],
            'signals': signal['signals'],
            'status': 'open',
            'profit': 0
        })
        log['positions'][signal['symbol']] = {
            'trade_id': trade_id,
            'entry_price': signal['price'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'qty': result['order']['qty'],
            'time': datetime.now().isoformat()
        }
        save_trade_log(log)
        
        return {
            'success': True,
            'trade_id': trade_id,
            'order': result['order']
        }
    
    return {'success': False, 'error': result.get('error', 'Unknown')}

def check_positions():
    """检查持仓是否触发止损止盈"""
    log = load_trade_log()
    closed = []
    
    for symbol, pos in list(log['positions'].items()):
        ticker = get_ticker(symbol + 'USDT')
        if not ticker:
            continue
        
        price = ticker['price']
        stop_loss = pos['stop_loss']
        take_profit = pos['take_profit']
        
        # 检查是否触发
        triggered = None
        if pos['entry_price'] > price and stop_loss > 0 and price <= stop_loss:
            triggered = 'stop_loss'
        elif pos['entry_price'] < price and take_profit > 0 and price >= take_profit:
            triggered = 'take_profit'
        
        if triggered:
            # 执行卖出
            from mock_trade import MockTrade
            trade = MockTrade(mode='spot')
            
            # 找到对应交易
            for t in log['trades']:
                if t['id'] == pos['trade_id']:
                    qty = t['qty']
                    break
            
            result = trade.sell_market(symbol + 'USDT', qty=qty, current_price=price)
            
            if result['success']:
                # 更新交易记录
                for t in log['trades']:
                    if t['id'] == pos['trade_id']:
                        t['status'] = triggered
                        t['close_price'] = price
                        t['profit'] = result['order']['profit']
                        t['close_time'] = datetime.now().isoformat()
                        break
                
                del log['positions'][symbol]
                closed.append({
                    'symbol': symbol,
                    'type': triggered,
                    'price': price,
                    'profit': result['order']['profit']
                })
    
    if closed:
        save_trade_log(log)
    
    return closed

def print_report(signals: List[dict], only_actionable: bool = True):
    """打印报告"""
    config = load_config()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║     🫙 AutoTrader 报告 - {now}                      ║
╚═══════════════════════════════════════════════════════════════════╝
    auto_trade: {'开启' if config['auto_trade'] else '关闭'}
    min_confidence: {config['min_confidence']}
""")
    
    if signals:
        print(f"📊 发现 {len(signals)} 个交易机会:\n")
        for i, s in enumerate(signals):
            risk = abs(s['price'] - s['stop_loss']) / s['price'] * 100 if s['stop_loss'] else 0
            reward = abs(s['take_profit'] - s['price']) / s['price'] * 100 if s['take_profit'] else 0
            
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"#{i+1} {s['symbol']} - {' + '.join(s['signals'])}")
            print(f"   价格: ${s['price']:.4f} | 24h: {s['change_24h']:+.2f}%")
            print(f"   操作: 【{s['action']}】信心度: {'★' * s['confidence']}")
            print(f"   止损: ${s['stop_loss']:.4f} (-{risk:.1f}%)" if s['stop_loss'] else "")
            print(f"   止盈: ${s['take_profit']:.4f} (+{reward:.1f}%)" if s['take_profit'] else "")
            print()
    
    # 检查持仓
    log = load_trade_log()
    if log['positions']:
        print(f"📌 当前持仓 ({len(log['positions'])}个):")
        for symbol, pos in log['positions'].items():
            ticker = get_ticker(symbol + 'USDT')
            if ticker:
                pnl = (ticker['price'] - pos['entry_price']) / pos['entry_price'] * 100
                print(f"   {symbol}: ${ticker['price']:.4f} ({pnl:+.2f}%) | 止损${pos['stop_loss']:.4f} 止盈${pos['take_profit']:.4f}")
    
    # 检查是否触发止损止盈
    closed = check_positions()
    if closed:
        print(f"\n🔔 已触发止损止盈:")
        for c in closed:
            print(f"   {c['symbol']}: {c['type']} @ ${c['price']:.4f} | 盈亏: ${c['profit']:.2f}")
    
    print("\n⚠️ 风险提示: 模拟交易，仅供参考!")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--scan', '-s', action='store_true', help='扫描市场')
    parser.add_argument('--status', action='store_true', help='查看持仓')
    parser.add_argument('--enable-auto', action='store_true', help='开启自动交易')
    parser.add_argument('--disable-auto', action='store_true', help='关闭自动交易')
    args = parser.parse_args()
    
    if args.enable_auto:
        config = load_config()
        config['auto_trade'] = True
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print("✅ 自动交易已开启")
    
    elif args.disable_auto:
        config = load_config()
        config['auto_trade'] = False
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print("✅ 自动交易已关闭")
    
    elif args.status:
        log = load_trade_log()
        print(f"当前持仓: {len(log['positions'])}个")
        print(f"历史交易: {len(log['trades'])}笔")
        if log['positions']:
            for symbol, pos in log['positions'].items():
                print(f"  {symbol}: {pos}")
    
    else:
        signals = scan_and_decide()
        print_report(signals)
