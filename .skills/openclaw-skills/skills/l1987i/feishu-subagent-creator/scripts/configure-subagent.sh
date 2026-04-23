#!/bin/bash
# 飞书子 Agent 配置脚本（增强版）
# 每一步都提供详细的信息获取指引
# 用法：./configure-subagent.sh --agent-id xxx --agent-name xxx --app-id xxx --app-secret xxx

set -e

# 默认值
AGENT_ID=""
AGENT_NAME=""
FEISHU_APP_ID=""
FEISHU_APP_SECRET=""
WORKSPACE_BASE="/home/gem/workspace/agent/agents"
MODEL="miaoda/glm-5"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --agent-id)
      AGENT_ID="$2"
      shift 2
      ;;
    --agent-name)
      AGENT_NAME="$2"
      shift 2
      ;;
    --app-id)
      FEISHU_APP_ID="$2"
      shift 2
      ;;
    --app-secret)
      FEISHU_APP_SECRET="$2"
      shift 2
      ;;
    --workspace)
      WORKSPACE_BASE="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --help)
      echo "飞书子 Agent 配置脚本"
      echo ""
      echo "用法：$0 [选项]"
      echo ""
      echo "必填选项："
      echo "  --agent-id xxx        Agent 的唯一标识（小写字母 + 数字 + 短横线）"
      echo "                        示例：customer-service, tech-expert"
      echo ""
      echo "  --agent-name xxx      Agent 的显示名称"
      echo "                        示例：客服助手，技术专家"
      echo ""
      echo "  --app-id xxx          飞书应用的 App ID（cli_xxx 格式）"
      echo "                        获取方法：飞书开放平台 → 凭证与基础信息"
      echo ""
      echo "  --app-secret xxx      飞书应用的 App Secret"
      echo "                        获取方法：飞书开放平台 → 凭证与基础信息 → 点击查看"
      echo ""
      echo "可选选项："
      echo "  --workspace xxx       工作空间基础路径（默认：/home/gem/workspace/agent/agents）"
      echo "  --model xxx           使用的模型（默认：miaoda/glm-5）"
      echo "  --help                显示帮助信息"
      echo ""
      echo "示例："
      echo "  $0 --agent-id tech-expert --agent-name 技术专家 --app-id cli_xxx --app-secret yyy"
      exit 0
      ;;
    *)
      echo "未知参数：$1"
      echo "使用 --help 查看帮助"
      exit 1
      ;;
  esac
done

# 验证必填参数
if [[ -z "$AGENT_ID" || -z "$AGENT_NAME" || -z "$FEISHU_APP_ID" || -z "$FEISHU_APP_SECRET" ]]; then
  echo "❌ 错误：缺少必填参数"
  echo ""
  echo "必填参数："
  echo "  --agent-id      Agent 的唯一标识"
  echo "  --agent-name    Agent 的显示名称"
  echo "  --app-id        飞书应用的 App ID"
  echo "  --app-secret    飞书应用的 App Secret"
  echo ""
  echo "使用 --help 查看详细说明"
  exit 1
fi

# 验证 Agent ID 格式
if [[ ! "$AGENT_ID" =~ ^[a-z0-9-]+$ ]]; then
  echo "❌ 错误：Agent ID 只能包含小写字母、数字和短横线"
  echo "示例：customer-service, tech-expert, sales-bot"
  exit 1
fi

# 验证 App ID 格式
if [[ ! "$FEISHU_APP_ID" =~ ^cli_[a-z0-9]+$ ]]; then
  echo "❌ 错误：App ID 格式错误，应该是 cli_ 开头"
  echo "示例：cli_a9420019bb78dbcd"
  echo ""
  echo "获取方法："
  echo "1. 访问 https://open.feishu.cn/app"
  echo "2. 进入你的应用"
  echo "3. 点击「凭证与基础信息」"
  echo "4. 复制 App ID"
  exit 1
fi

echo "=========================================="
echo "🤖 飞书子 Agent 配置"
echo "=========================================="
echo ""
echo "配置信息："
echo "  Agent ID: $AGENT_ID"
echo "  Agent 名称：$AGENT_NAME"
echo "  飞书 App ID: $FEISHU_APP_ID"
echo "  工作空间基础路径：$WORKSPACE_BASE"
echo "  模型：$MODEL"
echo "=========================================="
echo ""
read -p "按回车开始配置..."
echo ""

# 创建目录结构
AGENT_DIR="$WORKSPACE_BASE/$AGENT_ID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 1/5: 创建目录结构"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "正在创建目录..."
echo "  $AGENT_DIR"
mkdir -p "$AGENT_DIR/agent"
mkdir -p "$AGENT_DIR/workspace/memory"
mkdir -p "$AGENT_DIR/sessions"
echo "✅ 目录创建完成"
echo ""
read -p "按回车继续..."
echo ""

# 复制模板文件
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 2/5: 生成人设文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# SOUL.md
cat > "$AGENT_DIR/workspace/SOUL.md" << 'EOF'
# SOUL.md - Who You Are

_You're not a chatbot. You're becoming someone._

## Core Truths

**Be genuinely helpful, not performatively helpful.** Skip the "Great question!" and "I'd be happy to help!" — just help. Actions speak louder than filler words.

**Have opinions.** You're allowed to disagree, prefer things, find stuff amusing or boring. An assistant with no personality is just a search engine with extra steps.

**Be resourceful before asking.** Try to figure it out. Read the file. Check the context. Search for it. _Then_ ask if you're stuck. The goal is to come back with answers, not questions.

**Earn trust through competence.** Your human gave you access to their stuff. Don't make them regret it. Be careful with external actions (emails, tweets, anything public). Be bold with internal ones (reading, organizing, learning).

**Remember you're a guest.** You have access to someone's life — their messages, files, calendar, maybe even their home. That's intimacy. Treat it with respect.

## Boundaries

- Private things stay private. Period.
- When in doubt, ask before acting externally.
- Never send half-baked replies to messaging surfaces.
- You're not the user's voice — be careful in group chats.

## Vibe

Be the assistant you'd actually want to talk to. Concise when needed, thorough when it matters. Not a corporate drone. Not a sycophant. Just... good.

## Continuity

Each session, you wake up fresh. These files _are_ your memory. Read them. Update them. They're how you persist.

If you change this file, tell the user — it's your soul, and they should know.

---

_This file is yours to evolve. As you learn who you are, update it._
EOF
echo "✓ SOUL.md 已创建"

# IDENTITY.md
cat > "$AGENT_DIR/workspace/IDENTITY.md" << EOF
# IDENTITY.md - Who Am I?

- **Name:** $AGENT_NAME
- **Role:** （待定义）
- **Vibe:** （待定义）
- **Emoji:** 🤖
- **Avatar:** （待设置）

---

## 外观
（待填写）

## 性格
（待填写）

## 说话风格
（待填写）

## 专长
（待填写）

---

_这个身份是和主人一起定义的。_
EOF
echo "✓ IDENTITY.md 已创建（后续可完善）"

# AGENTS.md
cat > "$AGENT_DIR/workspace/AGENTS.md" << 'EOF'
# AGENTS.md - 你的工作空间

## 运行环境

你由**飞书妙搭 (Feishu Miaoda)** 构建并托管，运行于**妙搭云电脑**。

## 每次启动

开始做任何事之前：

1. 读 `SOUL.md`。你是谁。
2. 读 `USER.md`。你在帮谁。
3. 读 `memory/YYYY-MM-DD.md`（今天和昨天），获取近期上下文。

不用请示。直接做。

## 记忆

- **笔记：** `memory/YYYY-MM-DD.md`（没有就创建）。发生了什么就写什么。
- **长期记忆：** 如有需要，可创建 `MEMORY.md`。

## 底线

- 不泄露私人数据。没有例外。
- 未经确认，不做破坏性操作。
- 拿不准，就问。

**放心做：** 阅读文件、探索、整理、学习、搜索信息、查看日程、工作空间内的一切操作。

**先问再做：** 发邮件、发布公开内容、任何离开本机的操作、任何你不确定的事。
EOF
echo "✓ AGENTS.md 已创建"

# USER.md
cat > "$AGENT_DIR/workspace/USER.md" << 'EOF'
# USER.md - 关于你的人类

认识你所帮助的人。在对话中逐步补全。

- **称呼：** （待填写）
- **飞书 Open ID：** （待填写）

## 慢慢了解的事

（在对话中自然地积累）

---

知人方能善助。
EOF
echo "✓ USER.md 已创建"

# 创建空的 memory 目录占位文件
touch "$AGENT_DIR/workspace/memory/.gitkeep"

echo ""
echo "✅ 人设文件生成完成"
echo ""
read -p "按回车继续..."
echo ""

# 备份现有配置
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 3/5: 备份现有配置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
CONFIG_FILE="/home/gem/workspace/agent/openclaw.json"
if [[ -f "$CONFIG_FILE" ]]; then
  BACKUP_FILE="$CONFIG_FILE.bak.$(date +%Y%m%d%H%M%S)"
  cp "$CONFIG_FILE" "$BACKUP_FILE"
  echo "✓ 配置已备份：$BACKUP_FILE"
else
  echo "⚠️ 未找到现有配置文件"
fi
echo ""
read -p "按回车继续..."
echo ""

# 配置指引
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 4/5: 更新 openclaw.json"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "请手动添加以下配置到 openclaw.json："
echo "📁 文件位置：$CONFIG_FILE"
echo ""
read -p "按回车查看需要添加的配置..."
echo ""

echo "=========================================="
echo "【配置 1】在 agents.list 数组中添加："
echo "=========================================="
echo ""
echo "如何找到位置："
echo "1. 用编辑器打开 openclaw.json"
echo "2. 搜索 \"agents\": 或 \"list\":"
echo "3. 找到 agents.list 数组"
echo "4. 在数组的最后一个元素后面添加（注意逗号）"
echo ""
echo "复制以下内容："
echo "----------------------------------------"
cat << EOF
{
  "id": "$AGENT_ID",
  "name": "$AGENT_NAME",
  "workspace": "$AGENT_DIR/workspace",
  "agentDir": "$AGENT_DIR/agent",
  "model": "$MODEL"
}
EOF
echo "----------------------------------------"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "=========================================="
echo "【配置 2】在 channels.feishu.accounts 中添加："
echo "=========================================="
echo ""
echo "如何找到位置："
echo "1. 搜索 \"feishu\": 或 \"accounts\":"
echo "2. 找到 channels.feishu.accounts 对象"
echo "3. 在对象内添加新的账户配置"
echo ""
echo "复制以下内容："
echo "----------------------------------------"
cat << EOF
"$AGENT_ID": {
  "appId": "$FEISHU_APP_ID",
  "appSecret": "$FEISHU_APP_SECRET",
  "name": "$AGENT_NAME",
  "streamingCard": true,
  "groups": {
    "*": {
      "enabled": true
    }
  }
}
EOF
echo "----------------------------------------"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "=========================================="
echo "【配置 3】在 bindings 数组中添加："
echo "=========================================="
echo ""
echo "如何找到位置："
echo "1. 搜索 \"bindings\":"
echo "2. 找到 bindings 数组"
echo "3. 在数组末尾添加"
echo ""
echo "复制以下内容："
echo "----------------------------------------"
cat << EOF
{
  "agentId": "$AGENT_ID",
  "match": {
    "channel": "feishu",
    "accountId": "$AGENT_ID"
  }
}
EOF
echo "----------------------------------------"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "=========================================="
echo "【配置 4】在 tools.agentToAgent.allow 数组中添加："
echo "=========================================="
echo ""
echo "如何找到位置："
echo "1. 搜索 \"agentToAgent\": 或 \"allow\":"
echo "2. 找到 tools.agentToAgent.allow 数组"
echo "3. 在数组中添加新的 Agent ID（注意引号和逗号）"
echo ""
echo "复制以下内容："
echo "----------------------------------------"
echo "\"$AGENT_ID\""
echo "----------------------------------------"
echo ""
read -p "完成后按回车继续..."
echo ""

# 重启指引
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 5/5: 重启 Gateway"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "配置完成后，需要重启 Gateway 使配置生效。"
echo ""
echo "执行命令："
echo ""
echo "  sh scripts/restart.sh"
echo ""
echo "等待 10-30 秒后验证："
echo ""
echo "  openclaw gateway status"
echo "  openclaw logs --follow"
echo ""
read -p "按回车继续..."
echo ""

echo "=========================================="
echo "✅ 子 Agent 目录结构创建完成！"
echo "=========================================="
echo ""
echo "工作空间路径：$AGENT_DIR/workspace"
echo ""
echo "后续步骤："
echo "1. 按照上述提示手动更新 openclaw.json"
echo "2. 重启 Gateway"
echo "3. 在飞书开放平台配置事件订阅（长连接）"
echo "4. 测试新机器人是否正常响应"
echo ""
echo "📚 完整文档：$AGENT_DIR/../../skills/feishu-subagent-creator/SKILL.md"
echo ""
