#!/usr/bin/env bash
# think.sh — MiroThinker 1.7 入口脚本
# bash 3.2 兼容

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── 颜色定义 ─────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ── 依赖检查 ─────────────────────────────────────────────────
check_deps() {
    if ! command -v openclaw >/dev/null 2>&1; then
        echo -e "${RED}错误：未找到 openclaw 命令${RESET}"
        echo "请先安装 openclaw CLI: https://openclaw.ai"
        exit 1
    fi
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}错误：需要 python3${RESET}"
        exit 1
    fi
}

# ── 使用说明 ─────────────────────────────────────────────────
show_usage() {
    cat <<'EOF'
用法：
  openclaw run mirothinker1.7 "你的问题"
  openclaw run mirothinker1.7 --mode=quick "快速分析问题"
  openclaw run mirothinker1.7 --mode=deep  "深度分析重大决策"
  openclaw run mirothinker1.7 --save       "分析问题并保存报告"
  openclaw run mirothinker1.7 --file=problem.txt

选项：
  --mode=quick   快速模式，跳过 M3 批判（约 1-2 分钟）
  --mode=full    标准模式，默认（约 2-4 分钟）
  --mode=deep    深度模式，M2 迭代修订（约 4-6 分钟）
  --save         保存 Markdown 报告到 /tmp/
  --file=FILE    从文件读取问题
EOF
}

# ── 参数解析 ─────────────────────────────────────────────────
parse_args() {
    export MT_MODE="full"
    export MT_SAVE_REPORT=0
    export MT_QUERY=""
    export MT_TIMESTAMP
    MT_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    export MT_REPORT_PATH="/tmp"

    while [ $# -gt 0 ]; do
        case "$1" in
            --mode=*)
                MT_MODE="${1#--mode=}"
                ;;
            --file=*)
                local f="${1#--file=}"
                if [ -f "$f" ]; then
                    MT_QUERY=$(cat "$f")
                else
                    echo -e "${RED}错误：文件不存在: $f${RESET}"
                    exit 1
                fi
                ;;
            --save)
                MT_SAVE_REPORT=1
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            -*)
                echo -e "${YELLOW}未知参数: $1，已忽略${RESET}"
                ;;
            *)
                if [ -z "$MT_QUERY" ]; then
                    MT_QUERY="$1"
                fi
                ;;
        esac
        shift
    done

    # 从 stdin 读取（管道输入）
    if [ -z "$MT_QUERY" ] && [ ! -t 0 ]; then
        MT_QUERY=$(cat)
    fi

    if [ -z "$MT_QUERY" ]; then
        show_usage
        exit 1
    fi

    export MT_QUERY MT_MODE MT_SAVE_REPORT MT_REPORT_PATH MT_TIMESTAMP
}

# ── 进度提示 ─────────────────────────────────────────────────
show_stage() {
    local icon="$1"
    local name="$2"
    local current="$3"
    local total="$4"
    printf "\n${CYAN}[%d/%d]${RESET} %s ${BOLD}%s${RESET}...\n" \
        "$current" "$total" "$icon" "$name"
}

# ── 主流程 ───────────────────────────────────────────────────
main() {
    check_deps
    parse_args "$@"

    local start_time=$SECONDS

    # 确定执行阶段数
    case "$MT_MODE" in
        quick) export MT_TOTAL_STAGES=4 ;;
        deep)  export MT_TOTAL_STAGES=6 ;;
        *)     export MT_TOTAL_STAGES=5 ;;
    esac

    echo ""
    echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}║  MIROTHINKER 1.7  •  深度思考引擎${RESET}"
    printf "${BOLD}║  问题：%-54s║${RESET}\n" "$(echo "$MT_QUERY" | head -c 50)"
    echo -e "${BOLD}║  模式：%-10s${RESET}" "$MT_MODE"
    echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"

    # source 共享变量空间
    # shellcheck source=analyze.sh
    source "$SCRIPT_DIR/analyze.sh"

    export MT_ELAPSED=$((SECONDS - start_time))

    # shellcheck source=render.sh
    source "$SCRIPT_DIR/render.sh"
}

main "$@"
