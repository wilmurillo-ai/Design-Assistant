#!/usr/bin/env bash
# render.sh — MiroThinker 1.7 输出渲染
# 通过 source 加载，共享所有 MT_* 变量
# bash 3.2 兼容

# ── JSON 解析工具函数 ─────────────────────────────────────────

# 从 MT_DIVERGE 渲染发散维度树
render_diverge_tree() {
    python3 -c "
import json, re, os

raw = os.environ.get('MT_DIVERGE', '')
try:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    data = json.loads(match.group()) if match else {}
    dims = data.get('dimensions', [])
except:
    dims = []

if not dims:
    print('│   └── (发散数据解析失败，原始内容已记录)')
    exit()

total = len(dims)
for i, d in enumerate(dims):
    is_last_dim = (i == total - 1)
    prefix = '└──' if is_last_dim else '├──'
    cont   = '    ' if is_last_dim else '│   '
    name  = d.get('name', '未知维度')
    angle = d.get('angle', '')
    print(f'│   {prefix} {name}')
    if angle:
        print(f'│   {cont}  \033[2m{angle}\033[0m')
    perspectives = d.get('perspectives', [])
    wild = d.get('wild_card', '')
    for j, p in enumerate(perspectives):
        is_last_p = (j == len(perspectives)-1) and not wild
        pp = '└──' if is_last_p else '├──'
        print(f'│   {cont}  {pp} {p}')
    if wild:
        print(f'│   {cont}  └── \033[33m★ 野卡：{wild}\033[0m')
"
}

# 从 MT_CONVERGE 渲染收敛洞察
render_converge_tree() {
    python3 -c "
import json, re, os

raw = os.environ.get('MT_CONVERGE', '')
try:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    data = json.loads(match.group()) if match else {}
    insights = data.get('core_insights', [])
except:
    insights = []

if not insights:
    synth = os.environ.get('MT_CONVERGE_SYNTHESIS', '收敛分析完成')
    print(f'│   └── {synth}')
    exit()

colors = {'HIGH': '\033[32m', 'MEDIUM': '\033[33m', 'LOW': '\033[2m'}
reset = '\033[0m'

total = len(insights)
for i, ins in enumerate(insights):
    is_last = (i == total - 1)
    prefix = '└──' if is_last else '├──'
    cont   = '    ' if is_last else '│   '
    impact = ins.get('impact', 'MEDIUM')
    color = colors.get(impact, '')
    text = ins.get('insight', '')
    rat  = ins.get('rationale', '')
    print(f'│   {prefix} {color}[{impact}]{reset} {text}')
    if rat:
        print(f'│   {cont}  \033[2m→ {rat}\033[0m')
"
}

# 从 MT_CRITIQUE 渲染批判树
render_critique_tree() {
    python3 -c "
import json, re, os

raw = os.environ.get('MT_CRITIQUE', '')
try:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    data = json.loads(match.group()) if match else {}
except:
    data = {}

verdict  = os.environ.get('MT_CRITIQUE_VERDICT', 'NEEDS_REVISION')
steelman = os.environ.get('MT_CRITIQUE_STEELMAN', '')

v_colors = {'SOLID': '\033[32m', 'NEEDS_REVISION': '\033[33m', 'FUNDAMENTALLY_FLAWED': '\033[31m'}
reset = '\033[0m'
yellow = '\033[33m'
red    = '\033[31m'
dim    = '\033[2m'

# 假设被挑战
assumptions = data.get('assumptions_challenged', [])
if assumptions:
    print(f'│   ├── 假设挑战')
    for a in assumptions[:3]:
        sev = a.get('severity','MEDIUM')
        sc  = red if sev=='HIGH' else yellow
        print(f'│   │   ├── {sc}[{sev}]{reset} {a.get(\"assumption\",\"\")}')
        ch = a.get('challenge','')
        if ch:
            print(f'│   │   │   {dim}└── {ch}{reset}')

# 盲点
blind = data.get('blind_spots', [])
if blind:
    print(f'│   ├── 盲点清单')
    for b in blind[:3]:
        print(f'│   │   ├── {yellow}⚠{reset} {b}')

# 风险
risks = data.get('risks', [])
if risks:
    print(f'│   ├── 风险矩阵')
    for r in risks[:3]:
        prob   = r.get('probability','MEDIUM')
        impact = r.get('impact','MEDIUM')
        mit    = r.get('mitigation','')
        print(f'│   │   ├── {red}[{prob}×{impact}]{reset} {r.get(\"risk\",\"\")}')
        if mit:
            print(f'│   │   │   {dim}└── 缓解：{mit}{reset}')

# 裁定
vc = v_colors.get(verdict, yellow)
print(f'│   └── 裁定：{vc}{verdict}{reset}')
if steelman:
    print(f'│       {dim}最强辩护：{steelman}{reset}')
"
}

# 从 MT_CREATE 渲染创造方案树
render_create_tree() {
    python3 -c "
import json, re, os

raw = os.environ.get('MT_CREATE', '')
try:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    data = json.loads(match.group()) if match else {}
    solutions = data.get('final_solutions', [])
except:
    solutions = []

one_sentence = os.environ.get('MT_ONE_SENTENCE', '')
meta         = os.environ.get('MT_META_INSIGHT', '')

green  = '\033[32m'
cyan   = '\033[36m'
bold   = '\033[1m'
dim    = '\033[2m'
reset  = '\033[0m'

c_colors = {'HIGH': green, 'MEDIUM': '\033[33m', 'LOW': dim}

if not solutions:
    if one_sentence:
        print(f'│   └── {bold}{one_sentence}{reset}')
    exit()

total = len(solutions)
for i, sol in enumerate(solutions):
    is_last = (i == total - 1) and not one_sentence
    prefix = '└──' if is_last else '├──'
    cont   = '    ' if is_last else '│   '
    conf   = sol.get('confidence','MEDIUM')
    cc     = c_colors.get(conf, '')
    title  = sol.get('title','方案')
    idea   = sol.get('core_idea','')
    outcome= sol.get('expected_outcome','')
    steps  = sol.get('action_steps', [])

    print(f'│   {prefix} {bold}方案{chr(65+i)}：{title}{reset} {cc}[置信度:{conf}]{reset}')
    if idea:
        print(f'│   {cont}  {dim}核心：{idea}{reset}')
    for s in steps[:3]:
        act  = s.get('action','')
        tl   = s.get('timeline','')
        step_n = s.get('step', '')
        print(f'│   {cont}  ├── {step_n}. {act} {dim}({tl}){reset}')
    if outcome:
        print(f'│   {cont}  └── {cyan}预期：{outcome}{reset}')

if one_sentence:
    print(f'│   └── {bold}一句话答案：\"{one_sentence}\"{reset}')
"
}

# ── 置信度进度条 ──────────────────────────────────────────────
render_confidence_bar() {
    python3 -c "
import json, re, os

# 计算各阶段完整度
def bar(pct):
    filled = int(pct / 5)
    empty  = 20 - filled
    return '█' * filled + '░' * empty

# M1 维度数
raw1 = os.environ.get('MT_DIVERGE','')
try:
    m = re.search(r'\{.*\}', raw1, re.DOTALL)
    d1 = json.loads(m.group()) if m else {}
    div_count = len(d1.get('dimensions', []))
    div_pct = min(100, div_count * 16)
except:
    div_pct = 50

# M2 洞察数
raw2 = os.environ.get('MT_CONVERGE','')
try:
    m = re.search(r'\{.*\}', raw2, re.DOTALL)
    d2 = json.loads(m.group()) if m else {}
    ins_count = len(d2.get('core_insights', []))
    conv_pct = min(100, ins_count * 33)
except:
    conv_pct = 60

# M3
verdict = os.environ.get('MT_CRITIQUE_VERDICT','')
crit_pct = 100 if verdict else 0

# M4
one_s = os.environ.get('MT_ONE_SENTENCE','')
crea_pct = 90 if one_s else 0

print(f'  发散完整度  {bar(div_pct)} {div_pct}%')
print(f'  收敛准确度  {bar(conv_pct)} {conv_pct}%')
if verdict:
    print(f'  批判严格度  {bar(crit_pct)} {crit_pct}%')
print(f'  方案可行度  {bar(crea_pct)} {crea_pct}%')
"
}

# ── 生成 Markdown 报告 ────────────────────────────────────────
generate_markdown() {
    local report_file="/tmp/mirothinker_${MT_TIMESTAMP}.md"

    python3 -c "
import json, re, os
from datetime import datetime

query        = os.environ.get('MT_QUERY','')
topic        = os.environ.get('MT_TOPIC','')
mt_type      = os.environ.get('MT_TYPE','')
domain       = os.environ.get('MT_DOMAIN','')
complexity   = os.environ.get('MT_COMPLEXITY','')
mode         = os.environ.get('MT_MODE','full')
elapsed      = os.environ.get('MT_ELAPSED','0')
timestamp    = os.environ.get('MT_TIMESTAMP','')
entities     = os.environ.get('MT_ENTITIES','[]')
constraints  = os.environ.get('MT_CONSTRAINTS','[]')
metrics      = os.environ.get('MT_SUCCESS_METRICS','[]')
div_summary  = os.environ.get('MT_DIVERGE_SUMMARY','')
conv_synth   = os.environ.get('MT_CONVERGE_SYNTHESIS','')
priority     = os.environ.get('MT_PRIORITY_MATRIX','{}')
critique_raw = os.environ.get('MT_CRITIQUE','{}')
verdict      = os.environ.get('MT_CRITIQUE_VERDICT','')
steelman     = os.environ.get('MT_CRITIQUE_STEELMAN','')
create_raw   = os.environ.get('MT_CREATE','{}')
one_sentence = os.environ.get('MT_ONE_SENTENCE','')
meta_insight = os.environ.get('MT_META_INSIGHT','')
diverge_raw  = os.environ.get('MT_DIVERGE','{}')
converge_raw = os.environ.get('MT_CONVERGE','{}')

def parse_json(raw):
    try:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group()) if m else {}
    except:
        return {}

div_data  = parse_json(diverge_raw)
conv_data = parse_json(converge_raw)
crit_data = parse_json(critique_raw)
crea_data = parse_json(create_raw)
prio_data = parse_json(priority)

try:
    ents = json.loads(entities)
    cons = json.loads(constraints)
    mets = json.loads(metrics)
except:
    ents = cons = mets = []

lines = []
lines.append(f'# MiroThinker 1.7 深度思考报告')
lines.append(f'')
lines.append(f'**问题：** {query}')
lines.append(f'**分析时间：** {timestamp}  **耗时：** {elapsed}s  **模式：** {mode}')
lines.append(f'**类型：** {mt_type}  **复杂度：** {complexity}  **领域：** {domain}')
lines.append(f'')
lines.append(f'---')
lines.append(f'')
lines.append(f'## P0 问题解构')
lines.append(f'')
lines.append(f'- **核心主题：** {topic}')
if ents:
    lines.append(f'- **关键实体：** {\"、\".join(ents)}')
if cons:
    lines.append(f'- **约束条件：** {\"、\".join(cons)}')
if mets:
    lines.append(f'- **成功指标：** {\"、\".join(mets)}')
lines.append(f'')
lines.append(f'---')
lines.append(f'')
lines.append(f'## M1 发散模态')
lines.append(f'')
for d in div_data.get('dimensions', []):
    lines.append(f'### {d.get(\"name\",\"\")}')
    lines.append(f'> {d.get(\"angle\",\"\")}')
    lines.append(f'')
    for p in d.get('perspectives', []):
        lines.append(f'- {p}')
    wc = d.get('wild_card','')
    if wc:
        lines.append(f'- ★ **野卡：** {wc}')
    lines.append(f'')
lines.append(f'---')
lines.append(f'')
lines.append(f'## M2 收敛模态')
lines.append(f'')
lines.append(f'### 核心洞察')
for ins in conv_data.get('core_insights', []):
    lines.append(f'- **[{ins.get(\"impact\",\"\")}]** {ins.get(\"insight\",\"\")} — {ins.get(\"rationale\",\"\")}')
lines.append(f'')
if prio_data:
    lines.append(f'### 优先级矩阵')
    lines.append(f'')
    lines.append(f'| 立即行动 | 计划推进 | 观察等待 | 可以忽略 |')
    lines.append(f'|----------|----------|----------|----------|')
    do_f  = '<br>'.join(prio_data.get('do_first',[]))
    plan  = '<br>'.join(prio_data.get('plan_next',[]))
    watch = '<br>'.join(prio_data.get('watch_later',[]))
    drop  = '<br>'.join(prio_data.get('drop',[]))
    lines.append(f'| {do_f} | {plan} | {watch} | {drop} |')
    lines.append(f'')
lines.append(f'**综合结论：** {conv_synth}')
lines.append(f'')
lines.append(f'---')
lines.append(f'')

if verdict:
    lines.append(f'## M3 批判模态')
    lines.append(f'')
    for a in crit_data.get('assumptions_challenged', []):
        lines.append(f'- **[{a.get(\"severity\",\"\")}]** 假设：{a.get(\"assumption\",\"\")} → {a.get(\"challenge\",\"\")}')
    lines.append(f'')
    bls = crit_data.get('blind_spots', [])
    if bls:
        lines.append(f'**盲点：** {\"、\".join(bls)}')
        lines.append(f'')
    risks = crit_data.get('risks', [])
    if risks:
        lines.append(f'| 风险 | 概率 | 影响 | 缓解策略 |')
        lines.append(f'|------|------|------|----------|')
        for r in risks:
            lines.append(f'| {r.get(\"risk\",\"\")} | {r.get(\"probability\",\"\")} | {r.get(\"impact\",\"\")} | {r.get(\"mitigation\",\"\")} |')
        lines.append(f'')
    lines.append(f'**裁定：** {verdict}')
    if steelman:
        lines.append(f'**最强辩护：** {steelman}')
    lines.append(f'')
    lines.append(f'---')
    lines.append(f'')

lines.append(f'## M4 创造模态')
lines.append(f'')
for i, sol in enumerate(crea_data.get('final_solutions', [])):
    lines.append(f'### 方案 {chr(65+i)}：{sol.get(\"title\",\"\")}')
    lines.append(f'')
    lines.append(f'**核心理念：** {sol.get(\"core_idea\",\"\")}')
    lines.append(f'')
    for s in sol.get('action_steps', []):
        lines.append(f'{s.get(\"step\",\"\")}. {s.get(\"action\",\"\")}（{s.get(\"timeline\",\"\")}）')
    lines.append(f'')
    lines.append(f'**预期结果：** {sol.get(\"expected_outcome\",\"\")}')
    lines.append(f'')
lines.append(f'---')
lines.append(f'')
lines.append(f'## 一句话答案')
lines.append(f'')
lines.append(f'> {one_sentence}')
lines.append(f'')
if meta_insight:
    lines.append(f'## 元认知洞察')
    lines.append(f'')
    lines.append(f'{meta_insight}')
    lines.append(f'')
lines.append(f'---')
lines.append(f'*由 MiroThinker 1.7 生成 | openclaw skill*')

print('\n'.join(lines))
" > "$report_file"

    echo "$report_file"
}

# ════════════════════════════════════════════════════════════════
# 主渲染逻辑
# ════════════════════════════════════════════════════════════════

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║  思维导图${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# 问题根节点
echo -e "${BOLD}${MT_QUERY}${RESET}"

# M1 发散分支
echo -e "├── ${CYAN}[M1 发散]${RESET} 可能性空间"
render_diverge_tree

# M2 收敛分支
echo -e "├── ${GREEN}[M2 收敛]${RESET} 核心洞察"
render_converge_tree

# M3 批判分支（quick 模式跳过）
if [ "${MT_MODE:-full}" != "quick" ] && [ -n "${MT_CRITIQUE_VERDICT:-}" ]; then
    echo -e "├── ${YELLOW}[M3 批判]${RESET} 风险审查"
    render_critique_tree
fi

# M4 创造分支
echo -e "└── ${BOLD}[M4 创造]${RESET} 综合方案"
render_create_tree

# 置信度仪表
echo ""
echo -e "${BOLD}◆ 置信度分布${RESET}"
render_confidence_bar

# 元认知洞察
if [ -n "${MT_META_INSIGHT:-}" ]; then
    echo ""
    echo -e "${BOLD}◆ 元认知洞察${RESET}"
    echo -e "  ${DIM}\"${MT_META_INSIGHT}\"${RESET}"
fi

# 统计信息
echo ""
echo -e "${DIM}─────────────────────────────────────────────────────────────${RESET}"
echo -e "${DIM}耗时：${MT_ELAPSED:-0}s  模式：${MT_MODE:-full}  复杂度：${MT_COMPLEXITY:-MEDIUM}${RESET}"

# 保存报告
if [ "${MT_SAVE_REPORT:-0}" = "1" ]; then
    report_file=$(generate_markdown)
    echo -e "${GREEN}✓ 报告已保存：${report_file}${RESET}"
fi

echo ""
