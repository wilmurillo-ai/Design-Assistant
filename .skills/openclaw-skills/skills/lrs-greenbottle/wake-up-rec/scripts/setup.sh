#!/bin/bash
# wake-up-rec 安装配置脚本
# 功能：在 ~/.openclaw/hooks/ 创建 hook

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/wake-up-rec"
HOOKS_SOURCE="$SKILL_DIR/hooks/openclaw"
HOOKS_DEST="$HOME/.openclaw/hooks/wake-up-rec"

echo "=== wake-up-rec 安装配置 ==="

# 1. 检查技能hooks目录
echo ""
echo "【1/2】检查技能hooks目录..."

if [ ! -d "$HOOKS_SOURCE" ]; then
    echo "❌ 技能内无 hooks 目录: $HOOKS_SOURCE"
    exit 1
fi

echo "✅ 技能hooks目录存在"

# 2. 在 ~/.openclaw/hooks/ 创建 hook
echo ""
echo "【2/2】创建 hook..."

# 创建目录
mkdir -p "$HOME/.openclaw/hooks"

# 如果已存在，先删除
if [ -d "$HOOKS_DEST" ]; then
    rm -rf "$HOOKS_DEST"
fi

# 复制到 managed hooks 目录
cp -r "$HOOKS_SOURCE" "$HOOKS_DEST"

echo "✅ hook 已创建: $HOOKS_DEST"
echo ""
echo "=== 安装完成 ==="
echo ""
echo "注意：需要重启 OpenClaw 才能加载新 hook"
