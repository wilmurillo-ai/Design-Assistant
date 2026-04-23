#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
严格基于原始K线数据验证趋势 —— 399006创业板指
"""
import sys, os, json
from datetime import datetime
import pandas as pd
import numpy as np
import io, builtins
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
import chan_v6
chan_v6.stdout = sys.stdout
from chan_v6 import get_kline, find_fengxing, merge_fengxing, identify_bi, find_zhongshu_v2, calculate_macd, judge_trend_v2, detect_beichi_v2

code = '399006'
levels = [('daily','日线'),('30','30分钟'),('5','5分钟'),('1','1分钟')]

for period, name in levels:
    data, src = get_kline(code, period)
    if not data:
        print(f"\n❌ {name} 无数据")
        continue
    
    df_raw = pd.DataFrame(data)
    n = len(data)
    
    print(f"\n{'='*80}")
    print(f"  {name}（{period}）- 共{n}根K线")
    print(f"{'='*80}")
    
    # 最近10根K线
    print(f"\n  最近10根K线收盘价：")
    for i in range(-10, 0):
        d = data[i]
        chg = (d['close'] - data[i-1]['close']) / data[i-1]['close'] * 100 if i > -n else 0
        arrow = '↑' if chg > 0 else '↓' if chg < 0 else '→'
        print(f"    [{d['datetime'][:16]}]  开={d['open']:.2f}  高={d['high']:.2f}  低={d['low']:.2f}  收={d['close']:.2f}  {arrow}{abs(chg):.2f}%")
    
    # 缠论计算
    fx = find_fengxing(data)
    fx_merged = merge_fengxing(fx)
    bis = identify_bi(data, fx_merged)
    zss = find_zhongshu_v2(bis)
    macd = calculate_macd(data)
    beichi = detect_beichi_v2(bis, macd)
    trend = judge_trend_v2(data, bis, zss)
    
    print(f"\n  ── 缠论计算结果 ──")
    print(f"  当前价：{data[-1]['close']:.3f}")
    print(f"  脚本趋势判断：{trend}")
    
    if zss:
        last_zs = zss[-1]
        zs_low, zs_high = last_zs['range']
        print(f"  最新中枢：{zs_low:.3f} - {zs_high:.3f}")
        print(f"  中枢区间中位：{(zs_low+zs_high)/2:.3f}")
        print(f"  当前价 vs 中枢：{'在中枢内' if zs_low <= data[-1]['close'] <= zs_high else f'{'上方' if data[-1]['close'] > zs_high else '下方'}'}")
        print(f"  距中枢上轨：{data[-1]['close'] - zs_high:+.3f}")
        print(f"  距中枢下轨：{data[-1]['close'] - zs_low:+.3f}")
    
    if bis:
        last_bi = bis[-1]
        print(f"\n  最后一笔方向：{last_bi['direction']}（{last_bi['start_price']:.2f} → {last_bi['end_price']:.2f}, {last_bi['change_pct']:+.2f}%）")
        print(f"  笔的起始：{last_bi['start']['datetime'][:16]}")
        print(f"  笔的结束：{last_bi['end']['datetime'][:16]}")
    
    if macd:
        print(f"\n  MACD：DIF={macd['dif']:.3f}  DEA={macd['dea']:.3f}  柱={macd['macd']:.3f}")
        print(f"  MACD柱方向：{'红柱（多头）' if macd['macd'] > 0 else '绿柱（空头）'}")
    
    # 客观判断
    print(f"\n  ── 客观数据趋势验证 ──")
    # 方法1：最近N根K线的收盘价趋势
    closes = [d['close'] for d in data[-20:]]
    trend_20 = '上升' if closes[-1] > closes[0] else '下降' if closes[-1] < closes[0] else '持平'
    print(f"  最近20根K线收盘价趋势：{trend_20}（{closes[0]:.2f} → {closes[-1]:.2f}）")
    
    # 方法2：最近高点和低点
    recent_high = max(d['high'] for d in data[-20:])
    recent_low  = min(d['low']  for d in data[-20:])
    high_time = [d['datetime'] for d in data[-20:] if d['high'] == recent_high][0][:16]
    low_time  = [d['datetime'] for d in data[-20:] if d['low'] == recent_low][0][:16]
    print(f"  近20根最高：{recent_high:.2f}（{high_time}）")
    print(f"  近20根最低：{recent_low:.2f}（{low_time}）")
    
    # 方法3：价格在中枢的位置
    if zss:
        last_zs = zss[-1]
        zs_low, zs_high = last_zs['range']
        cur = data[-1]['close']
        if cur > zs_high:
            real_trend = "上升（已突破中枢上轨）"
        elif cur < zs_low:
            real_trend = "下降（已跌破中枢下轨）"
        else:
            real_trend = "盘整（在中枢内运行）"
        print(f"  基于中枢的客观判断：{real_trend}")
    
    if beichi:
        bc = beichi
        print(f"\n  背驰检测：{'底背驰' if bc['type']=='bottom' else '顶背驰'}（{'强' if bc['strength']=='strong' else '弱'}）")
        print(f"  进入段幅度：{bc['enter_pct']:.1f}%  离开段幅度：{bc['leave_pct']:.1f}%  比值：{bc['ratio']:.2f}")
    else:
        print(f"\n  背驰检测：无背驰信号")

    # 所有笔
    print(f"\n  ── 最近10笔 ──")
    for bi in bis[-10:]:
        arrow = '↑' if bi['direction'] == 'up' else '↓'
        print(f"    {arrow} {bi['start']['datetime'][:16]} → {bi['end']['datetime'][:16]}  ({bi['start_price']:.2f} → {bi['end_price']:.2f})  {bi['change_pct']:+.2f}%")
