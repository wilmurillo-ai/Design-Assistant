#!/bin/bash
# =============================================================================
# 定时回顾更新助手 (daily-review-helper) v2.0
# =============================================================================
# 创建者：思捷娅科技 (SJYKJ)
# 用途：收集今日数据，生成回顾报告，同步Git和ClawHub
# AI回顾由Agent读取报告后执行（更新记忆、知识库、查漏补缺）
# 许可证：MIT License
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-/root/.openclaw/workspace}"
TODAY=$(date +%Y-%m-%d)
REPORT_DIR="$WORKSPACE/memory/reviews"
REPORT_FILE="$REPORT_DIR/${TODAY}_review.md"
LOG_FILE="$SCRIPT_DIR/logs/daily-review.log"

mkdir -p "$REPORT_DIR" "$SCRIPT_DIR/logs"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" >&2; }
err() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2; }

# ==========================================
# 1. 同步 ClawHub 技能更新
# ==========================================
sync_clawhub() {
    log "🔄 [1/6] 同步 ClawHub 技能更新..."
    
    if ! command -v clawhub &>/dev/null; then
        warn "  clawhub CLI 未安装，跳过"
        return 0
    fi

    local result=""
    result=$(clawhub update --all --force --no-input 2>&1 || true)
    
    local updated=$(echo "$result" | grep -c "updated" || echo "0")
    local upto=$(echo "$result" | grep -c "up to date" || echo "0")
    log "  ✅ 更新 $updated 个，已是最新 $upto 个"
}

# ==========================================
# 2. Git 同步
# ==========================================
sync_git() {
    log "💾 [2/6] Git 同步..."
    
    cd "$WORKSPACE" || return 1
    
    # 拉取远程更新
    git fetch origin --quiet 2>&1 || warn "  git fetch 失败"
    
    # 检查未提交变更
    local changed=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ "$changed" -gt 0 ]; then
        git add -A 2>/dev/null
        git commit -m "auto: daily review sync ${TODAY}" --quiet 2>/dev/null || true
        log "  ✅ 自动提交 $changed 个文件变更"
    else
        log "  ✅ 无未提交变更"
    fi
    
    # 推送
    git push origin master --quiet 2>&1 && log "  ✅ 已推送 origin/master" || warn "  推送失败"
}

# ==========================================
# 3. 收集今日 Git 提交
# ==========================================
collect_commits() {
    log "📝 [3/6] 收集今日 Git 提交..."
    
    cd "$WORKSPACE" || return 1
    local commits=$(git log --since="${TODAY} 00:00" --until="${TODAY} 23:59" --oneline 2>/dev/null || echo "")
    
    if [ -n "$commits" ]; then
        echo "### Git 提交" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "$commits" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        log "  ✅ $(echo "$commits" | wc -l) 个提交"
    else
        echo "### Git 提交" >> "$REPORT_FILE"
        echo "无提交" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        log "  ⚠️ 今日无提交"
    fi
}

# ==========================================
# 4. 收集 Issues 状态
# ==========================================
collect_issues() {
    log "📝 [4/6] 收集 Issues 状态..."
    
    if ! command -v gh &>/dev/null; then
        warn "  gh CLI 未安装，跳过"
        return 0
    fi
    
    # 最近7天的issues
    local open_issues=$(gh issue list --state open --limit 10 2>/dev/null || echo "获取失败")
    local recent_closed=$(gh issue list --state closed --limit 5 2>/dev/null || echo "获取失败")
    
    echo "### Issues 状态" >> "$REPORT_FILE"
    echo "**当前 Open Issues:**" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "$open_issues" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "**最近关闭:**" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "$recent_closed" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    log "  ✅ Issues 状态已收集"
}

# ==========================================
# 5. 收集文件变更
# ==========================================
collect_file_changes() {
    log "📝 [5/6] 收集今日文件变更..."
    
    cd "$WORKSPACE" || return 1
    
    # 今日修改的文件
    local changed_files=$(git diff --name-only "@{${TODAY}}" 2>/dev/null || echo "")
    
    # 今日新增的文件
    local new_files=$(git diff --name-only --diff-filter=A "@{${TODAY}}" 2>/dev/null || echo "")
    
    echo "### 文件变更" >> "$REPORT_FILE"
    if [ -n "$changed_files" ]; then
        echo "**修改的文件:**" >> "$REPORT_FILE"
        echo "$changed_files" | sed 's/^/- /' >> "$REPORT_FILE"
    fi
    if [ -n "$new_files" ]; then
        echo -e "\n**新增的文件:**" >> "$REPORT_FILE"
        echo "$new_files" | sed 's/^/- /' >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    log "  ✅ 文件变更已收集"
}

# ==========================================
# 6. 收集知识库状态
# ==========================================
collect_knowledge() {
    log "📝 [6/6] 收集知识库状态..."
    
    local kb_dir="$WORKSPACE/knowledge"
    
    echo "### 知识库状态" >> "$REPORT_FILE"
    
    if [ -d "$kb_dir" ]; then
        local total=$(find "$kb_dir" -name "*.md" 2>/dev/null | wc -l)
        local today_kb=$(find "$kb_dir" -name "*.md" -newer "$kb_dir" -mtime -1 2>/dev/null | wc -l)
        echo "- 知识库总文档数: $total" >> "$REPORT_FILE"
        echo "- 今日新增/修改: $today_kb" >> "$REPORT_FILE"
        
        # QMD 索引状态
        if command -v qmd &>/dev/null; then
            local qmd_status=$(qmd status 2>/dev/null | head -5 || echo "状态获取失败")
            echo -e "\n**QMD 索引:**" >> "$REPORT_FILE"
            echo '```' >> "$REPORT_FILE"
            echo "$qmd_status" >> "$REPORT_FILE"
            echo '```' >> "$REPORT_FILE"
        fi
    else
        echo "- 知识库目录不存在" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    log "  ✅ 知识库状态已收集"
}

# ==========================================
# 生成回顾报告
# ==========================================
generate_report() {
    log "📋 生成今日回顾报告..."
    
    # 写入报告头
    cat > "$REPORT_FILE" << EOF
# 每日回顾报告 - ${TODAY}

> 由 daily-review-helper v2.0 自动生成
> 生成时间：$(date '+%Y-%m-%d %H:%M')

---

EOF

    # 依次收集数据
    collect_commits
    collect_issues
    collect_file_changes
    collect_knowledge

    # 追加 Agent 待办事项
    cat >> "$REPORT_FILE" << 'EOF'

---

## 🤖 Agent 待办事项

> 以下任务需要 Agent（AI）完成：

### 1. 回顾今日工作
- [ ] 阅读今日日志 `memory/YYYY-MM-DD.md`
- [ ] 总结今日完成的任务和成就
- [ ] 识别未完成的任务和延期事项

### 2. 查漏补缺
- [ ] 检查是否有遗漏的重要事项
- [ ] 检查 HEARTBEAT.md 中的待办任务
- [ ] 检查 Issue 是否有需要跟进的

### 3. 更新记忆
- [ ] 将今日精华更新到 MEMORY.md
- [ ] 更新 HEARTBEAT.md 任务状态
- [ ] 清理过时的记忆条目

### 4. 更新知识库
- [ ] 检查今日新增知识是否已索引
- [ ] 运行 QMD 索引更新（如有新文档）

### 5. 系统检查
- [ ] 检查磁盘空间
- [ ] 检查系统负载
- [ ] 检查 ClawHub 发布状态

---

*报告生成完成，等待 Agent 处理*
EOF

    log "  ✅ 报告已生成：$REPORT_FILE"
}

# ==========================================
# 执行完整回顾流程
# ==========================================
do_review() {
    log "╔════════════════════════════════════════════════════════╗"
    log "║  定时回顾更新助手 v2.0                                ║"
    log "╠════════════════════════════════════════════════════════╣"
    log "║  日期：$TODAY"
    log "╚════════════════════════════════════════════════════════╝"
    
    sync_clawhub
    sync_git
    generate_report
    
    log ""
    log "✅ 数据收集完成！"
    log "📍 回顾报告：$REPORT_FILE"
    log "👉 请 Agent 读取报告并执行智能回顾"
}

# ==========================================
# 状态查看
# ==========================================
show_status() {
    log "╔════════════════════════════════════════════════════════╗"
    log "║  daily-review-helper v2.0 - 状态                      ║"
    log "╚════════════════════════════════════════════════════════╝"
    
    echo ""
    log "📁 工作区：$WORKSPACE"
    log "📁 报告目录：$REPORT_DIR"
    log "📁 日志文件：$LOG_FILE"
    
    echo ""
    log "最近回顾报告："
    ls -lt "$REPORT_DIR"/*_review.md 2>/dev/null | head -3 || warn "  无报告"
    
    echo ""
    log "Crontab 状态："
    crontab -l 2>/dev/null | grep "daily-review" && log "  ✅ 已启用" || warn "  ⚠️ 未启用"
    
    echo ""
    log "工具检查："
    command -v clawhub &>/dev/null && log "  ✅ clawhub" || warn "  ❌ clawhub"
    command -v gh &>/dev/null && log "  ✅ gh" || warn "  ❌ gh"
    command -v git &>/dev/null && log "  ✅ git" || warn "  ❌ git"
}

# ==========================================
# Crontab 管理
# ==========================================
add_cron() {
    local mode="${1:-default}"
    
    # 移除旧的任务
    crontab -l 2>/dev/null | grep -v "daily-review" | crontab - 2>/dev/null || true
    
    case "$mode" in
        morning)
            echo "0 12 * * * $SCRIPT_DIR/skill.sh review >> $LOG_FILE 2>&1" | crontab -
            log "✅ 已添加：中午 12:00 回顾"
            ;;
        full)
            echo "50 23 * * * $SCRIPT_DIR/skill.sh review >> $LOG_FILE 2>&1" | crontab -
            log "✅ 已添加：晚上 23:50 回顾"
            ;;
        default|*)
            (crontab -l 2>/dev/null | grep -v "daily-review"; \
             echo "0 12 * * * $SCRIPT_DIR/skill.sh review >> $LOG_FILE 2>&1"; \
             echo "50 23 * * * $SCRIPT_DIR/skill.sh review >> $LOG_FILE 2>&1") | crontab -
            log "✅ 已添加：中午 12:00 + 晚上 23:50"
            ;;
    esac
}

remove_cron() {
    crontab -l 2>/dev/null | grep -v "daily-review" | crontab - 2>/dev/null || true
    log "✅ 定时任务已移除"
}

show_cron() {
    log "Crontab 任务："
    crontab -l 2>/dev/null | grep "daily-review" || warn "  无定时任务"
}

# ==========================================
# 帮助
# ==========================================
show_help() {
    cat << EOF
╔════════════════════════════════════════════════════════╗
║     daily-review-helper v2.0 - 思捷娅科技 (SJYKJ)       ║
╚════════════════════════════════════════════════════════╝

用法: $0 <命令> [选项]

命令:
  review              执行完整回顾（数据收集+同步+生成报告）
  status              查看状态
  cron-add [mode]     添加定时任务 (morning/full/default)
  cron-remove         移除定时任务
  cron-status         查看定时任务
  help                帮助

定时任务:
  🕛 中午 12:00  - 回顾上午工作
  🕚 晚上 23:50  - 回顾全天工作

回顾流程:
  1. 同步 ClawHub 技能更新
  2. Git 提交 + 推送
  3. 收集 Git 提交记录
  4. 收集 Issues 状态
  5. 收集文件变更
  6. 收集知识库状态
  7. 生成回顾报告 → Agent 读取后执行智能回顾

版权：思捷娅科技 (SJYKJ) | MIT License
EOF
}

# ==========================================
# 主入口
# ==========================================
main() {
    local cmd="${1:-help}"
    case "$cmd" in
        review)    do_review ;;
        status)    show_status ;;
        cron-add)  shift; add_cron "$@" ;;
        cron-remove) remove_cron ;;
        cron-status|cron) show_cron ;;
        help|--help|-h) show_help ;;
        *) err "未知命令：$cmd"; show_help; exit 1 ;;
    esac
}

main "$@"
