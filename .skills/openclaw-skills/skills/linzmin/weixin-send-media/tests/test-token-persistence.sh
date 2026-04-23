#!/bin/bash
# contextToken 持久化测试脚本
# 测试技能安装后 token 是否正确保存和读取

set -e

TOKEN_DIR="$HOME/.openclaw/openclaw-weixin/context-tokens"
TEST_ACCOUNT="test-account-id"
TEST_USER="test-user-id"
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')]"

echo "🧪 contextToken 持久化测试"
echo "=========================="
echo ""

# 测试 1: 检查目录是否存在
echo "测试 1: 检查 token 存储目录..."
if [ -d "$TOKEN_DIR" ]; then
    echo "  ✅ 目录存在：$TOKEN_DIR"
else
    echo "  ⚠️  目录不存在，创建中..."
    mkdir -p "$TOKEN_DIR"
    echo "  ✅ 已创建目录"
fi
echo ""

# 测试 2: 检查 token 文件
echo "测试 2: 检查现有 token 文件..."
TOKEN_COUNT=$(find "$TOKEN_DIR" -name "*.json" 2>/dev/null | wc -l)
if [ "$TOKEN_COUNT" -gt 0 ]; then
    echo "  ✅ 找到 $TOKEN_COUNT 个 token 文件"
    find "$TOKEN_DIR" -name "*.json" -exec basename {} \; | head -5 | while read f; do
        echo "    - $f"
    done
    if [ "$TOKEN_COUNT" -gt 5 ]; then
        echo "    ... 还有 $((TOKEN_COUNT - 5)) 个文件"
    fi
else
    echo "  ℹ️  暂无 token 文件（正常，需要先收到用户消息）"
fi
echo ""

# 测试 3: 验证 token 文件格式
echo "测试 3: 验证 token 文件格式..."
VALID=0
INVALID=0

if ! command -v jq &> /dev/null; then
    echo "  ℹ️  jq 未安装，跳过 JSON 格式验证"
    echo "     安装 jq 可获得更详细的验证：sudo apt-get install jq"
else
    for file in "$TOKEN_DIR"/*.json; do
        if [ -f "$file" ]; then
            if jq empty "$file" 2>/dev/null; then
                # 检查必需字段
                if jq -e '.accountId and .userId and .token and .savedAt' "$file" >/dev/null 2>&1; then
                    VALID=$((VALID + 1))
                else
                    INVALID=$((INVALID + 1))
                    echo "  ⚠️  格式不完整：$(basename "$file")"
                fi
            else
                INVALID=$((INVALID + 1))
                echo "  ❌ 无效 JSON: $(basename "$file")"
            fi
        fi
    done

    if [ $VALID -gt 0 ]; then
        echo "  ✅ $VALID 个有效 token 文件"
    fi
    if [ $INVALID -gt 0 ]; then
        echo "  ❌ $INVALID 个无效文件"
    fi
fi
if [ $VALID -eq 0 ] && [ $INVALID -eq 0 ] && [ $TOKEN_COUNT -gt 0 ]; then
    echo "  ℹ️  有 $TOKEN_COUNT 个文件（未验证格式）"
fi
echo ""

# 测试 4: 检查文件权限
echo "测试 4: 检查文件权限..."
INSECURE=0
for file in "$TOKEN_DIR"/*.json; do
    if [ -f "$file" ]; then
        PERMS=$(stat -c %a "$file" 2>/dev/null || stat -f %Lp "$file" 2>/dev/null)
        if [ "$PERMS" != "600" ] && [ "$PERMS" != "400" ]; then
            INSECURE=$((INSECURE + 1))
        fi
    fi
done

if [ $INSECURE -gt 0 ]; then
    echo "  ⚠️  $INSECURE 个文件权限不安全（建议 chmod 600）"
    echo "     运行：chmod 600 $TOKEN_DIR/*.json"
else
    echo "  ✅ 文件权限安全"
fi
if [ $INSECURE -eq 0 ] && [ $TOKEN_COUNT -eq 0 ]; then
    echo "  ℹ️  无 token 文件可检查"
fi
echo ""

# 测试 5: 检查 gateway 扩展
echo "测试 5: 检查 gateway 扩展文件..."
INBOUND_FILE="$HOME/.openclaw/extensions/openclaw-weixin/src/messaging/inbound.ts"
if [ -f "$INBOUND_FILE" ]; then
    if grep -q "CONTEXT_TOKEN_DIR" "$INBOUND_FILE"; then
        echo "  ✅ 补丁已应用（找到 CONTEXT_TOKEN_DIR）"
    else
        echo "  ❌ 补丁未应用（未找到 CONTEXT_TOKEN_DIR）"
        echo "     请运行：npx clawhub install weixin-send-media"
    fi
else
    echo "  ⚠️  未找到 inbound.ts 文件"
fi
echo ""

# 总结
echo "=========================="
echo "测试总结："
echo "  Token 文件数：$TOKEN_COUNT"
echo "  有效格式：$VALID"
echo "  无效格式：$INVALID"
echo "  权限不安全：$INSECURE"
echo ""

if [ $TOKEN_COUNT -eq 0 ]; then
    echo "💡 提示：先让微信用户发送一条消息，token 会自动保存"
fi

if [ $INSECURE -gt 0 ]; then
    echo "💡 提示：运行以下命令修复权限："
    echo "   chmod 600 $TOKEN_DIR/*.json"
fi

echo ""
echo "✅ 测试完成！"
