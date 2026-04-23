#!/bin/bash
# weixin-send-media 技能安装脚本
# 自动应用补丁并配置环境

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_DIR="$HOME/.openclaw"
EXTENSION_DIR="$OPENCLAW_DIR/extensions/openclaw-weixin/src/messaging"
TOKEN_DIR="$OPENCLAW_DIR/openclaw-weixin/context-tokens"

echo "🦆 微信发媒体技能安装脚本"
echo "========================"
echo ""

# 检查前置条件
echo "检查前置条件..."

if ! command -v patch &> /dev/null; then
    echo "❌ 未找到 patch 命令"
    echo "   请安装：sudo apt-get install patch  (Debian/Ubuntu)"
    echo "         或：sudo yum install patch    (CentOS/RHEL)"
    exit 1
fi
echo "  ✅ patch 命令可用"

if [ ! -d "$OPENCLAW_DIR" ]; then
    echo "❌ 未找到 OpenClaw 目录：$OPENCLAW_DIR"
    exit 1
fi
echo "  ✅ OpenClaw 已安装"

if [ ! -f "$EXTENSION_DIR/inbound.ts" ]; then
    echo "❌ 未找到 inbound.ts 文件：$EXTENSION_DIR/inbound.ts"
    exit 1
fi
echo "  ✅ 找到 inbound.ts"

echo ""

# 备份原文件
echo "备份原文件..."
BACKUP_FILE="$EXTENSION_DIR/inbound.ts.bak.$(date +%Y%m%d%H%M%S)"
cp "$EXTENSION_DIR/inbound.ts" "$BACKUP_FILE"
echo "  ✅ 已备份到：$BACKUP_FILE"
echo ""

# 应用补丁
echo "应用补丁..."
PATCH_FILE="$SCRIPT_DIR/patches/inbound.ts.patch"

if [ ! -f "$PATCH_FILE" ]; then
    echo "❌ 未找到补丁文件：$PATCH_FILE"
    exit 1
fi

cd "$EXTENSION_DIR"
if patch -p1 < "$PATCH_FILE"; then
    echo "  ✅ 补丁应用成功"
else
    echo "⚠️  补丁应用失败，尝试反向补丁..."
    # 如果失败，可能是已经打过补丁
    if grep -q "CONTEXT_TOKEN_DIR" "inbound.ts"; then
        echo "  ℹ️  补丁可能已经应用过"
    else
        echo "❌ 补丁应用失败，请手动检查"
        echo "   恢复备份：cp $BACKUP_FILE inbound.ts"
        exit 1
    fi
fi
echo ""

# 创建 token 存储目录
echo "创建 token 存储目录..."
mkdir -p "$TOKEN_DIR"
chmod 700 "$TOKEN_DIR"
echo "  ✅ 已创建：$TOKEN_DIR"
echo ""

# 设置脚本权限
echo "设置脚本权限..."
chmod +x "$SCRIPT_DIR/scripts/"*.js
chmod +x "$SCRIPT_DIR/tests/"*.sh
echo "  ✅ 脚本已设置为可执行"
echo ""

# 提示重启
echo "========================"
echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "  1. 重启 gateway: openclaw gateway restart"
echo "  2. 在微信里发送一条消息给机器人"
echo "  3. 验证 token 文件：ls -la $TOKEN_DIR"
echo "  4. 测试发送：$SCRIPT_DIR/scripts/send-image.js <user-id> <image>"
echo ""
echo "如需卸载，恢复备份："
echo "  cp $BACKUP_FILE $EXTENSION_DIR/inbound.ts"
echo "  openclaw gateway restart"
echo ""
