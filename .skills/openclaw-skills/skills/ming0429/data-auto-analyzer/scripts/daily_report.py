"""
每日投放日报生成器 - data-auto-analyzer
输入投放报表，生成钉钉/飞书可贴文本 + HTML 精美版
用法: python3 daily_report.py --today today.xlsx [--yesterday yesterday.xlsx] --out-dir /path/
"""
import sys
import os
import argparse
import json
import html as html_mod
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_file, auto_detect_columns, to_numeric_safe


def summarize(df, cols):
    """汇总一份报表的核心指标"""
    result = {}

    def sum_col(key):
        col = cols.get(key)
        if col is None:
            return 0
        return float(to_numeric_safe(df[col]).sum())

    result["cost"] = sum_col("cost")
    result["impression"] = sum_col("impression")
    result["click"] = sum_col("click")
    result["conversion"] = sum_col("conversion")
    result["revenue"] = sum_col("revenue")

    # 派生指标
    result["ctr"] = (result["click"] / result["impression"] * 100) if result["impression"] > 0 else 0
    result["cvr"] = (result["conversion"] / result["click"] * 100) if result["click"] > 0 else 0
    result["cpa"] = (result["cost"] / result["conversion"]) if result["conversion"] > 0 else 0
    result["cpc"] = (result["cost"] / result["click"]) if result["click"] > 0 else 0
    result["roi"] = (result["revenue"] / result["cost"]) if result["cost"] > 0 and result["revenue"] > 0 else 0

    return result


def get_top_campaigns(df, cols, top_n=3):
    """获取 TOP 最佳和 TOP 最差的计划"""
    campaign_col = cols.get("campaign")
    if not campaign_col:
        return [], []

    agg = {}
    for key in ["cost", "conversion", "click", "impression"]:
        if cols.get(key):
            agg[cols[key]] = "sum"

    df_agg = df.groupby(campaign_col).agg(agg).reset_index()

    # 加派生指标
    if cols.get("cost") and cols.get("conversion"):
        df_agg["_cpa"] = np.where(df_agg[cols["conversion"]] > 0,
                                   df_agg[cols["cost"]] / df_agg[cols["conversion"]],
                                   np.nan)
    else:
        df_agg["_cpa"] = np.nan

    # TOP 最佳：CPA 最低（有转化 ≥ 1）
    best_df = df_agg[df_agg[cols["conversion"]] >= 1].copy() if cols.get("conversion") else pd.DataFrame()
    best_df = best_df.sort_values("_cpa", ascending=True).head(top_n) if len(best_df) else pd.DataFrame()

    # TOP 最差：CPA 最高（消耗 ≥ 100 避免小消耗计划误报）
    total_cost = df_agg[cols["cost"]].sum() if cols.get("cost") else 0
    cost_threshold = max(100, total_cost * 0.02)  # 至少 100 或总消耗的 2%
    worst_df = df_agg[df_agg[cols["cost"]] >= cost_threshold].copy() if cols.get("cost") else pd.DataFrame()
    worst_df = worst_df.sort_values("_cpa", ascending=False, na_position="first").head(top_n) if len(worst_df) else pd.DataFrame()

    def to_list(d):
        out = []
        for _, r in d.iterrows():
            out.append({
                "name": str(r[campaign_col]),
                "cost": float(r[cols["cost"]]) if cols.get("cost") else 0,
                "conversion": float(r[cols["conversion"]]) if cols.get("conversion") else 0,
                "cpa": float(r["_cpa"]) if not pd.isna(r["_cpa"]) else None,
            })
        return out

    return to_list(best_df), to_list(worst_df)


def detect_anomalies(df_today, df_yesterday, cols):
    """检测需要提醒的异常"""
    anomalies = []

    if df_yesterday is None:
        # 无昨日数据，只能做单日异常
        campaign_col = cols.get("campaign")
        cost_col = cols.get("cost")
        conv_col = cols.get("conversion")

        if campaign_col and cost_col and conv_col:
            agg_dict = {cost_col: "sum", conv_col: "sum"}
            agg = df_today.groupby(campaign_col).agg(agg_dict).reset_index()
            total_cost = agg[cost_col].sum()

            # 有消耗但转化为 0 且消耗超过总消耗 5%
            zero_conv = agg[(agg[conv_col] == 0) & (agg[cost_col] > total_cost * 0.05)]
            for _, r in zero_conv.iterrows():
                anomalies.append(f"⚠️ 计划【{r[campaign_col]}】消耗 {r[cost_col]:,.0f} 元但转化为 0，建议立即暂停")

        return anomalies

    # 有昨日数据 - 做环比异常检测
    campaign_col = cols.get("campaign")
    if not campaign_col:
        return anomalies

    cost_col = cols.get("cost")
    conv_col = cols.get("conversion")

    if cost_col and conv_col:
        today_agg = df_today.groupby(campaign_col).agg({cost_col: "sum", conv_col: "sum"})
        yest_agg = df_yesterday.groupby(campaign_col).agg({cost_col: "sum", conv_col: "sum"})

        common = set(today_agg.index) & set(yest_agg.index)
        for name in common:
            t_cost = today_agg.loc[name, cost_col]
            y_cost = yest_agg.loc[name, cost_col]
            t_conv = today_agg.loc[name, conv_col]
            y_conv = yest_agg.loc[name, conv_col]

            # 消耗暴增但转化没跟上
            if y_cost > 0 and t_cost > y_cost * 2 and (y_conv == 0 or t_conv < y_conv * 1.1):
                anomalies.append(f"⚠️ 计划【{name}】消耗从 {y_cost:,.0f} 暴增至 {t_cost:,.0f}，但转化未同步增长")

            # 转化从非零降为零
            if y_conv > 0 and t_conv == 0 and t_cost > 100:
                anomalies.append(f"🚨 计划【{name}】转化从 {y_conv:.0f} 降为 0（今日消耗 {t_cost:,.0f} 元）")

            # CPA 暴涨
            if y_conv > 0 and t_conv > 0:
                y_cpa = y_cost / y_conv
                t_cpa = t_cost / t_conv
                if t_cpa > y_cpa * 1.8:
                    anomalies.append(f"📈 计划【{name}】CPA 从 {y_cpa:.1f} 涨至 {t_cpa:.1f}（+{(t_cpa/y_cpa-1)*100:.0f}%）")

    return anomalies[:10]  # 最多 10 条


def generate_suggestions(today_stats, yest_stats, best, worst, anomalies):
    """生成明日建议"""
    suggestions = []

    # 基于 TOP 差计划
    if worst:
        names = "、".join(w["name"] for w in worst[:2])
        suggestions.append(f"🛑 重点优化或暂停【{names}】（CPA 偏高）")

    # 基于 TOP 好计划
    if best:
        names = "、".join(b["name"] for b in best[:2])
        suggestions.append(f"📈 加大【{names}】预算（CPA 表现最优）")

    # 基于环比
    if yest_stats:
        if yest_stats.get("cpa", 0) > 0 and today_stats.get("cpa", 0) > yest_stats.get("cpa", 0) * 1.2:
            suggestions.append("⚡ 整体 CPA 环比上涨 20%+，建议收紧整体出价")
        if yest_stats.get("ctr", 0) > 0 and today_stats.get("ctr", 0) < yest_stats.get("ctr", 0) * 0.8:
            suggestions.append("💡 整体 CTR 下滑明显，建议更新素材池")

    # 基于异常数量
    if len(anomalies) >= 3:
        suggestions.append(f"🔍 今日有 {len(anomalies)} 条异常，建议下午集中排查")

    if not suggestions:
        suggestions.append("✅ 整体表现健康，继续保持当前策略")

    return suggestions[:5]


def pct_change_str(new, old):
    """生成环比字符串"""
    if old is None or old == 0:
        return ""
    change = (new - old) / abs(old) * 100
    if abs(change) < 0.5:
        return " →"
    arrow = "↑" if change > 0 else "↓"
    return f" {arrow} {abs(change):.1f}%"


def build_text_report(today_stats, yest_stats, best, worst, anomalies, suggestions, date_str):
    """生成纯文本日报（钉钉/飞书可贴）"""
    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 投放日报 · {date_str}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    lines.append("【核心指标】")
    s = today_stats
    y = yest_stats

    def _metric(label, key, fmt_func, is_cost=False):
        v = s[key]
        if y is None:
            return f"• {label}：{fmt_func(v)}"
        chg = pct_change_str(v, y[key])
        # 对 CPA、CPC 这类成本指标，上涨标红
        warning = ""
        if is_cost and y[key] > 0 and v > y[key] * 1.1:
            warning = " ⚠️"
        elif not is_cost and y[key] > 0 and v < y[key] * 0.9:
            warning = " ⚠️"
        return f"• {label}：{fmt_func(v)}{chg}{warning}"

    lines.append(_metric("消耗", "cost", lambda v: f"{v:,.0f} 元"))
    lines.append(_metric("曝光", "impression", lambda v: f"{v:,.0f}"))
    lines.append(_metric("点击", "click", lambda v: f"{v:,.0f}"))
    lines.append(_metric("转化", "conversion", lambda v: f"{v:,.0f}"))
    if s["cpa"] > 0:
        lines.append(_metric("CPA", "cpa", lambda v: f"{v:,.2f} 元", is_cost=True))
    if s["ctr"] > 0:
        lines.append(_metric("CTR", "ctr", lambda v: f"{v:.2f}%"))
    if s["cvr"] > 0:
        lines.append(_metric("转化率", "cvr", lambda v: f"{v:.2f}%"))
    if s["roi"] > 0:
        lines.append(_metric("ROI", "roi", lambda v: f"{v:.2f}"))

    lines.append("")

    if best:
        lines.append("【TOP 最佳计划】")
        for i, b in enumerate(best, 1):
            cpa_str = f"CPA {b['cpa']:.1f}" if b["cpa"] else "CPA N/A"
            lines.append(f"{i}. {b['name']}：消耗 {b['cost']:,.0f}，转化 {b['conversion']:.0f}，{cpa_str}")
        lines.append("")

    if worst:
        lines.append("【TOP 待优化计划】")
        for i, w in enumerate(worst, 1):
            cpa_str = f"CPA {w['cpa']:.1f}" if w["cpa"] else "CPA N/A（无转化）"
            lines.append(f"{i}. {w['name']}：消耗 {w['cost']:,.0f}，转化 {w['conversion']:.0f}，{cpa_str}")
        lines.append("")

    if anomalies:
        lines.append("【异常提醒】")
        for a in anomalies[:5]:
            lines.append(a)
        lines.append("")

    lines.append("【明日建议】")
    for s_text in suggestions:
        lines.append(f"• {s_text}")

    return "\n".join(lines)


def build_html_report(today_stats, yest_stats, best, worst, anomalies, suggestions, date_str):
    """生成 HTML 精美版日报"""

    report = {
        "today": today_stats,
        "yesterday": yest_stats,
        "best": best,
        "worst": worst,
        "anomalies": anomalies,
        "suggestions": suggestions,
        "date": date_str,
    }

    template = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>投放日报 - {{DATE}}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.5.0/echarts.min.js"></script>
<style>
:root {
  --bg-primary: #0f1117; --bg-card: #1a1d2e; --border: #2a2e42;
  --text-primary: #e8eaf0; --text-secondary: #8b90a5; --text-dim: #5c6078;
  --accent-blue: #4e7cff; --accent-green: #22c493; --accent-orange: #f5a623;
  --accent-red: #f25757; --accent-purple: #9370ff;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary); color: var(--text-primary);
  line-height: 1.6; min-height: 100vh;
}
.container { max-width: 1100px; margin: 0 auto; padding: 32px 24px; }
.header {
  text-align: center; padding: 48px 24px;
  background: linear-gradient(180deg, rgba(78,124,255,0.08) 0%, transparent 100%);
  border-bottom: 1px solid var(--border);
}
.header h1 {
  font-size: 1.8rem; font-weight: 700;
  background: linear-gradient(135deg, #4e7cff 0%, #9370ff 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 8px; letter-spacing: -0.02em;
}
.header .date { color: var(--text-secondary); font-size: 1rem; font-weight: 500; }
.section-title {
  font-size: 1.15rem; font-weight: 600; margin: 40px 0 20px;
  padding-left: 14px; border-left: 3px solid var(--accent-blue);
}

.metrics-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px; margin-bottom: 32px;
}
.metric-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 20px; position: relative;
}
.metric-card .lbl {
  font-size: 0.78rem; letter-spacing: 0.08em; color: var(--text-secondary);
  text-transform: uppercase; margin-bottom: 8px;
}
.metric-card .val {
  font-size: 1.7rem; font-weight: 700; letter-spacing: -0.02em;
  color: var(--text-primary); margin-bottom: 4px;
  font-variant-numeric: tabular-nums;
}
.metric-card .change { font-size: 0.82rem; display: inline-flex; align-items: center; gap: 4px; }
.metric-card .change.up { color: var(--accent-green); }
.metric-card .change.down { color: var(--accent-red); }
.metric-card .change.flat { color: var(--text-dim); }
.metric-card .change.bad-up { color: var(--accent-red); }
.metric-card .change.good-down { color: var(--accent-green); }

.top-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 32px;
}
.top-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 22px;
}
.top-card.best { border-left: 3px solid var(--accent-green); }
.top-card.worst { border-left: 3px solid var(--accent-red); }
.top-card h3 {
  font-size: 0.95rem; font-weight: 600; margin-bottom: 14px;
  display: flex; align-items: center; gap: 6px;
}
.camp-row {
  display: grid; grid-template-columns: 24px 1fr auto;
  gap: 12px; align-items: center;
  padding: 10px 0; border-top: 1px solid rgba(42,46,66,0.5);
}
.camp-row:first-of-type { border-top: none; }
.camp-row .rank {
  font-size: 0.85rem; font-weight: 600;
  color: var(--text-secondary); text-align: center;
}
.camp-row .name {
  font-size: 0.88rem; color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.camp-row .stats {
  font-size: 0.78rem; color: var(--text-secondary); white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.top-card.best .camp-row .stats { color: var(--accent-green); }
.top-card.worst .camp-row .stats { color: var(--accent-orange); }

.alert-list, .suggest-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 32px; }
.alert-item {
  background: rgba(242,87,87,0.06); border-left: 3px solid var(--accent-red);
  padding: 12px 18px; border-radius: 6px; font-size: 0.9rem;
  color: var(--text-primary);
}
.suggest-item {
  background: rgba(34,196,147,0.06); border-left: 3px solid var(--accent-green);
  padding: 12px 18px; border-radius: 6px; font-size: 0.9rem;
  color: var(--text-primary);
}

.chart-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 20px; margin-bottom: 20px;
}
.chart-box { width: 100%; height: 360px; }

.footer {
  text-align: center; padding: 32px;
  color: var(--text-dim); font-size: 0.78rem;
  border-top: 1px solid var(--border); margin-top: 40px;
}

@media (max-width: 768px) {
  .top-grid { grid-template-columns: 1fr; }
  .container { padding: 16px 12px; }
}
</style>
</head>
<body>

<div class="header">
  <h1>投放日报</h1>
  <div class="date">{{DATE}}</div>
</div>

<div class="container">

  <h2 class="section-title">核心指标</h2>
  <div class="metrics-grid" id="metrics-grid"></div>

  <h2 class="section-title">计划表现 TOP 榜</h2>
  <div class="top-grid">
    <div class="top-card best">
      <h3>🏆 最佳计划（CPA 最低）</h3>
      <div id="best-list"></div>
    </div>
    <div class="top-card worst">
      <h3>⚠️ 待优化计划（CPA 偏高）</h3>
      <div id="worst-list"></div>
    </div>
  </div>

  <div id="anomaly-section"></div>

  <h2 class="section-title">💡 明日建议</h2>
  <div class="suggest-list" id="suggest-list"></div>

  <div id="chart-section"></div>

</div>

<div class="footer">Generated by data-auto-analyzer · 日报生成模式</div>

<script>
const REPORT = {{REPORT_JSON}};

function fmt(n, digits) {
  if (n === null || n === undefined || isNaN(n)) return '-';
  if (typeof n !== 'number') return n;
  if (Math.abs(n) >= 1e8) return (n / 1e8).toFixed(2) + '亿';
  if (Math.abs(n) >= 1e4) return (n / 1e4).toFixed(2) + '万';
  return n.toLocaleString(undefined, {maximumFractionDigits: digits === undefined ? 2 : digits});
}

function pctChange(newV, oldV) {
  if (oldV === null || oldV === undefined || oldV === 0) return null;
  return (newV - oldV) / Math.abs(oldV) * 100;
}

function renderMetrics() {
  const t = REPORT.today;
  const y = REPORT.yesterday;
  const defs = [
    {lbl: '消耗', key: 'cost', fmt: v => fmt(v, 0) + ' 元', badUp: false},
    {lbl: '曝光', key: 'impression', fmt: v => fmt(v, 0), badUp: false},
    {lbl: '点击', key: 'click', fmt: v => fmt(v, 0), badUp: false},
    {lbl: '转化', key: 'conversion', fmt: v => fmt(v, 0), badUp: false},
    {lbl: 'CPA', key: 'cpa', fmt: v => fmt(v, 2) + ' 元', badUp: true, show: t.cpa > 0},
    {lbl: 'CTR', key: 'ctr', fmt: v => v.toFixed(2) + '%', badUp: false, show: t.ctr > 0},
    {lbl: '转化率', key: 'cvr', fmt: v => v.toFixed(2) + '%', badUp: false, show: t.cvr > 0},
    {lbl: 'ROI', key: 'roi', fmt: v => v.toFixed(2), badUp: false, show: t.roi > 0},
  ];

  document.getElementById('metrics-grid').innerHTML = defs
    .filter(d => d.show === undefined || d.show)
    .map(d => {
      let changeHtml = '';
      if (y) {
        const chg = pctChange(t[d.key], y[d.key]);
        if (chg !== null) {
          const absChg = Math.abs(chg);
          let cls, arrow;
          if (absChg < 0.5) {
            cls = 'flat'; arrow = '→';
          } else if (chg > 0) {
            cls = d.badUp ? 'bad-up' : 'up'; arrow = '↑';
          } else {
            cls = d.badUp ? 'good-down' : 'down'; arrow = '↓';
          }
          changeHtml = `<span class="change ${cls}">${arrow} ${absChg.toFixed(1)}%</span>`;
        }
      }
      return `
        <div class="metric-card">
          <div class="lbl">${d.lbl}</div>
          <div class="val">${d.fmt(t[d.key])}</div>
          ${changeHtml}
        </div>
      `;
    }).join('');
}

function renderTopList(elId, items, type) {
  const el = document.getElementById(elId);
  if (!items.length) {
    el.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-dim);font-size:0.85rem">无数据</div>';
    return;
  }
  el.innerHTML = items.map((c, i) => `
    <div class="camp-row">
      <div class="rank">${i + 1}</div>
      <div class="name" title="${c.name}">${c.name}</div>
      <div class="stats">
        消耗 ${fmt(c.cost, 0)} · 转化 ${c.conversion} · CPA ${c.cpa !== null ? fmt(c.cpa, 1) : 'N/A'}
      </div>
    </div>
  `).join('');
}

function renderAnomalies() {
  const sec = document.getElementById('anomaly-section');
  if (!REPORT.anomalies.length) {
    sec.innerHTML = '';
    return;
  }
  sec.innerHTML = `
    <h2 class="section-title">🚨 异常提醒</h2>
    <div class="alert-list">
      ${REPORT.anomalies.map(a => `<div class="alert-item">${a}</div>`).join('')}
    </div>
  `;
}

function renderSuggestions() {
  document.getElementById('suggest-list').innerHTML =
    REPORT.suggestions.map(s => `<div class="suggest-item">${s}</div>`).join('');
}

function renderCharts() {
  if (!REPORT.yesterday) return;
  const sec = document.getElementById('chart-section');
  sec.innerHTML = `
    <h2 class="section-title">今日 vs 昨日对比</h2>
    <div class="chart-card"><div class="chart-box" id="compare-chart"></div></div>
  `;

  const t = REPORT.today, y = REPORT.yesterday;
  const defs = [
    {lbl: '消耗', t: t.cost, y: y.cost},
    {lbl: '曝光', t: t.impression, y: y.impression},
    {lbl: '点击', t: t.click, y: y.click},
    {lbl: '转化', t: t.conversion, y: y.conversion},
  ];

  const chart = echarts.init(document.getElementById('compare-chart'));
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {trigger: 'axis', backgroundColor: '#1a1d2e', borderColor: '#2a2e42', textStyle: {color: '#e8eaf0'},
      formatter: params => {
        let html = params[0].axisValue + '<br/>';
        params.forEach(p => { html += `<span style="color:${p.color}">●</span> ${p.seriesName}: <b>${fmt(p.value)}</b><br/>`; });
        return html;
      }},
    legend: {data: ['昨日', '今日'], bottom: 10, textStyle: {color: '#8b90a5'}},
    xAxis: {type: 'category', data: defs.map(d => d.lbl), axisLabel: {color: '#8b90a5'}, axisLine: {lineStyle: {color: '#2a2e42'}}},
    yAxis: {type: 'value', axisLabel: {color: '#8b90a5', formatter: v => fmt(v)}, splitLine: {lineStyle: {color: '#2a2e42'}}},
    series: [
      {name: '昨日', type: 'bar', data: defs.map(d => d.y), itemStyle: {color: '#5c6078', borderRadius: [4,4,0,0]}, barMaxWidth: 40},
      {name: '今日', type: 'bar', data: defs.map(d => d.t), itemStyle: {color: '#4e7cff', borderRadius: [4,4,0,0]}, barMaxWidth: 40},
    ],
    grid: {top: 40, bottom: 60, left: 60, right: 30},
  });
  window.addEventListener('resize', () => chart.resize());
}

renderMetrics();
renderTopList('best-list', REPORT.best, 'best');
renderTopList('worst-list', REPORT.worst, 'worst');
renderAnomalies();
renderSuggestions();
setTimeout(renderCharts, 50);
</script>
</body>
</html>"""

    report_json = json.dumps(report, ensure_ascii=False, default=str)
    html = template.replace("{{REPORT_JSON}}", report_json)
    html = html.replace("{{DATE}}", html_mod.escape(date_str))
    return html


def main():
    parser = argparse.ArgumentParser(description="每日投放日报生成器")
    parser.add_argument("--today", required=True, help="今日报表文件")
    parser.add_argument("--yesterday", help="昨日报表文件（可选，用于环比）")
    parser.add_argument("--date", help="日报日期（默认今天）")
    parser.add_argument("--out-dir", default="/mnt/user-data/outputs/", help="输出目录")
    args = parser.parse_args()

    if not os.path.exists(args.today):
        print(f"❌ 今日报表不存在: {args.today}")
        sys.exit(1)

    print(f"\n读取今日报表: {args.today}")
    df_today = load_file(args.today)
    cols = auto_detect_columns(df_today)
    print(f"识别到的列: {cols}")

    if "cost" not in cols:
        print("❌ 未识别到消耗列，请确认报表含有消耗/花费/cost 相关列")
        sys.exit(1)

    today_stats = summarize(df_today, cols)
    best, worst = get_top_campaigns(df_today, cols)

    yest_stats = None
    df_yesterday = None
    if args.yesterday:
        if os.path.exists(args.yesterday):
            print(f"读取昨日报表: {args.yesterday}")
            df_yesterday = load_file(args.yesterday)
            yest_stats = summarize(df_yesterday, cols)
        else:
            print(f"⚠️ 昨日报表不存在，跳过环比: {args.yesterday}")

    anomalies = detect_anomalies(df_today, df_yesterday, cols)
    suggestions = generate_suggestions(today_stats, yest_stats, best, worst, anomalies)

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")

    # 生成文本
    text = build_text_report(today_stats, yest_stats, best, worst, anomalies, suggestions, date_str)

    # 生成 HTML
    html = build_html_report(today_stats, yest_stats, best, worst, anomalies, suggestions, date_str)

    os.makedirs(args.out_dir, exist_ok=True)
    txt_path = os.path.join(args.out_dir, "daily_report.txt")
    html_path = os.path.join(args.out_dir, "daily_report.html")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("\n" + "=" * 60)
    print("✅ 日报已生成")
    print(f"   纯文本版（可贴钉钉/飞书）: {os.path.abspath(txt_path)}")
    print(f"   HTML 精美版: {os.path.abspath(html_path)}")
    print("=" * 60)
    print("\n【日报预览】\n")
    print(text)


if __name__ == "__main__":
    main()
