"""
广告账户诊断器 - data-auto-analyzer
按业务规则给每条计划打红/黄/绿三级预警，输出处置建议
用法: python3 diagnose.py --file ads.xlsx --out /path/to/diagnose.html
"""
import sys
import os
import argparse
import json
import html as html_mod
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

# 支持两种运行方式：作为脚本直接运行 / 作为模块导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_file, auto_detect_columns, to_numeric_safe, fmt_number


def diagnose_campaigns(df, cols):
    """
    按规则给每条计划打诊断标签
    返回 list of dict: [{name, level, reasons, metrics, actions}, ...]
    """
    # 聚合到计划维度（可能原始数据按日期细分）
    campaign_col = cols.get("campaign")
    if campaign_col:
        agg_dict = {}
        for key in ["cost", "impression", "click", "conversion", "revenue"]:
            if cols.get(key):
                agg_dict[cols[key]] = "sum"
        df_agg = df.groupby(campaign_col).agg(agg_dict).reset_index()
    else:
        df_agg = df.copy()

    # 计算派生指标
    cost_col = cols.get("cost")
    imp_col = cols.get("impression")
    click_col = cols.get("click")
    conv_col = cols.get("conversion")

    if cost_col:
        df_agg["_cost"] = to_numeric_safe(df_agg[cost_col]).fillna(0)
    else:
        df_agg["_cost"] = 0

    if imp_col:
        df_agg["_impression"] = to_numeric_safe(df_agg[imp_col]).fillna(0)
    else:
        df_agg["_impression"] = 0

    if click_col:
        df_agg["_click"] = to_numeric_safe(df_agg[click_col]).fillna(0)
    else:
        df_agg["_click"] = 0

    if conv_col:
        df_agg["_conversion"] = to_numeric_safe(df_agg[conv_col]).fillna(0)
    else:
        df_agg["_conversion"] = 0

    # 派生指标
    df_agg["_ctr"] = np.where(df_agg["_impression"] > 0,
                              df_agg["_click"] / df_agg["_impression"] * 100, 0)
    df_agg["_cvr"] = np.where(df_agg["_click"] > 0,
                              df_agg["_conversion"] / df_agg["_click"] * 100, 0)
    df_agg["_cpa"] = np.where(df_agg["_conversion"] > 0,
                              df_agg["_cost"] / df_agg["_conversion"], np.nan)

    # 整体均值
    mean_cost = df_agg["_cost"].mean()
    mean_ctr = df_agg[df_agg["_impression"] > 1000]["_ctr"].mean() if (df_agg["_impression"] > 1000).any() else df_agg["_ctr"].mean()
    mean_cvr = df_agg["_cvr"].mean()
    mean_cpa = df_agg[df_agg["_conversion"] > 0]["_cpa"].mean() if (df_agg["_conversion"] > 0).any() else 0

    results = []
    for _, row in df_agg.iterrows():
        name = str(row[campaign_col]) if campaign_col else f"行{row.name+1}"
        cost = row["_cost"]
        imp = row["_impression"]
        click = row["_click"]
        conv = row["_conversion"]
        ctr = row["_ctr"]
        cvr = row["_cvr"]
        cpa = row["_cpa"]

        reasons = []  # 命中的规则
        actions = []  # 处置建议
        level = "green"

        # === 红色规则 ===
        # 1. 高消耗零转化
        if cost >= mean_cost * 2 and conv == 0 and mean_cost > 0:
            reasons.append(f"消耗是均值的 {cost/mean_cost:.1f} 倍但无转化")
            actions.append("⚠️ 建议立即暂停，检查落地页和定向人群")
            level = "red"

        # 2. CPA 严重超标
        if conv > 0 and mean_cpa > 0 and cpa >= mean_cpa * 3:
            reasons.append(f"CPA 是均值的 {cpa/mean_cpa:.1f} 倍")
            actions.append(f"❌ CPA 严重超标，建议暂停或降价 50%")
            level = "red"

        # 3. CTR 异常低
        if imp > 1000 and mean_ctr > 0 and ctr <= mean_ctr * 0.3:
            reasons.append(f"CTR {ctr:.2f}% 仅为均值 {mean_ctr:.2f}% 的 {ctr/mean_ctr*100:.0f}%")
            actions.append("📉 CTR 异常低，创意吸引力不足，建议更换素材")
            level = "red"

        # 4. 转化率极低（有成本前提）
        if click > 0 and cost >= mean_cost and mean_cvr > 0 and cvr <= mean_cvr * 0.2:
            reasons.append(f"转化率 {cvr:.2f}% 远低于均值 {mean_cvr:.2f}%")
            actions.append("❌ 转化率极低，检查落地页匹配度")
            level = "red"

        # === 黄色规则（未判红时才检查）===
        if level != "red":
            if conv > 0 and mean_cpa > 0 and cpa >= mean_cpa * 1.5:
                reasons.append(f"CPA 偏高 {(cpa/mean_cpa-1)*100:.0f}%")
                actions.append("⚡ 建议优化落地页、收窄定向")
                level = "yellow"

            if imp > 1000 and mean_ctr > 0 and ctr <= mean_ctr * 0.6:
                reasons.append(f"CTR 偏低 {(1-ctr/mean_ctr)*100:.0f}%")
                actions.append("💡 建议 A/B 测试新素材")
                level = "yellow"

            if click > 0 and mean_cvr > 0 and cvr <= mean_cvr * 0.5:
                reasons.append(f"转化率偏低 {(1-cvr/mean_cvr)*100:.0f}%")
                actions.append("🎯 检查落地页与广告素材的一致性")
                level = "yellow"

            if cost >= mean_cost * 1.5 and conv > 0 and conv <= df_agg["_conversion"].mean() * 0.5:
                reasons.append("高消耗低转化")
                actions.append("💰 消耗高转化少，建议适度降价观察 2-3 天")
                level = "yellow"

        # === 绿色（优秀）===
        if level == "green":
            if conv > 0 and mean_cpa > 0 and cpa <= mean_cpa * 0.7:
                pct = (1 - cpa/mean_cpa) * 100
                reasons.append(f"CPA 优于均值 {pct:.0f}%")
                actions.append("✅ 表现优异，建议适度加价扩量")
            else:
                reasons.append("各项指标健康")
                actions.append("✅ 保持当前投放策略")

        results.append({
            "name": name,
            "level": level,
            "reasons": reasons,
            "actions": actions,
            "cost": float(cost),
            "impression": float(imp),
            "click": float(click),
            "conversion": float(conv),
            "ctr": float(ctr),
            "cvr": float(cvr),
            "cpa": float(cpa) if not pd.isna(cpa) else None,
        })

    # 按等级 + 消耗排序（红色优先，消耗大的在前）
    level_order = {"red": 0, "yellow": 1, "green": 2}
    results.sort(key=lambda x: (level_order[x["level"]], -x["cost"]))

    return results, {
        "mean_cost": float(mean_cost),
        "mean_ctr": float(mean_ctr),
        "mean_cvr": float(mean_cvr),
        "mean_cpa": float(mean_cpa),
        "total_cost": float(df_agg["_cost"].sum()),
        "total_click": float(df_agg["_click"].sum()),
        "total_impression": float(df_agg["_impression"].sum()),
        "total_conversion": float(df_agg["_conversion"].sum()),
    }


def build_html(results, stats, cols, file_name):
    """生成诊断 HTML 报告"""
    red_count = sum(1 for r in results if r["level"] == "red")
    yellow_count = sum(1 for r in results if r["level"] == "yellow")
    green_count = sum(1 for r in results if r["level"] == "green")

    report = {
        "file_name": file_name,
        "total_campaigns": len(results),
        "red_count": red_count,
        "yellow_count": yellow_count,
        "green_count": green_count,
        "results": results,
        "stats": stats,
        "cols": {k: str(v) for k, v in cols.items()},
    }

    template = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>账户诊断报告</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.5.0/echarts.min.js"></script>
<style>
:root {
  --bg-primary: #0f1117; --bg-card: #1a1d2e; --bg-card-hover: #222640;
  --border: #2a2e42; --text-primary: #e8eaf0; --text-secondary: #8b90a5; --text-dim: #5c6078;
  --accent-blue: #4e7cff; --accent-green: #22c493; --accent-orange: #f5a623;
  --accent-red: #f25757; --accent-purple: #9370ff;
  --red-bg: rgba(242,87,87,0.08); --yellow-bg: rgba(245,166,35,0.08); --green-bg: rgba(34,196,147,0.08);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
  background: var(--bg-primary); color: var(--text-primary); line-height: 1.6; min-height: 100vh;
}
.container { max-width: 1400px; margin: 0 auto; padding: 32px 24px; }
.header {
  text-align: center; padding: 48px 24px;
  background: linear-gradient(180deg, rgba(78,124,255,0.08) 0%, transparent 100%);
  border-bottom: 1px solid var(--border);
}
.header h1 {
  font-size: 2rem; font-weight: 700;
  background: linear-gradient(135deg, #4e7cff 0%, #9370ff 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 8px; letter-spacing: -0.02em;
}
.header .subtitle { color: var(--text-secondary); font-size: 0.95rem; }
.section-title {
  font-size: 1.2rem; font-weight: 600; margin: 40px 0 20px;
  padding-left: 14px; border-left: 3px solid var(--accent-blue);
}

.summary-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px;
}
.sum-card {
  border-radius: 12px; padding: 24px 20px;
  border: 1px solid var(--border); position: relative; overflow: hidden;
}
.sum-card.red { background: var(--red-bg); border-color: rgba(242,87,87,0.25); }
.sum-card.yellow { background: var(--yellow-bg); border-color: rgba(245,166,35,0.25); }
.sum-card.green { background: var(--green-bg); border-color: rgba(34,196,147,0.25); }
.sum-card .icon { font-size: 1.5rem; margin-bottom: 8px; }
.sum-card .label { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px; }
.sum-card .value { font-size: 2.4rem; font-weight: 700; letter-spacing: -0.03em; }
.sum-card.red .value { color: var(--accent-red); }
.sum-card.yellow .value { color: var(--accent-orange); }
.sum-card.green .value { color: var(--accent-green); }
.sum-card .sub { font-size: 0.8rem; color: var(--text-dim); margin-top: 4px; }

.metric-row {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px; margin-bottom: 32px;
}
.metric-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 10px; padding: 16px;
}
.metric-card .lbl { font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 6px; }
.metric-card .val { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); }
.metric-card .sub { font-size: 0.75rem; color: var(--text-dim); margin-top: 2px; }

.filter-bar {
  display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;
}
.filter-btn {
  background: var(--bg-card); border: 1px solid var(--border);
  color: var(--text-secondary); padding: 8px 16px; border-radius: 8px;
  cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
}
.filter-btn:hover { border-color: var(--accent-blue); color: var(--text-primary); }
.filter-btn.active { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; }

.diagnose-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 32px; }
.diag-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-left: 4px solid var(--accent-blue);
  border-radius: 10px; padding: 18px 20px;
}
.diag-card.red { border-left-color: var(--accent-red); }
.diag-card.yellow { border-left-color: var(--accent-orange); }
.diag-card.green { border-left-color: var(--accent-green); }
.diag-card .top-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; flex-wrap: wrap; gap: 10px;
}
.diag-card .name { font-size: 1rem; font-weight: 600; color: var(--text-primary); }
.badge {
  display: inline-block; padding: 3px 10px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 600; letter-spacing: 0.04em;
}
.badge.red { background: var(--red-bg); color: var(--accent-red); }
.badge.yellow { background: var(--yellow-bg); color: var(--accent-orange); }
.badge.green { background: var(--green-bg); color: var(--accent-green); }

.diag-metrics {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 8px; margin-bottom: 12px; padding: 10px 12px;
  background: rgba(78,124,255,0.04); border-radius: 6px;
}
.diag-metrics .m { font-size: 0.78rem; }
.diag-metrics .m .lbl { color: var(--text-secondary); margin-right: 4px; }
.diag-metrics .m .val { color: var(--text-primary); font-weight: 600; font-variant-numeric: tabular-nums; }

.reason-list, .action-list { margin: 6px 0; }
.reason-list .item, .action-list .item {
  font-size: 0.85rem; color: var(--text-secondary); padding: 3px 0;
}
.action-list .item { color: var(--text-primary); font-weight: 500; }

.chart-grid {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: 20px; margin-bottom: 32px;
}
.chart-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 20px;
}
.chart-card.full { grid-column: 1 / -1; }
.chart-box { width: 100%; height: 400px; }

.footer {
  text-align: center; padding: 32px;
  color: var(--text-dim); font-size: 0.78rem;
  border-top: 1px solid var(--border); margin-top: 40px;
}

@media (max-width: 768px) {
  .summary-grid { grid-template-columns: 1fr; }
  .chart-grid { grid-template-columns: 1fr; }
  .container { padding: 16px 12px; }
  .header h1 { font-size: 1.5rem; }
}
</style>
</head>
<body>

<div class="header">
  <h1>账户诊断报告</h1>
  <p class="subtitle">{{FILE_NAME}} · 共诊断 {{TOTAL}} 条计划</p>
</div>

<div class="container">

  <h2 class="section-title">诊断总览</h2>
  <div class="summary-grid">
    <div class="sum-card red">
      <div class="icon">🔴</div>
      <div class="label">红色预警</div>
      <div class="value" id="sum-red"></div>
      <div class="sub">建议立即处理</div>
    </div>
    <div class="sum-card yellow">
      <div class="icon">🟡</div>
      <div class="label">黄色关注</div>
      <div class="value" id="sum-yellow"></div>
      <div class="sub">需要优化观察</div>
    </div>
    <div class="sum-card green">
      <div class="icon">🟢</div>
      <div class="label">绿色健康</div>
      <div class="value" id="sum-green"></div>
      <div class="sub">可保持或加量</div>
    </div>
  </div>

  <h2 class="section-title">核心指标</h2>
  <div class="metric-row" id="metric-row"></div>

  <h2 class="section-title">诊断详情</h2>
  <div class="filter-bar">
    <button class="filter-btn active" data-level="all" onclick="filterLevel('all', this)">全部 <span id="f-all-cnt"></span></button>
    <button class="filter-btn" data-level="red" onclick="filterLevel('red', this)">🔴 红色预警 <span id="f-red-cnt"></span></button>
    <button class="filter-btn" data-level="yellow" onclick="filterLevel('yellow', this)">🟡 黄色关注 <span id="f-yellow-cnt"></span></button>
    <button class="filter-btn" data-level="green" onclick="filterLevel('green', this)">🟢 绿色健康 <span id="f-green-cnt"></span></button>
  </div>
  <div class="diagnose-list" id="diagnose-list"></div>

  <h2 class="section-title">数据可视化</h2>
  <div class="chart-grid">
    <div class="chart-card"><div class="chart-box" id="chart-level-pie"></div></div>
    <div class="chart-card"><div class="chart-box" id="chart-top-cost"></div></div>
    <div class="chart-card full"><div class="chart-box" id="chart-cost-conv"></div></div>
  </div>

</div>

<div class="footer">Generated by data-auto-analyzer · 账户诊断模式</div>

<script>
const REPORT = {{REPORT_JSON}};
let activeLevel = 'all';

function fmt(n) {
  if (n === null || n === undefined || (typeof n === 'number' && isNaN(n))) return '-';
  if (typeof n !== 'number') return n;
  if (Math.abs(n) >= 1e8) return (n / 1e8).toFixed(2) + '亿';
  if (Math.abs(n) >= 1e4) return (n / 1e4).toFixed(2) + '万';
  if (Number.isInteger(n)) return n.toLocaleString();
  return n.toLocaleString(undefined, {maximumFractionDigits: 2});
}

function renderSummary() {
  document.getElementById('sum-red').textContent = REPORT.red_count;
  document.getElementById('sum-yellow').textContent = REPORT.yellow_count;
  document.getElementById('sum-green').textContent = REPORT.green_count;
  document.getElementById('f-all-cnt').textContent = `(${REPORT.total_campaigns})`;
  document.getElementById('f-red-cnt').textContent = `(${REPORT.red_count})`;
  document.getElementById('f-yellow-cnt').textContent = `(${REPORT.yellow_count})`;
  document.getElementById('f-green-cnt').textContent = `(${REPORT.green_count})`;
}

function renderMetrics() {
  const s = REPORT.stats;
  const metrics = [
    {lbl: '总消耗', val: fmt(s.total_cost), sub: '元'},
    {lbl: '总曝光', val: fmt(s.total_impression), sub: ''},
    {lbl: '总点击', val: fmt(s.total_click), sub: ''},
    {lbl: '总转化', val: fmt(s.total_conversion), sub: ''},
    {lbl: '平均 CPA', val: fmt(s.mean_cpa), sub: '元'},
    {lbl: '平均 CTR', val: s.mean_ctr.toFixed(2) + '%', sub: ''},
    {lbl: '平均转化率', val: s.mean_cvr.toFixed(2) + '%', sub: ''},
  ];
  document.getElementById('metric-row').innerHTML = metrics.map(m => `
    <div class="metric-card">
      <div class="lbl">${m.lbl}</div>
      <div class="val">${m.val}</div>
      ${m.sub ? `<div class="sub">${m.sub}</div>` : ''}
    </div>
  `).join('');
}

function renderDiagnose() {
  const list = document.getElementById('diagnose-list');
  const levelLabels = {red: '🔴 红色预警', yellow: '🟡 黄色关注', green: '🟢 绿色健康'};

  const filtered = activeLevel === 'all' ? REPORT.results : REPORT.results.filter(r => r.level === activeLevel);

  if (!filtered.length) {
    list.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-dim)">无此类别计划</div>';
    return;
  }

  list.innerHTML = filtered.map(r => `
    <div class="diag-card ${r.level}">
      <div class="top-row">
        <div class="name">${r.name}</div>
        <span class="badge ${r.level}">${levelLabels[r.level]}</span>
      </div>
      <div class="diag-metrics">
        <div class="m"><span class="lbl">消耗</span><span class="val">${fmt(r.cost)}</span></div>
        <div class="m"><span class="lbl">曝光</span><span class="val">${fmt(r.impression)}</span></div>
        <div class="m"><span class="lbl">点击</span><span class="val">${fmt(r.click)}</span></div>
        <div class="m"><span class="lbl">转化</span><span class="val">${fmt(r.conversion)}</span></div>
        <div class="m"><span class="lbl">CTR</span><span class="val">${r.ctr.toFixed(2)}%</span></div>
        <div class="m"><span class="lbl">转化率</span><span class="val">${r.cvr.toFixed(2)}%</span></div>
        <div class="m"><span class="lbl">CPA</span><span class="val">${r.cpa !== null ? fmt(r.cpa) : '-'}</span></div>
      </div>
      <div class="reason-list">
        ${r.reasons.map(reason => `<div class="item">· ${reason}</div>`).join('')}
      </div>
      <div class="action-list">
        ${r.actions.map(a => `<div class="item">${a}</div>`).join('')}
      </div>
    </div>
  `).join('');
}

function filterLevel(level, btn) {
  activeLevel = level;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderDiagnose();
}

function initCharts() {
  // 1. 等级分布饼图
  const pieEl = document.getElementById('chart-level-pie');
  echarts.init(pieEl).setOption({
    backgroundColor: 'transparent',
    title: {text: '诊断等级分布', left: 'center', textStyle: {color: '#e8eaf0', fontSize: 15, fontWeight: 600}},
    tooltip: {trigger: 'item', backgroundColor: '#1a1d2e', borderColor: '#2a2e42', textStyle: {color: '#e8eaf0'}},
    legend: {bottom: 10, textStyle: {color: '#8b90a5', fontSize: 11}},
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['50%', '48%'],
      data: [
        {name: '🔴 红色', value: REPORT.red_count, itemStyle: {color: '#f25757'}},
        {name: '🟡 黄色', value: REPORT.yellow_count, itemStyle: {color: '#f5a623'}},
        {name: '🟢 绿色', value: REPORT.green_count, itemStyle: {color: '#22c493'}},
      ],
      label: {color: '#8b90a5', fontSize: 11},
      itemStyle: {borderRadius: 6, borderColor: '#1a1d2e', borderWidth: 2},
    }],
  });

  // 2. 消耗 Top 10 柱状图
  const topCost = [...REPORT.results].sort((a, b) => b.cost - a.cost).slice(0, 10);
  const costEl = document.getElementById('chart-top-cost');
  echarts.init(costEl).setOption({
    backgroundColor: 'transparent',
    title: {text: '消耗 TOP 10', left: 'center', textStyle: {color: '#e8eaf0', fontSize: 15, fontWeight: 600}},
    tooltip: {trigger: 'axis', backgroundColor: '#1a1d2e', borderColor: '#2a2e42', textStyle: {color: '#e8eaf0'}},
    xAxis: {type: 'value', axisLabel: {color: '#8b90a5', formatter: fmt}, splitLine: {lineStyle: {color: '#2a2e42'}}},
    yAxis: {type: 'category', data: topCost.map(r => r.name).reverse(),
      axisLabel: {color: '#8b90a5', fontSize: 11, formatter: v => v.length > 15 ? v.slice(0,15)+'…' : v},
      axisLine: {lineStyle: {color: '#2a2e42'}}},
    series: [{
      type: 'bar', data: topCost.map(r => ({
        value: r.cost,
        itemStyle: {color: r.level === 'red' ? '#f25757' : r.level === 'yellow' ? '#f5a623' : '#22c493', borderRadius: [0, 4, 4, 0]}
      })).reverse(),
      barMaxWidth: 20,
      label: {show: true, position: 'right', color: '#8b90a5', fontSize: 10, formatter: p => fmt(p.value)},
    }],
    grid: {top: 50, bottom: 20, left: 120, right: 60},
  });

  // 3. 消耗 vs 转化散点图
  const scatterEl = document.getElementById('chart-cost-conv');
  echarts.init(scatterEl).setOption({
    backgroundColor: 'transparent',
    title: {text: '消耗 vs 转化散点图（颜色表示诊断等级）', left: 'center', textStyle: {color: '#e8eaf0', fontSize: 15, fontWeight: 600}},
    tooltip: {trigger: 'item', backgroundColor: '#1a1d2e', borderColor: '#2a2e42', textStyle: {color: '#e8eaf0'},
      formatter: p => `${p.data[2]}<br/>消耗: ${fmt(p.data[0])}<br/>转化: ${fmt(p.data[1])}`},
    xAxis: {type: 'value', name: '消耗', nameTextStyle: {color: '#8b90a5'}, axisLabel: {color: '#8b90a5', formatter: fmt}, splitLine: {lineStyle: {color: '#2a2e42'}}},
    yAxis: {type: 'value', name: '转化', nameTextStyle: {color: '#8b90a5'}, axisLabel: {color: '#8b90a5'}, splitLine: {lineStyle: {color: '#2a2e42'}}},
    series: [
      {name: '🔴 红色', type: 'scatter', symbolSize: 14,
        data: REPORT.results.filter(r => r.level === 'red').map(r => [r.cost, r.conversion, r.name]),
        itemStyle: {color: '#f25757', opacity: 0.8}},
      {name: '🟡 黄色', type: 'scatter', symbolSize: 12,
        data: REPORT.results.filter(r => r.level === 'yellow').map(r => [r.cost, r.conversion, r.name]),
        itemStyle: {color: '#f5a623', opacity: 0.8}},
      {name: '🟢 绿色', type: 'scatter', symbolSize: 10,
        data: REPORT.results.filter(r => r.level === 'green').map(r => [r.cost, r.conversion, r.name]),
        itemStyle: {color: '#22c493', opacity: 0.7}},
    ],
    legend: {bottom: 10, textStyle: {color: '#8b90a5'}},
    grid: {top: 60, bottom: 60, left: 70, right: 30},
  });

  window.addEventListener('resize', () => {
    [pieEl, costEl, scatterEl].forEach(el => {
      const inst = echarts.getInstanceByDom(el);
      if (inst) inst.resize();
    });
  });
}

renderSummary();
renderMetrics();
renderDiagnose();
setTimeout(initCharts, 100);
</script>
</body>
</html>"""

    report_json = json.dumps(report, ensure_ascii=False, default=str)
    html = template.replace("{{REPORT_JSON}}", report_json)
    html = html.replace("{{FILE_NAME}}", html_mod.escape(file_name))
    html = html.replace("{{TOTAL}}", str(len(results)))
    return html


def main():
    parser = argparse.ArgumentParser(description="广告账户诊断器")
    parser.add_argument("--file", required=True, help="投放报表文件 (xlsx/xls/csv)")
    parser.add_argument("--out", default="/mnt/user-data/outputs/diagnose_report.html")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)

    print(f"\n正在读取: {args.file}")
    df = load_file(args.file)
    print(f"读取成功，{len(df)} 行 × {len(df.columns)} 列")

    cols = auto_detect_columns(df)
    print(f"\n识别到的关键列:")
    for k, v in cols.items():
        print(f"  {k}: {v}")

    if "cost" not in cols or ("conversion" not in cols and "click" not in cols):
        print("\n❌ 未能识别到必要的列（需要消耗列 + 转化或点击列）")
        print("   请检查表头是否包含这些关键词：消耗/花费/cost, 转化/conversion, 点击/click")
        sys.exit(1)

    results, stats = diagnose_campaigns(df, cols)

    red_n = sum(1 for r in results if r["level"] == "red")
    yellow_n = sum(1 for r in results if r["level"] == "yellow")
    green_n = sum(1 for r in results if r["level"] == "green")

    print(f"\n诊断完成：")
    print(f"  🔴 红色预警: {red_n}")
    print(f"  🟡 黄色关注: {yellow_n}")
    print(f"  🟢 绿色健康: {green_n}")

    html = build_html(results, stats, cols, os.path.basename(args.file))

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ 诊断报告已生成: {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
