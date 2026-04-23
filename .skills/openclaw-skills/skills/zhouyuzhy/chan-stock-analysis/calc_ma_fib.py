#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
159890 云计算ETF - 均线和斐波那契回撤位计算
"""
import sys
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 导入futu
try:
    from futu import OpenQuoteContext, RET_OK, KLType
except:
    print("❌ 需要安装 futu-api: pip install futu-api")
    sys.exit(1)

def fetch_kline_futu(code, ktype, num=500):
    """从Futu获取K线数据"""
    try:
        ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = ctx.get_kline(f"HK.{code}", num, ktype)
        ctx.close()
        
        if ret == RET_OK:
            return data
        else:
            return None
    except Exception as e:
        print(f"  ❌ Futu获取失败: {e}")
        return None

def calculate_ma(prices, period):
    """计算移动平均线"""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def calculate_fibonacci(high, low):
    """计算斐波那契回撤位"""
    diff = high - low
    return {
        "23.6%": high - diff * 0.236,
        "38.2%": high - diff * 0.382,
        "50%": high - diff * 0.5,
        "61.8%": high - diff * 0.618,
        "78.6%": high - diff * 0.786,
    }

def main():
    code = "159890"
    print(f"\n{'='*75}")
    print(f"  159890 云计算ETF - 均线 & 斐波那契回撤位完整分析")
    print(f"  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*75}\n")
    
    # ==================== 日线分析 ====================
    print("📊 日线级别（Daily）")
    print("-" * 75)
    
    daily_df = fetch_kline_futu(code, KLType.K_DAY, 242)
    if daily_df is not None:
        daily_closes = daily_df['close'].values
        daily_highs = daily_df['high'].values
        daily_lows = daily_df['low'].values
        
        # 计算均线
        ma5_daily = calculate_ma(daily_closes, 5)
        ma13_daily = calculate_ma(daily_closes, 13)
        ma34_daily = calculate_ma(daily_closes, 34)
        ma89_daily = calculate_ma(daily_closes, 89)
        ma144_daily = calculate_ma(daily_closes, 144)
        
        current_price_daily = daily_closes[-1]
        
        print(f"当前价：{current_price_daily:.4f}")
        print(f"\n均线系统（支撑/压力判断）：")
        print(f"  MA5   = {ma5_daily:.4f}" + (f" ✅ 支撑" if ma5_daily and current_price_daily > ma5_daily else " ⚠️ 压力"))
        print(f"  MA13  = {ma13_daily:.4f}" + (f" ✅ 支撑" if ma13_daily and current_price_daily > ma13_daily else " ⚠️ 压力"))
        print(f"  MA34  = {ma34_daily:.4f}" + (f" ✅ 支撑" if ma34_daily and current_price_daily > ma34_daily else " ⚠️ 压力"))
        print(f"  MA89  = {ma89_daily:.4f}" + (f" ✅ 支撑" if ma89_daily and current_price_daily > ma89_daily else " ⚠️ 压力"))
        print(f"  MA144 = {ma144_daily:.4f}" + (f" ✅ 支撑" if ma144_daily and current_price_daily > ma144_daily else " ⚠️ 压力"))
        
        # 计算斐波那契（取最近的显著高低点）
        recent_high = daily_highs[-20:].max()
        recent_low = daily_lows[-20:].min()
        
        print(f"\n最近20根K线高低点：")
        print(f"  高点：{recent_high:.4f}")
        print(f"  低点：{recent_low:.4f}")
        
        fib_daily = calculate_fibonacci(recent_high, recent_low)
        print(f"\n斐波那契回撤位（从{recent_high:.4f}到{recent_low:.4f}）：")
        for level, price in fib_daily.items():
            status = "🔴 压力" if price > current_price_daily else "🟢 支撑"
            print(f"  {level:>6} = {price:.4f}  {status}")
    
    # ==================== 30分钟分析 ====================
    print(f"\n\n📊 30分钟级别（M30）")
    print("-" * 75)
    
    m30_df = fetch_kline_futu(code, KLType.K_30M, 160)
    if m30_df is not None:
        m30_closes = m30_df['close'].values
        m30_highs = m30_df['high'].values
        m30_lows = m30_df['low'].values
        
        ma5_m30 = calculate_ma(m30_closes, 5)
        ma13_m30 = calculate_ma(m30_closes, 13)
        ma34_m30 = calculate_ma(m30_closes, 34)
        ma89_m30 = calculate_ma(m30_closes, 89)
        
        current_price_m30 = m30_closes[-1]
        
        print(f"当前价：{current_price_m30:.4f}")
        print(f"\n均线系统（支撑/压力判断）：")
        print(f"  MA5   = {ma5_m30:.4f}" + (f" ✅ 支撑" if ma5_m30 and current_price_m30 > ma5_m30 else " ⚠️ 压力"))
        print(f"  MA13  = {ma13_m30:.4f}" + (f" ✅ 支撑" if ma13_m30 and current_price_m30 > ma13_m30 else " ⚠️ 压力"))
        print(f"  MA34  = {ma34_m30:.4f}" + (f" ✅ 支撑" if ma34_m30 and current_price_m30 > ma34_m30 else " ⚠️ 压力"))
        print(f"  MA89  = {ma89_m30:.4f}" + (f" ✅ 支撑" if ma89_m30 and current_price_m30 > ma89_m30 else " ⚠️ 压力"))
        
        # 30分钟斐波那契
        recent_high_m30 = m30_highs[-40:].max()
        recent_low_m30 = m30_lows[-40:].min()
        
        print(f"\n最近40根K线高低点：")
        print(f"  高点：{recent_high_m30:.4f}")
        print(f"  低点：{recent_low_m30:.4f}")
        
        fib_m30 = calculate_fibonacci(recent_high_m30, recent_low_m30)
        print(f"\n斐波那契回撤位（从{recent_high_m30:.4f}到{recent_low_m30:.4f}）：")
        for level, price in fib_m30.items():
            status = "🔴 压力" if price > current_price_m30 else "🟢 支撑"
            print(f"  {level:>6} = {price:.4f}  {status}")
    
    # ==================== 5分钟分析 ====================
    print(f"\n\n📊 5分钟级别（M5）")
    print("-" * 75)
    
    m5_df = fetch_kline_futu(code, KLType.K_5M, 500)
    if m5_df is not None:
        m5_closes = m5_df['close'].values
        m5_highs = m5_df['high'].values
        m5_lows = m5_df['low'].values
        
        ma5_m5 = calculate_ma(m5_closes, 5)
        ma13_m5 = calculate_ma(m5_closes, 13)
        ma34_m5 = calculate_ma(m5_closes, 34)
        
        current_price_m5 = m5_closes[-1]
        
        print(f"当前价：{current_price_m5:.4f}")
        print(f"\n均线系统（支撑/压力判断）：")
        print(f"  MA5   = {ma5_m5:.4f}" + (f" ✅ 支撑" if ma5_m5 and current_price_m5 > ma5_m5 else " ⚠️ 压力"))
        print(f"  MA13  = {ma13_m5:.4f}" + (f" ✅ 支撑" if ma13_m5 and current_price_m5 > ma13_m5 else " ⚠️ 压力"))
        print(f"  MA34  = {ma34_m5:.4f}" + (f" ✅ 支撑" if ma34_m5 and current_price_m5 > ma34_m5 else " ⚠️ 压力"))
        
        # 5分钟斐波那契
        recent_high_m5 = m5_highs[-100:].max()
        recent_low_m5 = m5_lows[-100:].min()
        
        print(f"\n最近100根K线高低点：")
        print(f"  高点：{recent_high_m5:.4f}")
        print(f"  低点：{recent_low_m5:.4f}")
        
        fib_m5 = calculate_fibonacci(recent_high_m5, recent_low_m5)
        print(f"\n斐波那契回撤位（从{recent_high_m5:.4f}到{recent_low_m5:.4f}）：")
        for level, price in fib_m5.items():
            status = "🔴 压力" if price > current_price_m5 else "🟢 支撑"
            print(f"  {level:>6} = {price:.4f}  {status}")
    
    # ==================== 1分钟分析 ====================
    print(f"\n\n📊 1分钟级别（M1）")
    print("-" * 75)
    
    m1_df = fetch_kline_futu(code, KLType.K_1M, 500)
    if m1_df is not None:
        m1_closes = m1_df['close'].values
        m1_highs = m1_df['high'].values
        m1_lows = m1_df['low'].values
        
        ma5_m1 = calculate_ma(m1_closes, 5)
        ma13_m1 = calculate_ma(m1_closes, 13)
        
        current_price_m1 = m1_closes[-1]
        
        print(f"当前价：{current_price_m1:.4f}")
        print(f"\n均线系统（支撑/压力判断）：")
        print(f"  MA5   = {ma5_m1:.4f}" + (f" ✅ 支撑" if ma5_m1 and current_price_m1 > ma5_m1 else " ⚠️ 压力"))
        print(f"  MA13  = {ma13_m1:.4f}" + (f" ✅ 支撑" if ma13_m1 and current_price_m1 > ma13_m1 else " ⚠️ 压力"))
        
        # 1分钟斐波那契
        recent_high_m1 = m1_highs[-100:].max()
        recent_low_m1 = m1_lows[-100:].min()
        
        print(f"\n最近100根K线高低点：")
        print(f"  高点：{recent_high_m1:.4f}")
        print(f"  低点：{recent_low_m1:.4f}")
        
        fib_m1 = calculate_fibonacci(recent_high_m1, recent_low_m1)
        print(f"\n斐波那契回撤位（从{recent_high_m1:.4f}到{recent_low_m1:.4f}）：")
        for level, price in fib_m1.items():
            status = "🔴 压力" if price > current_price_m1 else "🟢 支撑"
            print(f"  {level:>6} = {price:.4f}  {status}")
    
    print(f"\n{'='*75}\n")

if __name__ == "__main__":
    main()
