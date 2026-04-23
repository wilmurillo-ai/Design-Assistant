#!/bin/bash
# 飞书子 Agent 自动配置脚本（完全自动化版）
# 自动读取和修改 openclaw.json，无需用户手动编辑
# 用法：./auto-configure-subagent.sh --agent-id xxx --agent-name xxx --app-id xxx --app-secret xxx

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
AGENT_ID=""
AGENT_NAME=""
FEISHU_APP_ID=""
FEISHU_APP_SECRET=""
WORKSPACE_BASE="/home/gem/workspace/agent/agents"
MODEL="miaoda/glm-5"
CONFIG_FILE="/home/gem/workspace/agent/openclaw.json"

# 打印函数
print_step() {
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}步骤 $1: $2${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
}

print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
  echo -e "${RED}❌ $1${NC}"
}

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
      echo "飞书子 Agent 自动配置脚本"
      echo ""
      echo "用法：$0 [选项]"
      echo ""
      echo "必填选项："
      echo "  --agent-id xxx        Agent 的唯一标识（小写字母 + 数字 + 短横线）"
      echo "  --agent-name xxx      Agent 的显示名称"
      echo "  --app-id xxx          飞书应用的 App ID（cli_xxx 格式）"
      echo "  --app-secret xxx      飞书应用的 App Secret"
      echo ""
      echo "可选选项："
      echo "  --workspace xxx       工作空间基础路径（默认：/home/gem/workspace/agent/agents）"
      echo "  --model xxx           使用的模型（默认：miaoda/glm-5）"
      echo ""
      exit 0
      ;;
    *)
      print_error "未知参数：$1"
      exit 1
      ;;
  esac
done

# 验证必填参数
if [[ -z "$AGENT_ID" || -z "$AGENT_NAME" || -z "$FEISHU_APP_ID" || -z "$FEISHU_APP_SECRET" ]]; then
  print_error "缺少必填参数"
  echo ""
  echo "必填参数："
  echo "  --agent-id      Agent 的唯一标识"
  echo "  --agent-name    Agent 的显示名称"
  echo "  --app-id        飞书应用的 App ID"
  echo "  --app-secret    飞书应用的 App Secret"
  echo ""
  echo "使用 --help 查看详细帮助"
  exit 1
fi

# 验证格式
if [[ ! "$AGENT_ID" =~ ^[a-z0-9-]+$ ]]; then
  print_error "Agent ID 格式错误，只能包含小写字母、数字和短横线"
  exit 1
fi

if [[ ! "$FEISHU_APP_ID" =~ ^cli_[a-z0-9]+$ ]]; then
  print_error "App ID 格式错误，应该是 cli_ 开头"
  exit 1
fi

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}🤖 飞书子 Agent 自动配置${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "配置信息："
echo "  Agent ID: $AGENT_ID"
echo "  Agent 名称：$AGENT_NAME"
echo "  飞书 App ID: $FEISHU_APP_ID"
echo "  工作空间：$WORKSPACE_BASE"
echo "  模型：$MODEL"
echo ""
read -p "按回车开始自动配置..."
echo ""

# 步骤 1：创建目录结构
AGENT_DIR="$WORKSPACE_BASE/$AGENT_ID"
print_step "1/5" "创建 Agent 目录结构"

echo "正在创建目录..."
mkdir -p "$AGENT_DIR/agent"
mkdir -p "$AGENT_DIR/workspace/memory"
mkdir -p "$AGENT_DIR/sessions"
print_success "目录创建完成：$AGENT_DIR"
echo ""

# 步骤 2：生成人设文件
print_step "2/5" "生成人设文件"

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
print_success "SOUL.md 已创建"

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
print_success "IDENTITY.md 已创建"

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
print_success "AGENTS.md 已创建"

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
print_success "USER.md 已创建"

touch "$AGENT_DIR/workspace/memory/.gitkeep"
echo ""

# 步骤 3：备份并读取现有配置
print_step "3/5" "备份并读取现有配置"

if [[ ! -f "$CONFIG_FILE" ]]; then
  print_error "未找到配置文件：$CONFIG_FILE"
  exit 1
fi

# 备份配置
BACKUP_FILE="$CONFIG_FILE.bak.$(date +%Y%m%d%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP_FILE"
print_success "配置已备份：$BACKUP_FILE"

# 检查 jq 是否可用
if ! command -v jq &> /dev/null; then
  print_error "需要安装 jq 工具来处理 JSON"
  echo "请执行：sudo apt-get install jq 或 brew install jq"
  exit 1
fi

echo ""

# 步骤 4：自动修改 openclaw.json
print_step "4/5" "自动修改 openclaw.json"

echo "正在读取现有配置..."

# 4.1 添加 agent 到 agents.list
echo "添加 agent 配置..."
TEMP_FILE=$(mktemp)
jq --arg id "$AGENT_ID" \
   --arg name "$AGENT_NAME" \
   --arg workspace "$AGENT_DIR/workspace" \
   --arg agentDir "$AGENT_DIR/agent" \
   --arg model "$MODEL" \
   '.agents.list += [{
     "id": $id,
     "name": $name,
     "workspace": $workspace,
     "agentDir": $agentDir,
     "model": $model
   }]' "$CONFIG_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$CONFIG_FILE"
print_success "已添加 agent 到 agents.list"

# 4.2 添加飞书账户
echo "添加飞书账户配置..."
TEMP_FILE=$(mktemp)
jq --arg id "$AGENT_ID" \
   --arg appId "$FEISHU_APP_ID" \
   --arg secret "$FEISHU_APP_SECRET" \
   --arg name "$AGENT_NAME" \
   '.channels.feishu.accounts += {
     ($id): {
       "appId": $appId,
       "appSecret": $secret,
       "name": $name,
       "streamingCard": true,
       "groups": {
         "*": {
           "enabled": true
         }
       }
     }
   }' "$CONFIG_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$CONFIG_FILE"
print_success "已添加飞书账户到 channels.feishu.accounts"

# 4.3 添加 binding
echo "添加路由绑定..."
TEMP_FILE=$(mktemp)
jq --arg agentId "$AGENT_ID" \
   --arg accountId "$AGENT_ID" \
   '.bindings += [{
     "agentId": $agentId,
     "match": {
       "channel": "feishu",
       "accountId": $accountId
     }
   }]' "$CONFIG_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$CONFIG_FILE"
print_success "已添加路由绑定到 bindings"

# 4.4 更新 agentToAgent.allow
echo "更新 agentToAgent 允许列表..."
TEMP_FILE=$(mktemp)
jq --arg id "$AGENT_ID" \
   '.tools.agentToAgent.allow += [$id]' "$CONFIG_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$CONFIG_FILE"
print_success "已更新 agentToAgent 允许列表"

echo ""
print_success "openclaw.json 配置完成"
echo ""

# 步骤 5：重启 Gateway
print_step "5/5" "重启 Gateway"

echo "正在重启 Gateway..."
cd /home/gem/workspace/agent
sh scripts/restart.sh > /dev/null 2>&1 &
print_success "Gateway 重启中..."

echo ""
echo "等待 10-15 秒让 Gateway 完全启动..."
sleep 15

echo ""
echo "验证 Gateway 状态..."
if openclaw gateway status 2>/dev/null | grep -q "running"; then
  print_success "Gateway 运行正常"
else
  print_warning "Gateway 状态检查失败，请手动执行 'openclaw gateway status' 确认"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 子 Agent 创建完成！${NC}"
echo "=========================================="
echo ""
echo "工作空间路径：$AGENT_DIR/workspace"
echo ""
echo "后续步骤："
echo "1. 在飞书开放平台配置事件订阅（长连接）"
echo "   - 确保 Gateway 已启动"
echo "   - 添加事件：im.message.receive_v1"
echo ""
echo "2. 测试新机器人"
echo "   - 在飞书中搜索「$AGENT_NAME」"
echo "   - 发送一条测试消息"
echo "   - 检查是否收到回复"
echo ""
echo "3. 完善人设文件"
echo "   - 编辑 IDENTITY.md 添加外观、性格等描述"
echo "   - 根据需要调整 AGENTS.md"
echo ""
print_success "所有配置已自动完成，无需手动编辑文件！"
echo ""
