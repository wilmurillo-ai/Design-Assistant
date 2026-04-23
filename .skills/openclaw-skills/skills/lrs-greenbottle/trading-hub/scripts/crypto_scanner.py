#!/usr/bin/env python3
"""加密货币主动交易扫描器 - 主动出击创造机会

核心理念：
- 不等机会，主动发现机会
- 判断趋势顺势而为
- 超跌敢买，强势敢追
- 止损要快，止盈要狠
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

BINANCE_API = "https://api.binance.com"
COINS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
    'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
    'MATICUSDT', 'LTCUSDT', 'ATOMUSDT', 'UNIUSDT', 'XLMUSDT'
]

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
                'volume': float(d['quoteVolume']),
                'price_position': ((float(d['lastPrice']) - float(d['lowPrice'])) / (float(d['highPrice']) - float(d['lowPrice'])) * 100) if float(d['highPrice']) != float(d['lowPrice']) else 50
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
    signal = calc_ema([macd] * 9, 9) if macd != 0 else 0
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
    
    # 日线指标
    ema20_d = calc_ema(closes_d, 20)
    ema60_d = calc_ema(closes_d, 60)
    rsi_d = calc_rsi(closes_d)
    macd_d, signal_d, hist_d = calc_macd(closes_d)
    
    # 小时指标
    ema20_h = calc_ema(closes_h, 20)
    ema60_h = calc_ema(closes_h, 60)
    rsi_h = calc_rsi(closes_h)
    macd_h, signal_h, hist_h = calc_macd(closes_h)
    
    # ===== 趋势判断 =====
    trend = '震荡'
    trend_direction = 0
    
    if ema20_d > ema60_d and price > ema20_d:
        trend = '日线多头'
        trend_direction = 1
    elif ema20_d < ema60_d and price < ema20_d:
        trend = '日线空头'
        trend_direction = -1
    
    # ===== 交易信号 =====
    signals = []
    action = '无信号'
    action_type = ''
    confidence = 0
    entry_price = price
    stop_loss = 0
    take_profit = 0
    
    # 信号1: 超跌反弹 (RSI日线超卖)
    if rsi_d < 35 and change > -2:
        signals.append('超跌反弹')
        if action == '无信号' or confidence < 3:
            action = '买涨'
            action_type = '超跌反弹'
            confidence = 4
            stop_loss = low * 0.98
            take_profit = price * 1.05
    
    # 信号2: 强势币回踩支撑 (强势币 + 回踩EMA20)
    if abs(price - ema20_d) / price < 0.02 and rsi_d > 45:
        signals.append('回踩支撑')
        if confidence < 3:
            action = '买涨'
            action_type = '回踩支撑'
            confidence = 3
            stop_loss = ema20_d * 0.97
            take_profit = price * 1.08
    
    # 信号3: MACD金叉 (小时级别)
    if len(closes_h) > 26:
        prev_macd = calc_ema(closes_h[:-1], 12) - calc_ema(closes_h[:-1], 26)
        prev_signal = calc_ema([prev_macd] * 9, 9)
        if macd_h > signal_h and prev_macd <= prev_signal and hist_h > 0:
            signals.append('MACD金叉')
            if confidence < 2:
                action = '买涨'
                action_type = 'MACD金叉'
                confidence = 3
                stop_loss = price * 0.97
                take_profit = price * 1.06
    
    # 信号4: 强势突破 (RSI日线超买 + 放量)
    if rsi_d > 65 and change > 3:
        signals.append('强势突破')
        if confidence < 2:
            action = '买涨'
            action_type = '追强势'
            confidence = 2
            stop_loss = price * 0.95
            take_profit = price * 1.10
    
    # 信号5: 日线空头反弹做空
    if trend == '日线空头' and rsi_h > 60 and change > 1:
        signals.append('反弹做空')
        if confidence < 2:
            action = '买跌'
            action_type = '反弹做空'
            confidence = 2
            stop_loss = high * 1.02
            take_profit = price * 0.95
    
    # 信号6: 突破EMA60且站稳
    if price > ema60_d and price > ema20_d and rsi_d > 55:
        signals.append('趋势确立')
        if confidence < 3:
            action = '买涨'
            action_type = '趋势确立'
            confidence = 3
            stop_loss = ema60_d * 0.98
            take_profit = price * 1.12
    
    # ===== 评分 =====
    score = 0
    # 趋势加分
    if trend_direction == 1:
        score += 3
    elif trend_direction == -1:
        score += 1
    
    # RSI位置
    if 40 < rsi_d < 60:
        score += 2  # 中性偏多
    elif rsi_d < 35:
        score += 4  # 超卖加分
    elif rsi_d > 70:
        score += 1
    
    # MACD动能
    if hist_d > 0:
        score += 2
    elif hist_d < 0:
        score += 0
    
    # 强势币加分
    strong_coins = ['BTC', 'ETH', 'BNB', 'SOL']
    if ticker['symbol'] in strong_coins:
        score *= 1.2
    
    score = min(score, 10)
    
    # ===== 风险回报比 =====
    risk_reward = 0
    if stop_loss > 0 and take_profit > 0:
        risk = abs(price - stop_loss)
        reward = abs(take_profit - price)
        risk_reward = reward / risk if risk > 0 else 0
    
    return {
        'symbol': ticker['symbol'],
        'price': price,
        'change_24h': change,
        'high_24h': high,
        'low_24h': low,
        'trend': trend,
        'trend_direction': trend_direction,
        'ema20_d': ema20_d,
        'rsi_d': rsi_d,
        'rsi_h': rsi_h,
        'macd_d': macd_d,
        'hist_d': hist_d,
        'signals': signals,
        'action': action,
        'action_type': action_type,
        'confidence': confidence,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'risk_reward': risk_reward,
        'score': score,
        'volume': ticker['volume']
    }

def scan_market(coins: List[str] = None) -> List[dict]:
    if coins is None:
        coins = COINS
    
    results = []
    print(f"🔍 扫描 {len(coins)} 个币种，寻找交易机会...")
    
    for i, symbol in enumerate(coins):
        result = analyze_coin(symbol)
        if result:
            results.append(result)
        time.sleep(0.1)
    
    results.sort(key=lambda x: (x['confidence'], x['score']), reverse=True)
    for i, r in enumerate(results):
        r['rank'] = i + 1
    return results

def print_report(results: List[dict]):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 找出有信号的
    actionable = [r for r in results if r['action'] != '无信号' and r['confidence'] >= 2]
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║          🫙 主动交易信号报告 - {now}               ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    if actionable:
        print(f"📊 发现 {len(actionable)} 个交易机会:\n")
        
        for r in actionable[:5]:
            risk = abs(r['price'] - r['stop_loss']) if r['stop_loss'] else 0
            reward = abs(r['take_profit'] - r['price']) if r['take_profit'] else 0
            
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"🥇 #{r['rank']} {r['symbol']} - {r['action_type']}")
            print(f"   价格: ${r['price']:.4f} | 24h: {r['change_24h']:+.2f}%")
            print(f"   趋势: {r['trend']} | RSI日: {r['rsi_d']:.1f} | RSI时: {r['rsi_h']:.1f}")
            print(f"   信号: {' + '.join(r['signals'])}")
            print(f"   操作: 【{r['action']}】信心度: {'★' * r['confidence']}")
            if risk > 0:
                print(f"   建议: 入场 ${r['price']:.4f}")
                print(f"   止损: ${r['stop_loss']:.4f} (-{risk/r['price']*100:.1f}%)")
                print(f"   止盈: ${r['take_profit']:.4f} (+{reward/r['price']*100:.1f}%)")
                print(f"   风险回报比: 1:{r['risk_reward']:.1f}")
            print()
        
        print("💰 最佳推荐:")
        best = actionable[0]
        print(f"   {best['symbol']} - {best['action_type']}")
        print(f"   理由: {' + '.join(best['signals'])}")
        print(f"   预期收益: +{abs(best['take_profit'] - best['price'])/best['price']*100:.1f}%")
        print(f"   最大亏损: -{abs(best['price'] - best['stop_loss'])/best['price']*100:.1f}%")
        
    else:
        print("⚠️ 当前无高信心信号，市场震荡")
        print("\n📊 市场概览:")
        
        # 按趋势分类
        bull = [r for r in results if r['trend_direction'] == 1]
        bear = [r for r in results if r['trend_direction'] == -1]
        neutral = [r for r in results if r['trend_direction'] == 0]
        
        print(f"   多头币种: {len(bull)} 个")
        print(f"   空头币种: {len(bear)} 个")
        print(f"   震荡币种: {len(neutral)} 个")
        
        if bull:
            print(f"\n   强势币: {', '.join([r['symbol'] for r in bull[:5]])}")
        if bear:
            print(f"   弱势币: {', '.join([r['symbol'] for r in bear[:5]])}")
        
        print("\n🕐 建议: 等待更好的入场时机")
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 风险提示: 主动交易风险较高，请谨慎操作！
""")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', '-j', action='store_true')
    parser.add_argument('--top', '-n', type=int, default=10)
    args = parser.parse_args()
    
    results = scan_market()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)
