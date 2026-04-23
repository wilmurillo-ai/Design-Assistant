#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论多级别联立股票/指数行情分析 v3
- 优先使用akshare-stock获取数据
- 备用futu-stock获取数据
- 必须获取日K+30分钟+5分钟+1分钟四级数据
- 多级别联动判断是核心
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

# ========== 数据获取 ==========

def get_data_akshare(code, period):
    """使用akshare获取K线数据"""
    try:
        import akshare as ak
        
        # 日K
        if period == 'daily':
            df = ak.stock_zh_a_hist(symbol=code, period='daily', start_date='20250101', end_date='20991231', adjust='qfq')
            if df is not None and len(df) > 0:
                df = df.tail(90)
                df = df.sort_values('日期')
                klines = []
                for _, row in df.iterrows():
                    klines.append({
                        'datetime': str(row['日期']),
                        'open': float(row['开盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'close': float(row['收盘']),
                        'volume': float(row['成交量'])
                    })
                return klines
        
        # 分钟K - 股票用 stock_zh_a_hist_min_em
        elif period in ['30', '5', '1']:
            df = ak.stock_zh_a_hist_min_em(symbol=code, period=period, adjust='qfq')
            if df is not None and len(df) > 0:
                df = df.tail(500)
                df = df.sort_values('时间')
                klines = []
                for _, row in df.iterrows():
                    klines.append({
                        'datetime': str(row['时间']),
                        'open': float(row['开盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'close': float(row['收盘']),
                        'volume': float(row['成交量'])
                    })
                return klines
        
        return None
    except Exception as e:
        print(f"  akshare获取{period}失败: {e}")
        return None


def get_data_futu(code, period):
    """使用futu-stock获取K线数据"""
    try:
        import os
        # 禁用富途日志写入
        os.environ['FUTU_LOG'] = '0'
        os.environ['FUTU_LOG_LEVEL'] = '0'
        
        # 尝试导入富途API
        from futu import OpenQuoteContext, AuType
        
        # 富途股票代码转换
        if code.startswith('6'):
            futu_code = f"SH.{code}"
        else:
            futu_code = f"SZ.{code}"
        
        # 富途K线周期映射
        period_map = {
            'daily': AuType.DAY,
            '30': AuType.K_30M,
            '5': AuType.K_5M,
            '1': AuType.K_1M
        }
        
        if period not in period_map:
            return None
        
        with OpenQuoteContext('', '') as ctx:
            ret, data = ctx.get_kline_series(futu_code, period_map[period], 500)
            if ret == 0 and data is not None:
                klines = []
                for _, row in data.iterrows():
                    klines.append({
                        'datetime': str(row['time_key']),
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'close': float(row['close']),
                        'volume': float(row['volume'])
                    })
                return klines
        return None
    except Exception as e:
        print(f"  futu获取{period}失败: {e}")
        return None


def get_kline(code, period):
    """获取K线数据 - 先akshare后futu"""
    # 先尝试akshare
    data = get_data_akshare(code, period)
    if data:
        return data
    
    # 备用futu
    print(f"  尝试futu-stock...")
    data = get_data_futu(code, period)
    return data


# ========== 缠论核心算法 ==========

def find_fengxing(klines):
    """识别分型"""
    if len(klines) < 5:
        return []
    fengxing = []
    for i in range(2, len(klines) - 2):
        if (klines[i]['high'] > klines[i-1]['high'] and klines[i]['high'] > klines[i-2]['high'] and
            klines[i]['high'] > klines[i+1]['high'] and klines[i]['high'] > klines[i+2]['high']):
            fengxing.append({'type': 'top', 'index': i, 'price': klines[i]['high'],
                             'datetime': klines[i]['datetime']})
        elif (klines[i]['low'] < klines[i-1]['low'] and klines[i]['low'] < klines[i-2]['low'] and
              klines[i]['low'] < klines[i+1]['low'] and klines[i]['low'] < klines[i+2]['low']):
            fengxing.append({'type': 'bottom', 'index': i, 'price': klines[i]['low'],
                             'datetime': klines[i]['datetime']})
    return fengxing


def merge_fengxing(fengxing):
    """合并分型"""
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
    """识别笔"""
    if len(fengxing) < 2:
        return []
    bis = []
    for i in range(len(fengxing) - 1):
        f1, f2 = fengxing[i], fengxing[i + 1]
        if f2['index'] - f1['index'] >= 5:
            bis.append({
                'start': f1, 'end': f2,
                'direction': 'down' if f1['type'] == 'top' else 'up',
                'start_price': f1['price'], 'end_price': f2['price'],
                'change_pct': (f2['price'] - f1['price']) / f1['price'] * 100
            })
    return bis


def find_zhongshu(bis):
    """识别中枢"""
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
                zhongshus.append({
                    'range': (low, high),
                    'direction': b1['direction'],
                    'start': b1['start']['datetime'],
                    'end': b3['end']['datetime']
                })
    return zhongshus


def calculate_macd(klines, fast=12, slow=26, signal=9):
    """计算MACD"""
    closes = [k['close'] for k in klines]
    if len(closes) < slow + signal:
        return None
    ema_fast = [sum(closes[:fast]) / fast]
    for i in range(fast, len(closes)):
        ema_fast.append((closes[i] - ema_fast[-1]) * 2 / (fast + 1) + ema_fast[-1])
    ema_slow = [sum(closes[:slow]) / slow]
    for i in range(slow, len(closes)):
        ema_slow.append((closes[i] - ema_slow[-1]) * 2 / (slow + 1) + ema_slow[-1])
    min_len = min(len(ema_fast), len(ema_slow))
    dif = [ema_fast[i] - ema_slow[i] for i in range(min_len)]
    dea = [sum(dif[:signal]) / signal]
    for i in range(signal, len(dif)):
        dea.append((dif[i] - dea[-1]) * 2 / (signal + 1) + dea[-1])
    min_d = min(len(dif), len(dea))
    macd_hist = [(dif[i] - dea[i-min_d+len(dea)]) * 2 for i in range(min_d - len(dea) + 1, min_d)]
    return {
        'dif': dif[-1], 'dea': dea[-1], 'macd': macd_hist[-1] if macd_hist else 0,
        'trend': 'up' if macd_hist[-1] > 0 else 'down' if macd_hist else 'unknown'
    }


def analyze_key_levels(klines):
    """分析关键位置"""
    closes = [k['close'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    current = closes[-1]
    
    result = {
        'current': current,
        'recent_high': max(highs[-30:]) if len(highs) >= 30 else max(highs),
        'recent_low': min(lows[-30:]) if len(lows) >= 30 else min(lows),
    }
    
    # 均线
    for p in [5, 13, 21, 55, 89, 144]:
        if len(closes) >= p:
            result[f'ma{p}'] = sum(closes[-p:]) / p
    
    # 位置
    if result['recent_high'] != result['recent_low']:
        result['pos_pct'] = (current - result['recent_low']) / (result['recent_high'] - result['recent_low']) * 100
    else:
        result['pos_pct'] = 50
    
    return result


def analyze_level(klines, level_name):
    """分析单个级别"""
    if not klines or len(klines) < 10:
        return None
    
    fx = find_fengxing(klines)
    fx_merged = merge_fengxing(fx)
    bis = identify_bi(klines, fx_merged)
    zhongshus = find_zhongshu(bis)
    macd = calculate_macd(klines)
    levels = analyze_key_levels(klines)
    
    # 趋势判断
    direction = bis[-1]['direction'] if bis else 'unknown'
    
    # 背驰判断
    beichi = None
    if len(bis) >= 4 and zhongshus:
        last_zs = zhongshus[-1]
        same_bis = [b for b in bis if b['direction'] == last_zs['direction']]
        if len(same_bis) >= 4:
            enter = same_bis[-2]
            leave = same_bis[-1]
            beichi = {
                'enter_pct': abs(enter['change_pct']),
                'leave_pct': abs(leave['change_pct']),
                'beichi': abs(leave['change_pct']) < abs(enter['change_pct'])
            }
    
    return {
        'name': level_name,
        'count': len(klines),
        'current': levels['current'],
        'direction': direction,
        'bis': bis[-5:] if bis else [],
        'zhongshus': zhongshus[-3:] if zhongshus else [],
        'macd': macd,
        'levels': levels,
        'beichi': beichi,
        'fx_count': len(fx_merged)
    }


# ========== 多级别联动分析 ==========

def multi_level_analysis(daily, m30, m5, m1):
    """多级别联动分析"""
    result = {}
    
    # 提取各级别趋势
    trends = {}
    if daily: trends['日线'] = daily['direction']
    if m30: trends['30分钟'] = m30['direction']
    if m5: trends['5分钟'] = m5['direction']
    if m1: trends['1分钟'] = m1['direction']
    
    # 提取MACD状态
    macd_states = {}
    if daily and daily['macd']: macd_states['日线'] = daily['macd']['trend']
    if m30 and m30['macd']: macd_states['30分钟'] = m30['macd']['trend']
    if m5 and m5['macd']: macd_states['5分钟'] = m5['macd']['trend']
    if m1 and m1['macd']: macd_states['1分钟'] = m1['macd']['trend']
    
    # 判断共振
    up_count = sum(1 for t in trends.values() if t == 'up')
    down_count = sum(1 for t in trends.values() if t == 'down')
    
    if up_count >= 3:
        resonance = 'up'
        resonance_level = '强' if up_count == 4 else '中'
    elif down_count >= 3:
        resonance = 'down'
        resonance_level = '强' if down_count == 4 else '中'
    else:
        resonance = 'mixed'
        resonance_level = '弱'
    
    # 背离判断
    divergences = []
    
    # 日线与30分钟背离
    if daily and m30 and daily['direction'] != m30['direction']:
        divergences.append(f"日线{maily['direction']} vs 30分钟{m30['direction']}")
    
    # 小级别是否形成调整
    adjustment = False
    if m5 and m1:
        if trends.get('日线') == 'up' and trends.get('5分钟') == 'down':
            adjustment = True
            divergences.append("小级别调整信号")
        elif trends.get('日线') == 'down' and trends.get('5分钟') == 'up':
            divergences.append("小级别反弹信号")
    
    return {
        'trends': trends,
        'macd_states': macd_states,
        'resonance': resonance,
        'resonance_level': resonance_level,
        'divergences': divergences,
        'adjustment': adjustment
    }


# ========== 报告生成 ==========

def generate_report(stock_name, stock_code, daily, m30, m5, m1):
    """生成完整分析报告"""
    today = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    
    # 多级别分析
    daily_a = analyze_level(daily, '日线') if daily else None
    m30_a = analyze_level(m30, '30分钟') if m30 else None
    m5_a = analyze_level(m5, '5分钟') if m5 else None
    m1_a = analyze_level(m1, '1分钟') if m1 else None
    
    # 多级别联动
    ml = multi_level_analysis(daily, m30, m5, m1)
    
    report = []
    report.append(f"{'━'*60}")
    report.append(f"  缠论多级别联立分析报告")
    report.append(f"  标的：{stock_name}（{stock_code}）")
    report.append(f"  时间：{today}")
    report.append(f"{'━'*60}\n")
    
    # 一、日线
    report.append(f"{'一','、'}日线级别分析")
    report.append(f"{'─'*40}")
    if daily_a:
        d = daily_a
        l = d['levels']
        m = d['macd'] or {}
        report.append(f"  当前价格：{l['current']:.2f}")
        ma_info = [f"MA{p}={l[f'ma{p}']:.2f}" for p in [5, 13, 21, 55, 89, 144] if f'ma{p}' in l]
        report.append(f"  均线：{' | '.join(ma_info)}")
        if m:
            report.append(f"  MACD：DIF={m['dif']:.3f} DEA={m['dea']:.3f} 柱={m['macd']:.3f}")
            report.append(f"      {'🔴 多头' if m['trend'] == 'up' else '🟢 空头'}")
        report.append(f"  趋势：{'📈 上涨' if d['direction'] == 'up' else '📉 下跌'}")
        if d['zhongshus']:
            zs = d['zhongshus'][-1]
            report.append(f"  中枢：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        if d['beichi']:
            bc = d['beichi']
            if bc['beichi']:
                report.append(f"  ⚠️ 背驰：进入{bc['enter_pct']:.2f}% > 离开{bc['leave_pct']:.2f}%")
            else:
                report.append(f"  暂无背驰")
        report.append(f"  位置：{l['pos_pct']:.1f}%（{l['recent_low']:.2f} - {l['recent_high']:.2f}）")
    else:
        report.append("  ❌ 数据不足")
    report.append("")
    
    # 二、30分钟
    report.append(f"{'二','、'}30分钟级别分析")
    report.append(f"{'─'*40}")
    if m30_a:
        m = m30_a
        l = m['levels']
        macd = m['macd'] or {}
        report.append(f"  当前价格：{l['current']:.2f}")
        if macd:
            report.append(f"  MACD：DIF={macd['dif']:.3f} DEA={macd['dea']:.3f} 柱={macd['macd']:.3f}")
            report.append(f"      {'🔴 多头' if macd['trend'] == 'up' else '🟢 空头'}")
        report.append(f"  趋势：{'📈 上涨' if m['direction'] == 'up' else '📉 下跌'}")
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"  中枢：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        if m['beichi'] and m['beichi']['beichi']:
            bc = m['beichi']
            report.append(f"  ⚠️ 背驰：进入{bc['enter_pct']:.2f}% > 离开{bc['leave_pct']:.2f}%")
    else:
        report.append("  ❌ 数据不足")
    report.append("")
    
    # 三、5分钟
    report.append(f"{'三','、'}5分钟级别分析")
    report.append(f"{'─'*40}")
    if m5_a:
        m = m5_a
        l = m['levels']
        macd = m['macd'] or {}
        report.append(f"  当前价格：{l['current']:.2f}")
        if macd:
            report.append(f"  MACD：DIF={macd['dif']:.3f} DEA={macd['dea']:.3f} 柱={macd['macd']:.3f}")
            report.append(f"      {'🔴 多头' if macd['trend'] == 'up' else '🟢 空头'}")
        report.append(f"  趋势：{'📈 上涨' if m['direction'] == 'up' else '📉 下跌'}")
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"  中枢：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        if len(m['bis']) >= 3:
            last_bi = m['bis'][-1]
            prev_bi = m['bis'][-2]
            if abs(last_bi['change_pct']) < abs(prev_bi['change_pct']):
                report.append(f"  ⚠️ 盘整背驰：{last_bi['change_pct']:.2f}% < {prev_bi['change_pct']:.2f}%")
    else:
        report.append("  ❌ 数据不足")
    report.append("")
    
    # 四、1分钟
    report.append(f"{'四','、'}1分钟级别分析")
    report.append(f"{'─'*40}")
    if m1_a:
        m = m1_a
        l = m['levels']
        macd = m['macd'] or {}
        report.append(f"  当前价格：{l['current']:.2f}")
        if macd:
            report.append(f"  MACD：DIF={macd['dif']:.3f} DEA={macd['dea']:.3f} 柱={macd['macd']:.3f}")
            report.append(f"      {'🔴 多头' if macd['trend'] == 'up' else '🟢 空头'}")
        report.append(f"  趋势：{'📈 上涨' if m['direction'] == 'up' else '📉 下跌'}")
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"  中枢：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        if len(m['bis']) >= 3:
            last_bi = m['bis'][-1]
            prev_bi = m['bis'][-2]
            if abs(last_bi['change_pct']) < abs(prev_bi['change_pct']):
                report.append(f"  ⚠️ 盘整背驰：{last_bi['change_pct']:.2f}% < {prev_bi['change_pct']:.2f}%")
    else:
        report.append("  ❌ 数据不足")
    report.append("")
    
    # 五、多级别联立
    report.append(f"{'五','、'}多级别联立状态总结")
    report.append(f"{'━'*60}")
    for level, trend in ml['trends'].items():
        emoji = '📈' if trend == 'up' else '📉'
        report.append(f"  {level}：{emoji} {'上涨' if trend=='up' else '下跌'}")
    report.append("")
    
    res_text = '🔴 共振做多' if ml['resonance'] == 'up' else '🟢 共振做空' if ml['resonance'] == 'down' else '⚪ 震荡分化'
    report.append(f"  🔗 联立判断：{res_text}（{ml['resonance_level']}共振）")
    
    if ml['divergences']:
        report.append(f"  ⚠️ 背离信号：")
        for div in ml['divergences']:
            report.append(f"     - {div}")
    
    if ml['adjustment']:
        report.append(f"  📊 小级别调整中，需观察能否带动大级别")
    report.append("")
    
    # 六、走势分类
    report.append(f"{'六','、'}走势完全分类")
    report.append(f"{'─'*40}")
    if daily_a and m30_a:
        d_dir = m30_a['direction']
        d_high = daily_a['levels']['recent_high']
        d_low = daily_a['levels']['recent_low']
        
        report.append(f"  【分类一】大概率 >60%")
        if d_dir == 'up':
            report.append(f"    上涨延续：目标{d_high:.2f}")
            report.append(f"    操作：多头持有，突破跟进")
        else:
            report.append(f"    下跌延续：目标{d_low:.2f}")
            report.append(f"    操作：空头持有，等待反弹做空")
        
        report.append(f"  【分类二】中概率 ~30%")
        report.append(f"    震荡整理：{d_low:.2f} - {d_high:.2f}")
        report.append(f"    操作：高抛低吸")
        
        report.append(f"  【分类三】小概率 <10%")
        report.append(f"    趋势反转：出现背驰确认")
        report.append(f"    操作：反向操作")
    report.append("")
    
    # 七、操作策略
    report.append(f"{'七','、'}终极操作策略")
    report.append(f"{'─'*40}")
    if m30_a:
        if ml['resonance'] == 'up':
            report.append(f"  持有多单：持有，止盈{daily_a['levels']['recent_high']:.2f}")
            report.append(f"  空仓想做多：回调结束入场")
            report.append(f"  做空：暂不推荐，共振做多")
        elif ml['resonance'] == 'down':
            report.append(f"  持有多单：注意止损")
            report.append(f"  空仓想做空：反弹衰竭做空")
            report.append(f"  做多：暂不推荐，等待企稳")
        else:
            report.append(f"  震荡分化：观望为主")
            report.append(f"  等待共振信号明确后再操作")
    report.append("")
    
    # 八、风险
    report.append(f"{'八','、'}风险提示")
    report.append(f"{'─'*40}")
    report.append(f"  ⚠️ 本分析仅供学习参考，不构成投资建议")
    report.append(f"  ⚠️ 市场有风险，投资需谨慎")
    report.append(f"  ⚠️ 缠论学习曲线较陡，建议深入研究后再实盘")
    report.append("")
    report.append(f"{'━'*60}")
    report.append(f"  分析完成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"{'━'*60}")
    
    return '\n'.join(report)


# ========== 主函数 ==========

def main():
    parser = argparse.ArgumentParser(description='缠论多级别联立分析')
    parser.add_argument('--code', '-c', type=str, required=True, help='股票代码')
    args = parser.parse_args()
    
    code = args.code.strip()
    
    # 指数名称
    index_names = {
        '399006': '创业板指', '399001': '深证成指', '399300': '沪深300',
        '000001': '上证指数', '000016': '上证50', '000688': '科创50'
    }
    name = index_names.get(code, code)
    
    print(f"\n{'='*60}")
    print(f"  正在获取 {name}（{code}）数据...")
    print(f"  策略：akshare-stock → futu-stock")
    print(f"{'='*60}\n")
    
    # 获取数据
    print("📊 获取日K数据...")
    daily = get_kline(code, 'daily')
    if daily:
        print(f"   成功：{len(daily)}根\n")
    else:
        print("   ❌ 失败\n")
    
    print("📊 获取30分钟K数据...")
    m30 = get_kline(code, '30')
    if m30:
        print(f"   成功：{len(m30)}根\n")
    else:
        print("   ❌ 失败\n")
    
    print("📊 获取5分钟K数据...")
    m5 = get_kline(code, '5')
    if m5:
        print(f"   成功：{len(m5)}根\n")
    else:
        print("   ❌ 失败\n")
    
    print("📊 获取1分钟K数据...")
    m1 = get_kline(code, '1')
    if m1:
        print(f"   成功：{len(m1)}根\n")
    else:
        print("   ❌ 失败\n")
    
    # 检查是否获取到所有数据
    if not all([daily, m30, m5, m1]):
        missing = []
        if not daily: missing.append('日K')
        if not m30: missing.append('30分钟K')
        if not m5: missing.append('5分钟K')
        if not m1: missing.append('1分钟K')
        print(f"\n{'='*60}")
        print(f"  ❌ 分钟级数据获取失败，无法进行多级别联立分析")
        print(f"  失败数据：{', '.join(missing)}")
        print(f"{'='*60}")
        print(f"\n请检查网络连接或股票代码是否正确。")
        sys.exit(1)
    
    # 生成报告
    print("\n📝 生成分析报告...\n")
    report = generate_report(name, code, daily, m30, m5, m1)
    print(report)


if __name__ == "__main__":
    main()
