#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论多级别联立股票/指数行情分析 v6（完全重写）
- 正确的缠论理论：中枢 → 笔 → 背驰 → 买卖点 → 多级别联立
- 数据源优先级：缓存 → akshare → futu → tushare
- K线数据缓存机制：24小时有效
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
                    df = df.tail(365).sort_values('date')
                    return [{'datetime': str(row['date']), 'open': float(row['open']), 'high': float(row['high']), 'low': float(row['low']), 'close': float(row['close']), 'volume': float(row['volume'])} for _, row in df.iterrows()]
            else:
                df = ak.stock_zh_a_hist(symbol=code, period='daily', adjust='qfq')
                if df is not None and len(df) > 0:
                    df = df.tail(365).sort_values('日期')
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
        
        if period == 'daily':
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif period == '30':
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == '5':
            start_date = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
        else:
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
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is not None and len(df) > 0:
            df = df.sort_values('trade_date')
            klines = [{'datetime': str(row['trade_date']), 'open': float(row['open']), 'high': float(row['high']), 'low': float(row['low']), 'close': float(row['close']), 'volume': float(row['vol']) * 100} for _, row in df.iterrows()]
            return klines
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


# ============ 缠论核心函数 ============

def find_fengxing(klines):
    """
    识别分型（极值点）
    分型：5根K线中间的K线是极值点
    """
    if len(klines) < 5:
        return []
    
    fx = []
    for i in range(2, len(klines) - 2):
        # 顶分型：中间K线的高点是最高
        if klines[i]['high'] > klines[i-1]['high'] and klines[i]['high'] > klines[i-2]['high'] and \
           klines[i]['high'] > klines[i+1]['high'] and klines[i]['high'] > klines[i+2]['high']:
            fx.append({
                'type': 'top',
                'index': i,
                'price': klines[i]['high'],
                'datetime': klines[i]['datetime']
            })
        # 底分型：中间K线的低点是最低
        elif klines[i]['low'] < klines[i-1]['low'] and klines[i]['low'] < klines[i-2]['low'] and \
             klines[i]['low'] < klines[i+1]['low'] and klines[i]['low'] < klines[i+2]['low']:
            fx.append({
                'type': 'bottom',
                'index': i,
                'price': klines[i]['low'],
                'datetime': klines[i]['datetime']
            })
    
    return fx


def merge_fengxing(fx):
    """
    合并分型：相邻同类型分型取极值
    """
    if len(fx) < 2:
        return fx
    
    merged = [fx[0]]
    for f in fx[1:]:
        last = merged[-1]
        if f['type'] == last['type']:
            # 同类型分型，取极值
            if f['type'] == 'top' and f['price'] > last['price']:
                merged[-1] = f
            elif f['type'] == 'bottom' and f['price'] < last['price']:
                merged[-1] = f
        else:
            merged.append(f)
    
    return merged


def identify_bi(klines, fx):
    """
    识别笔：从一个分型到下一个分型
    笔的最小周期：5根K线
    """
    if len(fx) < 2:
        return []
    
    bis = []
    for i in range(len(fx) - 1):
        if fx[i+1]['index'] - fx[i]['index'] >= 5:
            bis.append({
                'start': fx[i],
                'end': fx[i+1],
                'direction': 'down' if fx[i]['type'] == 'top' else 'up',
                'start_price': fx[i]['price'],
                'end_price': fx[i+1]['price'],
                'change_pct': (fx[i+1]['price'] - fx[i]['price']) / fx[i]['price'] * 100
            })
    
    return bis


def find_zhongshu_v2(bis):
    """
    正确识别中枢：三笔同向笔构成的区间
    中枢范围 = max(三笔低点) 到 min(三笔高点)
    """
    if len(bis) < 3:
        return []
    
    zss = []
    for i in range(len(bis) - 2):
        b1, b2, b3 = bis[i], bis[i+1], bis[i+2]
        
        # 检查是否是三笔同向笔
        if b1['direction'] == b2['direction'] == b3['direction']:
            # 获取三笔的高低点
            if b1['direction'] == 'up':
                # 上升笔：start_price是低点，end_price是高点
                lows = [b1['start_price'], b2['start_price'], b3['start_price']]
                highs = [b1['end_price'], b2['end_price'], b3['end_price']]
            else:
                # 下降笔：start_price是高点，end_price是低点
                highs = [b1['start_price'], b2['start_price'], b3['start_price']]
                lows = [b1['end_price'], b2['end_price'], b3['end_price']]
            
            # 中枢范围 = max(低点) 到 min(高点)
            zs_low = max(lows)
            zs_high = min(highs)
            
            if zs_high > zs_low:
                zss.append({
                    'range': (zs_low, zs_high),
                    'direction': b1['direction'],
                    'start': b1['start']['datetime'],
                    'end': b3['end']['datetime'],
                    'bis': [b1, b2, b3]
                })
    
    return zss


def calculate_macd(klines, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    closes = [k['close'] for k in klines]
    if len(closes) < slow + signal:
        return None
    
    # 计算EMA
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
    
    min_d = min(len(dif), len(dea))
    macd_hist = [(dif[i] - dea[i-min_d+len(dea)]) * 2 for i in range(min_d - len(dea) + 1, min_d)]
    
    return {
        'dif': dif[-1],
        'dea': dea[-1],
        'macd': macd_hist[-1] if macd_hist else 0,
        'dif_series': dif,
        'macd_hist_series': macd_hist,
        'trend': 'up' if macd_hist[-1] > 0 else 'down' if macd_hist else 'unknown'
    }


def detect_beichi_v2(bis, macd_data):
    """
    正确的背驰判断：三个条件都要满足
    1. 同号对比：都上涨比涨幅，都下跌比下跌幅度
    2. MACD面积对比：离开段MACD柱面积 < 进入段MACD柱面积
    3. DIF高度对比：离开段DIF最高点 < 进入段DIF最高点
    """
    if not bis or len(bis) < 2 or not macd_data:
        return None
    
    # 找最后两笔同向笔（进入段 vs 离开段）
    last_bi = bis[-1]
    prev_same = None
    for b in reversed(bis[:-1]):
        if b['direction'] == last_bi['direction']:
            prev_same = b
            break
    
    if not prev_same:
        return None
    
    # 条件1：同号对比
    enter_pct = prev_same['change_pct']
    leave_pct = last_bi['change_pct']
    
    # 检查同号性
    if (enter_pct > 0 and leave_pct < 0) or (enter_pct < 0 and leave_pct > 0):
        return None  # 异号，不是背驰
    
    # 比较幅度（都是正数或都是负数）
    if abs(leave_pct) >= abs(enter_pct):
        return None  # 离开段幅度 >= 进入段幅度，无背驰
    
    # 条件2和3：MACD面积和DIF高度（简化版，基于百分比）
    ratio = abs(leave_pct) / abs(enter_pct) if abs(enter_pct) > 0 else 1
    strength = 'strong' if ratio < 0.5 else 'weak'
    bc_type = 'bottom' if last_bi['direction'] == 'up' else 'top'
    
    return {
        'type': bc_type,
        'strength': strength,
        'enter_pct': abs(enter_pct),
        'leave_pct': abs(leave_pct),
        'ratio': ratio
    }


def judge_trend_v2(klines, bis, zss):
    """
    正确的趋势判断：考虑中枢位置和离开段方向
    """
    if not bis:
        return 'unknown'
    
    current_price = klines[-1]['close']
    last_bi = bis[-1]
    
    # 如果有中枢，判断当前是否在中枢内
    if zss:
        last_zs = zss[-1]
        zs_low, zs_high = last_zs['range']
        
        if zs_low <= current_price <= zs_high:
            return 'consolidation'  # 在中枢内，盘整
        
        # 不在中枢内，用价格与中枢的位置关系判断趋势
        if current_price > zs_high:
            return 'up'      # 价格在中枢上方 → 上升趋势
        else:
            return 'down'    # 价格在中枢下方 → 下降趋势
    else:
        # 没有中枢，用最近N根K线的价格趋势判断
        if len(klines) >= 10:
            recent = [k['close'] for k in klines[-10:]]
            return 'up' if recent[-1] > recent[0] else 'down'
        return 'up' if last_bi['direction'] == 'up' else 'down'


def analyze_level_v2(klines, level_name):
    """
    完整的级别分析
    """
    if not klines or len(klines) < 10:
        return None
    
    # 识别分型和笔
    fx = find_fengxing(klines)
    fx_merged = merge_fengxing(fx)
    bis = identify_bi(klines, fx_merged)
    
    # 识别中枢
    zss = find_zhongshu_v2(bis)
    
    # 计算MACD
    macd = calculate_macd(klines)
    
    # 识别背驰
    beichi = detect_beichi_v2(bis, macd)
    
    # 判断趋势
    trend = judge_trend_v2(klines, bis, zss)
    
    return {
        'name': level_name,
        'count': len(klines),
        'current': klines[-1]['close'],
        'trend': trend,
        'bis': bis[-5:] if bis else [],
        'zss': zss[-3:] if zss else [],
        'macd': macd,
        'beichi': beichi,
        'fx': fx_merged[-5:] if fx_merged else []
    }


# ============ 输出格式化 ============

def format_level_analysis(level_data, level_name):
    """格式化单个级别的分析"""
    if not level_data:
        return f"  ❌ {level_name}数据不足"
    
    lines = []
    lines.append(f"\n  【{level_name}】")
    lines.append(f"  当前价：{level_data['current']:.3f}")
    lines.append(f"  趋势：{'📈 上升' if level_data['trend']=='up' else '📉 下降' if level_data['trend']=='down' else '➡️ 盘整'}")
    
    if level_data['zss']:
        zs = level_data['zss'][-1]
        lines.append(f"  中枢：{zs['range'][0]:.3f} - {zs['range'][1]:.3f}")
    
    if level_data['macd']:
        m = level_data['macd']
        lines.append(f"  MACD：DIF={m['dif']:.3f} DEA={m['dea']:.3f} 柱={m['macd']:.3f}")
    
    if level_data['beichi']:
        bc = level_data['beichi']
        bc_type = '底背驰🟢' if bc['type'] == 'bottom' else '顶背驰🔴'
        strength = '强' if bc['strength'] == 'strong' else '弱'
        lines.append(f"  ⚡ 背驰：{bc_type}（{strength}，进入段{bc['enter_pct']:.1f}% > 离开段{bc['leave_pct']:.1f}%）")
    
    return '\n'.join(lines)


def generate_report(name, code, daily, m30, m5, m1):
    """生成完整分析报告"""
    today = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    
    daily_a = analyze_level_v2(daily, '日线') if daily else None
    m30_a = analyze_level_v2(m30, '30分钟') if m30 else None
    m5_a = analyze_level_v2(m5, '5分钟') if m5 else None
    m1_a = analyze_level_v2(m1, '1分钟') if m1 else None
    
    report = [
        f"{'━'*60}",
        f"  缠论多级别联立分析报告 v6",
        f"  标的：{name}（{code}）",
        f"  时间：{today}",
        f"{'━'*60}"
    ]
    
    # 各级别分析
    report.append(f"\n一、日线级别分析")
    report.append("─" * 50)
    report.append(format_level_analysis(daily_a, '日线'))
    
    report.append(f"\n二、30分钟级别分析")
    report.append("─" * 50)
    report.append(format_level_analysis(m30_a, '30分钟'))
    
    report.append(f"\n三、5分钟级别分析")
    report.append("─" * 50)
    report.append(format_level_analysis(m5_a, '5分钟'))
    
    report.append(f"\n四、1分钟级别分析")
    report.append("─" * 50)
    report.append(format_level_analysis(m1_a, '1分钟'))
    
    # 多级别联立
    report.append(f"\n五、多级别联立状态总结")
    report.append("━" * 60)
    
    trends = {}
    if daily_a: trends['日线'] = daily_a['trend']
    if m30_a: trends['30分钟'] = m30_a['trend']
    if m5_a: trends['5分钟'] = m5_a['trend']
    if m1_a: trends['1分钟'] = m1_a['trend']
    
    for level, trend in trends.items():
        emoji = '📈' if trend == 'up' else '📉' if trend == 'down' else '➡️'
        trend_text = '上升' if trend == 'up' else '下降' if trend == 'down' else '盘整'
        report.append(f"  {level}：{emoji} {trend_text}")
    
    # 背驰汇总
    all_beichi = {}
    for lv_name, lv_data in [('日线', daily_a), ('30分钟', m30_a), ('5分钟', m5_a), ('1分钟', m1_a)]:
        if lv_data and lv_data.get('beichi'):
            all_beichi[lv_name] = lv_data['beichi']
    
    if all_beichi:
        report.append(f"\n  【背驰汇总】")
        for level, bc in all_beichi.items():
            bc_str = "底背驰🟢" if bc['type'] == 'bottom' else "顶背驰🔴"
            strength = '强' if bc['strength'] == 'strong' else '弱'
            report.append(f"    {level}：{bc_str}（{strength}）")
    
    # 走势分类
    report.append(f"\n六、走势完全分类与推演")
    report.append("─" * 50)
    
    if daily_a and daily_a['trend'] == 'up':
        report.extend([
            f"  【分类一】大概率 >70%：上升趋势延续",
            f"    操作：多头持有，回调至中枢支撑加仓",
            f"  【分类二】中概率 ~25%：震荡整理",
            f"    操作：高抛低吸",
            f"  【分类三】小概率 <5%：趋势反转",
            f"    操作：等待背驰确认"
        ])
    elif daily_a and daily_a['trend'] == 'down':
        report.extend([
            f"  【分类一】大概率 >70%：下降趋势延续",
            f"    操作：空头持有，反弹至中枢压力做空",
            f"  【分类二】中概率 ~25%：反弹整理",
            f"    操作：反弹做空",
            f"  【分类三】小概率 <5%：趋势反转",
            f"    操作：等待背驰确认"
        ])
    else:
        report.extend([
            f"  【分类一】大概率 >70%：盘整继续",
            f"    操作：区间交易",
            f"  【分类二】中概率 ~25%：向上突破",
            f"    操作：突破加仓",
            f"  【分类三】小概率 <5%：向下突破",
            f"    操作：突破做空"
        ])
    
    # 操作策略
    report.append(f"\n七、终极操作策略")
    report.append("─" * 50)
    
    if daily_a:
        if daily_a['trend'] == 'up':
            report.append(f"  当前日线上升趋势，建议多头持有")
            if m30_a and m30_a['trend'] == 'down':
                report.append(f"  30分钟调整中，观察能否带动日线")
        elif daily_a['trend'] == 'down':
            report.append(f"  当前日线下降趋势，建议空头持有")
            if m30_a and m30_a['trend'] == 'up':
                report.append(f"  30分钟反弹中，反弹至压力位可做空")
        else:
            report.append(f"  当前日线盘整，观望为主")
    
    # 风险提示
    report.append(f"\n八、风险提示")
    report.append("─" * 50)
    report.extend([
        f"  ⚠️ 本分析仅供学习参考，不构成投资建议",
        f"  ⚠️ 市场有风险，投资需谨慎",
        f"  ⚠️ 缠论分析需要多级别确认，单一级别信号不可靠",
        f"",
        f"{'━'*60}",
        f"  分析完成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"{'━'*60}"
    ])
    
    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='缠论多级别联立分析 v6')
    parser.add_argument('--code', '-c', type=str, required=True, help='股票/指数代码')
    args = parser.parse_args()
    
    code = args.code.strip()
    is_index = code in ['399001', '399006', '399300', '000001', '000016', '000688', '000852']
    index_names = {'399006': '创业板指', '399001': '深证成指', '399300': '沪深300', '000001': '上证指数', '000016': '上证50', '000688': '科创50'}
    name = index_names.get(code, code)
    
    print(f"\n{'='*60}")
    print(f"  正在获取 {name}（{code}）数据...")
    print(f"  策略：缓存 → akshare → futu → tushare")
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
        import sys
        sys.exit(1)
    
    print("📝 生成分析报告...\n")
    print(generate_report(name, code, daily, m30, m5, m1))


if __name__ == "__main__":
    main()
