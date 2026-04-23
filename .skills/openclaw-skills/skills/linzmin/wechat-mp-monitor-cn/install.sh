#!/bin/bash
# wechat-mp-monitor 安装脚本

set -e

echo "🦆 安装 wechat-mp-monitor 技能..."

# 创建配置目录
CONFIG_DIR="$HOME/.openclaw/wechat-mp"
mkdir -p "$CONFIG_DIR"

# 检查配置文件
if [ ! -f "$CONFIG_DIR/config.json" ]; then
  echo ""
  echo "⚠️  需要配置微信公众号信息"
  echo ""
  echo "请创建配置文件：$CONFIG_DIR/config.json"
  echo ""
  cat << 'EOF'
{
  "appId": "你的 APPID",
  "appSecret": "你的 APPSECRET",
  "notifyUser": "你的微信 ID@im.wechat"
}
EOF
  echo ""
  read -p "配置完成后按回车继续..."
fi

# 设置脚本权限
chmod +x "$(dirname "$0")/scripts/"*.js

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo ""
echo "  # 获取 token"
echo "  node $(dirname "$0")/scripts/get-token.js"
echo ""
echo "  # 获取昨日文章数据"
echo "  node $(dirname "$0")/scripts/fetch-articles.js --yesterday"
echo ""
echo "  # 生成并发送日报"
echo "  node $(dirname "$0")/scripts/generate-report.js --send"
echo ""
echo "详细文档：$(dirname "$0")/SKILL.md"
