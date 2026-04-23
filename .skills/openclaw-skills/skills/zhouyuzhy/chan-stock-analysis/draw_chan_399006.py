#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创业板指 399006 缠论多级别可视化图
绘制：K线 + MACD + 中枢 + 背驰点 + 买卖点
"""
import sys, os, json
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# ── 字体 ──────────────────────────────────────────────
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ── 颜色主题 ──────────────────────────────────────────
C = dict(
    bg='#0d1117', panel='#161b22', grid='#21262d',
    up='#26a641', down='#f85149', text='#e6edf3', sub='#8b949e',
    zhongshu='#f0c040', zhongshu_fill='#f0c04022',
    beichi_top='#ff6b6b', beichi_bot='#51cf66',
    buy1='#00d4ff', buy2='#00b4d8', buy3='#0096c7',
    sell1='#ff9f43', sell2='#ee5a24', sell3='#c0392b',
    macd_pos='#26a641', macd_neg='#f85149',
    dif='#58a6ff', dea='#f78166',
    ma5='#ffd700', ma13='#ff8c00', ma34='#00ced1',
)

# ── 数据获取 ──────────────────────────────────────────
def get_kline(code, period):
    """从 chan_v6 缓存或 akshare 获取数据"""
    try:
        from chan_v6 import get_kline as _get
        data, src = _get(code, period)
        if data:
            df = pd.DataFrame(data)
            df['datetime'] = pd.to_datetime(df['datetime'])
            return df
    except Exception as e:
        print(f"  获取{period}数据失败: {e}")
    return None

# ── 缠论计算 ──────────────────────────────────────────
def calc_macd(close, fast=12, slow=26, signal=9):
    ema_f = close.ewm(span=fast, adjust=False).mean()
    ema_s = close.ewm(span=slow, adjust=False).mean()
    dif = ema_f - ema_s
    dea = dif.ewm(span=signal, adjust=False).mean()
    hist = (dif - dea) * 2
    return dif, dea, hist

def calc_ma(close, period):
    return close.rolling(period).mean()

def find_bi_points(df, min_gap=5):
    """简化版笔识别：找局部极值点"""
    highs = df['high'].values
    lows  = df['low'].values
    n = len(df)
    tops, bots = [], []
    w = 3
    for i in range(w, n - w):
        if highs[i] == max(highs[max(0,i-w):i+w+1]):
            tops.append(i)
        if lows[i] == min(lows[max(0,i-w):i+w+1]):
            bots.append(i)
    # 合并相邻同类
    def merge(pts, kind):
        if not pts: return []
        res = [pts[0]]
        for p in pts[1:]:
            if p - res[-1] < min_gap:
                if kind == 'top' and highs[p] > highs[res[-1]]:
                    res[-1] = p
                elif kind == 'bot' and lows[p] < lows[res[-1]]:
                    res[-1] = p
            else:
                res.append(p)
        return res
    tops = merge(tops, 'top')
    bots = merge(bots, 'bot')
    # 交替排列
    pts = sorted([(i,'top') for i in tops] + [(i,'bot') for i in bots])
    alt = []
    for idx, kind in pts:
        if not alt or alt[-1][1] != kind:
            alt.append((idx, kind))
        else:
            if kind == 'top' and highs[idx] > highs[alt[-1][0]]:
                alt[-1] = (idx, kind)
            elif kind == 'bot' and lows[idx] < lows[alt[-1][0]]:
                alt[-1] = (idx, kind)
    return alt

def find_zhongshu(bi_pts, df):
    """识别中枢：三笔重叠区间"""
    zss = []
    highs = df['high'].values
    lows  = df['low'].values
    for i in range(len(bi_pts) - 2):
        p0, p1, p2 = bi_pts[i], bi_pts[i+1], bi_pts[i+2]
        # 取三段的高低点
        seg_highs = [highs[p0[0]], highs[p1[0]], highs[p2[0]]]
        seg_lows  = [lows[p0[0]],  lows[p1[0]],  lows[p2[0]]]
        zs_high = min(seg_highs)
        zs_low  = max(seg_lows)
        if zs_high > zs_low:
            zss.append(dict(
                start=p0[0], end=p2[0],
                high=zs_high, low=zs_low
            ))
    # 合并重叠中枢
    merged = []
    for zs in zss:
        if merged and zs['low'] < merged[-1]['high'] and zs['start'] <= merged[-1]['end']:
            merged[-1]['high'] = max(merged[-1]['high'], zs['high'])
            merged[-1]['low']  = min(merged[-1]['low'],  zs['low'])
            merged[-1]['end']  = max(merged[-1]['end'],  zs['end'])
        else:
            merged.append(dict(**zs))
    return merged

def find_beichi(bi_pts, df, dif, hist):
    """识别背驰点"""
    beichi = []
    highs = df['high'].values
    lows  = df['low'].values
    dif_v = dif.values
    hist_v = hist.values
    for i in range(2, len(bi_pts)):
        cur = bi_pts[i]
        prv = bi_pts[i-2]
        if cur[1] == 'top' and prv[1] == 'top':
            # 顶背驰：价格新高但MACD面积缩小
            if highs[cur[0]] >= highs[prv[0]]:
                area_prv = sum(abs(hist_v[prv[0]:bi_pts[i-1][0]]))
                area_cur = sum(abs(hist_v[bi_pts[i-1][0]:cur[0]]))
                if area_cur < area_prv * 0.85:
                    beichi.append(dict(idx=cur[0], kind='top',
                                       price=highs[cur[0]], strength='strong' if area_cur < area_prv*0.6 else 'weak'))
        elif cur[1] == 'bot' and prv[1] == 'bot':
            # 底背驰：价格新低但MACD面积缩小
            if lows[cur[0]] <= lows[prv[0]]:
                area_prv = sum(abs(hist_v[prv[0]:bi_pts[i-1][0]]))
                area_cur = sum(abs(hist_v[bi_pts[i-1][0]:cur[0]]))
                if area_cur < area_prv * 0.85:
                    beichi.append(dict(idx=cur[0], kind='bot',
                                       price=lows[cur[0]], strength='strong' if area_cur < area_prv*0.6 else 'weak'))
    return beichi

def find_buy_sell(bi_pts, zss, beichi, df):
    """识别买卖点"""
    points = []
    highs = df['high'].values
    lows  = df['low'].values
    bc_idx = {b['idx']: b for b in beichi}

    for i, (idx, kind) in enumerate(bi_pts):
        # 一买：底背驰
        if kind == 'bot' and idx in bc_idx and bc_idx[idx]['kind'] == 'bot':
            points.append(dict(idx=idx, kind='buy1', price=lows[idx], label='①买'))
        # 一卖：顶背驰
        if kind == 'top' and idx in bc_idx and bc_idx[idx]['kind'] == 'top':
            points.append(dict(idx=idx, kind='sell1', price=highs[idx], label='①卖'))
        # 三买：离开中枢后不回中枢
        for zs in zss:
            if kind == 'bot' and idx > zs['end'] and lows[idx] > zs['low']:
                if i > 0 and bi_pts[i-1][0] >= zs['start']:
                    points.append(dict(idx=idx, kind='buy3', price=lows[idx], label='③买'))
                    break
            if kind == 'top' and idx > zs['end'] and highs[idx] < zs['high']:
                if i > 0 and bi_pts[i-1][0] >= zs['start']:
                    points.append(dict(idx=idx, kind='sell3', price=highs[idx], label='③卖'))
                    break
    return points

# ── 绘图函数 ──────────────────────────────────────────
def draw_panel(ax_k, ax_m, df, title, zss, beichi, bsp, show_n=80):
    """绘制单个级别面板"""
    df = df.tail(show_n).reset_index(drop=True)
    n = len(df)
    xs = np.arange(n)

    # 重新映射索引
    orig_len = len(df) + (show_n - n)
    offset = show_n - n

    def remap(idx):
        return idx - offset

    # ── K线 ──
    ax_k.set_facecolor(C['panel'])
    for i, row in df.iterrows():
        color = C['up'] if row['close'] >= row['open'] else C['down']
        # 实体
        ax_k.bar(i, abs(row['close']-row['open']),
                 bottom=min(row['open'], row['close']),
                 color=color, width=0.6, linewidth=0)
        # 影线
        ax_k.plot([i, i], [row['low'], row['high']], color=color, linewidth=0.8)

    # ── 均线 ──
    for period, color, lw in [(5, C['ma5'], 1.0), (13, C['ma13'], 1.0), (34, C['ma34'], 0.8)]:
        ma = calc_ma(df['close'], period)
        ax_k.plot(xs, ma, color=color, linewidth=lw, alpha=0.8, label=f'MA{period}')

    # ── 中枢 ──
    for zs in zss:
        x0 = remap(zs['start'])
        x1 = remap(zs['end'])
        if x1 < 0 or x0 >= n: continue
        x0 = max(0, x0)
        x1 = min(n-1, x1)
        rect = mpatches.FancyBboxPatch(
            (x0-0.5, zs['low']), x1-x0+1, zs['high']-zs['low'],
            boxstyle="square,pad=0", linewidth=1.5,
            edgecolor=C['zhongshu'], facecolor=C['zhongshu_fill'], zorder=2
        )
        ax_k.add_patch(rect)
        mid = (zs['high'] + zs['low']) / 2
        ax_k.text(x0+0.3, zs['high'], f"中枢\n{zs['low']:.1f}-{zs['high']:.1f}",
                  color=C['zhongshu'], fontsize=6.5, va='bottom', zorder=5,
                  bbox=dict(boxstyle='round,pad=0.2', facecolor='#0d1117aa', edgecolor='none'))

    # ── 背驰点 ──
    for bc in beichi:
        xi = remap(bc['idx'])
        if xi < 0 or xi >= n: continue
        color = C['beichi_top'] if bc['kind'] == 'top' else C['beichi_bot']
        marker = 'v' if bc['kind'] == 'top' else '^'
        offset_y = df['high'].iloc[xi]*1.003 if bc['kind'] == 'top' else df['low'].iloc[xi]*0.997
        ax_k.scatter(xi, offset_y, marker=marker, color=color, s=80, zorder=6)
        label = '顶背驰' if bc['kind'] == 'top' else '底背驰'
        strength = '★' if bc['strength'] == 'strong' else '☆'
        ax_k.annotate(f'{label}{strength}', xy=(xi, offset_y),
                      xytext=(xi+1, offset_y * (1.005 if bc['kind']=='top' else 0.995)),
                      color=color, fontsize=6, zorder=7,
                      arrowprops=dict(arrowstyle='->', color=color, lw=0.8))

    # ── 买卖点 ──
    for pt in bsp:
        xi = remap(pt['idx'])
        if xi < 0 or xi >= n: continue
        if 'buy' in pt['kind']:
            color = C['buy1'] if '1' in pt['kind'] else (C['buy2'] if '2' in pt['kind'] else C['buy3'])
            y = df['low'].iloc[xi] * 0.995
            ax_k.scatter(xi, y, marker='^', color=color, s=120, zorder=8)
            ax_k.text(xi, y*0.993, pt['label'], color=color, fontsize=7,
                      ha='center', va='top', fontweight='bold', zorder=9)
        else:
            color = C['sell1'] if '1' in pt['kind'] else (C['sell2'] if '2' in pt['kind'] else C['sell3'])
            y = df['high'].iloc[xi] * 1.005
            ax_k.scatter(xi, y, marker='v', color=color, s=120, zorder=8)
            ax_k.text(xi, y*1.007, pt['label'], color=color, fontsize=7,
                      ha='center', va='bottom', fontweight='bold', zorder=9)

    # ── 当前价格线 ──
    cur_price = df['close'].iloc[-1]
    ax_k.axhline(cur_price, color='#ffffff44', linewidth=0.8, linestyle='--')
    ax_k.text(n-0.5, cur_price, f' {cur_price:.2f}', color=C['text'],
              fontsize=7.5, va='center', fontweight='bold')

    ax_k.set_title(title, color=C['text'], fontsize=10, fontweight='bold', pad=6)
    ax_k.tick_params(colors=C['sub'], labelsize=7)
    ax_k.spines[:].set_color(C['grid'])
    ax_k.yaxis.set_label_position('right')
    ax_k.yaxis.tick_right()
    ax_k.grid(axis='y', color=C['grid'], linewidth=0.5, alpha=0.5)
    ax_k.legend(loc='upper left', fontsize=6, framealpha=0.3,
                 labelcolor=C['sub'], facecolor=C['panel'])

    # ── MACD ──
    dif, dea, hist = calc_macd(df['close'])
    ax_m.set_facecolor(C['panel'])
    colors = [C['macd_pos'] if v >= 0 else C['macd_neg'] for v in hist]
    ax_m.bar(xs, hist, color=colors, width=0.6, linewidth=0, alpha=0.85)
    ax_m.plot(xs, dif, color=C['dif'], linewidth=1.0, label='DIF')
    ax_m.plot(xs, dea, color=C['dea'], linewidth=1.0, label='DEA')
    ax_m.axhline(0, color=C['grid'], linewidth=0.8)
    ax_m.tick_params(colors=C['sub'], labelsize=6)
    ax_m.spines[:].set_color(C['grid'])
    ax_m.yaxis.set_label_position('right')
    ax_m.yaxis.tick_right()
    ax_m.grid(axis='y', color=C['grid'], linewidth=0.5, alpha=0.4)
    ax_m.legend(loc='upper left', fontsize=6, framealpha=0.3,
                 labelcolor=C['sub'], facecolor=C['panel'])

    # 标注最新DIF/DEA
    ax_m.text(n-0.5, dif.iloc[-1], f' {dif.iloc[-1]:.1f}', color=C['dif'], fontsize=6, va='center')

# ── 主程序 ──────────────────────────────────────────
def main():
    code = '399006'
    print(f"\n{'='*60}")
    print(f"  创业板指 {code} 缠论可视化图生成")
    print(f"{'='*60}\n")

    # 获取数据
    levels = [
        ('daily', '日线', 80),
        ('30',    '30分钟', 80),
        ('5',     '5分钟', 80),
        ('1',     '1分钟', 80),
    ]

    dfs = {}
    for period, name, show_n in levels:
        print(f"  获取{name}数据...")
        df = get_kline(code, period)
        if df is not None:
            print(f"  ✅ {name}: {len(df)}根")
            dfs[period] = df
        else:
            print(f"  ❌ {name}: 获取失败")

    if not dfs:
        print("❌ 无数据，退出")
        return

    # ── 创建画布 ──
    fig = plt.figure(figsize=(22, 26), facecolor=C['bg'])
    fig.suptitle(
        f'创业板指（399006）缠论多级别联立分析\n{datetime.now().strftime("%Y-%m-%d %H:%M")}',
        color=C['text'], fontsize=14, fontweight='bold', y=0.99
    )

    # 4个级别，每个级别 K线(3) + MACD(1)
    outer = gridspec.GridSpec(4, 1, figure=fig, hspace=0.45,
                               top=0.96, bottom=0.03, left=0.03, right=0.97)

    level_configs = [
        ('daily', '📈 日线级别  中枢: 3078-3137  趋势: 上升', 80),
        ('30',    '📊 30分钟级别  中枢: 3298-3343  趋势: 上升', 80),
        ('5',     '📊 5分钟级别  中枢: 3305-3318  趋势: 上升', 80),
        ('1',     '📊 1分钟级别  中枢: 3317-3324  趋势: 上升', 80),
    ]

    for row_idx, (period, title, show_n) in enumerate(level_configs):
        if period not in dfs:
            continue
        df = dfs[period]

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[row_idx],
            height_ratios=[3, 1], hspace=0.05
        )
        ax_k = fig.add_subplot(inner[0])
        ax_m = fig.add_subplot(inner[1], sharex=ax_k)
        plt.setp(ax_k.get_xticklabels(), visible=False)

        # 计算缠论结构
        bi_pts = find_bi_points(df, min_gap=5 if period in ['daily','30'] else 3)
        zss    = find_zhongshu(bi_pts, df)
        dif, dea, hist = calc_macd(df['close'])
        beichi = find_beichi(bi_pts, df, dif, hist)
        bsp    = find_buy_sell(bi_pts, zss, beichi, df)

        # 只取最近 show_n 根
        df_show = df.tail(show_n).reset_index(drop=True)
        offset  = len(df) - show_n

        # 过滤到可见范围
        zss_v    = [z for z in zss    if z['end']   >= offset]
        beichi_v = [b for b in beichi if b['idx']   >= offset]
        bsp_v    = [p for p in bsp    if p['idx']   >= offset]

        draw_panel(ax_k, ax_m, df_show, title, zss_v, beichi_v, bsp_v, show_n)

        # X轴时间标签
        step = max(1, show_n // 8)
        ticks = list(range(0, len(df_show), step))
        labels = [str(df_show['datetime'].iloc[i])[:16] for i in ticks]
        ax_m.set_xticks(ticks)
        ax_m.set_xticklabels(labels, rotation=20, ha='right',
                              color=C['sub'], fontsize=6)

    # ── 图例说明 ──
    legend_items = [
        mpatches.Patch(color=C['zhongshu'],   label='中枢区间'),
        mpatches.Patch(color=C['beichi_top'], label='顶背驰'),
        mpatches.Patch(color=C['beichi_bot'], label='底背驰'),
        mpatches.Patch(color=C['buy1'],       label='①买点'),
        mpatches.Patch(color=C['buy3'],       label='③买点'),
        mpatches.Patch(color=C['sell1'],      label='①卖点'),
        mpatches.Patch(color=C['sell3'],      label='③卖点'),
        mpatches.Patch(color=C['ma5'],        label='MA5'),
        mpatches.Patch(color=C['ma13'],       label='MA13'),
        mpatches.Patch(color=C['ma34'],       label='MA34'),
    ]
    fig.legend(handles=legend_items, loc='lower center', ncol=10,
               fontsize=8, framealpha=0.4, facecolor=C['panel'],
               labelcolor=C['text'], bbox_to_anchor=(0.5, 0.005))

    # ── 保存 ──
    out_path = os.path.join(os.path.dirname(__file__), 'output_399006_chan.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight',
                facecolor=C['bg'], edgecolor='none')
    plt.close()
    print(f"\n✅ 图表已保存: {out_path}")
    return out_path

if __name__ == '__main__':
    main()
