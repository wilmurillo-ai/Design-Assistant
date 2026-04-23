#!/usr/bin/env bash
# analyze.sh — MiroThinker 1.7 核心分析引擎
# 通过 source 加载，共享 think.sh 的变量空间
# bash 3.2 兼容

# ── LLM 调用封装 ─────────────────────────────────────────────
# 用法：mt_call_llm "阶段名" "prompt内容" "输出变量名"
mt_call_llm() {
    local stage="$1"
    local prompt="$2"
    local out_var="$3"
    local tmpfile="/tmp/mt_${stage}_$$.txt"
    local resp_file="/tmp/mt_${stage}_resp_$$.json"
    local retry=0

    # 把 prompt 写入临时文件，避免命令行引号问题
    printf '%s' "$prompt" > "$tmpfile"

    while [ $retry -lt 3 ]; do
        if openclaw agent --local --json \
            --message "$(cat "$tmpfile")" \
            > "$resp_file" 2>/dev/null; then
            break
        fi
        retry=$((retry + 1))
        if [ $retry -lt 3 ]; then
            echo -e "${YELLOW}  重试 ($retry/2)...${RESET}"
        fi
    done

    local raw=""
    if [ -f "$resp_file" ]; then
        raw=$(python3 -c "
import json, sys
try:
    data = json.load(open('$resp_file'))
    payloads = data.get('payloads', [])
    print(payloads[0].get('text', '') if payloads else '')
except:
    sys.stdout.write('')
")
    fi

    rm -f "$tmpfile" "$resp_file"

    # 导出到指定变量名
    export "${out_var}"="$raw"
}

# ── JSON 安全提取 ─────────────────────────────────────────────
# 用法：mt_json_field "变量名" "字段" "默认值"
mt_json_field() {
    local var_name="$1"
    local field="$2"
    local default="${3:-}"
    local raw
    raw=$(eval "echo \"\${${var_name}:-}\"")

    python3 -c "
import json, re, sys

raw = '''$raw'''
field = '$field'
default = '$default'

# 从 LLM 输出中提取 JSON（可能有前缀文字）
match = re.search(r'\{.*\}', raw, re.DOTALL)
if not match:
    print(default)
    sys.exit(0)
try:
    data = json.loads(match.group())
    val = data.get(field, default)
    if isinstance(val, (dict, list)):
        print(json.dumps(val, ensure_ascii=False))
    else:
        print(val if val is not None else default)
except Exception:
    print(default)
"
}

# ── JSON 数组转可读摘要 ───────────────────────────────────────
mt_json_array_summary() {
    local json_str="$1"
    local key="${2:-name}"
    python3 -c "
import json, sys
try:
    data = json.loads('''$json_str''')
    if isinstance(data, list):
        items = [str(x.get('$key', x) if isinstance(x, dict) else x) for x in data[:6]]
        print(', '.join(items))
    else:
        print('')
except:
    print('')
"
}

# ════════════════════════════════════════════════════════════════
# P0 — 问题解构
# ════════════════════════════════════════════════════════════════
run_p0() {
    show_stage "🔍" "P0 问题解构" 1 "$MT_TOTAL_STAGES"

    local prompt
    prompt="你是专业的问题分析师。请对以下问题进行元分析，不要直接回答。

问题：${MT_QUERY}

以 JSON 格式输出（只输出 JSON，无任何前缀后缀）：
{
  \"topic\": \"问题核心主题（6字以内）\",
  \"type\": \"DECISION或CREATIVE或ANALYSIS或PLANNING之一\",
  \"domain\": \"所属领域（如：职业发展/产品设计/商业战略）\",
  \"entities\": [\"关键实体1\", \"关键实体2\"],
  \"constraints\": [\"约束条件1\", \"约束条件2\"],
  \"success_metrics\": [\"成功标准1\", \"成功标准2\"],
  \"complexity\": \"LOW或MEDIUM或HIGH之一\"
}

注意：只输出 JSON，不要有任何前缀、后缀或解释。"

    mt_call_llm "p0" "$prompt" "MT_P0_RAW"

    export MT_TOPIC
    MT_TOPIC=$(mt_json_field "MT_P0_RAW" "topic" "未知主题")
    export MT_TYPE
    MT_TYPE=$(mt_json_field "MT_P0_RAW" "type" "ANALYSIS")
    export MT_DOMAIN
    MT_DOMAIN=$(mt_json_field "MT_P0_RAW" "domain" "通用")
    export MT_COMPLEXITY
    MT_COMPLEXITY=$(mt_json_field "MT_P0_RAW" "complexity" "MEDIUM")
    export MT_ENTITIES
    MT_ENTITIES=$(mt_json_field "MT_P0_RAW" "entities" "[]")
    export MT_CONSTRAINTS
    MT_CONSTRAINTS=$(mt_json_field "MT_P0_RAW" "constraints" "[]")
    export MT_SUCCESS_METRICS
    MT_SUCCESS_METRICS=$(mt_json_field "MT_P0_RAW" "success_metrics" "[]")

    echo -e "  ${DIM}类型:${RESET} $MT_TYPE  ${DIM}复杂度:${RESET} $MT_COMPLEXITY  ${DIM}领域:${RESET} $MT_DOMAIN"
}

# ════════════════════════════════════════════════════════════════
# M1 — 发散模态
# ════════════════════════════════════════════════════════════════
run_m1() {
    show_stage "🌊" "M1 发散思维" 2 "$MT_TOTAL_STAGES"

    local prompt
    prompt="你是发散思维专家。对以下问题，用最宽广视角展开思考，不评判，不收敛。

问题：${MT_QUERY}
问题类型：${MT_TYPE}
核心领域：${MT_DOMAIN}

生成 6 个完全不同的思维维度，维度间差异显著，覆盖理性/感性、短期/长期、个人/系统等对立面。

以 JSON 格式输出（只输出 JSON）：
{
  \"dimensions\": [
    {
      \"name\": \"维度名称（4字以内）\",
      \"angle\": \"切入角度（20字以内）\",
      \"perspectives\": [\"视角1（30字以内）\", \"视角2（30字以内）\"],
      \"wild_card\": \"大胆假设（30字以内）\"
    }
  ]
}

注意：只输出 JSON，不要有任何前缀、后缀或解释。"

    mt_call_llm "m1" "$prompt" "MT_DIVERGE"

    export MT_DIVERGE_SUMMARY
    MT_DIVERGE_SUMMARY=$(python3 -c "
import json, re
raw = '''${MT_DIVERGE}'''
try:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    data = json.loads(match.group()) if match else {}
    dims = data.get('dimensions', [])
    names = [d.get('name','') for d in dims if d.get('name')]
    print(', '.join(names[:6]))
except:
    print('发散维度')
")

    echo -e "  ${DIM}维度:${RESET} $MT_DIVERGE_SUMMARY"
}

# ════════════════════════════════════════════════════════════════
# M2 — 收敛模态
# ════════════════════════════════════════════════════════════════
run_m2() {
    show_stage "🎯" "M2 收敛提炼" 3 "$MT_TOTAL_STAGES"

    local prompt
    prompt="你是结构化思维专家。基于发散思维产物，进行聚焦提炼。

原始问题：${MT_QUERY}
已识别维度：${MT_DIVERGE_SUMMARY}

从以上维度中提炼最有价值的洞察，构建优先级矩阵。

以 JSON 格式输出（只输出 JSON）：
{
  \"core_insights\": [
    {
      \"insight\": \"核心洞察（40字以内）\",
      \"impact\": \"HIGH或MEDIUM或LOW之一\",
      \"confidence\": \"HIGH或MEDIUM或LOW之一\",
      \"rationale\": \"理由（30字以内）\"
    }
  ],
  \"priority_matrix\": {
    \"do_first\": [\"立即行动项1\", \"立即行动项2\"],
    \"plan_next\": [\"计划推进项1\"],
    \"watch_later\": [\"观察等待项1\"],
    \"drop\": [\"可忽略项1\"]
  },
  \"synthesis\": \"综合性结论（80字以内）\"
}

注意：只输出 JSON，不要有任何前缀、后缀或解释。"

    mt_call_llm "m2" "$prompt" "MT_CONVERGE"

    export MT_CONVERGE_SYNTHESIS
    MT_CONVERGE_SYNTHESIS=$(mt_json_field "MT_CONVERGE" "synthesis" "综合分析完成")

    export MT_PRIORITY_MATRIX
    MT_PRIORITY_MATRIX=$(mt_json_field "MT_CONVERGE" "priority_matrix" "{}")

    echo -e "  ${DIM}结论:${RESET} $(echo "$MT_CONVERGE_SYNTHESIS" | head -c 60)..."
}

# ════════════════════════════════════════════════════════════════
# M3 — 批判模态
# ════════════════════════════════════════════════════════════════
run_m3() {
    show_stage "⚡" "M3 批判审查" 4 "$MT_TOTAL_STAGES"

    local prompt
    prompt="你是批判性思维专家，专门寻找漏洞、盲点和风险。直接挑战，不要客气。

原始问题：${MT_QUERY}
当前结论：${MT_CONVERGE_SYNTHESIS}

对以上结论进行深度批判性审查。

以 JSON 格式输出（只输出 JSON）：
{
  \"assumptions_challenged\": [
    {
      \"assumption\": \"被挑战的假设（30字以内）\",
      \"challenge\": \"挑战方式（40字以内）\",
      \"severity\": \"HIGH或MEDIUM或LOW之一\"
    }
  ],
  \"blind_spots\": [\"盲点1（30字以内）\", \"盲点2（30字以内）\"],
  \"risks\": [
    {
      \"risk\": \"风险描述（30字以内）\",
      \"probability\": \"HIGH或MEDIUM或LOW之一\",
      \"impact\": \"HIGH或MEDIUM或LOW之一\",
      \"mitigation\": \"缓解策略（30字以内）\"
    }
  ],
  \"steelman\": \"对当前结论最强力的辩护（50字以内）\",
  \"verdict\": \"SOLID或NEEDS_REVISION或FUNDAMENTALLY_FLAWED之一\"
}

注意：只输出 JSON，不要有任何前缀、后缀或解释。"

    mt_call_llm "m3" "$prompt" "MT_CRITIQUE"

    export MT_CRITIQUE_VERDICT
    MT_CRITIQUE_VERDICT=$(mt_json_field "MT_CRITIQUE" "verdict" "NEEDS_REVISION")

    export MT_CRITIQUE_STEELMAN
    MT_CRITIQUE_STEELMAN=$(mt_json_field "MT_CRITIQUE" "steelman" "")

    echo -e "  ${DIM}裁定:${RESET} $MT_CRITIQUE_VERDICT"
}

# ════════════════════════════════════════════════════════════════
# M4 — 创造模态
# ════════════════════════════════════════════════════════════════
run_m4() {
    local step_num="$1"
    show_stage "✨" "M4 创造综合" "$step_num" "$MT_TOTAL_STAGES"

    local critique_context=""
    if [ -n "${MT_CRITIQUE_VERDICT:-}" ]; then
        critique_context="批判裁定：${MT_CRITIQUE_VERDICT}
最强辩护：${MT_CRITIQUE_STEELMAN}"
    fi

    local prompt
    prompt="你是创造性综合专家。在发散和批判的基础上，提出突破性方案。

原始问题：${MT_QUERY}
发散维度：${MT_DIVERGE_SUMMARY}
收敛结论：${MT_CONVERGE_SYNTHESIS}
${critique_context}

综合以上思维过程，提出 1-2 个创新性最终方案。

以 JSON 格式输出（只输出 JSON）：
{
  \"final_solutions\": [
    {
      \"title\": \"方案标题（10字以内）\",
      \"core_idea\": \"核心理念（30字以内）\",
      \"action_steps\": [
        {\"step\": 1, \"action\": \"具体行动（30字以内）\", \"timeline\": \"时间范围\"}
      ],
      \"expected_outcome\": \"预期结果（40字以内）\",
      \"confidence\": \"HIGH或MEDIUM或LOW之一\"
    }
  ],
  \"meta_insight\": \"这次思考过程带来的元认知洞察（60字以内）\",
  \"one_sentence_answer\": \"如果只能给一句话答案（30字以内）\"
}

注意：只输出 JSON，不要有任何前缀、后缀或解释。"

    mt_call_llm "m4" "$prompt" "MT_CREATE"

    export MT_ONE_SENTENCE
    MT_ONE_SENTENCE=$(mt_json_field "MT_CREATE" "one_sentence_answer" "请结合具体情况做决定")

    export MT_META_INSIGHT
    MT_META_INSIGHT=$(mt_json_field "MT_CREATE" "meta_insight" "")

    echo -e "  ${DIM}一句话:${RESET} $MT_ONE_SENTENCE"
}

# ════════════════════════════════════════════════════════════════
# 主分析流程调度
# ════════════════════════════════════════════════════════════════
export MT_PARSE_ERROR=0

run_p0

run_m1

run_m2

case "${MT_MODE:-full}" in
    quick)
        run_m4 4
        ;;
    deep)
        run_m3
        # deep 模式：M3 后再跑一次 M2 修订
        show_stage "🔄" "M2 修订（深度模式）" 5 "$MT_TOTAL_STAGES"
        # 将 M3 的批判纳入 M2 重新收敛
        MT_CONVERGE_SYNTHESIS="${MT_CONVERGE_SYNTHESIS} [经批判修订：${MT_CRITIQUE_VERDICT}]"
        export MT_CONVERGE_SYNTHESIS
        run_m4 6
        ;;
    *)  # full
        run_m3
        run_m4 5
        ;;
esac
