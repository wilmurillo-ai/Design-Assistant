#!/bin/bash
# 大汪心跳脚本 - 每30分钟执行

AGENT_ID="dawang"
STATE_DIR="/Users/godspeed/.openclaw/agents/${AGENT_ID}"
WORKSPACE="/Users/godspeed/.openclaw/workspaces/${AGENT_ID}"
TODO_FILE="${WORKSPACE}/TODO.md"
HEARTBEAT_FILE="${WORKSPACE}/HEARTBEAT.md"
LOG_FILE="${STATE_DIR}/cron/heartbeat.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录执行时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 心跳检查开始" >> "$LOG_FILE"

# 检查 TODO 文件是否存在
if [ ! -f "$TODO_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 错误: TODO.md 不存在" >> "$LOG_FILE"
    exit 1
fi

# 统计任务数量
TODO_COUNT=$(grep -c "\- \[ \]" "$TODO_FILE" 2>/dev/null || echo "0")
DONE_COUNT=$(grep -c "\- \[x\]" "$TODO_FILE" 2>/dev/null || echo "0")

# 更新 HEARTBEAT.md
if [ -f "$HEARTBEAT_FILE" ]; then
    sed -i.bak "s/最后检查:.*/最后检查: $(date '+%Y-%m-%d %H:%M')/" "$HEARTBEAT_FILE"
    sed -i.bak "s/进行中任务:.*/进行中任务: ${TODO_COUNT}/" "$HEARTBEAT_FILE"
    sed -i.bak "s/已完成任务:.*/已完成任务: ${DONE_COUNT}/" "$HEARTBEAT_FILE"
    rm -f "${HEARTBEAT_FILE}.bak"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 待办: ${TODO_COUNT}, 已完成: ${DONE_COUNT}" >> "$LOG_FILE"

# 如果有待办任务，发送提醒（每小时一次）
HOUR=$(date +%H)
MINUTE=$(date +%M)

if [ "$TODO_COUNT" -gt 0 ] && [ "$MINUTE" -lt 5 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 需要发送状态汇报" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 心跳检查完成" >> "$LOG_FILE"
