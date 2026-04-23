#!/bin/bash
# 大汪每日汇报脚本

AGENT_ID="dawang"
WORKSPACE="/Users/godspeed/.openclaw/workspaces/${AGENT_ID}"
TODO_FILE="${WORKSPACE}/TODO.md"
HEARTBEAT_FILE="${WORKSPACE}/HEARTBEAT.md"
LOG_FILE="/Users/godspeed/.openclaw/agents/${AGENT_ID}/cron/daily-report.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 生成每日汇报..." >> "$LOG_FILE"

# 统计任务
TODO_COUNT=$(grep -c "\- \[ \]" "$TODO_FILE" 2>/dev/null || echo "0")
DONE_COUNT=$(grep -c "\- \[x\]" "$TODO_FILE" 2>/dev/null || echo "0")

# 获取待办任务列表
TODO_LIST=$(grep "\- \[ \]" "$TODO_FILE" 2>/dev/null | head -5 || echo "无")

# 生成汇报消息
REPORT="🐕💪 大汪 $(date '+%m月%d日 %H:%M') 状态汇报

📊 任务统计:
• 进行中: ${TODO_COUNT}
• 已完成: ${DONE_COUNT}

📝 当前待办:
${TODO_LIST}

💪 随时待命，有活儿随时喊我！"

echo "$REPORT"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 汇报生成完成" >> "$LOG_FILE"
