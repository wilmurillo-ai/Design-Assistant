#!/bin/bash
# 交互式子 Agent 创建向导（增强版）
# 每一步都提供详细的信息获取指引
# 用法：./interactive-wizard.sh

set -e

echo "🤖 飞书子 Agent 创建向导"
echo "=========================================="
echo ""
echo "这个向导会一步步带你创建一个新的子 Agent，并绑定到飞书机器人。"
echo "每一步我都会告诉你如何获取所需信息，即使是从未接触过的新手也能完成。"
echo ""
read -p "按回车开始..."
echo ""

# 步骤 1：收集角色信息
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 1/6: 收集角色信息"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "【角色名称】"
echo "这是什么：这个 Agent 在飞书中显示的名字"
echo "如何确定：想一个符合角色定位的名字"
echo "示例：客服助手、技术专家、销售专员"
echo ""
read -p "请输入角色名称：" ROLE_NAME
echo "✅ 已记录：$ROLE_NAME"
echo ""

echo "【Agent ID】"
echo "这是什么：系统内部用来标识这个 Agent 的唯一代号"
echo "如何确定：用角色名称的英文或拼音，全部小写，单词间用短横线连接"
echo "格式要求：只能包含小写字母 (a-z)、数字 (0-9)、短横线 (-)"
echo "示例："
echo "  - 客服助手 → customer-service"
echo "  - 技术专家 → tech-expert"
echo "  - 销售专员 → sales-bot"
echo ""
read -p "请输入 Agent ID：" AGENT_ID
if [[ ! "$AGENT_ID" =~ ^[a-z0-9-]+$ ]]; then
  echo "❌ Agent ID 格式错误，只能包含小写字母、数字和短横线"
  exit 1
fi
echo "✅ 已记录：$AGENT_ID"
echo ""

echo "【角色定位】"
echo "这是什么：这个 Agent 主要负责什么任务"
echo "如何确定：用一句话描述它的核心职责"
echo "示例：回答客户咨询问题、处理技术支持请求、协助销售流程"
echo ""
read -p "请输入角色定位：" ROLE_DESCRIPTION
echo "✅ 已记录：$ROLE_DESCRIPTION"
echo ""

echo "【性格特点】"
echo "这是什么：这个 Agent 的说话风格和语气"
echo "如何确定：想 2-4 个形容词描述它的个性"
echo "示例：专业严谨但耐心、活泼开朗爱开玩笑、简洁直接高效率"
echo ""
read -p "请输入性格特点：" PERSONALITY
echo "✅ 已记录：$PERSONALITY"
echo ""

echo "【Emoji】"
echo "这是什么：代表这个角色的表情符号"
echo "如何确定：选一个符合角色气质的 emoji"
echo "示例：客服→💁、技术→🔧、销售→💼、通用→🤖"
echo ""
read -p "请输入 Emoji（直接回车使用默认🤖）：" EMOJI
if [[ -z "$EMOJI" ]]; then
  EMOJI="🤖"
fi
echo "✅ 已记录：$EMOJI"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 角色信息收集完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "汇总："
echo "  角色名称：$ROLE_NAME"
echo "  Agent ID: $AGENT_ID"
echo "  角色定位：$ROLE_DESCRIPTION"
echo "  性格特点：$PERSONALITY"
echo "  Emoji: $EMOJI"
echo ""
read -p "按回车继续..."
echo ""

# 步骤 2：飞书应用创建指引
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 2/6: 创建飞书应用"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "接下来需要在飞书开放平台创建一个应用。"
echo "我会一步步告诉你怎么操作，即使从未接触过也能完成。"
echo ""
read -p "按回车查看步骤 1..."
echo ""

echo "【步骤 1】访问飞书开放平台"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 在浏览器中打开：https://open.feishu.cn/app"
echo "2. 用你的飞书账号登录"
echo ""
echo "💡 提示：需要使用企业管理员账号或有应用创建权限的账号"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "【步骤 2】创建企业自建应用"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 点击页面右上角的「创建应用」按钮"
echo "2. 在弹出的窗口中选择「企业自建应用」"
echo "3. 填写应用名称：建议填写「$ROLE_NAME 助手」"
echo "4. 填写应用描述（可选）：简单描述这个应用的用途"
echo "5. 选择一个应用图标：可以上传角色头像或选择一个默认图标"
echo "6. 点击「确定」完成创建"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "【步骤 3】复制 App ID 和 App Secret"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 创建应用后，自动进入应用管理页面"
echo "2. 在左侧菜单点击「凭证与基础信息」"
echo "3. 页面会显示 App ID 和 App Secret"
echo "4. 复制 App ID（格式如：cli_a9420019bb78dbcd）"
echo "5. 点击 App Secret 右侧的「查看」按钮"
echo "6. 复制 App Secret（一串字母数字组合）"
echo ""
echo "⚠️ 重要：App Secret 只显示一次，请务必妥善保存！如丢失需重新生成"
echo ""
read -p "请输入飞书应用的 App ID（cli_xxx 格式）：" FEISHU_APP_ID
if [[ ! "$FEISHU_APP_ID" =~ ^cli_[a-z0-9]+$ ]]; then
  echo "❌ App ID 格式错误，应该是 cli_ 开头"
  exit 1
fi
echo ""
read -p "请输入飞书应用的 App Secret：" FEISHU_APP_SECRET
if [[ -z "$FEISHU_APP_SECRET" ]]; then
  echo "❌ App Secret 不能为空"
  exit 1
fi
echo "✅ 已记录飞书应用信息"
echo ""
read -p "按回车继续..."
echo ""

echo "【步骤 4】配置权限"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 在左侧菜单点击「权限管理」"
echo "2. 找到「权限配置」区域"
echo "3. 点击「批量导入」按钮"
echo "4. 在弹出的文本框中粘贴以下 JSON："
echo ""
echo '```json'
cat << 'PERMISSIONS'
{
  "scopes": {
    "tenant": [
      "im:message",
      "im:message:send_as_bot",
      "im:message:readonly",
      "im:chat.members:bot_access",
      "contact:user.employee_id:readonly"
    ],
    "user": ["im:chat.access_event.bot_p2p_chat:read"]
  }
}
PERMISSIONS
echo '```'
echo ""
echo "5. 点击「确定」完成导入"
echo "6. 确认权限列表中出现了刚才导入的权限"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "【步骤 5】启用机器人能力"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 在左侧菜单点击「应用功能」"
echo "2. 点击「机器人」进入配置页面"
echo "3. 打开「启用机器人」开关"
echo "4. 设置机器人名称：填写「$ROLE_NAME」"
echo "5. （可选）上传机器人头像"
echo "6. 点击「保存」"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "【步骤 6】配置事件订阅（关键步骤）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️ 前置条件：必须先启动 OpenClaw Gateway，否则长连接无法配置"
echo ""
echo "检查 Gateway 是否运行："
echo "  openclaw gateway status"
echo ""
echo "如果未运行，先执行："
echo "  sh scripts/restart.sh"
echo ""
read -p "确认 Gateway 已运行后，按回车继续..."
echo ""
echo "1. 在左侧菜单点击「事件订阅」"
echo "2. 找到「事件接收配置」"
echo "3. 选择「使用长连接接收事件」（不要选 webhook）"
echo "4. 点击「添加事件」按钮"
echo "5. 在搜索框中输入 im.message"
echo "6. 选择 im.message.receive_v1 事件"
echo "7. 点击「确定」保存"
echo ""
echo "💡 如果提示「验证失败」，请检查 Gateway 是否正常运行"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "【步骤 7】发布应用"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 在左侧菜单点击「版本管理与发布」"
echo "2. 点击「创建版本」按钮"
echo "3. 填写版本号：如 1.0.0"
echo "4. 填写版本说明：如「初始版本」"
echo "5. 点击「提交审核」"
echo "6. 企业自建应用通常自动审核通过，等待几秒即可"
echo "7. 审核通过后，点击「发布」按钮"
echo ""
read -p "完成后按回车继续..."
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 飞书应用创建完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 步骤 3：创建目录结构
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 3/6: 创建 Agent 目录结构"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

WORKSPACE_BASE="/home/gem/workspace/agent/agents"
AGENT_DIR="$WORKSPACE_BASE/$AGENT_ID"

echo "正在创建目录..."
echo "  $AGENT_DIR"
mkdir -p "$AGENT_DIR/agent"
mkdir -p "$AGENT_DIR/workspace/memory"
mkdir -p "$AGENT_DIR/sessions"

echo "✅ 目录创建完成"
echo ""
read -p "按回车继续..."
echo ""

# 步骤 4：生成人设文件
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 4/6: 生成人设文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# SOUL.md
cat > "$AGENT_DIR/workspace/SOUL.md" << 'SOUL_EOF'
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
SOUL_EOF
echo "✓ SOUL.md - 核心人格模板"

# IDENTITY.md
cat > "$AGENT_DIR/workspace/IDENTITY.md" << IDENTITY_EOF
# IDENTITY.md - Who Am I?

- **Name:** $ROLE_NAME
- **Role:** $ROLE_DESCRIPTION
- **Vibe:** $PERSONALITY
- **Emoji:** $EMOJI
- **Avatar:** （待设置）

---

## 外观
（待填写 - 可以描述这个角色的虚拟形象）

## 性格
$PERSONALITY

## 说话风格
（待填写 - 如"专业严谨"、"轻松幽默"、"简洁直接"）

## 专长
$ROLE_DESCRIPTION

---

_这个身份是和主人一起定义的。_
IDENTITY_EOF
echo "✓ IDENTITY.md - 身份设定（已根据你的输入生成）"

# AGENTS.md
cat > "$AGENT_DIR/workspace/AGENTS.md" << 'AGENTS_EOF'
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
AGENTS_EOF
echo "✓ AGENTS.md - 工作指南"

# USER.md
cat > "$AGENT_DIR/workspace/USER.md" << 'USER_EOF'
# USER.md - 关于你的人类

认识你所帮助的人。在对话中逐步补全。

- **称呼：** （待填写）
- **飞书 Open ID：** （待填写）

## 慢慢了解的事

（在对话中自然地积累）

---

知人方能善助。
USER_EOF
echo "✓ USER.md - 用户信息"

touch "$AGENT_DIR/workspace/memory/.gitkeep"
echo "✓ memory/.gitkeep"

echo ""
echo "✅ 人设文件生成完成"
echo ""
read -p "按回车继续..."
echo ""

# 步骤 5：配置指引
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 5/6: 配置 openclaw.json"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "接下来需要修改主配置文件。我会提供可直接复制的配置片段。"
echo ""
echo "📁 文件位置：/home/gem/workspace/agent/openclaw.json"
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
  "name": "$ROLE_NAME",
  "workspace": "$AGENT_DIR/workspace",
  "agentDir": "$AGENT_DIR/agent",
  "model": "miaoda/glm-5"
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
  "name": "$ROLE_NAME",
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

# 步骤 6：重启和测试
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 6/6: 重启 Gateway 并测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "【1】备份当前配置"
echo "----------------------------------------"
echo "✅ 修改前已自动备份 openclaw.json"
echo ""

echo "【2】重启 Gateway"
echo "----------------------------------------"
echo "执行命令："
echo ""
echo "  sh scripts/restart.sh"
echo ""
read -p "执行完成后按回车继续..."
echo ""

echo "【3】验证重启成功"
echo "----------------------------------------"
echo "等待 10-30 秒后，执行："
echo ""
echo "  openclaw gateway status"
echo ""
echo "如果显示运行中，说明重启成功。"
echo ""
echo "如有问题，查看日志："
echo "  openclaw logs --follow"
echo ""
read -p "按回车继续..."
echo ""

echo "【4】在飞书开放平台配置事件订阅"
echo "----------------------------------------"
echo "⚠️ 确保 Gateway 已启动后："
echo "1. 回到飞书开放平台的事件订阅页面"
echo "2. 确认已添加事件：im.message.receive_v1"
echo "3. 如果之前验证失败，现在应该可以保存了"
echo ""
read -p "按回车继续..."
echo ""

echo "【5】测试新机器人"
echo "----------------------------------------"
echo "1. 打开飞书"
echo "2. 在搜索框中搜索：$ROLE_NAME"
echo "3. 点击进入对话"
echo "4. 发送一条测试消息，如「你好」"
echo "5. 检查是否收到回复"
echo ""
echo "✅ 如果收到回复，说明配置成功！"
echo ""
read -p "按回车继续..."
echo ""

echo "【6】验证会话隔离（可选）"
echo "----------------------------------------"
echo "1. 用新机器人发送消息"
echo "2. 切换到其他机器人（如机车兔）"
echo "3. 询问刚才和新机器人聊的内容"
echo "4. 如果其他机器人不知道，说明会话隔离正常"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 子 Agent 创建完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "工作空间路径：$AGENT_DIR/workspace"
echo ""
echo "后续优化建议："
echo "1. 完善 IDENTITY.md 中的外观、说话风格等描述"
echo "2. 根据实际任务需求，在 AGENTS.md 中添加特殊指引"
echo "3. 在 USER.md 中记录用户信息"
echo "4. 开始和这个新角色对话，建立记忆"
echo ""
echo "📚 完整文档：/home/gem/workspace/agent/skills/feishu-subagent-creator/SKILL.md"
echo ""
