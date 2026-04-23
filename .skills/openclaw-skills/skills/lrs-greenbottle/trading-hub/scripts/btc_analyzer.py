#!/usr/bin/env python3
"""BTC Technical Analyzer - BTC/USDT技术分析

计算 EMA20 和 RSI14，输出交易信号
"""

import requests
import json
import sys
import datetime


BASE_URL = "https://api.binance.com"


def get_klines(symbol="BTCUSDT", interval="15m", limit=200):
    """获取K线数据"""
    url = f"{BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] API returned {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Network error: {e}")
        return None


def calculate_ema(prices, period=20):
    """计算指数移动平均线"""
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema


def calculate_rsi(prices, period=14):
    """计算相对强弱指数 RSI"""
    if len(prices) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_bollinger(prices, period=20, std_dev=2):
    """计算布林带"""
    if len(prices) < period:
        return None, None, None
    
    sma = sum(prices[-period:]) / period
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    std = variance ** 0.5
    
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    
    return upper, sma, lower


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """计算MACD"""
    if len(prices) < slow:
        return None, None, None
    
    # 计算EMA
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_val = sum(data[:period]) / period
        for price in data[period:]:
            ema_val = (price - ema_val) * multiplier + ema_val
        return ema_val
    
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    
    macd_line = ema_fast - ema_slow
    
    # Signal line (simplified - 9 period EMA of macd values)
    # For simplicity, we use the difference
    signal_line = macd_line * 0.9  # Simplified
    
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def analyze_signal(prices, ema20, rsi14, upper_boll=None, lower_boll=None):
    """分析交易信号"""
    current_price = prices[-1]
    
    # 计算最近3根K线的斜率
    slope = 0
    if len(prices) >= 4:
        for i in range(-3, 0):
            slope += prices[i+1] - prices[i]
    
    # 计算动量
    momentum = prices[-1] - prices[-15] if len(prices) >= 15 else 0
    momentum_pct = (momentum / prices[-15]) * 100 if len(prices) >= 15 else 0
    
    signals = []
    confidence_scores = []
    
    # RSI分析
    if rsi14 < 30:
        signals.append(("BUY", 85, f"RSI超卖({rsi14:.1f})"))
        confidence_scores.append(85)
    elif rsi14 > 70:
        signals.append(("SELL", 80, f"RSI超买({rsi14:.1f})"))
        confidence_scores.append(80)
    elif rsi14 < 60 and current_price > ema20 and slope > 0:
        signals.append(("BUY", 70, f"上升趋势，RSI健康({rsi14:.1f})"))
        confidence_scores.append(70)
    elif rsi14 > 50 and current_price < ema20 and slope < 0:
        signals.append(("SELL", 65, f"下降趋势({rsi14:.1f})"))
        confidence_scores.append(65)
    else:
        signals.append(("HOLD", 50, f"中性区域(RSI={rsi14:.1f})"))
        confidence_scores.append(50)
    
    # 布林带分析
    if upper_boll and lower_boll:
        boll_width = upper_boll - lower_boll
        price_pos = (current_price - lower_boll) / boll_width if boll_width > 0 else 0.5
        
        if price_pos < 0.2:
            signals.append(("BUY", 20, f"触及布林下轨"))
            confidence_scores.append(20)
        elif price_pos > 0.8:
            signals.append(("SELL", 20, f"触及布林上轨"))
            confidence_scores.append(20)
    
    # EMA趋势分析
    if current_price > ema20 and slope > 0:
        signals.append(("BUY", 15, f"价格>EMA20，趋势向上"))
    elif current_price < ema20 and slope < 0:
        signals.append(("SELL", 15, f"价格<EMA20，趋势向下"))
    
    # 动量分析
    if momentum_pct > 5:
        signals.append(("BUY", 10, f"强势动量(+{momentum_pct:.1f}%)"))
    elif momentum_pct < -5:
        signals.append(("SELL", 10, f"弱势动量({momentum_pct:.1f}%)"))
    
    # 综合判断
    buy_count = sum(1 for s, _, _ in signals if s == "BUY")
    sell_count = sum(1 for s, _, _ in signals if s == "SELL")
    hold_count = sum(1 for s, _, _ in signals if s == "HOLD")
    
    if buy_count > sell_count and buy_count > hold_count:
        final_signal = "BUY"
        avg_conf = sum(c for s, c, _ in signals if s == "BUY") / max(buy_count, 1)
    elif sell_count > buy_count and sell_count > hold_count:
        final_signal = "SELL"
        avg_conf = sum(c for s, c, _ in signals if s == "SELL") / max(sell_count, 1)
    else:
        final_signal = "HOLD"
        avg_conf = sum(c for s, c, _ in signals if s == "HOLD") / max(hold_count, 1)
    
    # 收集所有理由
    reasons = [r for _, _, r in signals if "中性" not in r]
    
    return final_signal, round(min(avg_conf, 95)), reasons


def get_signal_emoji(signal):
    """获取信号表情"""
    return {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")


def main():
    print("[BTC分析] 获取K线数据...")
    
    klines = get_klines()
    if not klines:
        print('{"signal":"ERROR","reason":"获取数据失败"}')
        sys.exit(1)
    
    # 提取收盘价
    closes = [float(k[4]) for k in klines]
    current_price = closes[-1]
    
    # 计算指标
    ema20 = calculate_ema(closes, 20)
    rsi14 = calculate_rsi(closes, 14)
    upper_boll, middle_boll, lower_boll = calculate_bollinger(closes, 20, 2)
    macd, signal, histogram = calculate_macd(closes)
    
    # 分析信号
    signal_name, confidence, reasons = analyze_signal(closes, ema20, rsi14, upper_boll, lower_boll)
    emoji = get_signal_emoji(signal_name)
    
    # 获取时间戳
    timestamp = klines[-1][0] / 1000
    dt = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # 计算涨跌
    price_change_24h = closes[-1] - closes[-96] if len(closes) >= 96 else 0
    price_change_pct_24h = (price_change_24h / closes[-96]) * 100 if len(closes) >= 96 else 0
    
    # 输出结果
    result = {
        "signal": signal_name,
        "signal_emoji": emoji,
        "confidence": confidence,
        "price": round(current_price, 2),
        "price_change_24h_pct": round(price_change_pct_24h, 2),
        "ema20": round(ema20, 2) if ema20 else 0,
        "rsi14": round(rsi14, 1) if rsi14 else 0,
        "bollinger_upper": round(upper_boll, 2) if upper_boll else 0,
        "bollinger_middle": round(middle_boll, 2) if middle_boll else 0,
        "bollinger_lower": round(lower_boll, 2) if lower_boll else 0,
        "macd": round(macd, 2) if macd else 0,
        "macd_signal": round(signal, 2) if signal else 0,
        "macd_histogram": round(histogram, 2) if histogram else 0,
        "reasons": reasons[:3],  # 最多3个理由
        "timestamp": dt,
        "klines_count": len(klines)
    }
    
    print(json.dumps(result, ensure_ascii=False))
    
    # 打印易读格式
    print(f"\n{emoji} 信号: {signal_name} (置信度: {confidence}%)")
    print(f"💰 价格: ${current_price:,.2f} ({'+' if price_change_pct_24h >= 0 else ''}{price_change_pct_24h:.2f}% 24h)")
    print(f"📊 EMA20: ${ema20:,.2f}" if ema20 else "")
    print(f"📉 RSI14: {rsi14:.1f}" if rsi14 else "")
    if upper_boll and lower_boll:
        print(f"📈 布林带: ${lower_boll:,.2f} - ${middle_boll:,.2f} - ${upper_boll:,.2f}")
    if macd is not None:
        print(f"📉 MACD: {macd:.2f} (signal: {signal:.2f}, hist: {histogram:.2f})")
    if reasons:
        print(f"💡 理由: {'; '.join(reasons[:3])}")


if __name__ == "__main__":
    main()
