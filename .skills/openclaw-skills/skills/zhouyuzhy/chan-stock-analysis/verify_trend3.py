#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, json
import pandas as pd
import numpy as np

def load_cache(code, period):
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
    ml = min(len(ema_f), len(ema_s))
    dif = [ema_f[i] - ema_s[i] for i in range(ml)]
    dea = [sum(dif[:signal]) / signal]
    for i in range(signal, len(dif)):
        dea.append((dif[i] - dea[-1]) * 2 / (signal + 1) + dea[-1])
    hist = [(dif[i] - dea[i-len(dea)]) * 2 for i in range(len(dea), ml)]
    return dif[-1], dea[-1], hist[-1] if hist else 0

code = '399006'
levels = [('daily','Daily'),('30','30min'),('5','5min'),('1','1min')]

for period, name in levels:
    klines = load_cache(code, period)
    if not klines:
        print(f"\n*** {name}: NO DATA ***")
        continue
    n = len(klines)

    print(f"\n{'='*80}")
    print(f"  {name} ({period}) - {n} bars")
    print(f"{'='*80}")

    # Last 10 bars
    print(f"\n  Last 10 bars:")
    for i in range(-10, 0):
        d = klines[i]
        prev_c = klines[i-1]['close'] if i > -n else d['open']
        chg = (d['close'] - prev_c) / prev_c * 100
        bar = '+' if d['close'] >= d['open'] else '-'
        print(f"    {d['datetime'][:16]} {bar} O={d['open']:8.2f} H={d['high']:8.2f} L={d['low']:8.2f} C={d['close']:8.2f} {chg:+.2f}%")

    # MACD
    closes = [k['close'] for k in klines]
    dif, dea, hist = calc_macd(closes)
    print(f"\n  MACD: DIF={dif:.3f}  DEA={dea:.3f}  HIST={hist:.3f}")
    print(f"  MACD bar: {'GREEN (Bearish)' if hist < 0 else 'RED (Bullish)'}")

    # Price trends
    c20 = [k['close'] for k in klines[-20:]]
    c10 = [k['close'] for k in klines[-10:]]
    c5 = [k['close'] for k in klines[-5:]]
    print(f"\n  Last20: {c20[0]:.2f} -> {c20[-1]:.2f} ({(c20[-1]-c20[0])/c20[0]*100:+.2f}%)")
    print(f"  Last10: {c10[0]:.2f} -> {c10[-1]:.2f} ({(c10[-1]-c10[0])/c10[0]*100:+.2f}%)")
    print(f"   Last5: {c5[0]:.2f} -> {c5[-1]:.2f} ({(c5[-1]-c5[0])/c5[0]*100:+.2f}%)")

    # High/Low order
    recent_high = max(k['high'] for k in klines[-20:])
    recent_low  = min(k['low']  for k in klines[-20:])
    hi_k = [k for k in klines[-20:] if k['high'] == recent_high][0]
    lo_k = [k for k in klines[-20:] if k['low']  == recent_low][0]
    hi_idx = klines[-20:].index(hi_k)
    lo_idx = klines[-20:].index(lo_k)
    print(f"\n  Last20 High: {recent_high:.2f} ({hi_k['datetime'][:16]}) idx={hi_idx}")
    print(f"  Last20 Low:  {recent_low:.2f} ({lo_k['datetime'][:16]}) idx={lo_idx}")
    print(f"  High/Low order: {'Low first -> UP trend' if hi_idx > lo_idx else 'High first -> DOWN trend'}")

    # Zhongshu (from chan_v6)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))
    import chan_v6
    raw, src = chan_v6.get_kline(code, period)
    if raw:
        fx = chan_v6.find_fengxing(raw)
        fxm = chan_v6.merge_fengxing(fx)
        bis = chan_v6.identify_bi(raw, fxm)
        zss = chan_v6.find_zhongshu_v2(bis)

        if zss:
            zs = zss[-1]
            zl, zh = zs['range']
            cur = klines[-1]['close']
            pos = 'IN' if zl <= cur <= zh else ('ABOVE' if cur > zh else 'BELOW')
            print(f"\n  Latest Zhongshu: {zl:.3f} - {zh:.3f}")
            print(f"  Current Price:   {cur:.3f}")
            print(f"  Position:        {pos} (dist upper: {cur-zh:+.3f}, dist lower: {cur-zl:+.3f})")

        if bis:
            print(f"\n  Last 5 strokes:")
            for bi in bis[-5:]:
                d = bi['direction']
                print(f"    {'UP' if d=='up' else 'DN'} {bi['start']['datetime'][:16]}->{bi['end']['datetime'][:16]} {bi['start_price']:.2f}->{bi['end_price']:.2f} {bi['change_pct']:+.2f}%")

        # Objective trend
        cur = klines[-1]['close']
        if zss:
            zl, zh = zss[-1]['range']
            trend = 'CONSOLIDATION' if zl <= cur <= zh else ('UP' if cur > zh else 'DOWN')
        else:
            trend = 'UP' if c5[-1] > c5[0] else 'DOWN'
        print(f"\n  *** OBJECTIVE TREND: {trend} ***")

    print()
