"""
A/B 测试显著性分析 - data-auto-analyzer
比例型：Z 检验（两比例差异）
均值型：Welch's T 检验（独立样本）
用法: 见 references/ab_test_guide.md
"""
import sys
import os
import argparse
import json
import math
import html as html_mod
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats as sp_stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_file, to_numeric_safe


# ───────────── 比例型 Z 检验 ─────────────
def z_test_proportions(a_success, a_total, b_success, b_total, alpha=0.05):
    """
    两比例 Z 检验（Pooled）
    返回: dict with p_value, z, a_rate, b_rate, diff, ci_lower, ci_upper, significant, confidence
    """
    p1 = a_success / a_total if a_total > 0 else 0
    p2 = b_success / b_total if b_total > 0 else 0

    # Pooled 比例
    p_pool = (a_success + b_success) / (a_total + b_total) if (a_total + b_total) > 0 else 0
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1/a_total + 1/b_total)) if a_total > 0 and b_total > 0 else 0

    # 非 pooled（用于置信区间）
    se_unpool = math.sqrt(p1*(1-p1)/a_total + p2*(1-p2)/b_total) if a_total > 0 and b_total > 0 else 0

    if se_pool == 0:
        z = 0
        p_value = 1.0
    else:
        z = (p2 - p1) / se_pool
        p_value = 2 * (1 - sp_stats.norm.cdf(abs(z)))

    # 差异的 95% 置信区间
    diff = p2 - p1
    z_crit = sp_stats.norm.ppf(1 - alpha/2)
    ci_lower = diff - z_crit * se_unpool
    ci_upper = diff + z_crit * se_unpool

    # 判定
    significant = p_value < alpha
    if p_value < 0.01:
        confidence = "极显著"
        confidence_level = 99
    elif p_value < 0.05:
        confidence = "显著"
        confidence_level = 95
    elif p_value < 0.1:
        confidence = "边缘显著"
        confidence_level = 90
    else:
        confidence = "不显著"
        confidence_level = None

    # 样本量建议（达到 95% 置信度所需）
    effect_size = abs(p2 - p1) if abs(p2 - p1) > 0 else 0.01
    required_n_per_group = math.ceil((2 * (sp_stats.norm.ppf(0.975) + sp_stats.norm.ppf(0.80))**2
                                       * p_pool * (1 - p_pool)) / (effect_size**2)) if effect_size > 0 else None

    return {
        "type": "rate",
        "a_success": a_success, "a_total": a_total, "a_rate": p1,
        "b_success": b_success, "b_total": b_total, "b_rate": p2,
        "diff": diff,
        "relative_lift": (p2 - p1) / p1 * 100 if p1 > 0 else 0,
        "z": z, "p_value": p_value,
        "ci_lower": ci_lower, "ci_upper": ci_upper,
        "significant": significant,
        "confidence": confidence,
        "confidence_level": confidence_level,
        "required_n_per_group": required_n_per_group,
        "winner": "B" if p2 > p1 else ("A" if p2 < p1 else "tie"),
    }


# ───────────── 均值型 T 检验 ─────────────
def t_test_means(a_values, b_values, alpha=0.05):
    """
    Welch's T 检验（不假设方差齐性）
    """
    a_values = np.array(a_values, dtype=float)
    a_values = a_values[~np.isnan(a_values)]
    b_values = np.array(b_values, dtype=float)
    b_values = b_values[~np.isnan(b_values)]

    if len(a_values) < 2 or len(b_values) < 2:
        return {"error": "每组至少需要 2 个有效样本"}

    t_stat, p_value = sp_stats.ttest_ind(a_values, b_values, equal_var=False)

    m1, m2 = a_values.mean(), b_values.mean()
    s1, s2 = a_values.std(ddof=1), b_values.std(ddof=1)
    n1, n2 = len(a_values), len(b_values)

    # Welch 自由度
    df_w = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1)) if (n1 > 1 and n2 > 1) else 1
    se_diff = math.sqrt(s1**2/n1 + s2**2/n2)
    t_crit = sp_stats.t.ppf(1 - alpha/2, df_w)
    diff = m2 - m1
    ci_lower = diff - t_crit * se_diff
    ci_upper = diff + t_crit * se_diff

    if p_value < 0.01:
        confidence, level = "极显著", 99
    elif p_value < 0.05:
        confidence, level = "显著", 95
    elif p_value < 0.1:
        confidence, level = "边缘显著", 90
    else:
        confidence, level = "不显著", None

    return {
        "type": "mean",
        "a_n": int(n1), "a_mean": float(m1), "a_std": float(s1),
        "b_n": int(n2), "b_mean": float(m2), "b_std": float(s2),
        "diff": float(diff),
        "relative_lift": (m2 - m1) / m1 * 100 if m1 != 0 else 0,
        "t": float(t_stat), "p_value": float(p_value),
        "ci_lower": float(ci_lower), "ci_upper": float(ci_upper),
        "significant": p_value < alpha,
        "confidence": confidence,
        "confidence_level": level,
        "winner": "B" if m2 > m1 else ("A" if m2 < m1 else "tie"),
    }


def generate_conclusion(result, a_name="A", b_name="B", metric_name="指标", higher_is_better=True):
    """生成人类可读的结论"""
    if "error" in result:
        return result["error"]

    if result["type"] == "rate":
        lift = result["relative_lift"]
        winner = result["winner"]
        if not result["significant"]:
            return f"两组 {metric_name} 无显著差异（p={result['p_value']:.4f}），不能证明哪个版本更好。建议扩大样本继续观察。"

        # 判断实际好坏
        if winner == "B":
            is_winner_better = lift > 0 if higher_is_better else lift < 0
            winner_name = b_name
            loser_name = a_name
        else:
            is_winner_better = lift < 0 if higher_is_better else lift > 0
            winner_name = a_name
            loser_name = b_name
            lift = -lift

        level_txt = f"置信度 {result['confidence_level']}%"
        if is_winner_better or (winner == "B" and lift > 0) or (winner == "A" and lift > 0):
            return f"【{winner_name}】优于【{loser_name}】：{metric_name}相对提升 {abs(lift):.2f}%，差异{result['confidence']}（{level_txt}），建议采用【{winner_name}】。"
        else:
            return f"【{winner_name}】与【{loser_name}】差异{result['confidence']}（{level_txt}），但 {metric_name} 提升 {abs(lift):.2f}%，请结合业务判断。"

    else:  # mean
        if not result["significant"]:
            return f"两组 {metric_name} 均值无显著差异（p={result['p_value']:.4f}），建议扩大样本继续观察。"

        winner = result["winner"]
        winner_mean = result["b_mean"] if winner == "B" else result["a_mean"]
        loser_mean = result["a_mean"] if winner == "B" else result["b_mean"]
        winner_name = b_name if winner == "B" else a_name
        loser_name = a_name if winner == "B" else b_name

        if higher_is_better:
            action = f"建议采用【{winner_name}】"
        else:
            # 对于 CPA、CPC 等成本指标，值小的好
            # winner 是均值大的一方，但 higher_is_better=False 时实际 loser 更优
            winner_name, loser_name = loser_name, winner_name
            winner_mean, loser_mean = loser_mean, winner_mean
            action = f"建议采用【{winner_name}】（成本更低）"

        level_txt = f"置信度 {result['confidence_level']}%"
        return f"【{winner_name}】（均值 {winner_mean:.4f}）优于【{loser_name}】（均值 {loser_mean:.4f}），差异{result['confidence']}（{level_txt}），{action}。"


def build_html(result, a_name, b_name, metric_name, higher_is_better):
    conclusion = generate_conclusion(result, a_name, b_name, metric_name, higher_is_better)

    report = {
        "result": result,
        "a_name": a_name,
        "b_name": b_name,
        "metric_name": metric_name,
        "conclusion": conclusion,
        "higher_is_better": higher_is_better,
    }

    template = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A/B 测试分析报告</title>
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

.conclusion-card {
  background: linear-gradient(135deg, rgba(78,124,255,0.1), rgba(147,112,255,0.1));
  border: 1px solid var(--accent-blue);
  border-radius: 12px; padding: 28px 32px; margin-bottom: 32px;
}
.conclusion-card.sig { border-color: var(--accent-green); background: linear-gradient(135deg, rgba(34,196,147,0.12), rgba(78,124,255,0.08)); }
.conclusion-card.not-sig { border-color: var(--accent-orange); background: linear-gradient(135deg, rgba(245,166,35,0.12), rgba(78,124,255,0.05)); }
.conclusion-card .title {
  font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--text-secondary); margin-bottom: 10px;
}
.conclusion-card .body { font-size: 1.15rem; line-height: 1.7; font-weight: 500; }

.compare-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 32px;
}
.group-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 24px;
}
.group-card.winner { border-color: var(--accent-green); background: rgba(34,196,147,0.04); }
.group-card .grp-name { font-size: 1.2rem; font-weight: 700; margin-bottom: 4px; }
.group-card.winner .grp-name::after { content: ' 🏆'; }
.group-card .grp-desc { font-size: 0.82rem; color: var(--text-dim); margin-bottom: 20px; }
.group-card .main-val {
  font-size: 2.6rem; font-weight: 700; letter-spacing: -0.03em;
  background: linear-gradient(135deg, #4e7cff 0%, #9370ff 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 4px;
}
.group-card.winner .main-val { background: linear-gradient(135deg, #22c493 0%, #4e7cff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.group-card .main-label { font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 18px; }
.group-card .detail {
  display: flex; justify-content: space-between;
  padding: 6px 0; font-size: 0.88rem;
  border-top: 1px solid rgba(42,46,66,0.6);
}
.group-card .detail .lbl { color: var(--text-secondary); }
.group-card .detail .val { color: var(--text-primary); font-weight: 500; font-variant-numeric: tabular-nums; }

.stats-box {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 24px; margin-bottom: 32px;
}
.stats-box .stat-row {
  display: grid; grid-template-columns: 180px 1fr; gap: 12px;
  padding: 10px 0; font-size: 0.9rem;
  border-bottom: 1px solid rgba(42,46,66,0.5);
}
.stats-box .stat-row:last-child { border-bottom: none; }
.stats-box .stat-row .lbl { color: var(--text-secondary); }
.stats-box .stat-row .val { color: var(--text-primary); font-variant-numeric: tabular-nums; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.tag.green { background: rgba(34,196,147,0.15); color: var(--accent-green); }
.tag.orange { background: rgba(245,166,35,0.15); color: var(--accent-orange); }
.tag.red { background: rgba(242,87,87,0.15); color: var(--accent-red); }

.chart-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 20px; margin-bottom: 20px;
}
.chart-box { width: 100%; height: 340px; }

.note { font-size: 0.85rem; color: var(--text-secondary); padding: 14px 18px;
  background: rgba(78,124,255,0.05); border-left: 3px solid var(--accent-purple);
  border-radius: 6px; margin-top: 16px; line-height: 1.7;
}

.footer {
  text-align: center; padding: 32px;
  color: var(--text-dim); font-size: 0.78rem;
  border-top: 1px solid var(--border); margin-top: 40px;
}

@media (max-width: 768px) {
  .compare-grid { grid-template-columns: 1fr; }
  .stats-box .stat-row { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<div class="header">
  <h1>A/B 测试分析报告</h1>
  <p class="subtitle">{{METRIC_NAME}} · {{TEST_TYPE}}</p>
</div>

<div class="container">

  <div class="conclusion-card {{SIG_CLASS}}">
    <div class="title">业务结论</div>
    <div class="body">{{CONCLUSION}}</div>
  </div>

  <h2 class="section-title">两组数据对比</h2>
  <div class="compare-grid" id="compare-grid"></div>

  <h2 class="section-title">可视化对比</h2>
  <div class="chart-card">
    <div class="chart-box" id="chart-compare"></div>
  </div>

  <h2 class="section-title">统计检验详情</h2>
  <div class="stats-box" id="stats-box"></div>

</div>

<div class="footer">Generated by data-auto-analyzer · A/B 测试模式</div>

<script>
const REPORT = {{REPORT_JSON}};

function fmt(n, digits = 2) {
  if (n === null || n === undefined || isNaN(n)) return '-';
  if (typeof n !== 'number') return n;
  return n.toLocaleString(undefined, {maximumFractionDigits: digits, minimumFractionDigits: Number.isInteger(n) ? 0 : digits});
}

function fmtPct(n, digits = 2) {
  if (n === null || n === undefined || isNaN(n)) return '-';
  return (n * 100).toFixed(digits) + '%';
}

function renderCompare() {
  const r = REPORT.result;
  const winner = r.winner;
  const winnerIsA = winner === 'A' && (REPORT.higher_is_better || r.type === 'rate');
  const winnerIsB = winner === 'B' && (REPORT.higher_is_better || r.type === 'rate');
  // For cost-type (higher_is_better = false), winner flips
  const actualWinner = REPORT.higher_is_better ? winner : (winner === 'A' ? 'B' : winner === 'B' ? 'A' : 'tie');

  let aCard, bCard;
  if (r.type === 'rate') {
    aCard = `
      <div class="group-card ${r.significant && actualWinner === 'A' ? 'winner' : ''}">
        <div class="grp-name">${REPORT.a_name}</div>
        <div class="grp-desc">对照组</div>
        <div class="main-val">${fmtPct(r.a_rate)}</div>
        <div class="main-label">${REPORT.metric_name}</div>
        <div class="detail"><span class="lbl">成功次数</span><span class="val">${r.a_success.toLocaleString()}</span></div>
        <div class="detail"><span class="lbl">总样本量</span><span class="val">${r.a_total.toLocaleString()}</span></div>
      </div>
    `;
    bCard = `
      <div class="group-card ${r.significant && actualWinner === 'B' ? 'winner' : ''}">
        <div class="grp-name">${REPORT.b_name}</div>
        <div class="grp-desc">实验组</div>
        <div class="main-val">${fmtPct(r.b_rate)}</div>
        <div class="main-label">${REPORT.metric_name}</div>
        <div class="detail"><span class="lbl">成功次数</span><span class="val">${r.b_success.toLocaleString()}</span></div>
        <div class="detail"><span class="lbl">总样本量</span><span class="val">${r.b_total.toLocaleString()}</span></div>
      </div>
    `;
  } else {
    aCard = `
      <div class="group-card ${r.significant && actualWinner === 'A' ? 'winner' : ''}">
        <div class="grp-name">${REPORT.a_name}</div>
        <div class="grp-desc">对照组</div>
        <div class="main-val">${fmt(r.a_mean, 3)}</div>
        <div class="main-label">${REPORT.metric_name} 均值</div>
        <div class="detail"><span class="lbl">样本量</span><span class="val">${r.a_n}</span></div>
        <div class="detail"><span class="lbl">标准差</span><span class="val">${fmt(r.a_std, 3)}</span></div>
      </div>
    `;
    bCard = `
      <div class="group-card ${r.significant && actualWinner === 'B' ? 'winner' : ''}">
        <div class="grp-name">${REPORT.b_name}</div>
        <div class="grp-desc">实验组</div>
        <div class="main-val">${fmt(r.b_mean, 3)}</div>
        <div class="main-label">${REPORT.metric_name} 均值</div>
        <div class="detail"><span class="lbl">样本量</span><span class="val">${r.b_n}</span></div>
        <div class="detail"><span class="lbl">标准差</span><span class="val">${fmt(r.b_std, 3)}</span></div>
      </div>
    `;
  }
  document.getElementById('compare-grid').innerHTML = aCard + bCard;
}

function renderStats() {
  const r = REPORT.result;
  let sigTag;
  if (r.confidence_level === 99) sigTag = '<span class="tag green">极显著</span>';
  else if (r.confidence_level === 95) sigTag = '<span class="tag green">显著</span>';
  else if (r.confidence_level === 90) sigTag = '<span class="tag orange">边缘显著</span>';
  else sigTag = '<span class="tag red">不显著</span>';

  let rows = [
    {lbl: '检验方法', val: r.type === 'rate' ? 'Z 检验（两比例差异）' : 'Welch\'s T 检验（独立样本，不假设方差齐性）'},
    {lbl: 'p 值', val: `${r.p_value.toFixed(6)} ${sigTag}`},
    {lbl: '显著性判定', val: `${r.confidence}（α = 0.05）`},
    {lbl: r.type === 'rate' ? 'Z 统计量' : 'T 统计量', val: fmt(r.z !== undefined ? r.z : r.t, 4)},
    {lbl: '绝对差异', val: r.type === 'rate' ? fmtPct(r.diff, 3) : fmt(r.diff, 4)},
    {lbl: '相对提升', val: `${r.relative_lift >= 0 ? '+' : ''}${r.relative_lift.toFixed(2)}%`},
    {lbl: '95% 置信区间', val: r.type === 'rate' ? `[${fmtPct(r.ci_lower, 3)}, ${fmtPct(r.ci_upper, 3)}]` : `[${fmt(r.ci_lower, 4)}, ${fmt(r.ci_upper, 4)}]`},
  ];
  if (r.type === 'rate' && r.required_n_per_group && !r.significant) {
    rows.push({lbl: '建议样本量', val: `每组至少 ${r.required_n_per_group.toLocaleString()} 条（当前检验功效 80%）`});
  }

  const box = document.getElementById('stats-box');
  box.innerHTML = rows.map(row => `
    <div class="stat-row">
      <span class="lbl">${row.lbl}</span>
      <span class="val">${row.val}</span>
    </div>
  `).join('');

  if (!r.significant) {
    box.innerHTML += '<div class="note">💡 结论不显著可能原因：样本量不足、两版本本身差异确实小。建议收集更多样本再判定，或检查实验设计是否合理。</div>';
  }
}

function renderChart() {
  const r = REPORT.result;
  const el = document.getElementById('chart-compare');
  let option;

  if (r.type === 'rate') {
    option = {
      backgroundColor: 'transparent',
      title: {text: `${REPORT.metric_name} 对比`, left: 'center', textStyle: {color: '#e8eaf0', fontSize: 15, fontWeight: 600}},
      tooltip: {trigger: 'axis', backgroundColor: '#1a1d2e', borderColor: '#2a2e42', textStyle: {color: '#e8eaf0'},
        formatter: p => `${p[0].name}<br/>${REPORT.metric_name}: <b>${fmtPct(p[0].value / 100)}</b>`},
      xAxis: {type: 'category', data: [REPORT.a_name, REPORT.b_name], axisLabel: {color: '#8b90a5', fontSize: 13}, axisLine: {lineStyle: {color: '#2a2e42'}}},
      yAxis: {type: 'value', axisLabel: {color: '#8b90a5', formatter: '{value}%'}, splitLine: {lineStyle: {color: '#2a2e42'}}},
      series: [{
        type: 'bar', barMaxWidth: 80,
        data: [
          {value: (r.a_rate * 100).toFixed(3), itemStyle: {color: '#4e7cff', borderRadius: [6,6,0,0]}},
          {value: (r.b_rate * 100).toFixed(3), itemStyle: {color: r.significant ? '#22c493' : '#9370ff', borderRadius: [6,6,0,0]}},
        ],
        label: {show: true, position: 'top', color: '#e8eaf0', fontSize: 13, fontWeight: 600, formatter: p => p.value + '%'},
      }],
      grid: {top: 60, bottom: 40, left: 60, right: 30},
    };
  } else {
    // 均值型：条形图 + 误差棒（标准差范围）
    const aLo = r.a_mean - r.a_std;
    const aHi = r.a_mean + r.a_std;
    const bLo = r.b_mean - r.b_std;
    const bHi = r.b_mean + r.b_std;
    option = {
      backgroundColor: 'transparent',
      title: {text: `${REPORT.metric_name} 均值对比（误差棒为±标准差）`, left: 'center', textStyle: {color: '#e8eaf0', fontSize: 15, fontWeight: 600}},
      tooltip: {trigger: 'axis', backgroundColor: '#1a1d2e', borderColor: '#2a2e42', textStyle: {color: '#e8eaf0'}},
      xAxis: {type: 'category', data: [REPORT.a_name, REPORT.b_name], axisLabel: {color: '#8b90a5', fontSize: 13}, axisLine: {lineStyle: {color: '#2a2e42'}}},
      yAxis: {type: 'value', axisLabel: {color: '#8b90a5'}, splitLine: {lineStyle: {color: '#2a2e42'}}},
      series: [
        {type: 'bar', barMaxWidth: 80,
          data: [
            {value: r.a_mean.toFixed(4), itemStyle: {color: '#4e7cff', borderRadius: [6,6,0,0]}},
            {value: r.b_mean.toFixed(4), itemStyle: {color: r.significant ? '#22c493' : '#9370ff', borderRadius: [6,6,0,0]}},
          ],
          label: {show: true, position: 'top', color: '#e8eaf0', fontSize: 13, fontWeight: 600},
        },
        {type: 'custom', renderItem: (params, api) => {
          const categoryIdx = api.value(0);
          const low = api.coord([categoryIdx, categoryIdx === 0 ? aLo : bLo]);
          const high = api.coord([categoryIdx, categoryIdx === 0 ? aHi : bHi]);
          return {
            type: 'group', children: [
              {type: 'line', shape: {x1: low[0], y1: low[1], x2: high[0], y2: high[1]}, style: {stroke: '#e8eaf0', lineWidth: 2}},
              {type: 'line', shape: {x1: low[0]-10, y1: low[1], x2: low[0]+10, y2: low[1]}, style: {stroke: '#e8eaf0', lineWidth: 2}},
              {type: 'line', shape: {x1: high[0]-10, y1: high[1], x2: high[0]+10, y2: high[1]}, style: {stroke: '#e8eaf0', lineWidth: 2}},
            ],
          };
        }, data: [[0], [1]], silent: true},
      ],
      grid: {top: 60, bottom: 40, left: 60, right: 30},
    };
  }

  const chart = echarts.init(el);
  chart.setOption(option);
  window.addEventListener('resize', () => chart.resize());
}

renderCompare();
renderStats();
setTimeout(renderChart, 50);
</script>
</body>
</html>"""

    sig_class = "sig" if result.get("significant") else "not-sig"
    test_type_txt = "比例型指标（Z 检验）" if result.get("type") == "rate" else "均值型指标（T 检验）"

    report_json = json.dumps(report, ensure_ascii=False, default=str)
    html = template.replace("{{REPORT_JSON}}", report_json)
    html = html.replace("{{METRIC_NAME}}", html_mod.escape(metric_name))
    html = html.replace("{{TEST_TYPE}}", test_type_txt)
    html = html.replace("{{SIG_CLASS}}", sig_class)
    html = html.replace("{{CONCLUSION}}", html_mod.escape(conclusion))
    return html


def main():
    parser = argparse.ArgumentParser(description="A/B 测试分析")
    parser.add_argument("--inline", action="store_true", help="使用命令行参数直接输入数据")
    parser.add_argument("--file", help="Excel/CSV 文件路径")

    # Inline mode
    parser.add_argument("--a-success", type=float, help="A 组成功数")
    parser.add_argument("--a-total", type=float, help="A 组总数")
    parser.add_argument("--b-success", type=float, help="B 组成功数")
    parser.add_argument("--b-total", type=float, help="B 组总数")

    # File mode
    parser.add_argument("--group-col", help="分组列名")
    parser.add_argument("--metric-col", help="指标列名（均值型）")
    parser.add_argument("--success-col", help="成功次数列（比例型）")
    parser.add_argument("--total-col", help="总次数列（比例型）")
    parser.add_argument("--metric-type", choices=["rate", "mean"], help="指标类型：rate=比例, mean=均值")

    # 通用
    parser.add_argument("--a-name", default="A", help="A 组名称")
    parser.add_argument("--b-name", default="B", help="B 组名称")
    parser.add_argument("--metric-name", default="指标", help="指标名称")
    parser.add_argument("--lower-is-better", action="store_true", help="指标越低越好（用于 CPA/CPC 等成本指标）")
    parser.add_argument("--out", default="/mnt/user-data/outputs/ab_result.html")

    args = parser.parse_args()
    higher_is_better = not args.lower_is_better

    if args.inline:
        if args.a_success is None or args.a_total is None or args.b_success is None or args.b_total is None:
            print("❌ inline 模式需要同时提供 --a-success --a-total --b-success --b-total")
            sys.exit(1)
        result = z_test_proportions(args.a_success, args.a_total, args.b_success, args.b_total)
        metric_name = args.metric_name if args.metric_name != "指标" else "转化率"
        print(f"\nA 组: {args.a_success}/{args.a_total} = {result['a_rate']*100:.3f}%")
        print(f"B 组: {args.b_success}/{args.b_total} = {result['b_rate']*100:.3f}%")
    elif args.file:
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}")
            sys.exit(1)
        df = load_file(args.file)
        if args.metric_type is None:
            print("❌ 从文件读取时必须指定 --metric-type (rate 或 mean)")
            sys.exit(1)
        if args.metric_type == "rate":
            if not (args.group_col and args.success_col and args.total_col):
                print("❌ rate 模式需要 --group-col --success-col --total-col")
                sys.exit(1)
            grouped = df.groupby(args.group_col).agg({args.success_col: "sum", args.total_col: "sum"})
            if len(grouped) != 2:
                print(f"❌ 分组列需要正好两组，当前: {list(grouped.index)}")
                sys.exit(1)
            groups = list(grouped.index)
            result = z_test_proportions(
                float(grouped.loc[groups[0], args.success_col]),
                float(grouped.loc[groups[0], args.total_col]),
                float(grouped.loc[groups[1], args.success_col]),
                float(grouped.loc[groups[1], args.total_col]),
            )
            args.a_name = str(groups[0]) if args.a_name == "A" else args.a_name
            args.b_name = str(groups[1]) if args.b_name == "B" else args.b_name
            metric_name = args.metric_name if args.metric_name != "指标" else args.success_col + " / " + args.total_col
        else:  # mean
            if not (args.group_col and args.metric_col):
                print("❌ mean 模式需要 --group-col --metric-col")
                sys.exit(1)
            df[args.metric_col] = to_numeric_safe(df[args.metric_col])
            groups = df[args.group_col].dropna().unique()
            if len(groups) != 2:
                print(f"❌ 分组列需要正好两组，当前: {list(groups)}")
                sys.exit(1)
            a_vals = df[df[args.group_col] == groups[0]][args.metric_col].dropna().values
            b_vals = df[df[args.group_col] == groups[1]][args.metric_col].dropna().values
            result = t_test_means(a_vals, b_vals)
            args.a_name = str(groups[0]) if args.a_name == "A" else args.a_name
            args.b_name = str(groups[1]) if args.b_name == "B" else args.b_name
            metric_name = args.metric_name if args.metric_name != "指标" else args.metric_col
    else:
        print("❌ 需要指定 --inline 或 --file")
        sys.exit(1)

    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)

    print(f"\np 值: {result['p_value']:.6f}")
    print(f"显著性: {result['confidence']}")
    print(f"结论: {generate_conclusion(result, args.a_name, args.b_name, metric_name, higher_is_better)}")

    html = build_html(result, args.a_name, args.b_name, metric_name, higher_is_better)
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ A/B 测试报告已生成: {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
