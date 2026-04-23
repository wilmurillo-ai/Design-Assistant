#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示159611的最新K线数据 - 独立版本
"""
import sys
import json
import os
from datetime import datetime
import pandas as pd
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Futu导入
try:
    from futu import OpenQuoteContext, RET_OK, KLType
except:
    print("需要安装 futu-api")
    sys.exit(1)

def fetch_data(code, ktype, num):
    """获取K线数据"""
    try:
        ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = ctx.get_kline(f"HK.{code}", num, ktype)
        ctx.close()
        if ret == RET_OK:
            return data
        return None
    except Exception as e:
        print(f"Futu错误: {e}")
        return None

def calc_ma(prices, period):
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def calc_fib(high, low):
    diff = high - low
    return {
        "23.6%": high - diff * 0.236,
        "38.2%": high - diff * 0.382,
        "50%": high - diff * 0.5,
        "61.8%": high - diff * 0.618,
        "78.6%": high - diff * 0.786,
    }

def print_klines(df, name, n=5):
    print(f"\n📊 {name} - 最新{n}根K线")
    print("-" * 85)
    print(f"{'时间':<20} {'开盘':<10} {'最高':<10} {'最低':<10} {'收盘':<10} {'成交量'}")
    print("-" * 85)
    for idx, row in df.tail(n).iterrows():
        time_str = str(row.get('time_key', row.get('time', row.get('date', 'N/A'))))[:19]
        vol = row.get('volume', 0)
        print(f"{time_str:<20} {row['close']:<10.4f} {row['high']:<10.4f} {row['low']:<10.4f} {row['close']:<10.4f} {vol:>15.0f}")

# 主程序
code = "159611"
print(f"\n{'='*90}")
print(f"  159611 电力ETF - 最新K线数据")
print(f"  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*90}")

# 获取各周期数据
print("\n正在获取数据...")
daily_df = fetch_data(code, KLType.K_DAY, 250)
m30_df = fetch_data(code, KLType.K_30M, 200)
m5_df = fetch_data(code, KLType.K_5M, 500)
m1_df = fetch_data(code, KLType.K_1M, 500)

if daily_df is not None:
    print_klines(daily_df, "日线 (Daily)", 5)
    
    # 日线均线和斐波那契
    closes = daily_df['close'].values
    highs = daily_df['high'].values
    lows = daily_df['low'].values
    
    print(f"\n📈 日线级别分析")
    print(f"当前价：{closes[-1]:.4f}")
    print(f"\n均线系统：")
    for period in [5, 13, 34, 89, 144]:
        ma = calc_ma(closes, period)
        if ma:
            status = "✅ 支撑" if closes[-1] > ma else "⚠️ 压力"
            print(f"  MA{period:<4} = {ma:.4f}  {status}")
    
    recent_high = highs[-20:].max()
    recent_low = lows[-20:].min()
    print(f"\n斐波那契回撤（{recent_high:.4f} → {recent_low:.4f}）：")
    for level, price in calc_fib(recent_high, recent_low).items():
        status = "🔴 压力" if price > closes[-1] else "🟢 支撑"
        print(f"  {level:<6} = {price:.4f}  {status}")

if m30_df is not None:
    print_klines(m30_df, "30分钟 (M30)", 5)
    
    closes = m30_df['close'].values
    highs = m30_df['high'].values
    lows = m30_df['low'].values
    
    print(f"\n📈 30分钟级别分析")
    print(f"当前价：{closes[-1]:.4f}")
    print(f"\n均线系统：")
    for period in [5, 13, 34, 89]:
        ma = calc_ma(closes, period)
        if ma:
            status = "✅ 支撑" if closes[-1] > ma else "⚠️ 压力"
            print(f"  MA{period:<4} = {ma:.4f}  {status}")
    
    recent_high = highs[-40:].max()
    recent_low = lows[-40:].min()
    print(f"\n斐波那契回撤（{recent_high:.4f} → {recent_low:.4f}）：")
    for level, price in calc_fib(recent_high, recent_low).items():
        status = "🔴 压力" if price > closes[-1] else "🟢 支撑"
        print(f"  {level:<6} = {price:.4f}  {status}")

if m5_df is not None:
    print_klines(m5_df, "5分钟 (M5)", 5)
    
    closes = m5_df['close'].values
    highs = m5_df['high'].values
    lows = m5_df['low'].values
    
    print(f"\n📈 5分钟级别分析")
    print(f"当前价：{closes[-1]:.4f}")
    print(f"\n均线系统：")
    for period in [5, 13, 34]:
        ma = calc_ma(closes, period)
        if ma:
            status = "✅ 支撑" if closes[-1] > ma else "⚠️ 压力"
            print(f"  MA{period:<4} = {ma:.4f}  {status}")
    
    recent_high = highs[-100:].max()
    recent_low = lows[-100:].min()
    print(f"\n斐波那契回撤（{recent_high:.4f} → {recent_low:.4f}）：")
    for level, price in calc_fib(recent_high, recent_low).items():
        status = "🔴 压力" if price > closes[-1] else "🟢 支撑"
        print(f"  {level:<6} = {price:.4f}  {status}")

if m1_df is not None:
    print_klines(m1_df, "1分钟 (M1)", 5)
    
    closes = m1_df['close'].values
    highs = m1_df['high'].values
    lows = m1_df['low'].values
    
    print(f"\n📈 1分钟级别分析")
    print(f"当前价：{closes[-1]:.4f}")
    print(f"\n均线系统：")
    for period in [5, 13]:
        ma = calc_ma(closes, period)
        if ma:
            status = "✅ 支撑" if closes[-1] > ma else "⚠️ 压力"
            print(f"  MA{period:<4} = {ma:.4f}  {status}")
    
    recent_high = highs[-100:].max()
    recent_low = lows[-100:].min()
    print(f"\n斐波那契回撤（{recent_high:.4f} → {recent_low:.4f}）：")
    for level, price in calc_fib(recent_high, recent_low).items():
        status = "🔴 压力" if price > closes[-1] else "🟢 支撑"
        print(f"  {level:<6} = {price:.4f}  {status}")

print(f"\n{'='*90}\n")
