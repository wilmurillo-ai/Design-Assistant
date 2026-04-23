#!/bin/bash
# 小红书 OpenClaw 活动爬虫 Cron Wrapper
# 每天晚上7点自动执行

WORKSPACE="/Users/godspeed/.openclaw/workspaces/dawang"
SCRIPT_DIR="${WORKSPACE}/scripts"
LOG_FILE="${WORKSPACE}/scripts/cron_xhs.log"
FEISHU_TOKEN="${WORKSPACE}/scripts/feishu_token.txt"

# 日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行..." >> "${LOG_FILE}"

# 确保 Chrome 正在运行（启动调试模式如果需要）
if ! curl -s http://localhost:18800/json/list > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Chrome 未运行，启动中..." >> "${LOG_FILE}"
    open -a "Google Chrome" --args --remote-debugging-port=18800 --no-first-run --no-default-browser-check --user-data-dir=/tmp/chrome-openclaw &
    sleep 5
fi

# 运行爬虫
cd "${SCRIPT_DIR}"
python3 xhs_openclaw_scraper.py >> "${LOG_FILE}" 2>&1

# 检查输出
if [ -f xhs_openclaw_output.json ]; then
    CONTENT=$(cat xhs_openclaw_output.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('content',''))")
    if [ -n "$CONTENT" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 飞书文档已更新" >> "${LOG_FILE}"
    fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 执行完成" >> "${LOG_FILE}"
