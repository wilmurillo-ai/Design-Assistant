#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论多级别联立股票/指数行情分析 v5
- 数据源优先级：akshare → futu → tushare
- K线数据缓存机制：已存在的数据不重复获取
- 均线只用于支撑/压力分析，不判断多空
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
import pandas as pd
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 缓存目录
try:
    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
    os.makedirs(CACHE_DIR, exist_ok=True)
except:
    CACHE_DIR = os.path.join(os.path.expanduser('~'), '.chan_cache')

def get_cache_path(code, period):
    return os.path.join(CACHE_DIR, f"{code}_{period}.json")

def load_cache(code, period):
    cache_path = get_cache_path(code, period)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            cache_time = datetime.fromisoformat(data.get('cache_time', '2000-01-01'))
            if (datetime.now() - cache_time).total_seconds() < 24 * 3600:
                print(f"   📂 缓存命中: {len(data.get('klines', []))}根")
                return data.get('klines', []), data.get('source', 'cache')
        except:
            pass
    return None, None

def save_cache(code, period, klines, source):
    cache_path = get_cache_path(code, period)
    data = {
        'klines': klines,
        'source': source,
        'cache_time': datetime.now().isoformat()
    }
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except:
        pass


def get_data_akshare(code, period, is_index=False):
    try:
        import akshare as ak
        if period == 'daily':
            if is_index:
                symbol = f"sz{code}" if code.startswith('399') else f"sh{code}"
                df = ak.stock_zh_index_daily(symbol=symbol)
                if df is not None and len(df) > 0:
                    df = df.tail(90).sort_values('date')
                    return [{'datetime': str(row['date']), 'open': float(row['open']), 'high': float(row['high']), 'low': float(row['low']), 'close': float(row['close']), 'volume': float(row['volume'])} for _, row in df.iterrows()]
            else:
                df = ak.stock_zh_a_hist(symbol=code, period='daily', adjust='qfq')
                if df is not None and len(df) > 0:
                    df = df.tail(90).sort_values('日期')
                    return [{'datetime': str(row['日期']), 'open': float(row['开盘']), 'high': float(row['最高']), 'low': float(row['最低']), 'close': float(row['收盘']), 'volume': float(row['成交量'])} for _, row in df.iterrows()]
        else:
            if is_index:
                df = ak.index_zh_a_hist_min_em(symbol=code, period=period)
            else:
                df = ak.stock_zh_a_hist_min_em(symbol=code, period=period, adjust='qfq')
            if df is not None and len(df) > 0:
                df = df.tail(500).sort_values('时间')
                return [{'datetime': str(row['时间']), 'open': float(row['开盘']), 'high': float(row['最高']), 'low': float(row['最低']), 'close': float(row['收盘']), 'volume': float(row['成交量'])} for _, row in df.iterrows()]
        return None
    except Exception as e:
        print(f"  akshare获取{period}失败: {e}")
        return None


def get_data_futu(code, period):
    try:
        os.environ['FUTU_LOG'] = '0'
        os.environ['FUTU_LOG_LEVEL'] = '0'
        from futu import OpenQuoteContext, KLType
        from datetime import datetime, timedelta
        
        futu_code = f"SZ.{code}" if not ('.' in code) else code
        period_map = {'daily': KLType.K_DAY, '30': KLType.K_30M, '5': KLType.K_5M, '1': KLType.K_1M}
        
        if period not in period_map:
            return None
        
        # 根据周期确定数据范围
        if period == 'daily':
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif period == '30':
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == '5':
            start_date = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
        else:  # 1分钟
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        with OpenQuoteContext(host='127.0.0.1', port=11111) as ctx:
            result = ctx.request_history_kline(
                futu_code, 
                ktype=period_map[period], 
                start=start_date,
                end=end_date,
                max_count=500
            )
            ret = result[0] if isinstance(result, tuple) else result
            data = result[1] if isinstance(result, tuple) and len(result) > 1 else None
            if ret == 0 and data is not None and len(data) > 0:
                return [{'datetime': str(row['time_key']), 'open': float(row['open']), 'high': float(row['high']), 'low': float(row['low']), 'close': float(row['close']), 'volume': float(row['volume'])} for _, row in data.iterrows()]
        return None
    except Exception as e:
        print(f"  futu获取{period}失败: {e}")
        return None


def get_data_tushare(code, period):
    try:
        import tushare as ts
        pro = ts.pro_api("38d141546ad7a95940b8f3ca3dcbdf5184b936c8ce517eeed9d647e6")
        ts_code = f"{code}.SZ" if code.startswith('3') or code.startswith('0') else f"{code}.SH"
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is not None and len(df) > 0:
            df = df.sort_values('trade_date')
            klines = [{'datetime': str(row['trade_date']), 'open': float(row['open']), 'high': float(row['high']), 'low': float(row['low']), 'close': float(row['close']), 'volume': float(row['vol']) * 100} for _, row in df.iterrows()]
            return klines[-90:] if len(klines) > 90 else klines
        return None
    except Exception as e:
        print(f"  tushare获取{period}失败: {e}")
        return None


def get_kline(code, period, is_index=False, use_cache=True):
    if use_cache:
        cached_data, cache_src = load_cache(code, period)
        if cached_data:
            return cached_data, cache_src
    data = get_data_akshare(code, period, is_index)
    if data:
        if use_cache: save_cache(code, period, data, 'akshare')
        return data, 'akshare'
    data = get_data_futu(code, period)
    if data:
        if use_cache: save_cache(code, period, data, 'futu')
        return data, 'futu'
    data = get_data_tushare(code, period)
    if data:
        if use_cache: save_cache(code, period, data, 'tushare')
        return data, 'tushare'
    return None, 'none'


def analyze_ma_support_resistance(klines, ma_periods=[5, 13, 21, 34, 55, 89, 144, 233]):
    # 动态调整均线参数，根据数据量
    max_data_needed = max(ma_periods) + 10 if ma_periods else 10
    if len(klines) < max_data_needed:
        # 数据不够，分析不了所有均线，减少均线
        available_periods = [p for p in ma_periods if len(klines) >= p + 10]
        if len(available_periods) < 3:
            return None
        ma_periods = available_periods
    closes = [k['close'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    current = closes[-1]
    ma_values = {p: sum(closes[-p:]) / p for p in ma_periods if len(closes) >= p}
    if not ma_values:
        return None
    
    # 上方压力
    resistance_ma, resistance_price = None, None
    for p in sorted(ma_values.keys()):
        if ma_values[p] > current:
            resistance_ma, resistance_price = p, ma_values[p]
            break
    
    # 下方支撑
    support_ma, support_price = None, None
    for p in sorted(ma_values.keys(), reverse=True):
        if ma_values[p] < current:
            support_ma, support_price = p, ma_values[p]
            break
    
    # 历史统计
    support_counts = {p: 0 for p in ma_periods}
    resistance_counts = {p: 0 for p in ma_periods}
    for i in range(20, len(closes) - 5):
        if highs[i] == max(highs[max(0,i-5):min(len(highs),i+6)]):
            for p, ma_val in ma_values.items():
                if i < len(closes) - 5 and highs[i] > ma_val and min(closes[i:i+5]) < ma_val:
                    resistance_counts[p] += 1
        if lows[i] == min(lows[max(0,i-5):min(len(lows),i+6)]):
            for p, ma_val in ma_values.items():
                if i < len(closes) - 5 and lows[i] < ma_val and max(closes[i:i+5]) > ma_val:
                    support_counts[p] += 1
    
    # 多次支撑/压力
    strong_support = next(((p, c) for p, c in sorted(support_counts.items(), key=lambda x: -x[1]) if c >= 3), None)
    strong_resistance = next(((p, c) for p, c in sorted(resistance_counts.items(), key=lambda x: -x[1]) if c >= 3), None)
    
    # 信号判断
    signal = None
    if len(closes) >= 5 and resistance_ma and resistance_price:
        recent_closes = closes[-5:]
        if any(c > resistance_price for c in recent_closes):
            for i in range(-5, 0):
                if closes[i] > resistance_price and min(closes[i:]) > resistance_price * 0.995:
                    signal = 'bullish_breakout'
                    break
    if len(closes) >= 5 and support_ma and support_price and not signal:
        recent_closes = closes[-5:]
        if any(c < support_price for c in recent_closes):
            for i in range(-5, 0):
                if closes[i] < support_price and max(closes[i:]) < support_price * 1.005:
                    signal = 'bearish_breakdown'
                    break
    
    return {'current': current, 'ma_values': ma_values, 'resistance_ma': resistance_ma, 'resistance_price': resistance_price, 'support_ma': support_ma, 'support_price': support_price, 'strong_support': strong_support, 'strong_resistance': strong_resistance, 'signal': signal}


def format_ma_analysis(ma):
    if not ma: return "  均线：数据不足"
    lines = []
    current = ma['current']
    
    # 当前价
    lines.append(f"  当前价：{current:.3f}")
    
    # 上方压力
    if ma['resistance_ma']:
        diff_pct = (ma['resistance_price'] - current) / current * 100
        lines.append(f"  📍 上方压力：MA{ma['resistance_ma']}={ma['resistance_price']:.3f}（距当前 {diff_pct:+.2f}%）")
    else:
        lines.append(f"  📍 上方压力：无")
    
    # 下方支撑
    if ma['support_ma']:
        diff_pct = (current - ma['support_price']) / ma['support_price'] * 100
        lines.append(f"  📍 下方支撑：MA{ma['support_ma']}={ma['support_price']:.3f}（距当前 {diff_pct:+.2f}%）")
    else:
        lines.append(f"  📍 下方支撑：无")
    
    # 多次支撑
    if ma['strong_support']:
        p, c = ma['strong_support']
        ma_val = ma['ma_values'].get(p, 0)
        diff_pct = (current - ma_val) / ma_val * 100
        lines.append(f"  💪 历史多次支撑：MA{p}={ma_val:.3f}（{c}次，距当前 {diff_pct:+.2f}%）")
    
    # 多次压力
    if ma['strong_resistance']:
        p, c = ma['strong_resistance']
        ma_val = ma['ma_values'].get(p, 0)
        diff_pct = (ma_val - current) / current * 100
        lines.append(f"  💪 历史多次压力：MA{p}={ma_val:.3f}（{c}次，距当前 {diff_pct:+.2f}%）")
    
    # 信号
    if ma['signal'] == 'bullish_breakout': 
        lines.append(f"  🚀 看多信号：有效突破多次承压均线，回踩不破")
    elif ma['signal'] == 'bearish_breakdown': 
        lines.append(f"  🔻 看空信号：有效跌破多次支撑均线，回升未突破")
    
    return '\n'.join(lines)


def calculate_fibonacci(klines, lookback=30):
    if len(klines) < 5: return None
    highs = [k['high'] for k in klines[-lookback:]]
    lows = [k['low'] for k in klines[-lookback:]]
    max_high, min_low, diff = max(highs), min(lows), max(highs) - min(lows)
    if diff == 0: return None
    current = klines[-1]['close']
    trend = 'up' if current > (max_high + min_low) / 2 else 'down'
    fib_levels = {'0.236': min_low + diff * 0.236, '0.382': min_low + diff * 0.382, '0.500': min_low + diff * 0.500, '0.618': min_low + diff * 0.618}
    pos = (current - min_low) / diff
    support = next(((l, p) for l, p in sorted(fib_levels.items(), key=lambda x: x[1], reverse=True) if p < current), None)
    resistance = next(((l, p) for l, p in sorted(fib_levels.items(), key=lambda x: x[1]) if p > current), None)
    return {'high': max_high, 'low': min_low, 'current': current, 'trend': trend, 'position': pos, 'levels': fib_levels, 'support': support, 'resistance': resistance}


def find_fengxing(klines):
    if len(klines) < 5: return []
    fx = []
    for i in range(2, len(klines) - 2):
        if all(klines[i]['high'] > klines[j]['high'] for j in [i-2, i-1, i+1, i+2]):
            fx.append({'type': 'top', 'index': i, 'price': klines[i]['high'], 'datetime': klines[i]['datetime']})
        elif all(klines[i]['low'] < klines[j]['low'] for j in [i-2, i-1, i+1, i+2]):
            fx.append({'type': 'bottom', 'index': i, 'price': klines[i]['low'], 'datetime': klines[i]['datetime']})
    return fx


def merge_fengxing(fx):
    if len(fx) < 2: return fx
    merged = [fx[0]]
    for f in fx[1:]:
        last = merged[-1]
        if f['type'] == last['type']:
            if f['type'] == 'top' and f['price'] > last['price']: merged[-1] = f
            elif f['type'] == 'bottom' and f['price'] < last['price']: merged[-1] = f
        else: merged.append(f)
    return merged


def identify_bi(klines, fx):
    if len(fx) < 2: return []
    return [{'start': fx[i], 'end': fx[i+1], 'direction': 'down' if fx[i]['type'] == 'top' else 'up', 'start_price': fx[i]['price'], 'end_price': fx[i+1]['price'], 'change_pct': (fx[i+1]['price'] - fx[i]['price']) / fx[i]['price'] * 100} for i in range(len(fx) - 1) if fx[i+1]['index'] - fx[i]['index'] >= 5]


def find_zhongshu(bis):
    if len(bis) < 3: return []
    zss = []
    for i in range(len(bis) - 2):
        b1, b2, b3 = bis[i], bis[i+1], bis[i+2]
        if b1['direction'] == b2['direction'] == b3['direction']:
            highs = [b['end_price'] for b in [b1, b2, b3]]
            lows = [b['start_price'] for b in [b1, b2, b3]]
            high, low = min(highs), max(lows)
            if high > low: zss.append({'range': (low, high), 'direction': b1['direction'], 'start': b1['start']['datetime'], 'end': b3['end']['datetime']})
    return zss


def calculate_macd(klines, fast=12, slow=26, signal=9):
    closes = [k['close'] for k in klines]
    if len(closes) < slow + signal: return None
    ema_f = [sum(closes[:fast]) / fast]
    for i in range(fast, len(closes)): ema_f.append((closes[i] - ema_f[-1]) * 2 / (fast + 1) + ema_f[-1])
    ema_s = [sum(closes[:slow]) / slow]
    for i in range(slow, len(closes)): ema_s.append((closes[i] - ema_s[-1]) * 2 / (slow + 1) + ema_s[-1])
    min_len = min(len(ema_f), len(ema_s))
    dif = [ema_f[i] - ema_s[i] for i in range(min_len)]
    dea = [sum(dif[:signal]) / signal]
    for i in range(signal, len(dif)): dea.append((dif[i] - dea[-1]) * 2 / (signal + 1) + dea[-1])
    min_d = min(len(dif), len(dea))
    macd_hist = [(dif[i] - dea[i-min_d+len(dea)]) * 2 for i in range(min_d - len(dea) + 1, min_d)]
    return {'dif': dif[-1], 'dea': dea[-1], 'macd': macd_hist[-1] if macd_hist else 0, 'trend': 'up' if macd_hist[-1] > 0 else 'down' if macd_hist else 'unknown'}


def detect_beichi(bis, macd_hist_series, klines):
    """
    背驰检测：对比进入段与离开段的MACD面积
    返回: {'type': 'bottom'/'top'/None, 'strength': 'strong'/'weak', 'enter_pct': x, 'leave_pct': y, 'ratio': z}
    """
    if not bis or len(bis) < 2:
        return None
    
    # 取最后两笔同向笔（进入段 vs 离开段）
    last_bi = bis[-1]
    # 找同向的前一笔
    prev_same = None
    for b in reversed(bis[:-1]):
        if b['direction'] == last_bi['direction']:
            prev_same = b
            break
    if not prev_same:
        return None

    enter_pct = abs(prev_same['change_pct'])
    leave_pct = abs(last_bi['change_pct'])

    if leave_pct >= enter_pct:
        return None  # 无背驰

    ratio = leave_pct / enter_pct if enter_pct > 0 else 1
    strength = 'strong' if ratio < 0.5 else 'weak'
    bc_type = 'bottom' if last_bi['direction'] == 'up' else 'top'

    return {
        'type': bc_type,
        'strength': strength,
        'enter_pct': enter_pct,
        'leave_pct': leave_pct,
        'ratio': ratio
    }


def identify_buy_sell_points(bis, zss, beichi):
    """
    识别买卖点：
    - 一买：下跌趋势底背驰
    - 二买：一买后反弹+回落不破前低
    - 三买：一买后形成中枢+离开中枢后回落不回中枢
    - 一卖/二卖/三卖：同理反向
    返回: {'type': '1buy'/'2buy'/'3buy'/'1sell'/'2sell'/'3sell', 'desc': str, 'confirmed': bool}
    """
    if not bis or not beichi:
        return None

    result = []

    # ===== 买点判断 =====
    if beichi and beichi['type'] == 'bottom':
        # 一买：下跌趋势底背驰
        down_bis = [b for b in bis if b['direction'] == 'down']
        if len(down_bis) >= 2:
            result.append({
                'type': '1buy',
                'desc': f"下跌趋势底背驰（离开段{beichi['leave_pct']:.1f}% < 进入段{beichi['enter_pct']:.1f}%，强度：{'强' if beichi['strength']=='strong' else '弱'}）",
                'confirmed': beichi['strength'] == 'strong'
            })

    # 二买：一买后反弹一笔+回落一笔不破前低
    if len(bis) >= 3:
        last3 = bis[-3:]
        # 下跌→上涨→下跌，且最后下跌低点 > 第一笔下跌低点
        if (last3[0]['direction'] == 'down' and
            last3[1]['direction'] == 'up' and
            last3[2]['direction'] == 'down' and
            last3[2]['end_price'] > last3[0]['end_price']):
            result.append({
                'type': '2buy',
                'desc': f"回落不破前低（前低{last3[0]['end_price']:.3f}，当前低{last3[2]['end_price']:.3f}）",
                'confirmed': beichi is not None and beichi['type'] == 'bottom'
            })

    # 三买：中枢形成后，离开中枢的回落不回中枢
    if zss and len(bis) >= 2:
        last_zs = zss[-1]
        last_bi = bis[-1]
        if (last_bi['direction'] == 'down' and
            last_bi['end_price'] > last_zs['range'][0]):  # 回落不破中枢下沿
            result.append({
                'type': '3buy',
                'desc': f"回落不回中枢（中枢下沿{last_zs['range'][0]:.3f}，当前{last_bi['end_price']:.3f}）",
                'confirmed': beichi is not None and beichi['type'] == 'bottom'
            })

    # ===== 卖点判断 =====
    if beichi and beichi['type'] == 'top':
        # 一卖：上涨趋势顶背驰
        up_bis = [b for b in bis if b['direction'] == 'up']
        if len(up_bis) >= 2:
            result.append({
                'type': '1sell',
                'desc': f"上涨趋势顶背驰（离开段{beichi['leave_pct']:.1f}% < 进入段{beichi['enter_pct']:.1f}%，强度：{'强' if beichi['strength']=='strong' else '弱'}）",
                'confirmed': beichi['strength'] == 'strong'
            })

    # 二卖：一卖后下跌一笔+反弹一笔不破前高
    if len(bis) >= 3:
        last3 = bis[-3:]
        if (last3[0]['direction'] == 'up' and
            last3[1]['direction'] == 'down' and
            last3[2]['direction'] == 'up' and
            last3[2]['end_price'] < last3[0]['end_price']):
            result.append({
                'type': '2sell',
                'desc': f"反弹不破前高（前高{last3[0]['end_price']:.3f}，当前高{last3[2]['end_price']:.3f}）",
                'confirmed': beichi is not None and beichi['type'] == 'top'
            })

    # 三卖：中枢形成后，离开中枢的反弹不回中枢
    if zss and len(bis) >= 2:
        last_zs = zss[-1]
        last_bi = bis[-1]
        if (last_bi['direction'] == 'up' and
            last_bi['end_price'] < last_zs['range'][1]):  # 反弹不破中枢上沿
            result.append({
                'type': '3sell',
                'desc': f"反弹不回中枢（中枢上沿{last_zs['range'][1]:.3f}，当前{last_bi['end_price']:.3f}）",
                'confirmed': beichi is not None and beichi['type'] == 'top'
            })

    return result if result else None


def analyze_level(klines, level_name):
    if not klines or len(klines) < 10: return None
    fx = find_fengxing(klines)
    fx_merged = merge_fengxing(fx)
    bis = identify_bi(klines, fx_merged)
    zss = find_zhongshu(bis)
    macd = calculate_macd(klines)
    ma = analyze_ma_support_resistance(klines)
    fib = calculate_fibonacci(klines)
    direction = bis[-1]['direction'] if bis else 'unknown'

    # 背驰检测（增强版）
    beichi = detect_beichi(bis, None, klines)

    # 买卖点识别
    buy_sell_points = identify_buy_sell_points(bis, zss, beichi)

    return {
        'name': level_name,
        'count': len(klines),
        'current': klines[-1]['close'],
        'direction': direction,
        'bis': bis[-5:],
        'zhongshus': zss[-3:],
        'macd': macd,
        'ma_analysis': ma,
        'beichi': beichi,
        'buy_sell_points': buy_sell_points,
        'fib': fib
    }


def format_fib(fib):
    if not fib: return "  斐波那契：数据不足"
    lines = [f"  斐波那契回撤位（{fib['trend']}趋势）：", f"    区间：{fib['low']:.3f} - {fib['high']:.3f}", f"    当前位置：{fib['position']*100:.1f}%", f"    关键位："]
    for level in ['0.618', '0.500', '0.382', '0.236']:
        price = fib['levels'][level]
        marker = ""
        if fib['support'] and fib['support'][0] == level: marker = " ←支撑"
        elif fib['resistance'] and fib['resistance'][0] == level: marker = " ←阻力"
        lines.append(f"      {level}: {price:.3f}{marker}")
    return '\n'.join(lines)


def generate_report(name, code, daily, m30, m5, m1):
    today = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    daily_a = analyze_level(daily, '日线') if daily else None
    m30_a = analyze_level(m30, '30分钟') if m30 else None
    m5_a = analyze_level(m5, '5分钟') if m5 else None
    m1_a = analyze_level(m1, '1分钟') if m1 else None
    
    trends = {}
    if daily_a: trends['日线'] = daily_a['direction']
    if m30_a: trends['30分钟'] = m30_a['direction']
    if m5_a: trends['5分钟'] = m5_a['direction']
    if m1_a: trends['1分钟'] = m1_a['direction']
    
    up_count = sum(1 for t in trends.values() if t == 'up')
    down_count = sum(1 for t in trends.values() if t == 'down')
    resonance = 'up' if up_count >= 3 else 'down' if down_count >= 3 else 'mixed'
    resonance_level = '强' if (up_count if resonance == 'up' else down_count) == 4 else '中'
    
    divergences = []
    if daily_a and m30_a and daily_a['direction'] != m30_a['direction']:
        divergences.append(f"日线{daily_a['direction']} vs 30分钟{m30_a['direction']}")
    adjustment = trends.get('日线') == 'up' and trends.get('5分钟') == 'down'
    
    # 均线信号汇总
    all_signals = []
    for level_data in [daily_a, m30_a, m5_a, m1_a]:
        if level_data and level_data.get('ma_analysis'):
            ma_data = level_data['ma_analysis']
            if ma_data and ma_data.get('signal'):
                all_signals.append(ma_data['signal'])
    
    report = [f"{'━'*60}", f"  缠论多级别联立分析报告 v5", f"  标的：{name}（{code}）", f"  时间：{today}", f"{'━'*60}\n"]
    
    # 日线
    report.extend(["一、日线级别分析", "─"*40])
    if daily_a and daily_a.get('ma_analysis'):
        l = daily_a['ma_analysis']
        m = daily_a['macd'] or {}
        report.append(f"\n{format_ma_analysis(l)}")
        if m: report.append(f"\n  MACD：DIF={m['dif']:.3f} DEA={m['dea']:.3f} 柱={m['macd']:.3f}")
        report.append(f"  趋势：{'📈 上涨' if daily_a['direction'] == 'up' else '📉 下跌'}")
        if daily_a['zhongshus']: report.append(f"  中枢：{daily_a['zhongshus'][-1]['range'][0]:.3f} - {daily_a['zhongshus'][-1]['range'][1]:.3f}")
        if daily_a.get('beichi'): bc = daily_a['beichi']; report.append(f"  ⚡ 背驰：{'底背驰' if bc['type']=='bottom' else '顶背驰'}（{'强' if bc['strength']=='strong' else '弱'}，进入段{bc['enter_pct']:.1f}% > 离开段{bc['leave_pct']:.1f}%，比值{bc['ratio']:.0%}）")
        report.append(f"\n{format_fib(daily_a['fib'])}")
    else: report.append("  ❌ 数据不足")
    report.append("")
    
    # 30分钟
    report.extend(["二、30分钟级别分析", "─"*40])
    if m30_a and m30_a.get('ma_analysis'):
        l = m30_a['ma_analysis']
        m = m30_a['macd'] or {}
        report.append(f"\n{format_ma_analysis(l)}")
        if m: report.append(f"\n  MACD：DIF={m['dif']:.3f} DEA={m['dea']:.3f} 柱={m['macd']:.3f}")
        report.append(f"  趋势：{'📈 上涨' if m30_a['direction'] == 'up' else '📉 下跌'}")
        if m30_a['zhongshus']: report.append(f"  中枢：{m30_a['zhongshus'][-1]['range'][0]:.3f} - {m30_a['zhongshus'][-1]['range'][1]:.3f}")
        report.append(f"\n{format_fib(m30_a['fib'])}")
    else: report.append("  ❌ 数据不足")
    report.append("")
    
    # 5分钟
    report.extend(["三、5分钟级别分析", "─"*40])
    if m5_a and m5_a.get('ma_analysis'):
        l = m5_a['ma_analysis']
        m = m5_a['macd'] or {}
        report.append(f"\n{format_ma_analysis(l)}")
        if m: report.append(f"\n  MACD：DIF={m['dif']:.3f} DEA={m['dea']:.3f} 柱={m['macd']:.3f}")
        report.append(f"  趋势：{'📈 上涨' if m5_a['direction'] == 'up' else '📉 下跌'}")
        if m5_a['zhongshus']: report.append(f"  中枢：{m5_a['zhongshus'][-1]['range'][0]:.3f} - {m5_a['zhongshus'][-1]['range'][1]:.3f}")
        if len(m5_a['bis']) >= 3 and abs(m5_a['bis'][-1]['change_pct']) < abs(m5_a['bis'][-2]['change_pct']): report.append(f"  ⚠️ 盘整背驰：{m5_a['bis'][-1]['change_pct']:.2f}% < {m5_a['bis'][-2]['change_pct']:.2f}%")
        report.append(f"\n{format_fib(m5_a['fib'])}")
    else: report.append("  ❌ 数据不足")
    report.append("")
    
    # 1分钟
    report.extend(["四、1分钟级别分析", "─"*40])
    if m1_a and m1_a.get('ma_analysis'):
        l = m1_a['ma_analysis']
        m = m1_a['macd'] or {}
        report.append(f"\n{format_ma_analysis(l)}")
        if m: report.append(f"\n  MACD：DIF={m['dif']:.3f} DEA={m['dea']:.3f} 柱={m['macd']:.3f}")
        report.append(f"  趋势：{'📈 上涨' if m1_a['direction'] == 'up' else '📉 下跌'}")
        if m1_a['zhongshus']: report.append(f"  中枢：{m1_a['zhongshus'][-1]['range'][0]:.3f} - {m1_a['zhongshus'][-1]['range'][1]:.3f}")
        report.append(f"\n{format_fib(m1_a['fib'])}")
    else: report.append("  ❌ 数据不足")
    report.append("")
    
    # 五、多级别联立
    report.extend(["五、多级别联立状态总结", "━"*60])
    for level, trend in trends.items(): report.append(f"  {level}：{'📈' if trend == 'up' else '📉'} {'上涨' if trend=='up' else '下跌'}")
    report.append("")
    
    if all_signals:
        bullish, bearish = all_signals.count('bullish_breakout'), all_signals.count('bearish_breakdown')
        if bullish >= 2: report.append(f"  🚀 均线看多信号：{bullish}个级别出现有效突破")
        elif bearish >= 2: report.append(f"  🔻 均线看空信号：{bearish}个级别出现有效跌破")
        report.append("")
    
    res_text = '🔴 共振做多' if resonance == 'up' else '🟢 共振做空' if resonance == 'down' else '⚪ 震荡分化'
    report.append(f"  🔗 联立判断：{res_text}（{resonance_level}共振）")
    if divergences: [report.append(f"     - {d}") for d in divergences]
    if adjustment: report.append(f"  📊 小级别调整中，需观察能否带动大级别")
    report.append("")
    
    # 分类
    report.extend(["六、走势完全分类", "─"*40])
    if daily_a and m30_a and daily_a.get('fib'):
        d_dir = m30_a['direction']
        d_high, d_low = daily_a['fib']['high'], daily_a['fib']['low']
        if d_dir == 'up':
            report.extend([f"  【分类一】大概率 >60%", f"    上涨延续：目标{d_high:.3f}", f"    操作：多头持有，突破跟进"])
        else:
            report.extend([f"  【分类一】大概率 >60%", f"    下跌延续：目标{d_low:.3f}", f"    操作：空头持有"])
        report.extend([f"  【分类二】中概率 ~30%", f"    震荡整理：{d_low:.3f} - {d_high:.3f}", f"  【分类三】小概率 <10%", f"    趋势反转：出现背驰确认"])
    report.append("")
    
    # 策略
    report.extend(["七、终极操作策略", "─"*40])
    if m30_a:
        if resonance == 'up': report.extend([f"  持有多单：持有", f"  空仓想做多：回调至均线支撑位入场", f"  做空：暂不推荐"])
        elif resonance == 'down': report.extend([f"  持有多单：注意止损", f"  空仓想做空：反弹至均线压力位做空", f"  做多：暂不推荐"])
        else: report.append("  震荡分化：观望为主，等待共振信号明确后再操作")
    report.append("")
    
    report.extend(["八、风险提示", "─"*40, f"  ⚠️ 本分析仅供学习参考，不构成投资建议", f"  ⚠️ 市场有风险，投资需谨慎", "", f"{'━'*60}", f"  分析完成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"{'━'*60}"])
    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='缠论多级别联立分析 v5')
    parser.add_argument('--code', '-c', type=str, required=True, help='股票/指数代码')
    args = parser.parse_args()
    code = args.code.strip()
    is_index = code in ['399001', '399006', '399300', '000001', '000016', '000688', '000852']
    index_names = {'399006': '创业板指', '399001': '深证成指', '399300': '沪深300', '000001': '上证指数', '000016': '上证50', '000688': '科创50'}
    name = index_names.get(code, code)
    
    print(f"\n{'='*60}")
    print(f"  正在获取 {name}（{code}）数据...")
    print(f"  策略：akshare → futu → tushare（缓存优先）")
    print(f"{'='*60}\n")
    
    print("📊 获取日K数据...")
    daily, daily_src = get_kline(code, 'daily', is_index)
    print(f"   {'✅' if daily else '❌'} {len(daily) if daily else 0}根 (来源: {daily_src})\n")
    
    print("📊 获取30分钟K数据...")
    m30, m30_src = get_kline(code, '30', is_index)
    print(f"   {'✅' if m30 else '❌'} {len(m30) if m30 else 0}根 (来源: {m30_src})\n")
    
    print("📊 获取5分钟K数据...")
    m5, m5_src = get_kline(code, '5', is_index)
    print(f"   {'✅' if m5 else '❌'} {len(m5) if m5 else 0}根 (来源: {m5_src})\n")
    
    print("📊 获取1分钟K数据...")
    m1, m1_src = get_kline(code, '1', is_index)
    print(f"   {'✅' if m1 else '❌'} {len(m1) if m1 else 0}根 (来源: {m1_src})\n")
    
    if not all([daily, m30, m5, m1]):
        missing = [n for n, d in [('日K', daily), ('30分钟K', m30), ('5分钟K', m5), ('1分钟K', m1)] if not d]
        print(f"\n{'='*60}")
        print(f"  ❌ 分钟级数据获取失败，无法进行多级别联立分析")
        print(f"  失败数据：{', '.join(missing)}")
        print(f"{'='*60}")
        sys.exit(1)
    
    print("\n📝 生成分析报告...\n")
    print(generate_report(name, code, daily, m30, m5, m1))


if __name__ == "__main__":
    main()
