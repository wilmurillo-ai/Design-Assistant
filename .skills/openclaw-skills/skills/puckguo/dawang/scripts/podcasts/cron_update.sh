#!/bin/bash
# 播客更新 cron 脚本
# 每天晚上8点执行

SCRIPT_DIR="$HOME/.openclaw/workspaces/dawang/scripts/podcasts"
LOG_FILE="$HOME/.openclaw/workspaces/dawang/scripts/podcasts/cron.log"
STATE_FILE="$HOME/.openclaw/workspaces/dawang/scripts/podcasts/podcast_state.json"
DOC_LINK_FILE="$HOME/.openclaw/workspaces/dawang/scripts/podcasts/feishu_doc_link.txt"
MASTER_DOC_FILE="$HOME/.openclaw/workspaces/dawang/scripts/podcasts/master_doc_id.txt"

# 飞书应用凭据
APP_ID="cli_a92d7a49c9399bca"
APP_SECRET="45KmSon6mcZ1hPsSEdXtnLkDEqII5QAw"
USER_ID="ou_2ef0900a3185db3f04cb7796f12e6ca1"

echo "$(date): 开始抓取播客更新" >> "$LOG_FILE"

cd "$SCRIPT_DIR"

# 获取 access token（使用curl绕过代理）
get_token() {
    curl -s --noproxy '*' -X POST \
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
        -H 'Content-Type: application/json' \
        -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}"
}

# 发送飞书消息
send_message() {
    local token="$1"
    local msg="$2"
    curl -s --noproxy '*' -X POST \
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' \
        -H "Authorization: Bearer $token" \
        -H 'Content-Type: application/json' \
        -d "{\"receive_id\":\"$USER_ID\",\"msg_type\":\"text\",\"content\":\"{\\\"text\\\":\\\"$msg\\\"}\"}"
}

# 读取上一期文档链接
PREV_DOC_LINK=""
if [ -f "$DOC_LINK_FILE" ]; then
    PREV_DOC_LINK=$(cat "$DOC_LINK_FILE")
    echo "$(date): 上一期文档: $PREV_DOC_LINK" >> "$LOG_FILE"
fi

# 抓取播客
python3 fetch_podcasts.py >> "$LOG_FILE" 2>&1

# 检查是否有内容
if [ -f "latest_report.md" ] && [ -s "latest_report.md" ]; then
    REPORT_LINES=$(wc -l < "latest_report.md")
    if [ "$REPORT_LINES" -gt 5 ]; then
        echo "$(date): 有新内容，开始创建飞书文档..." >> "$LOG_FILE"

        # 调用 update_feishu.py 创建文档
        python3 update_feishu.py >> "$LOG_FILE" 2>&1

        # 读取新创建的文档链接
        NEW_DOC_LINK=""
        if [ -f "$DOC_LINK_FILE" ]; then
            NEW_DOC_LINK=$(cat "$DOC_LINK_FILE")
        fi

        # 发送飞书消息（包含文档链接）
        TOKEN_RESP=$(get_token)
        TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))" 2>/dev/null)

        if [ -n "$TOKEN" ]; then
            TODAY=$(date '+%Y年%m月%d日')
            PREV_MSG=""
            if [ -n "$PREV_DOC_LINK" ]; then
                PREV_MSG="📎 往期日报: $PREV_DOC_LINK"$'\n\n'
            fi
            DOC_MSG=""
            if [ -n "$NEW_DOC_LINK" ]; then
                DOC_MSG="📎 今日日报: $NEW_DOC_LINK"$'\n\n'
            fi
            FULL_MSG="📬 播客日报 ${TODAY}"$'\n\n'"${DOC_MSG}${PREV_MSG}点击上方链接查看完整内容"
            echo "$(date): 发送飞书通知" >> "$LOG_FILE"
            SEND_RESP=$(send_message "$TOKEN" "$FULL_MSG")
            echo "$(date): 发送结果: $SEND_RESP" >> "$LOG_FILE"
        fi
    else
        echo "$(date): 无新内容，跳过创建文档" >> "$LOG_FILE"
        # 发送"无更新"通知
        TOKEN_RESP=$(get_token)
        TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))" 2>/dev/null)
        if [ -n "$TOKEN" ]; then
            TODAY=$(date '+%Y年%m月%d日')
            PREV_MSG=""
            if [ -n "$PREV_DOC_LINK" ]; then
                PREV_MSG="📎 往期日报: $PREV_DOC_LINK"$'\n\n'
            fi
            FULL_MSG="📬 播客日报 ${TODAY}"$'\n\n'"${PREV_MSG}⚠️ 本周暂无新更新"
            send_message "$TOKEN" "$FULL_MSG" >> "$LOG_FILE" 2>&1
        fi
    fi
fi

echo "$(date): 抓取完成" >> "$LOG_FILE"
