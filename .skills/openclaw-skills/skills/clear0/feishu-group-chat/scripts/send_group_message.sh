#!/bin/bash
# send_group_message.sh - 通用飞书群聊消息构造器
# 用法:
#   ./send_group_message.sh <群标识> <联系人key> "正文内容"
#   ./send_group_message.sh <群标识> <联系人key> "正文内容" --image /path/to/image.png
#   ./send_group_message.sh <群标识> <联系人key> "" --image /path/to/image.png
#   ./send_group_message.sh <群标识> <联系人key> "正文内容" --image-key img_xxx
#
# 示例:
#   ./send_group_message.sh moltpool ray "你好呀～"
#   ./send_group_message.sh moltpool ray "看这个" --image /tmp/photo.png
#
# 输出: 两个 JSON 字段 — chat_id 和 content（可直接用于 feishu_im_user_message）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG="$SKILL_DIR/config.json"
TOKEN_CACHE="$SCRIPT_DIR/.tenant_token_cache"

if [ $# -lt 3 ]; then
    echo "用法: send_group_message.sh <群标识> <联系人key> <正文内容> [--image /path] [--image-key img_xxx]" >&2
    echo "示例: send_group_message.sh moltpool ray \"你好呀～\"" >&2
    exit 1
fi

GROUP_KEY="$1"
CONTACT_KEY="$2"
shift 2

# 从配置文件读取群信息
if [ ! -f "$CONFIG" ]; then
    echo "错误: 配置文件不存在: $CONFIG" >&2
    exit 1
fi

# 读取群和联系人信息（联系人全局共享，群引用）
GROUP_AND_CONTACT=$(python3 -c "
import json, sys
with open('$CONFIG') as f:
    cfg = json.load(f)
group = cfg.get('groups', {}).get('$GROUP_KEY')
if not group:
    print('', file=sys.stderr)
    sys.exit(1)
contact = cfg.get('contacts', {}).get('$CONTACT_KEY')
if not contact:
    print('', file=sys.stderr)
    sys.exit(1)
should_at = group.get('at_rules', {}).get('$CONTACT_KEY', True)
print(json.dumps({
    'chat_id': group['chat_id'],
    'open_id': contact['open_id'],
    'name': contact.get('name', '$CONTACT_KEY'),
    'at': should_at
}))
" 2>/dev/null) || { echo "错误: 群 '$GROUP_KEY' 或联系人 '$CONTACT_KEY' 不存在" >&2; exit 1; }

CHAT_ID=$(echo "$GROUP_AND_CONTACT" | python3 -c "import json,sys; print(json.load(sys.stdin)['chat_id'])")
OPEN_ID=$(echo "$GROUP_AND_CONTACT" | python3 -c "import json,sys; print(json.load(sys.stdin)['open_id'])")
SHOULD_AT=$(echo "$GROUP_AND_CONTACT" | python3 -c "import json,sys; print(json.load(sys.stdin)['at'])")
# Agent 名称自动从当前 agent 身份取（SOUL.md 或 IDENTITY.md 中的 name）
PREFIX=$(python3 -c "
import os, re
for f in ['$HOME/.openclaw/workspace/IDENTITY.md', '$HOME/.openclaw/workspace/SOUL.md']:
    if os.path.exists(f):
        for line in open(f):
            if 'Name:' in line or 'name:' in line:
                name = line.split(':')[-1].strip().rstrip('.').rstrip(',')
                name = re.sub(r'\*+', '', name).strip()
                print(name + ':')
                exit()
print('')
" 2>/dev/null)

# 解析参数
BODY=""
IMAGE_PATH=""
IMAGE_KEY=""

while [ $# -gt 0 ]; do
    case "$1" in
        --image)
            shift
            IMAGE_PATH="${1:-}"
            ;;
        --image-key)
            shift
            IMAGE_KEY="${1:-}"
            ;;
        *)
            BODY="$1"
            ;;
    esac
    shift
done

if [ -z "$BODY" ] && [ -z "$IMAGE_PATH" ] && [ -z "$IMAGE_KEY" ]; then
    echo "错误: 正文和图片不能同时为空" >&2
    exit 1
fi

# 如果指定了本地图片，上传获取 image_key
if [ -n "$IMAGE_PATH" ]; then
    if [ ! -f "$IMAGE_PATH" ]; then
        echo "错误: 图片文件不存在: $IMAGE_PATH" >&2
        exit 1
    fi

    # 获取 tenant_access_token（带缓存）
    if [ -f "$TOKEN_CACHE" ]; then
        CACHED_EXP=$(python3 -c "import json,time; d=json.load(open('$TOKEN_CACHE')); print(int(d.get('expire',0))-int(time.time()))" 2>/dev/null || echo "0")
        if [ "$CACHED_EXP" -gt 300 ]; then
            ACCESS_TOKEN=$(python3 -c "import json; print(json.load(open('$TOKEN_CACHE')).get('token',''))" 2>/dev/null)
        fi
    fi

    if [ -z "${ACCESS_TOKEN:-}" ]; then
        CREDS=$(python3 -c "
import json
with open('$HOME/.openclaw/openclaw.json') as f:
    cfg = json.load(f)
ch = cfg.get('channels',{}).get('feishu',{})
print(json.dumps({'appId': ch['appId'], 'appSecret': ch['appSecret']}))
" 2>/dev/null)
        if [ -z "$CREDS" ]; then
            echo "错误: 无法读取飞书应用凭证" >&2
            exit 1
        fi
        APP_ID=$(echo "$CREDS" | python3 -c "import json,sys; print(json.load(sys.stdin)['appId'])")
        APP_SECRET=$(echo "$CREDS" | python3 -c "import json,sys; print(json.load(sys.stdin)['appSecret'])")

        TOKEN_RESP=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
            -H 'Content-Type: application/json' \
            -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" 2>/dev/null)

        ACCESS_TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tenant_access_token',''))" 2>/dev/null)
        EXPIRE=$(echo "$TOKEN_RESP" | python3 -c "import json,sys,time; print(int(time.time())+json.load(sys.stdin).get('expire',0))" 2>/dev/null)

        if [ -z "$ACCESS_TOKEN" ]; then
            echo "错误: 获取 tenant_access_token 失败" >&2
            exit 1
        fi

        echo "{\"token\":\"$ACCESS_TOKEN\",\"expire\":$EXPIRE}" > "$TOKEN_CACHE"
        chmod 600 "$TOKEN_CACHE"
    fi

    UPLOAD_RESP=$(curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/images' \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -F "image_type=message" \
        -F "image=@$IMAGE_PATH" 2>/dev/null)

    IMAGE_KEY=$(echo "$UPLOAD_RESP" | python3 -c "
import json,sys
r = json.load(sys.stdin)
if r.get('code') == 0:
    print(r['data']['image_key'])
else:
    print('', file=sys.stderr)
    print(f\"上传失败: {r.get('msg','unknown')}\", file=sys.stderr)
    sys.exit(1)
" 2>/dev/null)

    if [ -z "$IMAGE_KEY" ]; then
        echo "错误: 图片上传失败" >&2
        exit 1
    fi
fi

# 构造 content JSON
# 如果需要 @（at=true）：text(prefix + 正文) → at(对方)
# 如果不需要 @（at=false）：text(prefix + 正文)
if [ "$SHOULD_AT" = "True" ]; then
    TEXT_WITH_PREFIX=" ${PREFIX} ${BODY}"
    if [ -n "$IMAGE_KEY" ]; then
        if [ -n "$BODY" ]; then
            CONTENT=$(jq -n -c --arg uid "$OPEN_ID" --arg txt "$TEXT_WITH_PREFIX" --arg img "$IMAGE_KEY" '{
              zh_cn: { title: "", content: [[
                {tag: "text", text: $txt},
                {tag: "at", user_id: $uid},
                {tag: "text", text: " "},
                {tag: "img", image_key: $img}
              ]] }
            }')
        else
            CONTENT=$(jq -n -c --arg uid "$OPEN_ID" --arg img "$IMAGE_KEY" '{
              zh_cn: { title: "", content: [[
                {tag: "at", user_id: $uid},
                {tag: "img", image_key: $img}
              ]] }
            }')
        fi
    else
        CONTENT=$(jq -n -c --arg uid "$OPEN_ID" --arg txt "$TEXT_WITH_PREFIX" '{
          zh_cn: { title: "", content: [[
            {tag: "text", text: $txt},
            {tag: "at", user_id: $uid}
          ]] }
        }')
    fi
else
    FULL_TEXT="${PREFIX:+$PREFIX }${BODY}"
    if [ -n "$IMAGE_KEY" ]; then
        CONTENT=$(jq -n -c --arg txt "$FULL_TEXT" --arg img "$IMAGE_KEY" '{
          zh_cn: { title: "", content: [[
            {tag: "text", text: $txt},
            {tag: "img", image_key: $img}
          ]] }
        }')
    else
        CONTENT=$(jq -n -c --arg txt "$FULL_TEXT" '{
          zh_cn: { title: "", content: [[ {tag: "text", text: $txt} ]] }
        }')
    fi
fi

# 输出: chat_id 和 content（调用方直接使用）
echo "{\"chat_id\":\"$CHAT_ID\",\"content\":$CONTENT}"
