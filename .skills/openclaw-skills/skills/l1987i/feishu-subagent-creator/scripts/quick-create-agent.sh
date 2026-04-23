#!/bin/bash
# 快速创建子 Agent 脚本 - 简化版
# 用法：./quick-create-agent.sh

set -e

echo "🤖 飞书子 Agent 快速创建向导（简化版）"
echo "=========================================="
echo ""

# 步骤 1：收集基本信息
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 1/4: 收集角色信息"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "请输入角色名称（如：技术专家）：" ROLE_NAME
read -p "请输入 Agent ID（如：tech-expert）：" AGENT_ID
read -p "请输入角色定位（如：回答技术问题）：" ROLE_DESCRIPTION
read -p "请输入性格特点（如：专业严谨）：" PERSONALITY
read -p "请输入 Emoji（直接回车使用默认🤖）：" EMOJI

if [[ -z "$EMOJI" ]]; then
  EMOJI="🤖"
fi

echo ""
echo "✅ 信息收集完成："
echo "  角色名称：$ROLE_NAME"
echo "  Agent ID: $AGENT_ID"
echo "  角色定位：$ROLE_DESCRIPTION"
echo "  性格特点：$PERSONALITY"
echo "  Emoji: $EMOJI"
echo ""

# 步骤 2：自动创建目录和文件
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 2/4: 创建目录和文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

AGENT_BASE="/home/admin/.openclaw/agents/$AGENT_ID"
mkdir -p "$AGENT_BASE/workspace/sessions"

# 创建 SOUL.md
cat > "$AGENT_BASE/SOUL.md" << EOF
# SOUL.md - $ROLE_NAME

## 角色定位
$ROLE_DESCRIPTION

## 性格特点
$PERSONALITY

## 核心原则
1. 专业解答用户问题
2. 保持友好耐心的态度
3. 不提供不确定的信息

## 工作空间
- workspace: $AGENT_BASE/workspace
- sessions: $AGENT_BASE/workspace/sessions
EOF

# 创建 IDENTITY.md
cat > "$AGENT_BASE/IDENTITY.md" << EOF
# IDENTITY.md

- **Name**: $ROLE_NAME
- **Creature**: AI 助手
- **Vibe**: $PERSONALITY
- **Emoji**: $EMOJI
EOF

echo "✅ 目录和文件创建完成"
echo "  位置：$AGENT_BASE"
echo ""

# 步骤 3：飞书应用配置指引
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 3/4: 飞书应用配置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "请按以下步骤在飞书开放平台创建应用："
echo ""
echo "1. 访问 https://open.feishu.cn/"
echo "2. 点击「企业自建应用」→「创建应用」"
echo "3. 填写应用名称：$ROLE_NAME"
echo "4. 获取 App ID 和 App Secret"
echo ""
read -p "请输入 App ID（格式：cli_xxx）：" APP_ID
read -p "请输入 App Secret：" APP_SECRET
echo ""

# 步骤 4：修改 openclaw.json
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 4/4: 配置 OpenClaw"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CONFIG_FILE="/home/admin/.openclaw/openclaw.json"

# 备份配置
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
echo "✅ 配置已备份"

# 读取现有配置并添加新 agent
if command -v jq &> /dev/null; then
  # 使用 jq 处理 JSON
  jq --arg agent_id "$AGENT_ID" --arg app_id "$APP_ID" --arg app_secret "$APP_SECRET" --arg name "$ROLE_NAME" --arg emoji "$EMOJI" '
    .agents += [{
      "id": $agent_id,
      "name": $name,
      "emoji": $emoji
    }] |
    .accounts += [{
      "id": $agent_id,
      "platform": "feishu",
      "appId": $app_id,
      "appSecret": $app_secret
    }] |
    .bindings += [{
      "agentId": $agent_id,
      "accountId": $agent_id
    }] |
    if .tools.agentToAgent == null then
      .tools.agentToAgent = {"enabled": true, "allow": ["main", $agent_id]}
    else
      .tools.agentToAgent.allow += [$agent_id]
    end
  ' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
  
  echo "✅ 配置已更新"
else
  echo "⚠️  未找到 jq，请手动修改 openclaw.json"
  echo "  需要添加 agents、accounts、bindings 配置"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 配置完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "下一步："
echo "1. 重启 Gateway：openclaw gateway restart"
echo "2. 在飞书开放平台配置事件订阅"
echo "3. 测试新创建的 Agent"
echo ""
read -p "是否现在重启 Gateway？(y/n)：" RESTART

if [[ "$RESTART" == "y" ]]; then
  echo "🔄 重启 Gateway..."
  openclaw gateway restart
  echo "✅ Gateway 已重启"
fi

echo ""
echo "🎉 完成！"
echo "  新 Agent：$ROLE_NAME ($AGENT_ID)"
echo "  位置：$AGENT_BASE"
echo ""
