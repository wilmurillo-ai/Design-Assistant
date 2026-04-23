#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示159611的最新K线数据
"""
import sys
import json
import os
from datetime import datetime
import pandas as pd
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加scripts目录
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# 导入数据获取函数
try:
    from chan_v6 import fetch_kline_data
    
    code = "159611"
    print(f"\n{'='*90}")
    print(f"  159611 电力ETF - 最新K线数据")
    print(f"  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*90}\n")
    
    # 获取数据
    daily_df, m30_df, m5_df, m1_df = fetch_kline_data(code)
    
    def print_klines(df, name, n=5):
        print(f"\n📊 {name} - 最新{n}根K线")
        print("-" * 90)
        print(f"{'时间':<20} {'开盘':<10} {'最高':<10} {'最低':<10} {'收盘':<10} {'成交量':<15}")
        print("-" * 90)
        
        for idx, row in df.tail(n).iterrows():
            time_str = str(row.get('time_key', row.get('time', row.get('date', 'N/A'))))[:19]
            print(f"{time_str:<20} {row['open']:<10.4f} {row['high']:<10.4f} {row['low']:<10.4f} {row['close']:<10.4f} {row.get('volume', 0):<15.0f}")
    
    # 显示各周期数据
    print_klines(daily_df, "日线 (Daily)", 5)
    print_klines(m30_df, "30分钟 (M30)", 5)
    print_klines(m5_df, "5分钟 (M5)", 5)
    print_klines(m1_df, "1分钟 (M1)", 5)
    
    # 计算均线和斐波那契
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
    
    # 日线分析
    print(f"\n\n{'='*90}")
    print(f"  均线 & 斐波那契计算")
    print(f"{'='*90}")
    
    daily_closes = daily_df['close'].values
    daily_highs = daily_df['high'].values
    daily_lows = daily_df['low'].values
    
    print(f"\n📈 日线级别")
    print(f"当前价：{daily_closes[-1]:.4f}")
    print(f"\n均线：")
    for period in [5, 13, 34, 89, 144]:
        ma = calc_ma(daily_closes, period)
        if ma:
            status = "✅ 支撑" if daily_closes[-1] > ma else "⚠️ 压力"
            print(f"  MA{period:<4} = {ma:.4f}  {status}")
    
    # 日线斐波那契
    recent_high = daily_highs[-20:].max()
    recent_low = daily_lows[-20:].min()
    print(f"\n斐波那契（{recent_high:.4f} → {recent_low:.4f}）：")
    fib = calc_fib(recent_high, recent_low)
    for level, price in fib.items():
        status = "🔴 压力" if price > daily_closes[-1] else "🟢 支撑"
        print(f"  {level:<6} = {price:.4f}  {status}")
    
    # 30分钟分析
    m30_closes = m30_df['close'].values
    m30_highs = m30_df['high'].values
    m30_lows = m30_df['low'].values
    
    print(f"\n\n📈 30分钟级别")
    print(f"当前价：{m30_closes[-1]:.4f}")
    print(f"\n均线：")
    for period in [5, 13, 34, 89]:
        ma = calc_ma(m30_closes, period)
        if ma:
            status = "✅ 支撑" if m30_closes[-1] > ma else "⚠️ 压力"
            print(f"  MA{period:<4} = {ma:.4f}  {status}")
    
    recent_high_m30 = m30_highs[-40:].max()
    recent_low_m30 = m30_lows[-40:].min()
    print(f"\n斐波那契（{recent_high_m30:.4f} → {recent_low_m30:.4f}）：")
    fib_m30 = calc_fib(recent_high_m30, recent_low_m30)
    for level, price in fib_m30.items():
        status = "🔴 压力" if price > m30_closes[-1] else "🟢 支撑"
        print(f"  {level:<6} = {price:.4f}  {status}")
    
    # 5分钟分析
    m5_closes = m5_df['close'].values
    m5_highs = m5_df['high'].values
    m5_lows = m5_df['low'].values
    
    print(f"\n\n📈 5分钟级别")
    print(f"当前价：{m5_closes[-1]:.4f}")
    print(f"\n均线：")
    for period in [5, 13, 34]:
        ma = calc_ma(m5_closes, period)
        if ma:
            status = "✅ 支撑" if m5_closes[-1] > ma else "⚠️ 压力"
            print(f"  MA{period:<4} = {ma:.4f}  {status}")
    
    recent_high_m5 = m5_highs[-100:].max()
    recent_low_m5 = m5_lows[-100:].min()
    print(f"\n斐波那契（{recent_high_m5:.4f} → {recent_low_m5:.4f}）：")
    fib_m5 = calc_fib(recent_high_m5, recent_low_m5)
    for level, price in fib_m5.items():
        status = "🔴 压力" if price > m5_closes[-1] else "🟢 支撑"
        print(f"  {level:<6} = {price:.4f}  {status}")
    
    # 1分钟分析
    m1_closes = m1_df['close'].values
    m1_highs = m1_df['high'].values
    m1_lows = m1_df['low'].values
    
    print(f"\n\n📈 1分钟级别")
    print(f"当前价：{m1_closes[-1]:.4f}")
    print(f"\n均线：")
    for period in [5, 13]:
        ma = calc_ma(m1_closes, period)
        if ma:
            status = "✅ 支撑" if m1_closes[-1] > ma else "⚠️ 压力"
            print(f"  MA{period:<4} = {ma:.4f}  {status}")
    
    recent_high_m1 = m1_highs[-100:].max()
    recent_low_m1 = m1_lows[-100:].min()
    print(f"\n斐波那契（{recent_high_m1:.4f} → {recent_low_m1:.4f}）：")
    fib_m1 = calc_fib(recent_high_m1, recent_low_m1)
    for level, price in fib_m1.items():
        status = "🔴 压力" if price > m1_closes[-1] else "🟢 支撑"
        print(f"  {level:<6} = {price:.4f}  {status}")
    
    print(f"\n\n{'='*90}\n")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
