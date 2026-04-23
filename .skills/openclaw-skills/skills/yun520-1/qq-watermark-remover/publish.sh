#!/bin/bash

echo "================================================================"
echo "📦 QQ Video Watermark Remover - 发布到 ClawHub"
echo "================================================================"
echo ""

# 检查登录状态
echo "🔍 检查登录状态..."
clawhub whoami > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  未登录，请先登录 ClawHub"
    echo ""
    echo "运行：clawhub login"
    echo "或访问：https://clawhub.ai/cli/auth"
    echo ""
    exit 1
fi

echo "✅ 已登录"
echo ""

# 发布
echo "🚀 开始发布..."
echo ""

clawhub publish ./ \
  --slug qq-watermark-remover \
  --name "QQ Video Watermark Remover" \
  --version 1.0.0 \
  --changelog "初始版本 - 智能 QQ 视频水印去除工具，支持自动识别和精确定位水印" \
  --tags "latest,watermark,video,qq,doubao,ai"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================"
    echo "🎉 发布成功！"
    echo "================================================================"
    echo ""
    echo "📦 项目名称：qq-watermark-remover"
    echo "🏷️  版本：1.0.0"
    echo "🔖 标签：watermark, video, qq, doubao, ai"
    echo ""
    echo "📥 安装命令:"
    echo "   clawhub install qq-watermark-remover"
    echo ""
    echo "🔗 ClawHub 页面:"
    echo "   https://clawhub.ai/skills/qq-watermark-remover"
    echo ""
else
    echo ""
    echo "================================================================"
    echo "❌ 发布失败"
    echo "================================================================"
    echo ""
    echo "请检查:"
    echo "1. 是否已登录 ClawHub (运行：clawhub login)"
    echo "2. 网络连接是否正常"
    echo "3. slug 是否已被占用"
    echo ""
    exit 1
fi
