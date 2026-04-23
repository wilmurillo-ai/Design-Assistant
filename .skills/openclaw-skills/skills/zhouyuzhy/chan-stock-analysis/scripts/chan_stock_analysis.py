#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论多级别联立股票行情分析
使用Tushare/baostock获取数据，参照黄金走势归档结论格式输出专业分析报告
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
import pandas as pd

# 设置中文编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
import tushare as ts
import baostock as bs


# ========== 配置 ==========

# Tushare Token
TUSHARE_TOKEN = "38d141546ad7a95940b8f3ca3dcbdf5184b936c8ce517eeed9d647e6"
pro = ts.pro_api(TUSHARE_TOKEN)

# 初始化baostock
bs.login()


# ========== 数据获取模块 ==========

def get_stock_name(code):
    """获取股票名称"""
    # 指数名称映射
    index_names = {
        '399001': '深证成指',
        '399006': '创业板指',
        '399300': '沪深300',
        '000001': '上证指数',
        '000016': '上证50',
        '000688': '科创50',
        '000852': '中证1000',
    }
    if code in index_names:
        return index_names[code]
    
    try:
        df = pro.stock_basic(ts_code=f'{code}.SZ', fields='name,ts_code')
        if df is not None and len(df) > 0:
            return df.iloc[0]['name']
        df = pro.stock_basic(ts_code=f'{code}.SH', fields='name,ts_code')
        if df is not None and len(df) > 0:
            return df.iloc[0]['name']
        return code
    except:
        return code


def is_index_code(code):
    """判断是否为指数代码"""
    index_prefixes = ['399', '000', '001', '002', '003']  # 常见指数前缀
    # 特定指数代码
    known_indices = ['399001', '399006', '399300', '000001', '000016', '000688', '000852']
    return code in known_indices or any(code.startswith(p) for p in index_prefixes if len(code) == 6)


def format_ts_code(code):
    """格式化股票代码为tushare格式"""
    code = code.strip()
    if '.' in code:
        return code
    if code.startswith('6'):
        return f"{code}.SH"
    else:
        return f"{code}.SZ"


def get_daily_kline(code, days=90):
    """获取日K数据"""
    # 判断是否为指数
    index_names = {
        '399001': ('sz', '399001'),
        '399006': ('sz', '399006'),
        '399300': ('sh', '399300'),
        '000001': ('sh', '000001'),
        '000016': ('sh', '000016'),
        '000688': ('sh', '000688'),
        '000852': ('sh', '000852'),
    }
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days+30)).strftime('%Y-%m-%d')
        
        # 指数使用baostock
        if code in index_names:
            _, bs_code = index_names[code]
            rs = bs.query_history_k_data_plus(
                f"sz.{code}" if code.startswith('399') else f"sh.{code}",
                "date,open,high,low,close,volume",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                frequency="d"
            )
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return None
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            df = df.sort_values('date')
            
            klines = []
            for _, row in df.iterrows():
                try:
                    klines.append({
                        'date': row['date'],
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'close': float(row['close']),
                        'volume': float(row['volume'])
                    })
                except:
                    continue
            return klines[-days:]
        
        # 普通股票使用tushare
        ts_code = format_ts_code(code)
        df = pro.daily(ts_code=ts_code, start_date=start_date.replace('-', ''), end_date=end_date.replace('-', ''))
        if df is None or len(df) == 0:
            return None
        
        df = df.sort_values('trade_date')
        
        klines = []
        for _, row in df.iterrows():
            klines.append({
                'date': str(row['trade_date']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['vol'])
            })
        return klines[-days:]
    except Exception as e:
        print(f"获取日K失败: {e}", file=sys.stderr)
        return None


def get_minute_kline(code, period='30'):
    """获取分钟K数据 - 使用baostock"""
    try:
        # period映射
        freq_map = {'1': '5', '5': '5', '15': '15', '30': '30', '60': '60'}
        freq = freq_map.get(str(period), '30')
        
        # 计算日期范围
        days = 5
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 判断交易所
        if code.startswith('6') or code in ['000001', '000016', '000688', '000852', '399300']:
            bs_code = f"sh.{code}"
        else:
            bs_code = f"sz.{code}"
        
        # 使用baostock获取数据
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,time,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency=freq
        )
        
        if rs.error_code != '0':
            print(f"baostock错误: {rs.error_msg}", file=sys.stderr)
            return None
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            return None
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        df = df.sort_values('time')
        
        klines = []
        for _, row in df.iterrows():
            try:
                klines.append({
                    'datetime': row['time'],
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
            except:
                continue
        
        return klines[-500:]
    except Exception as e:
        print(f"获取{period}分钟K失败: {e}", file=sys.stderr)
        return None


# ========== 均线计算 ==========

def calculate_ma(klines, periods=[5, 13, 21, 34, 55, 89, 144]):
    """计算均线"""
    closes = [k['close'] for k in klines]
    result = {}
    for p in periods:
        if len(closes) >= p:
            result[f'ma{p}'] = sum(closes[-p:]) / p
    return result


def calculate_ema(data, period):
    """计算EMA"""
    if len(data) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = data[0]
    for d in data[1:]:
        ema = (d - ema) * multiplier + ema
    return ema


# ========== 缠论核心算法 ==========

def find_fengxing(klines):
    """识别分型（顶分型/底分型）"""
    if len(klines) < 5:
        return []
    
    fengxing = []
    
    for i in range(2, len(klines) - 2):
        # 顶分型：中K线高点最高
        if (klines[i]['high'] > klines[i-1]['high'] and 
            klines[i]['high'] > klines[i-2]['high'] and
            klines[i]['high'] > klines[i+1]['high'] and 
            klines[i]['high'] > klines[i+2]['high']):
            fengxing.append({
                'type': 'top',
                'index': i,
                'price': klines[i]['high'],
                'date': klines[i].get('date', klines[i].get('datetime', ''))
            })
        
        # 底分型：中K线低点最低
        elif (klines[i]['low'] < klines[i-1]['low'] and 
              klines[i]['low'] < klines[i-2]['low'] and
              klines[i]['low'] < klines[i+1]['low'] and 
              klines[i]['low'] < klines[i+2]['low']):
            fengxing.append({
                'type': 'bottom',
                'index': i,
                'price': klines[i]['low'],
                'date': klines[i].get('date', klines[i].get('datetime', ''))
            })
    
    return fengxing


def merge_fengxing(fengxing):
    """合并分型（取同向分型的高/低）"""
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
        f1 = fengxing[i]
        f2 = fengxing[i + 1]
        
        # 笔：两个分型之间至少5根K线
        if f2['index'] - f1['index'] >= 5:
            direction = 'down' if f1['type'] == 'top' else 'up'
            bis.append({
                'start': f1,
                'end': f2,
                'direction': direction,
                'start_price': f1['price'],
                'end_price': f2['price'],
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
            # 计算重叠区间
            if b1['direction'] == 'down':
                highs = [b['end_price'] for b in [b1, b2, b3]]
                lows = [b['start_price'] for b in [b1, b2, b3]]
            else:
                highs = [b['end_price'] for b in [b1, b2, b3]]
                lows = [b['start_price'] for b in [b1, b2, b3]]
            
            high = min(highs)
            low = max(lows)
            
            if high > low:
                zhongshus.append({
                    'range': (low, high),
                    'start': b1['start']['date'],
                    'end': b3['end']['date'],
                    'bars': b3['end']['index'] - b1['start']['index'],
                    'direction': b1['direction']
                })
    
    return zhongshus


def find_trend_beichi(bis, zhongshus):
    """判断趋势背驰"""
    if len(bis) < 5 or len(zhongshus) == 0:
        return None
    
    last_zs = zhongshus[-1]
    dir = last_zs['direction']
    
    # 找到进入段和离开段
    trend_bis = [b for b in bis if b['direction'] == dir]
    if len(trend_bis) < 4:
        return None
    
    # 最后一段是离开段，倒数第二段是进入段
    enter_bi = trend_bis[-2]  # 进入段
    leave_bi = trend_bis[-1]  # 离开段
    
    return {
        'enter_pct': abs(enter_bi['change_pct']),
        'leave_pct': abs(leave_bi['change_pct']),
        'beichi': abs(leave_bi['change_pct']) < abs(enter_bi['change_pct']),
        'enter_price': enter_bi['start_price'],
        'leave_price': leave_bi['end_price']
    }


# ========== MACD计算 ==========

def calculate_macd(klines, fast=12, slow=26, signal=9):
    """计算MACD"""
    closes = [k['close'] for k in klines]
    
    if len(closes) < slow + signal:
        return None
    
    # 计算EMA
    ema_fast = []
    ema_slow = []
    
    multiplier_fast = 2 / (fast + 1)
    multiplier_slow = 2 / (slow + 1)
    
    ema_fast.append(sum(closes[:fast]) / fast)
    ema_slow.append(sum(closes[:slow]) / slow)
    
    for i in range(fast, len(closes)):
        ema_fast.append((closes[i] - ema_fast[-1]) * multiplier_fast + ema_fast[-1])
    
    for i in range(slow, len(closes)):
        ema_slow.append((closes[i] - ema_slow[-1]) * multiplier_slow + ema_slow[-1])
    
    # 对齐
    min_len = min(len(ema_fast), len(ema_slow))
    dif = [ema_fast[i] - ema_slow[i] for i in range(min_len)]
    
    # 计算DEA
    multiplier_signal = 2 / (signal + 1)
    dea = [sum(dif[:signal]) / signal]
    for i in range(signal, len(dif)):
        dea.append((dif[i] - dea[-1]) * multiplier_signal + dea[-1])
    
    # MACD柱
    min_d = min(len(dif), len(dea))
    macd_hist = [(dif[i] - dea[i-min_d+len(dea)]) * 2 for i in range(min_d - len(dea) + 1, min_d)]
    
    return {
        'dif': dif[-1],
        'dea': dea[-1],
        'macd': macd_hist[-1] if macd_hist else 0,
        'macd_list': macd_hist[-20:],
        'trend': 'up' if macd_hist[-1] > 0 else 'down' if macd_hist else 'unknown'
    }


def calculate_macd_area(klines, start_idx, end_idx):
    """计算MACD柱面积"""
    sub_klines = klines[max(0, start_idx):end_idx+1]
    if len(sub_klines) < 5:
        return 0
    macd = calculate_macd(sub_klines)
    if macd and macd['macd_list']:
        return sum(macd['macd_list'])
    return 0


# ========== 关键位置分析 ==========

def analyze_key_levels(klines, periods=[5, 13, 21, 34, 55, 89, 144]):
    """分析关键位置"""
    closes = [k['close'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    
    result = {
        'current': closes[-1] if closes else 0,
        'recent_high': max(highs[-30:]) if len(highs) >= 30 else max(highs),
        'recent_low': min(lows[-30:]) if len(lows) >= 30 else min(lows),
    }
    
    # 计算均线
    for p in periods:
        if len(closes) >= p:
            result[f'ma{p}'] = sum(closes[-p:]) / p
    
    # 均线位置判断
    current = result['current']
    ma89 = result.get('ma89', current)
    ma144 = result.get('ma144', current)
    
    if current > ma89:
        result['ma89_pos'] = 'above'
    elif current < ma89:
        result['ma89_pos'] = 'below'
    else:
        result['ma89_pos'] = 'cross'
    
    if current > ma144:
        result['ma144_pos'] = 'above'
    elif current < ma144:
        result['ma144_pos'] = 'below'
    else:
        result['ma144_pos'] = 'cross'
    
    # 相对位置百分比
    if result['recent_high'] != result['recent_low']:
        result['pos_pct'] = (current - result['recent_low']) / (result['recent_high'] - result['recent_low']) * 100
    else:
        result['pos_pct'] = 50
    
    return result


# ========== 级别分析 ==========

def analyze_level(klines, level_name):
    """分析单个级别"""
    if not klines or len(klines) < 10:
        return None
    
    # 分型
    fx_list = find_fengxing(klines)
    fx_merged = merge_fengxing(fx_list)
    
    # 笔
    bis = identify_bi(klines, fx_merged)
    
    # 中枢
    zhongshus = find_zhongshu(bis)
    
    # MACD
    macd = calculate_macd(klines)
    
    # 均线和关键位置
    levels = analyze_key_levels(klines)
    
    return {
        'name': level_name,
        'count': len(klines),
        'current': klines[-1]['close'],
        'fx_count': len(fx_merged),
        'bi_count': len(bis),
        'bis': bis[-5:] if bis else [],
        'zhongshus': zhongshus[-3:] if zhongshus else [],
        'macd': macd,
        'levels': levels,
        'direction': bis[-1]['direction'] if bis else 'unknown'
    }


# ========== 完整分析报告生成 ==========

def generate_report(stock_name, stock_code, daily, m30, m5, m1):
    """生成完整的分析报告"""
    today = datetime.now().strftime('%Y年%m月%d日')
    
    # 各级别分析
    daily_analysis = analyze_level(daily, '日线')
    m30_analysis = analyze_level(m30, '30分钟')
    m5_analysis = analyze_level(m5, '5分钟')
    m1_analysis = analyze_level(m1, '1分钟')
    
    report = []
    report.append(f"{'='*60}")
    report.append(f"缠论多级别联立分析报告")
    report.append(f"标的：{stock_name}（{stock_code}）| {today}")
    report.append(f"{'='*60}\n")
    
    # ===== 日线级别 =====
    report.append(f"一、日线级别分析")
    report.append("-" * 40)
    
    if daily_analysis:
        d = daily_analysis
        levels = d['levels']
        macd = d['macd'] or {}
        direction = "上涨" if d['direction'] == 'up' else "下跌"
        
        report.append(f"当前价格：{levels['current']:.2f}")
        
        # 均线状态
        ma_info = []
        for p in [5, 13, 21, 55, 89, 144]:
            if f'ma{p}' in levels:
                ma_info.append(f"MA{p}={levels[f'ma{p}']:.2f}")
        if ma_info:
            report.append(f"均线状态：{' | '.join(ma_info)}")
        
        # 均线位置
        if levels.get('ma89_pos') == 'above':
            report.append(f"价格已突破MA89均线")
        else:
            report.append(f"价格位于MA89均线下方")
        
        if levels.get('ma144_pos') == 'above':
            report.append(f"价格已突破MA144均线")
        else:
            report.append(f"价格位于MA144均线下方")
        
        # MACD状态
        if macd:
            macd_state = "多头" if macd['trend'] == 'up' else "空头"
            report.append(f"MACD状态：DIF={macd['dif']:.3f}，DEA={macd['dea']:.3f}，MACD柱={macd['macd']:.3f}，当前{macd_state}")
        
        # 趋势判断
        report.append(f"近期趋势：{direction}趋势")
        
        # 关键位置
        report.append(f"关键支撑：{levels['recent_low']:.2f}（近期最低）")
        report.append(f"关键阻力：{levels['recent_high']:.2f}（近期最高）")
        report.append(f"当前位置：{levels['pos_pct']:.1f}%区间")
        
        # 中枢
        if d['zhongshus']:
            zs = d['zhongshus'][-1]
            report.append(f"中枢区间：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
    else:
        report.append("数据不足，无法分析")
    
    report.append("")
    
    # ===== 30分钟级别 =====
    report.append(f"二、30分钟级别分析")
    report.append("-" * 40)
    
    if m30_analysis:
        m = m30_analysis
        levels = m['levels']
        macd = m['macd'] or {}
        direction = "上涨" if m['direction'] == 'up' else "下跌"
        
        report.append(f"当前价格：{levels['current']:.2f}")
        
        # 均线状态
        ma_info = []
        for p in [5, 13, 21, 89]:
            if f'ma{p}' in levels:
                ma_info.append(f"MA{p}={levels[f'ma{p}']:.2f}")
        if ma_info:
            report.append(f"均线状态：{' | '.join(ma_info)}")
        
        # MACD
        if macd:
            macd_state = "多头" if macd['trend'] == 'up' else "空头"
            report.append(f"MACD状态：DIF={macd['dif']:.3f}，DEA={macd['dea']:.3f}，MACD柱={macd['macd']:.3f}，当前{macd_state}")
        
        report.append(f"近期趋势：{direction}趋势")
        
        # 背驰判断
        beichi = find_trend_beichi(m['bis'], m['zhongshus'])
        if beichi:
            if beichi['beichi']:
                report.append(f"⚠️ 趋势背驰确认：进入段幅度{beichi['enter_pct']:.2f}% > 离开段幅度{beichi['leave_pct']:.2f}%")
            else:
                report.append(f"暂无背驰迹象")
        
        # 中枢
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"中枢区间：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        
        # 关键位置
        report.append(f"近期高/低点：{levels['recent_high']:.2f} / {levels['recent_low']:.2f}")
    else:
        report.append("数据不足，无法分析")
    
    report.append("")
    
    # ===== 5分钟级别 =====
    report.append(f"三、5分钟级别分析")
    report.append("-" * 40)
    
    if m5_analysis:
        m = m5_analysis
        levels = m['levels']
        macd = m['macd'] or {}
        direction = "上涨" if m['direction'] == 'up' else "下跌"
        
        report.append(f"当前价格：{levels['current']:.2f}")
        
        if macd:
            macd_state = "多头" if macd['trend'] == 'up' else "空头"
            report.append(f"MACD状态：DIF={macd['dif']:.3f}，DEA={macd['dea']:.3f}，MACD柱={macd['macd']:.3f}，当前{macd_state}")
        
        report.append(f"近期趋势：{direction}趋势")
        
        # 中枢
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"中枢区间：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        
        report.append(f"近期高/低点：{levels['recent_high']:.2f} / {levels['recent_low']:.2f}")
    else:
        report.append("数据不足，无法分析")
    
    report.append("")
    
    # ===== 1分钟级别 =====
    report.append(f"四、1分钟级别分析")
    report.append("-" * 40)
    
    if m1_analysis:
        m = m1_analysis
        levels = m['levels']
        macd = m['macd'] or {}
        direction = "上涨" if m['direction'] == 'up' else "下跌"
        
        report.append(f"当前价格：{levels['current']:.2f}")
        
        if macd:
            macd_state = "多头" if macd['trend'] == 'up' else "空头"
            report.append(f"MACD状态：DIF={macd['dif']:.3f}，DEA={macd['dea']:.3f}，MACD柱={macd['macd']:.3f}，当前{macd_state}")
        
        report.append(f"近期趋势：{direction}趋势")
        
        # 中枢
        if m['zhongshus']:
            zs = m['zhongshus'][-1]
            report.append(f"中枢区间：{zs['range'][0]:.2f} - {zs['range'][1]:.2f}")
        
        report.append(f"近期高/低点：{levels['recent_high']:.2f} / {levels['recent_low']:.2f}")
        
        # 检查1分钟是否有盘整背驰
        if len(m['bis']) >= 3:
            last_bi = m['bis'][-1]
            prev_bi = m['bis'][-2]
            if abs(last_bi['change_pct']) < abs(prev_bi['change_pct']):
                report.append(f"⚠️ 内部盘整背驰：{last_bi['change_pct']:.2f}% < {prev_bi['change_pct']:.2f}%")
    else:
        report.append("数据不足，无法分析")
    
    report.append("")
    
    # ===== 多级别联立状态 =====
    report.append(f"五、多级别联立状态总结")
    report.append("-" * 40)
    
    if all([daily_analysis, m30_analysis, m5_analysis, m1_analysis]):
        daily_dir = daily_analysis['direction']
        m30_dir = m30_analysis['direction']
        m5_dir = m5_analysis['direction']
        m1_dir = m1_analysis['direction']
        
        report.append(f"日线：{daily_dir}趋势")
        report.append(f"30分钟：{m30_dir}趋势")
        report.append(f"5分钟：{m5_dir}趋势")
        report.append(f"1分钟：{m1_dir}趋势")
        
        # 联立判断
        if daily_dir == m30_dir == m5_dir:
            report.append(f"⚠️ 当前各周期趋势同向，共振效应，中线趋势延续概率大")
        elif daily_dir != m30_dir:
            report.append(f"⚠️ 日线与30分钟趋势背离，注意短期震荡")
        
        if m1_dir == 'up' and m5_dir == 'up' and m30_dir == 'down':
            report.append(f"⚠️ 小级别反弹，需观察能否带动大级别")
        elif m1_dir == 'down' and m5_dir == 'down' and m30_dir == 'down':
            report.append(f"⚠️ 各周期共振下跌，趋势延续")
    
    report.append("")
    
    # ===== 走势完全分类 =====
    report.append(f"六、走势完全分类与推演")
    report.append("-" * 40)
    
    if all([daily_analysis, m30_analysis]):
        current_price = m30_analysis['levels']['current']
        daily_high = daily_analysis['levels']['recent_high']
        daily_low = daily_analysis['levels']['recent_low']
        m30_high = m30_analysis['levels']['recent_high']
        m30_low = m30_analysis['levels']['recent_low']
        
        # 分类一：延续当前趋势
        report.append(f"【分类一】（大概率 >60%）")
        if m30_dir == 'down':
            report.append(f"下跌延续：价格继续向下考验{daily_low:.2f}支撑")
            report.append(f"操作建议：空头持有或等待反弹后做空")
        else:
            report.append(f"上涨延续：价格向上测试{daily_high:.2f}阻力")
            report.append(f"操作建议：多头持有，关注能否突破")
        
        report.append("")
        
        # 分类二：震荡
        report.append(f"【分类二】（中概率 ~30%）")
        report.append(f"震荡整理：价格在区间内波动")
        report.append(f"区间参考：{daily_low:.2f} - {daily_high:.2f}")
        report.append(f"操作建议：高抛低吸，突破后跟进")
        
        report.append("")
        
        # 分类三：反转
        report.append(f"【分类三】（小概率 <10%）")
        report.append(f"趋势反转：出现背驰或重大突破")
        if m30_dir == 'down':
            report.append(f"操作建议：若出现底背驰，可分批建仓")
        else:
            report.append(f"操作建议：若出现顶背驰，注意止盈")
    
    report.append("")
    
    # ===== 操作策略 =====
    report.append(f"七、终极操作策略")
    report.append("-" * 40)
    
    if all([daily_analysis, m30_analysis]):
        current = m30_analysis['levels']['current']
        daily_high = daily_analysis['levels']['recent_high']
        daily_low = daily_analysis['levels']['recent_low']
        
        if m30_dir == 'up':
            report.append(f"持有多单者：")
            report.append(f"  核心持有，等待趋势延续")
            report.append(f"  止盈参考区域：{daily_high:.2f}附近")
            report.append(f"  离场信号：1分钟出现顶背驰+跌破均线")
            
            report.append(f"\n空仓/想做多者：")
            report.append(f"  等待回调结束信号")
            report.append(f"  入场区域：回调不破关键支撑时")
        else:
            report.append(f"持有多单者：")
            report.append(f"  注意风控，密切关注出场信号")
            report.append(f"  止损参考：日内高点{daily_high:.2f}上方")
            
            report.append(f"\n空仓/想做空者：")
            report.append(f"  可在反弹衰竭时做空")
            report.append(f"  理想做空区域：{daily_high:.2f}附近（反弹高点）")
            report.append(f"  止损设置：突破{daily_high:.2f}时严格止损")
    
    report.append("")
    
    # ===== 风险提示 =====
    report.append(f"八、风险提示")
    report.append("-" * 40)
    report.append(f"⚠️ 本分析仅供学习参考，不构成投资建议")
    report.append(f"⚠️ 市场有风险，投资需谨慎")
    report.append(f"⚠️ 请结合自身风险承受能力制定交易计划")
    report.append(f"⚠️ 缠论学习曲线较陡，建议深入研究后再实盘")
    
    report.append("")
    report.append(f"{'='*60}")
    report.append(f"分析完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"{'='*60}")
    
    return '\n'.join(report)


# ========== 主函数 ==========

def main():
    parser = argparse.ArgumentParser(description='缠论多级别联立股票分析')
    parser.add_argument('--code', '-c', type=str, required=True, help='股票代码')
    args = parser.parse_args()
    
    code = args.code.strip()
    
    print(f"\n{'='*60}")
    print(f"开始获取 {code} 数据...")
    print(f"{'='*60}\n")
    
    # 获取股票名称
    stock_name = get_stock_name(code)
    print(f"股票名称：{stock_name}")
    
    # 获取各周期数据
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
    
    # 生成报告
    print("\n正在生成分析报告...\n")
    report = generate_report(stock_name, code, daily, m30, m5, m1)
    print(report)
    
    # 保存报告
    output_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
    output_file = os.path.join(output_dir, f'{stock_name}_{code}_缠论分析_{datetime.now().strftime("%Y%m%d")}.txt')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存至：{output_file}")
    except:
        pass


if __name__ == "__main__":
    main()
