# feishu-subagent-creator

飞书子 Agent 创建向导 Skill。**全自动配置**，无需用户手动编辑任何文件。

**特点：** 
- ✅ 所有配置自动完成
- ✅ 无需手动粘贴代码
- ✅ 无需手动编辑 JSON
- ✅ 自动备份、自动重启

## 功能特点

- ✅ 交互式引导流程
- ✅ 自动生成目录结构和人设文件
- ✅ **自动读取和修改 openclaw.json**
- ✅ **自动添加 agent、account、binding 配置**
- ✅ **自动更新 agentToAgent 允许列表**
- ✅ 自动备份配置
- ✅ 自动重启 Gateway
- ✅ 提供详细的飞书应用配置指引

## 使用方式

### 方式 1：对话引导（最简单）

直接对我说：
- "创建一个新的子 agent"
- "添加一个新的飞书机器人角色"
- "我想创建 tech-expert 这个角色"

我会：
1. 逐步引导你提供必要信息
2. 指导你在飞书开放平台创建应用
3. **自动完成所有配置**（无需你手动编辑文件）
4. 自动重启 Gateway
5. 告诉你测试方法

### 方式 2：自动配置脚本

```bash
cd /home/gem/workspace/agent/skills/feishu-subagent-creator
./scripts/auto-configure-subagent.sh \
  --agent-id "tech-expert" \
  --agent-name "技术专家" \
  --app-id "cli_xxx" \
  --app-secret "your-secret"
```

脚本会自动：
- 创建目录结构
- 生成人设文件
- 备份现有配置
- 修改 openclaw.json
- 重启 Gateway

### 方式 3：Node.js 配置工具

```bash
node scripts/update-config.js \
  --agent-id "tech-expert" \
  --agent-name "技术专家" \
  --app-id "cli_xxx" \
  --app-secret "your-secret"
```

然后重启 Gateway：
```bash
sh scripts/restart.sh
```

## 目录结构

```
feishu-subagent-creator/
├── SKILL.md                          # 技能说明
├── README.md                         # 本文件
├── references/                       # 模板文件
│   ├── SOUL-template.md
│   ├── IDENTITY-template.md
│   ├── AGENTS-template.md
│   └── USER-template.md
└── scripts/
    ├── auto-configure-subagent.sh    # 全自动配置脚本
    ├── update-config.js              # Node.js 配置工具
    ├── configure-subagent.sh         # 命令行配置脚本
    └── interactive-wizard.sh         # 交互式引导脚本
```

## 自动化流程

```
┌─────────────────────────────────────────────────────────┐
│ 步骤 1: 收集角色信息                                      │
│ - 角色名称、Agent ID、定位、性格                          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 2: 创建飞书应用（用户操作）                           │
│ - 开放平台创建应用、配置权限、启用机器人                   │
│ - 获取 App ID 和 App Secret                               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 3: 自动创建 Agent 目录                               │
│ - agents/{agent-id}/{agent,workspace,sessions}          │
│ - SOUL.md、IDENTITY.md、AGENTS.md、USER.md              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 4: 自动修改 openclaw.json                           │
│ - ✅ 自动读取现有配置                                     │
│ - ✅ 自动添加 agent 到 agents.list                        │
│ - ✅ 自动添加 account 到 channels.feishu.accounts         │
│ - ✅ 自动添加 binding 到 bindings                         │
│ - ✅ 自动更新 agentToAgent.allow                         │
│ - ✅ 自动备份原配置                                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 5: 自动重启 Gateway                                  │
│ - sh scripts/restart.sh                                 │
│ - 等待启动完成                                           │
│ - 验证运行状态                                           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 6: 测试验证                                         │
│ - 飞书发消息、检查路由、验证会话隔离                       │
└─────────────────────────────────────────────────────────┘
```

## 配置示例

### 输入参数
```bash
--agent-id "tech-expert"
--agent-name "技术专家"
--app-id "cli_a9420019bb78dbcd"
--app-secret "your-secret"
```

### 自动生成的配置

#### 1. agents.list（自动添加）
```json5
{
  "id": "tech-expert",
  "name": "技术专家",
  "workspace": "/home/gem/workspace/agent/agents/tech-expert/workspace",
  "agentDir": "/home/gem/workspace/agent/agents/tech-expert/agent",
  "model": "miaoda/glm-5"
}
```

#### 2. channels.feishu.accounts（自动添加）
```json5
{
  "tech-expert": {
    "appId": "cli_a9420019bb78dbcd",
    "appSecret": "your-secret",
    "name": "技术专家",
    "streamingCard": true,
    "groups": {
      "*": {
        "enabled": true
      }
    }
  }
}
```

#### 3. bindings（自动添加）
```json5
{
  "agentId": "tech-expert",
  "match": {
    "channel": "feishu",
    "accountId": "tech-expert"
  }
}
```

#### 4. tools.agentToAgent.allow（自动更新）
```json5
{
  "tools": {
    "agentToAgent": {
      "enabled": true,
      "allow": ["main", "pipi", "juka", "bobby", "tech-expert"]
    }
  }
}
```

## 飞书应用权限配置

批量导入以下权限：
```json
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
```

## 注意事项

### ⚠️ 需要用户手动操作的

| 任务 | 原因 |
|------|------|
| 创建飞书应用 | 需要在飞书开放平台操作 |
| 复制 App ID/Secret | 涉及安全凭证，需用户确认 |
| 配置飞书权限 | 需要在飞书开放平台操作 |
| 配置事件订阅 | 需要在飞书开放平台操作 |

### ✅ 自动完成的

| 任务 | 说明 |
|------|------|
| 创建目录结构 | 自动创建 agent、workspace、sessions 目录 |
| 生成人设文件 | 自动写入 SOUL.md、IDENTITY.md 等 |
| 读取配置 | 自动读取 openclaw.json 当前内容 |
| 修改配置 | 自动添加 agent、account、binding 配置 |
| 备份配置 | 修改前自动备份 |
| 重启 Gateway | 自动执行重启命令 |
| 验证状态 | 自动检查 Gateway 运行状态 |

### ✅ 最佳实践
- Agent ID 使用小写字母 + 短横线
- 每个 Agent 独立工作空间
- 确保人设差异化
- 设置 `dmScope: "per-channel-peer"`

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 长连接配置失败 | 先启动 Gateway 再配置事件订阅 |
| 消息路由错误 | 检查 bindings 中 accountId 是否匹配 |
| 会话混淆 | 设置 dmScope: "per-channel-peer" |
| 权限不足 | 确保应用已发布且权限完整 |
| 机器人不回复 | 检查事件订阅是否配置了 `im.message.receive_v1` |
| App Secret 找不到 | 在「凭证与基础信息」页面重新生成 |
| 配置修改失败 | 检查是否有 jq 或 Node.js 环境 |

## 环境要求

### 自动配置脚本需要：
- `jq` - JSON 处理工具
- `bash` - Shell 环境

安装 jq：
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

### Node.js 工具需要：
- Node.js v14+

## 帮助

查看脚本帮助：
```bash
./scripts/auto-configure-subagent.sh --help
```

## 相关文档

- [OpenClaw 飞书频道文档](/channels/feishu)
- [多 Agent 路由配置](/channels/channel-routing)
- [Agent 工作空间指南](/agents/workspace)
