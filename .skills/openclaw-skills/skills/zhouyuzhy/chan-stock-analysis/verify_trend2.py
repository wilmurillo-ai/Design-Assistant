#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
严格基于原始K线数据验证趋势 —— 399006创业板指（独立版本，不导入chan_v6）
"""
import sys, os, json
from datetime import datetime
import pandas as pd
import numpy as np

# 数据获取
def get_kline_data(code, period):
    """从缓存加载数据"""
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'cache')
    cache_path = os.path.join(cache_dir, f"{code}_{period}.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('klines', [])
    return []

def calc_macd(closes, fast=12, slow=26, signal=9):
    ema_f = [sum(closes[:fast]) / fast]
    for i in range(fast, len(closes)):
        ema_f.append((closes[i] - ema_f[-1]) * 2 / (fast + 1) + ema_f[-1])
    ema_s = [sum(closes[:slow]) / slow]
    for i in range(slow, len(closes)):
        ema_s.append((closes[i] - ema_s[-1]) * 2 / (slow + 1) + ema_s[-1])
    min_len = min(len(ema_f), len(ema_s))
    dif = [ema_f[i] - ema_s[i] for i in range(min_len)]
    dea = [sum(dif[:signal]) / signal]
    for i in range(signal, len(dif)):
        dea.append((dif[i] - dea[-1]) * 2 / (signal + 1) + dea[-1])
    macd_hist = [(dif[i] - dea[i-len(dea)]) * 2 for i in range(len(dea), min_len)]
    return dif[-1], dea[-1], macd_hist[-1] if macd_hist else 0

def find_local_extremes(data, window=3):
    """找局部极值点"""
    n = len(data)
    tops, bots = [], []
    for i in range(window, n - window):
        h = data[i]['high']
        l = data[i]['low']
        is_top = all(data[i]['high'] >= data[j]['high'] for j in range(i-window, i+window+1))
        is_bot = all(data[i]['low']  <= data[j]['low']  for j in range(i-window, i+window+1))
        if is_top: tops.append(i)
        if is_bot: bots.append(i)
    return tops, bots

def main():
    code = '399006'
    levels = [('daily','日线'),('30','30分钟'),('5','5分钟'),('1','1分钟')]

    for period, name in levels:
        klines = get_kline_data(code, period)
        if not klines:
            print(f"\n❌ {name} 无数据")
            continue
        n = len(klines)

        print(f"\n{'='*80}")
        print(f"  {name}（{period}）- 共{n}根K线")
        print(f"{'='*80}")

        # 最近10根K线
        print(f"\n  最近10根K线：")
        for i in range(-10, 0):
            d = klines[i]
            prev_c = klines[i-1]['close'] if i > -n else d['open']
            chg = (d['close'] - prev_c) / prev_c * 100
            arrow = '↑' if chg > 0 else '↓' if chg < 0 else '→'
            bar = '+' if d['close'] >= d['open'] else '-'
            print(f"    {d['datetime'][:16]}  {bar} O={d['open']:8.2f} H={d['high']:8.2f} L={d['low']:8.2f} C={d['close']:8.2f}  {arrow}{abs(chg):.2f}%")

        # MACD
        closes = [k['close'] for k in klines]
        dif, dea, hist = calc_macd(closes)

        print(f"\n  -- MACD --")
        print(f"  DIF={dif:.3f}  DEA={dea:.3f}  柱={hist:.3f}")
        macd_dir = 'Green bar (Bearish)' if hist < 0 else 'Red bar (Bullish)'
        print(f"  MACD bar direction: {macd_dir}")

        # 最近20根趋势
        c20 = [k['close'] for k in klines[-20:]]
        print(f"\n  -- Objective Data --")
        print(f"  Last20 first/last: {c20[0]:.2f} -> {c20[-1]:.2f} ({'+' if c20[-1]>c20[0] else ''}{(c20[-1]-c20[0])/c20[0]*100:.2f}%)")

        # near 10
        c10 = [k['close'] for k in klines[-10:]]
        print(f"  Last10 first/last: {c10[0]:.2f} -> {c10[-1]:.2f} ({'+' if c10[-1]>c10[0] else ''}{(c10[-1]-c10[0])/c10[0]*100:.2f}%)")

        # near 5
        c5 = [k['close'] for k in klines[-5:]]
        print(f"   Last5 first/last: {c5[0]:.2f} -> {c5[-1]:.2f} ({'+' if c5[-1]>c5[0] else ''}{(c5[-1]-c5[0])/c5[0]*100:.2f}%)")

        # 高低点位置
        recent_high = max(k['high'] for k in klines[-20:])
        recent_low  = min(k['low']  for k in klines[-20:])
        hi_k = [k for k in klines[-20:] if k['high'] == recent_high][0]
        lo_k = [k for k in klines[-20:] if k['low']  == recent_low][0]
        print(f"  Last20 High: {recent_high:.2f} ({hi_k['datetime'][:16]})")
        print(f"  Last20 Low:  {recent_low:.2f} ({lo_k['datetime'][:16]})")
        
        # 高低点先后顺序
        hi_idx = klines[-20:].index(hi_k)
        lo_idx = klines[-20:].index(lo_k)
        if hi_idx > lo_idx:
            print(f"  -> Low first then High, objective trend: UP")
        else:
            print(f"  -> High first then Low, objective trend: DOWN")

        # 中枢位置
        print(f"\n  -- Zhongshu & Price --")
        # 用脚本的笔和中枢来验证
        from chan_v6 import get_kline as _get, find_fengxing, merge_fengxing, identify_bi, find_zhongshu_v2
        raw_data, src = _get(code, period)
        if raw_data:
            fx = find_fengxing(raw_data)
            fx_m = merge_fengxing(fx)
            bis = identify_bi(raw_data, fx_m)
            zss = find_zhongshu_v2(bis)

            if zss:
                zs = zss[-1]
                zl, zh = zs['range']
                cur = klines[-1]['close']
                pos = 'IN zhongshu (Consolidation)' if zl <= cur <= zh else ('ABOVE zhongshu (UP)' if cur > zh else 'BELOW zhongshu (DOWN)')
                print(f"  最新中枢：{zl:.3f} - {zh:.3f}")
                print(f"  当前价：{cur:.3f}")
                print(f"  位置：{pos}")
                print(f"  距上轨：{cur - zh:+.3f}  距下轨：{cur - zl:+.3f}")

            # 最近笔
            if bis:
            print(f"\n  -- Last 5 bi (strokes) --")
                for bi in bis[-5:]:
                    arrow = '↑' if bi['direction']=='up' else '↓'
                    print(f"    {arrow} {bi['start']['datetime'][:16]}→{bi['end']['datetime'][:16]}  {bi['start_price']:.2f}→{bi['end_price']:.2f}  {bi['change_pct']:+.2f}%")

            # 最终客观判断
            cur = klines[-1]['close']
            cur_trend = '未知'
            if zss:
                zl, zh = zss[-1]['range']
                if cur > zh:
                    cur_trend = '上升'
                elif cur < zl:
                    cur_trend = '下降'
                else:
                    cur_trend = '盘整'
            else:
                cur_trend = '上升' if c5[-1] > c5[0] else '下降'

            print(f"\n  == Objective trend: {cur_trend} ==")

if __name__ == '__main__':
    main()
