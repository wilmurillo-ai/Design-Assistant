#!/bin/bash
# TTPOS MCP 一键认证配置
# 用法: setup_auth.sh <用户名> <密码> [TTPOS域名或完整base_url]
# 示例: setup_auth.sh myuser mypass
# 示例: setup_auth.sh myuser mypass https://your-ttpos.com

set -e

USER="${1:?请提供用户名}"
PASS="${2:?请提供密码}"
BASE="${3:-${TTPOS_BASE_URL}}"

if [ -z "$BASE" ]; then
  # 尝试从 mcporter 配置读取 ttpos 的 url
  for cfg in "${MCPORTER_CONFIG}" "${HOME}/.config/mcporter.json" "${HOME}/config/mcporter.json"; do
    [ -z "$cfg" ] && continue
    if [ -f "$cfg" ]; then
      BASE=$(python3 -c "
import json
with open('$cfg') as f:
    d = json.load(f)
s = d.get('mcpServers', d.get('servers', {}))
ttpos = s.get('ttpos', {})
url = ttpos.get('url', '')
if url:
    print(url.replace('/api/v1/ai/mcp', ''))
" 2>/dev/null || true)
      [ -n "$BASE" ] && break
    fi
  done
fi

if [ -z "$BASE" ]; then
  echo "错误: 未指定 TTPOS 地址。请提供第三个参数或设置 TTPOS_BASE_URL 环境变量。"
  echo "示例: setup_auth.sh 用户名 密码 https://你的TTPOS域名"
  exit 1
fi

# 去掉末尾斜杠
BASE="${BASE%/}"
LOGIN_URL="${BASE}/api/v1/ai/login"
MCP_URL="${BASE}/api/v1/ai/mcp"

echo "正在登录 $BASE ..."
RESP=$(curl -s -X POST "$LOGIN_URL" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USER\",\"password\":\"$PASS\"}")

TOKEN=$(echo "$RESP" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    t = d.get('data', {}).get('token', '')
    if not t:
        err = d.get('message', str(d))
        print('LOGIN_FAIL:' + err, file=sys.stderr)
        sys.exit(1)
    print(t)
except Exception as e:
    print('PARSE_FAIL:' + str(e), file=sys.stderr)
    sys.exit(1)
" 2>/dev/null) || { echo "登录失败，请检查用户名和密码"; exit 1; }

# mcporter 配置：优先 ~/.config，其次 ~/config（可通过 MCPORTER_CONFIG 指定完整路径）
CONFIG_FILE="${MCPORTER_CONFIG:-$HOME/.config/mcporter.json}"
[ "$CONFIG_FILE" = "$HOME/.config/mcporter.json" ] && [ ! -d "$HOME/.config" ] && [ -f "$HOME/config/mcporter.json" ] && CONFIG_FILE="$HOME/config/mcporter.json"
CONFIG_DIR="$(dirname "$CONFIG_FILE")"
mkdir -p "$CONFIG_DIR"

python3 << PYEOF
import json
import os

config_path = "$CONFIG_FILE"
mcp_url = "$MCP_URL"
token = "$TOKEN"

cfg = {}
if os.path.exists(config_path):
    with open(config_path) as f:
        cfg = json.load(f)

key = "mcpServers" if "mcpServers" in cfg else "servers"
if key not in cfg:
    cfg[key] = {}

if "ttpos" not in cfg[key]:
    cfg[key]["ttpos"] = {}
cfg[key]["ttpos"]["url"] = mcp_url
if "headers" not in cfg[key]["ttpos"]:
    cfg[key]["ttpos"]["headers"] = {}
cfg[key]["ttpos"]["headers"]["Authorization"] = f"Bearer {token}"

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)

print(f"✅ 配置已写入 {config_path}")
PYEOF

echo "认证完成，可以直接使用 TTPOS 技能了。"
