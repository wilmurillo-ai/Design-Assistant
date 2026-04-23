---
name: workshub-mcp
description: >
  让 AI Agent 能够雇佣真人工作者完成现实任务。
  支持：浏览和搜索工作者、发布悬赏任务、与工作者对话沟通、支付并完成任务。
  已实现 17 个工具，覆盖认证管理、技能查询、工作者管理、悬赏任务、对话管理 5 大功能模块。
  首次使用可通过手机号验证码获取 API Key，无需预先配置。
version: 1.0.2
metadata:
  openclaw:
    requires:
      env: []
      bins:
        - node
        - npx
    optional:
      env:
        - WORKSHUB_API_KEY
        - WORKSHUB_API_URL
    primaryEnv: WORKSHUB_API_KEY
    homepage: https://www.npmjs.com/package/workshub-mcp
---

# WorksHub MCP Skill

## 安全检查（首次使用必做）

执行以下步骤验证代码来源：

1. 访问 https://www.npmjs.com/package/workshub-mcp 确认包信息
2. 确认维护者为官方账号
3. 首次使用先创建低权限测试 Key

⚠️ **警告**：API Key 可创建任务、触发支付，务必妥善保管。

---

## 快速开始

### 步骤 1：验证环境

```bash
node --version  # 需 v18+
npx --version
```

### 步骤 2：获取 API Key（二选一）

**方式 A：已有 API Key**

```bash
export WORKSHUB_API_KEY="your_api_key_here"
```

**方式 B：首次使用，通过手机号获取（无需 API Key）**

直接启动服务：

```bash
npx workshub-mcp
```

然后执行：
1. 调用 `send_code` 发送验证码到手机
2. 调用 `login` 使用验证码登录
3. 保存返回的 `api_key`，后续使用方式 A 设置

### 步骤 3：启动服务

```bash
# 方式 A：已有 Key 时
export WORKSHUB_API_KEY="your_key"
npx workshub-mcp

# 方式 B：首次获取 Key 时（无需设置环境变量）
npx workshub-mcp
```

---

## 工具调用指南

### 认证管理（无需 API Key）

> 以下工具不需要 WORKSHUB_API_KEY，用于首次获取 API Key

| 工具 | 何时调用 | 参数 |
|------|----------|------|
| send_code | 用户首次使用，需要获取 API Key 时 | phone_number |
| login | 已发送验证码，需要登录获取 Key 时 | phone_number, code |

### 技能查询（需要 API Key）

| 工具 | 何时调用 | 参数 |
|------|----------|------|
| get_skills | 用户想找某类服务/技能时 | keyword (可选), category (可选) |

### 工作者管理（需要 API Key）

| 工具 | 何时调用 | 参数 |
|------|----------|------|
| get_workers | 用户说"找人"、"找开发者"、"找设计师"等 | skills (可选数组), page, limit |
| get_worker_detail | 需要查看某人详细资料、评价、作品时 | worker_id |
| get_worker_qrcode | 需要给某人付款、查看收款方式时 | worker_id |

### 悬赏任务管理（需要 API Key）

| 工具 | 何时调用 | 参数 | 风险 |
|------|----------|------|------|
| get_bounties | 用户说"查看我的任务"、"看看有哪些悬赏" | status (可选), page | ✅ 安全 |
| get_bounty_detail | 需要查看某个任务的具体详情时 | bounty_id | ✅ 安全 |
| create_bounty | 用户说"发布任务"、"我要悬赏"、"找人做XX" | title, description, budget, skills (数组) | 🚨 付费 |
| cancel_bounty | 用户说"取消任务"、"不做了" | bounty_id | 🚨 不可逆 |
| get_bounty_applications | 用户说"查看申请"、"谁报名了" | bounty_id | ✅ 安全 |
| accept_bounty_application | 用户说"接受申请"、"选这个人"、"雇佣TA" | application_id | 🚨 不可逆，拒绝其他 |

### 对话管理（需要 API Key）

| 工具 | 何时调用 | 参数 | 风险 |
|------|----------|------|------|
| get_conversations | 用户说"查看消息"、"我的对话" | page (可选) | ✅ 安全 |
| start_conversation | 用户说"联系TA"、"发消息给TA" | worker_id | ⚠️ 通知对方 |
| get_conversation_messages | 需要查看某对话的历史记录时 | conversation_id | ✅ 安全 |
| send_message | 用户说"发送消息"、"回复"、"告诉TA" | conversation_id, content | ⚠️ 不可撤回 |

---

## 典型工作流

### 场景 1：用户说"我想找人做设计"

**判断**：用户有明确需求（设计），但未确定具体人选。

**执行**：
1. 调用 `get_skills` 搜索关键词"设计"
2. 调用 `get_workers` 筛选有设计技能的工作者（取前 5 个）
3. 向用户展示候选人列表，询问预算和具体需求
4. 如用户确认发布任务，询问：title（任务标题）, description（详细描述）, budget（预算金额）, skills（需要的技能数组）
5. 调用 `create_bounty` 创建任务
6. 告知用户任务已发布，可稍后查看申请

### 场景 2：用户说"查看我的任务申请"

**判断**：用户已有任务，想查看谁申请了。

**执行**：
1. 调用 `get_bounties` 获取用户的任务列表
2. 如只有一个任务，直接获取其 `bounty_id`；如有多个，询问用户查看哪个
3. 调用 `get_bounty_applications` 获取申请列表
4. 展示申请者信息（姓名、技能、报价等）
5. 询问用户是否查看某个申请者的详细资料
6. 如用户要求，调用 `get_worker_detail` 查看详情

### 场景 3：用户说"接受张三的申请"

**判断**：用户想雇佣特定申请者。

**执行**：
1. 确认用户指的是哪个任务的申请（询问 `bounty_id` 或从上下文获取）
2. 调用 `get_bounty_applications` 获取该任务的申请列表
3. 找到"张三"对应的 `application_id`
4. 🚨 人工确认：向用户确认："接受后系统将自动拒绝其他所有申请者，确定要继续吗？"
5. 用户确认后，调用 `accept_bounty_application`
6. 告知用户已成功雇佣，建议立即联系对方

### 场景 4：用户说"联系刚才那个开发者"

**判断**：用户想与特定工作者沟通。

**执行**：
1. 从上下文获取 `worker_id`（如刚才查看过详情或接受过申请），或询问用户具体是谁
2. 调用 `start_conversation` 开启对话，获取 `conversation_id`
3. 询问用户要说什么内容
4. 调用 `send_message` 发送消息
5. 告知用户消息已发送，对方会收到通知

### 场景 5：用户首次使用，没有 API Key

**判断**：用户说"怎么使用"、"我没有 Key"、"如何开始"。

**执行**：
1. 询问用户手机号
2. 调用 `send_code` 发送验证码
3. 询问用户收到的验证码
4. 调用 `login` 登录，获取 `api_key`
5. 告知用户："您的 API Key 是：xxx，请保存好。下次使用前先执行 `export WORKSHUB_API_KEY=xxx`"

---

## 安全操作分级

### 🚨 高风险（必须人工确认）

| 操作 | 风险说明 | 确认话术 |
|------|----------|----------|
| accept_bounty_application | 接受后自动拒绝其他所有申请，不可逆 | "接受后将拒绝其他申请者，确定吗？" |
| cancel_bounty | 取消已发布任务，可能影响已申请者 | "取消后任务将下架，确定吗？" |
| create_bounty | 创建真实付费任务，会扣款 | "创建任务将冻结预算金额，确定吗？" |

### ⚠️ 中风险（建议确认）

| 操作 | 风险说明 | 建议 |
|------|----------|------|
| send_message | 消息发送后不可撤回 | 提醒用户检查内容 |
| start_conversation | 会通知对方，可能打扰 | 确认用户确实要联系 |

### ✅ 低风险（可直接执行）

- 所有 `get_` 开头的查询操作
- `send_code`, `login`（无需 API Key）

---

## 环境变量配置

### 首次使用流程

1. **首次使用不需要配置 API Key**，直接使用本技能
2. 调用 `send_code` 输入手机号获取验证码
3. 调用 `login` 输入验证码，返回 `api_key`
4. **在 openclaw 中配置环境变量** `WORKSHUB_API_KEY`

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| WORKSHUB_API_KEY | 首次后必填 | 手机号登录后获取的 API Key |
| WORKSHUB_API_URL | 可选 | 默认 https://workshub.ai/mcp |

---

## 故障排查

| 问题 | 检查项 | 解决 |
|------|--------|------|
| 提示缺少 API Key | 是否已设置环境变量 | `echo $WORKSHUB_API_KEY` |
| 认证失败 | Key 是否有效或过期 | 重新调用 `send_code` + `login` 获取新 Key |
| 连接失败 | API URL 是否正确 | 检查 `WORKSHUB_API_URL`，默认应为 https://workshub.ai/mcp |
| 工具调用报错 | 参数格式是否正确 | 参考"工具调用指南"检查必填参数 |
| 收不到验证码 | 手机号格式是否正确 | 检查是否为 11 位手机号 |
| 无法启动服务 | Node 版本是否满足 | 需 Node.js v18+ |

---

## 文件参考

| 文件/资源 | 说明 |
|-----------|------|
| SKILL.md | 本文件，包含完整指令 |
| npm:workshub-mcp | MCP 服务器包，提供 17 个工具 |
| WORKSHUB_API_KEY | API 认证密钥，首次可通过手机号获取 |
| WORKSHUB_API_URL | 可选，默认 https://workshub.ai/mcp |

---

## 相关链接

- WorksHub 官网：https://workshub.ai
- npm 包页：https://www.npmjs.com/package/workshub-mcp
- MCP 协议文档：https://modelcontextprotocol.io
