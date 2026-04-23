#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论多级别联立股票/指数行情分析 v2
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
import pandas as pd

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
import akshare as ak
import tushare as ts
import baostock as bs

TUSHARE_TOKEN = "38d141546ad7a95940b8f3ca3dcbdf5184b936c8ce517eeed9d647e6"
pro = ts.pro_api(TUSHARE_TOKEN)
bs.login()

# ========== 指数/股票名称映射 ==========

INDEX_NAMES = {
    '399001': '深证成指',
    '399006': '创业板指',
    '399300': '沪深300',
    '000001': '上证指数',
    '000016': '上证50',
    '000688': '科创50',
    '000852': '中证1000',
}

STOCK_NAMES = {}

def get_name(code):
    if code in INDEX_NAMES:
        return INDEX_NAMES[code]
    if code in STOCK_NAMES:
        return STOCK_NAMES[code]
    return code

# ========== 数据获取 ==========

def get_daily_kline(code, days=90):
    """获取日K数据"""
    index_codes = {
        '399001': 'sz.399001', '399006': 'sz.399006', '399300': 'sh.399300',
        '000001': 'sh.000001', '000016': 'sh.000016', '000688': 'sh.000688', '000852': 'sh.000852',
    }
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days+30)).strftime('%Y-%m-%d')
        
        if code in index_codes:
            rs = bs.query_history_k_data_plus(
                index_codes[code], "date,open,high,low,close,volume",
                start_date=start_date, end_date=end_date, frequency="d"
            )
            if rs.error_code != '0':
                return None
            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())
            if not data_list:
                return None
            df = pd.DataFrame(data_list, columns=rs.fields)
            klines = []
            for _, row in df.iterrows():
                try:
                    klines.append({'date': row['date'], 'open': float(row['open']), 'high': float(row['high']),
                                   'low': float(row['low']), 'close': float(row['close']), 'volume': float(row['volume'])})
                except:
                    continue
            return klines[-days:]
        
        ts_code = f"{code}.SH" if code.startswith('6') else f"{code}.SZ"
        end_t = datetime.now().strftime('%Y%m%d')
        start_t = (datetime.now() - timedelta(days=days+30)).strftime('%Y%m%d')
        df = pro.daily(ts_code=ts_code, start_date=start_t, end_date=end_t)
        if df is None or len(df) == 0:
            return None
        klines = []
        for _, row in df.iterrows():
            klines.append({'date': str(row['trade_date']), 'open': float(row['open']), 'high': float(row['high']),
                           'low': float(row['low']), 'close': float(row['close']), 'volume': float(row['vol'])})
        return klines[-days:]
    except Exception as e:
        print(f"获取日K失败: {e}", file=sys.stderr)
        return None

def get_minute_kline(code, period='30'):
    """获取分钟K数据 - 仅支持股票，指数暂不支持"""
    # 注意：baostock对指数分钟数据有限制，此处仅处理股票
    freq_map = {'1': '5', '5': '5', '15': '15', '30': '30', '60': '60'}
    freq = freq_map.get(str(period), '30')
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # 判断交易所
    if code.startswith('6') or code in ['000001', '000016', '000688', '000852', '399300']:
        bs_code = f"sh.{code}"
    else:
        bs_code = f"sz.{code}"
    
    try:
        rs = bs.query_history_k_data_plus(
            bs_code, "date,time,open,high,low,close,volume",
            start_date=start_date, end_date=end_date, frequency=freq
        )
        if rs.error_code != '0':
            return None
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        if not data_list:
            return None
        df = pd.DataFrame(data_list, columns=rs.fields)
        klines = []
        for _, row in df.iterrows():
            try:
                klines.append({'datetime': row['time'], 'open': float(row['open']), 'high': float(row['high']),
                               'low': float(row['low']), 'close': float(row['close']), 'volume': float(row['volume'])})
            except:
                continue
        return klines[-500:]
    except Exception as e:
        print(f"获取{period}分钟K失败: {e}", file=sys.stderr)
        return None

# ========== 缠论核心算法 ==========

def find_fengxing(klines):
    if len(klines) < 5:
        return []
    fengxing = []
    for i in range(2, len(klines) - 2):
        if (klines[i]['high'] > klines[i-1]['high'] and klines[i]['high'] > klines[i-2]['high'] and
            klines[i]['high'] > klines[i+1]['high'] and klines[i]['high'] > klines[i+2]['high']):
            fengxing.append({'type': 'top', 'index': i, 'price': klines[i]['high'],
                             'date': klines[i].get('date', klines[i].get('datetime', ''))})
        elif (klines[i]['low'] < klines[i-1]['low'] and klines[i]['low'] < klines[i-2]['low'] and
              klines[i]['low'] < klines[i+1]['low'] and klines[i]['low'] < klines[i+2]['low']):
            fengxing.append({'type': 'bottom', 'index': i, 'price': klines[i]['low'],
                             'date': klines[i].get('date', klines[i].get('datetime', ''))})
    return fengxing

def merge_fengxing(fengxing):
    if len(fengxing) < 2:
        return fengxing
    merged = [fengxing[0]]
    for fx in fengxing[1:]:
        last = merged[-1]
        if fx['type'] == last['type']:
            if fx['type'] == 'top' and fx['price'] > last['price']:
                merged[-1] = fx
            elif fx['type'] == 'bottom' and fx['price'] < last['price']:
                merged[-1] = fx
        else:
            merged.append(fx)
    return merged

def identify_bi(klines, fengxing):
    if len(fengxing) < 2:
        return []
    bis = []
    for i in range(len(fengxing) - 1):
        f1, f2 = fengxing[i], fengxing[i + 1]
        if f2['index'] - f1['index'] >= 5:
            bis.append({'start': f1, 'end': f2, 'direction': 'down' if f1['type'] == 'top' else 'up',
                        'start_price': f1['price'], 'end_price': f2['price'],
                        'change_pct': (f2['price'] - f1['price']) / f1['price'] * 100})
    return bis

def find_zhongshu(bis):
    if len(bis) < 3:
        return []
    zhongshus = []
    for i in range(len(bis) - 2):
        b1, b2, b3 = bis[i], bis[i+1], bis[i+2]
        if b1['direction'] == b2['direction'] == b3['direction']:
            highs = [b['end_price'] for b in [b1, b2, b3]]
            lows = [b['start_price'] for b in [b1, b2, b3]]
            high, low = min(highs), max(lows)
            if high > low:
                zhongshus.append({'range': (low, high), 'start': b1['start']['date'], 'end': b3['end']['date'],
                                  'bars': b3['end']['index'] - b1['start']['index'], 'direction': b1['direction']})
    return zhongshus

def find_trend_beichi(bis, zhongshus):
    if len(bis) < 5 or len(zhongshus) == 0:
        return None
    last_zs = zhongshus[-1]
    dir = last_zs['direction']
    trend_bis = [b for b in bis if b['direction'] == dir]
    if len(trend_bis) < 4:
        return None
    enter_bi, leave_bi = trend_bis[-2], trend_bis[-1]
    return {'enter_pct': abs(enter_bi['change_pct']), 'leave_pct': abs(leave_bi['change_pct']),
            'beichi': abs(leave_bi['change_pct']) < abs(enter_bi['change_pct'])}

def calculate_macd(klines, fast=12, slow=26, signal=9):
    closes = [k['close'] for k in klines]
    if len(closes) < slow + signal:
        return None
    ema_fast, ema_slow = [sum(closes[:fast]) / fast], [sum(closes[:slow]) / slow]
    for i in range(fast, len(closes)):
        ema_fast.append((closes[i] - ema_fast[-1]) * 2 / (fast + 1) + ema_fast[-1])
    for i in range(slow, len(closes)):
        ema_slow.append((closes[i] - ema_slow[-1]) * 2 / (slow + 1) + ema_slow[-1])
    min_len = min(len(ema_fast), len(ema_slow))
    dif = [ema_fast[i] - ema_slow[i] for i in range(min_len)]
    dea = [sum(dif[:signal]) / signal]
    for i in range(signal, len(dif)):
        dea.append((dif[i] - dea[-1]) * 2 / (signal + 1) + dea[-1])
    min_d = min(len(dif), len(dea))
    macd_hist = [(dif[i] - dea[i-min_d+len(dea)]) * 2 for i in range(min_d - len(dea) + 1, min_d)]
    return {'dif': dif[-1], 'dea': dea[-1], 'macd': macd_hist[-1] if macd_hist else 0,
            'macd_list': macd_hist[-20:] if macd_hist else [], 'trend': 'up' if macd_hist[-1] > 0 else 'down'}

def analyze_key_levels(klines, periods=[5, 13, 21, 34, 55, 89, 144]):
    closes = [k['close'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    result = {'current': closes[-1] if closes else 0,
              'recent_high': max(highs[-30:]) if len(highs) >= 30 else max(highs),
              'recent_low': min(lows[-30:]) if len(lows) >= 30 else min(lows)}
    for p in periods:
        if len(closes) >= p:
            result[f'ma{p}'] = sum(closes[-p:]) / p
    current = result['current']
    ma89, ma144 = result.get('ma89', current), result.get('ma144', current)
    result['ma89_pos'] = 'above' if current > ma89 else 'below' if current < ma89 else 'cross'
    result['ma144_pos'] = 'above' if current > ma144 else 'below' if current < ma144 else 'cross'
    result['pos_pct'] = ((current - result['recent_low']) / (result['recent_high'] - result['recent_low']) * 100
                        if result['recent_high'] != result['recent_low'] else 50)
    return result

def analyze_level(klines, level_name):
    if not klines or len(klines) < 10:
        return None
    fx_list = find_fengxing(klines)
    fx_merged = merge_fengxing(fx_list)
    bis = identify_bi(klines, fx_merged)
    zhongshus = find_zhongshu(bis)
    macd = calculate_macd(klines)
    levels = analyze_key_levels(klines)
    return {'name': level_name, 'count': len(klines), 'current': klines[-1]['close'],
            'bis': bis[-5:] if bis else [], 'zhongshus': zhongshus[-3:] if zhongshus else [],
            'macd': macd, 'levels': levels, 'direction': bis[-1]['direction'] if bis else 'unknown'}

# ========== 报告生成 ==========

def generate_report(stock_name, stock_code, daily, m30, m5, m1):
    today = datetime.now().strftime('%Y年%m月%d日')
    daily_a = analyze_level(daily, '日线')
    m30_a = analyze_level(m30, '30分钟')
    m5_a = analyze_level(m5, '5分钟')
    m1_a = analyze_level(m1, '1分钟')
    
    report = []
    report.append(f"{'='*60}")
    report.append(f"缠论多级别联立分析报告")
    report.append(f"标的：{stock_name}（{stock_code}）| {today}")
    report.append(f"{'='*60}\n")
    
    # 日线
    report.append("一、日线级别分析")
    report.append("-" * 40)
    if daily_a:
        d = daily_a
        l = d['levels']
        m = d['macd'] or {}
        report.append(f"当前价格：{l['current']:.2f}")
        ma_info = [f"MA{p}={l[f'ma{p}']:.2f}" for p in [5, 13, 21, 55, 89, 144] if f'ma{p}' in l]
        report.append(f"均线状态：{' | '.join(ma_info)}")
        report.append(f"MA89位置：{'上方' if l.get('ma89_pos') == 'above' else '下方'}")
        report.append(f"MA144位置：{'上方' if l.get('ma144_pos') == 'above' else '下方'}")
        if m:
            report.append(f"MACD状态：DIF={m['dif']:.3f}，DEA={m['dea']:.3f}，MACD柱={m['macd']:.3f}，{'多头' if m['trend'] == 'up' else '空头'}")
        report.append(f"近期趋势：{'上涨' if d['direction'] == 'up' else '下跌'}趋势")
        report.append(f"关键支撑：{l['recent_low']:.2f}")
        report.append(f"关键阻力：{l['recent_high']:.2f}")
        report.append(f"当前位置：{l['pos_pct']:.1f}%区间")
        if d['zhongshus']:
            zs = d['zhongshus'][-1]
            report.append(f"中枢区间：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
    else:
        report.append("数据不足")
    report.append("")
    
    # 30分钟
    report.append("二、30分钟级别分析")
    report.append("-" * 40)
    if m30_a:
        m = m30_a
        l = m['levels']
        macd = m['macd'] or {}
        report.append(f"当前价格：{l['current']:.2f}")
        ma_info = [f"MA{p}={l[f'ma{p}']:.2f}" for p in [5, 13, 21, 89] if f'ma{p}' in l]
        if ma_info:
            report.append(f"均线状态：{' | '.join(ma_info)}")
        if macd:
            report.append(f"MACD状态：DIF={macd['dif']:.3f}，DEA={macd['dea']:.3f}，MACD柱={macd['macd']:.3f}，{'多头' if macd['trend'] == 'up' else '空头'}")
        report.append(f"近期趋势：{'上涨' if m['direction'] == 'up' else '下跌'}趋势")
        beichi = find_trend_beichi(m['bis'], m['zhongshus'])
        if beichi:
            report.append(f"{'⚠️ 趋势背驰确认' if beichi['beichi'] else '暂无背驰'}：进入段{beichi['enter_pct']:.2f}% vs 离开段{beichi['leave_pct']:.2f}%")
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"中枢区间：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        report.append(f"近期高/低点：{l['recent_high']:.2f} / {l['recent_low']:.2f}")
    else:
        report.append("数据不足")
    report.append("")
    
    # 5分钟
    report.append("三、5分钟级别分析")
    report.append("-" * 40)
    if m5_a:
        m = m5_a
        l = m['levels']
        macd = m['macd'] or {}
        report.append(f"当前价格：{l['current']:.2f}")
        if macd:
            report.append(f"MACD状态：DIF={macd['dif']:.3f}，DEA={macd['dea']:.3f}，MACD柱={macd['macd']:.3f}，{'多头' if macd['trend'] == 'up' else '空头'}")
        report.append(f"近期趋势：{'上涨' if m['direction'] == 'up' else '下跌'}趋势")
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"中枢区间：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        report.append(f"近期高/低点：{l['recent_high']:.2f} / {l['recent_low']:.2f}")
    else:
        report.append("数据不足")
    report.append("")
    
    # 1分钟
    report.append("四、1分钟级别分析")
    report.append("-" * 40)
    if m1_a:
        m = m1_a
        l = m['levels']
        macd = m['macd'] or {}
        report.append(f"当前价格：{l['current']:.2f}")
        if macd:
            report.append(f"MACD状态：DIF={macd['dif']:.3f}，DEA={macd['dea']:.3f}，MACD柱={macd['macd']:.3f}，{'多头' if macd['trend'] == 'up' else '空头'}")
        report.append(f"近期趋势：{'上涨' if m['direction'] == 'up' else '下跌'}趋势")
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"中枢区间：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        report.append(f"近期高/低点：{l['recent_high']:.2f} / {l['recent_low']:.2f}")
        if len(m['bis']) >= 3:
            last_bi, prev_bi = m['bis'][-1], m['bis'][-2]
            if abs(last_bi['change_pct']) < abs(prev_bi['change_pct']):
                report.append(f"⚠️ 内部盘整背驰：{last_bi['change_pct']:.2f}% < {prev_bi['change_pct']:.2f}%")
    else:
        report.append("数据不足")
    report.append("")
    
    # 多级别联立
    report.append("五、多级别联立状态总结")
    report.append("-" * 40)
    if all([daily_a, m30_a, m5_a, m1_a]):
        dirs = {'日线': daily_a['direction'], '30分钟': m30_a['direction'], '5分钟': m5_a['direction'], '1分钟': m1_a['direction']}
        for k, v in dirs.items():
            report.append(f"{k}：{'上涨' if v == 'up' else '下跌'}趋势")
        if daily_a['direction'] == m30_a['direction'] == m5_a['direction']:
            report.append("⚠️ 各周期趋势同向，共振效应，中线趋势延续概率大")
        elif daily_a['direction'] != m30_a['direction']:
            report.append("⚠️ 日线与30分钟趋势背离，注意短期震荡")
    report.append("")
    
    # 走势分类
    report.append("六、走势完全分类与推演")
    report.append("-" * 40)
    if daily_a and m30_a:
        d_dir = m30_a['direction']
        d_high, d_low = daily_a['levels']['recent_high'], daily_a['levels']['recent_low']
        report.append("【分类一】（大概率 >60%）")
        if d_dir == 'down':
            report.append(f"下跌延续：价格继续向下考验{d_low:.2f}支撑")
            report.append("操作建议：空头持有或等待反弹后做空")
        else:
            report.append(f"上涨延续：价格向上测试{d_high:.2f}阻力")
            report.append("操作建议：多头持有，关注能否突破")
        report.append("")
        report.append("【分类二】（中概率 ~30%）")
        report.append(f"震荡整理：价格在{d_low:.2f} - {d_high:.2f}区间波动")
        report.append("操作建议：高抛低吸，突破后跟进")
        report.append("")
        report.append("【分类三】（小概率 <10%）")
        report.append("趋势反转：出现背驰或重大突破")
        report.append("操作建议：若出现底/顶背驰，关注反向机会")
    report.append("")
    
    # 操作策略
    report.append("七、终极操作策略")
    report.append("-" * 40)
    if m30_a:
        current = m30_a['levels']['current']
        d_high = daily_a['levels']['recent_high']
        d_low = daily_a['levels']['recent_low']
        if m30_a['direction'] == 'up':
            report.append("持有多单者：")
            report.append(f"  核心持有，止盈参考：{d_high:.2f}附近")
            report.append("  离场信号：1分钟出现顶背驰+跌破均线")
            report.append("空仓/想做多者：")
            report.append("  等待回调结束信号")
        else:
            report.append("持有多单者：")
            report.append(f"  注意风控，止损参考：{d_high:.2f}上方")
            report.append("空仓/想做空者：")
            report.append(f"  可在反弹衰竭时做空，理想区域：{d_high:.2f}附近")
            report.append(f"  止损设置：突破{d_high:.2f}时严格止损")
    report.append("")
    
    # 风险提示
    report.append("八、风险提示")
    report.append("-" * 40)
    report.append("⚠️ 本分析仅供学习参考，不构成投资建议")
    report.append("⚠️ 市场有风险，投资需谨慎")
    report.append("⚠️ 缠论学习曲线较陡，建议深入研究后再实盘")
    report.append("")
    report.append(f"{'='*60}")
    report.append(f"分析完成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"{'='*60}")
    
    return '\n'.join(report)

# ========== 主函数 ==========

def main():
    parser = argparse.ArgumentParser(description='缠论多级别联立分析')
    parser.add_argument('--code', '-c', type=str, required=True, help='股票/指数代码')
    args = parser.parse_args()
    
    code = args.code.strip()
    name = get_name(code)
    
    print(f"\n{'='*60}")
    print(f"开始获取 {name}（{code}）数据...")
    print(f"{'='*60}\n")
    
    print("正在获取日K数据...")
    daily = get_daily_kline(code, 90)
    if not daily:
        print("❌ 日K数据获取失败")
        sys.exit(1)
    print(f"日K数据：{len(daily)}根")
    
    print("正在获取30分钟K数据...")
    m30 = get_minute_kline(code, '30')
    print(f"30分钟数据：{len(m30) if m30 else 0}根")
    
    print("正在获取5分钟K数据...")
    m5 = get_minute_kline(code, '5')
    print(f"5分钟数据：{len(m5) if m5 else 0}根")
    
    print("正在获取1分钟K数据...")
    m1 = get_minute_kline(code, '1')
    print(f"1分钟数据：{len(m1) if m1 else 0}根")
    
    print("\n正在生成分析报告...\n")
    report = generate_report(name, code, daily, m30, m5, m1)
    print(report)
    
    bs.logout()

if __name__ == "__main__":
    main()
