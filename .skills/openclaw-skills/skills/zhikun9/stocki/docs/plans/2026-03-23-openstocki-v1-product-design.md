# OpenStocki 1.0 产品设计文档

## 1. 产品定位

**OpenStocki** 是面向个人投资者的 AI 金融分析助手，通过微信生态触达用户。用户在微信内通过 ClawBot（OpenClaw agent）提问，OpenStocki 调用 Stocki 分析引擎给出回答。

**产品关系**：
- **Stocki**：底层金融分析引擎（2C 产品，有自己的 Web 前端），提供专业金融数据和 AI 分析能力
- **OpenStocki**：基于 Stocki 引擎的 OpenClaw skill，让用户通过微信内的 ClawBot 使用 Stocki 的金融分析能力，并提供用户管理、额度计量、分享裂变等运营功能

**1.0 目标**：完成从 PoC 到可运营产品的转变——加入用户体系、用量管控和增长机制，跑通「注册 → 使用 → 分享 → 拉新」闭环。

## 2. 用户旅程

```
User sees friend's OpenStocki answer (WeChat chat / Moments)
  -> Click short link -> H5 share page -> see analysis content
  -> CTA at bottom: "Follow ClawBot to use OpenStocki analyst for free"
  -> Follow ClawBot, send financial question in chat
  -> ClawBot -> open-stocki skill -> Gateway auth -> Stocki engine -> reply
  -> Answer footer includes share short link
  -> User forwards to friends -> loop
```

## 3. 产品形态

| 端 | 形态 | 用途 |
|---|---|---|
| OpenClaw (ClawBot) | 微信内对话 | 主要使用入口，用户提问获得金融分析 |
| H5 网页 | 微信内浏览器打开 | 注册/登录、查看用量、管理 API Key、邀请码页、分享页 |
| 微信小程序 | 后续迁移 | 1.0 不做，H5 验证流程后再考虑 |

## 4. 系统架构

```
+------------------+    +----------------------------------+    +----------------------+
|  ClawBot/OpenClaw|    | OpenStocki Gateway (FastAPI)     |    | open-stocki-internal |
|  (WeChat)        |--->|                                  |--->| LangGraph agents     |
+------------------+    | Auth -> Quota -> LangGraph call  |    | (instant + quant)    |
                        |                                  |    +----------+-----------+
+------------------+    | /auth/*   WeChat OAuth + phone   |               |
|  H5 Frontend     |--->| /v1/*     instant + quant + task |               v
|  (WeChat browser)|    | /user/*   Usage, invite, keys    |    +----------------------+
+------------------+    | /share/*  Share page render      |    | Tencent Cloud COS    |
                        |                                  |    | /threads/{thread_id}/ |
                        |         PostgreSQL               |--->| status.json, reports |
                        +----------------------------------+    +----------------------+
```

**核心原则**：
- OpenStocki Gateway 是唯一入口，所有客户端通过它访问 open-stocki-internal（LangGraph agents）
- OpenClaw skill 通过 API Key 鉴权；H5 通过微信 OAuth + session token 鉴权
- Instant 调用：鉴权 → 检查额度 → 扣减额度 → 调用 LangGraph instant agent → 返回
- Quant 调用：鉴权 → 检查额度 → 创建 task → 调用 LangGraph quant agent（异步）→ 结果写入 COS
- Gateway 和 LangGraph agents 共享 COS 存储（按 thread_id 组织工作目录）

**技术栈**：
- 后端：Python FastAPI
- 数据库：PostgreSQL
- 部署：自有服务器

## 5. 账户体系

### 5.1 注册与登录

- **主要方式**：微信 OAuth 授权登录（获取 openid）
- **补充方式**：手机号绑定（后续可选）
- **流程**：H5 页面发起微信 OAuth → 获取 openid → 自动创建账户 → 生成邀请码和首个 API Key

### 5.2 API Key

- 用户在 H5 管理页创建/吊销 API Key
- Key 格式：`sk_` 前缀 + 随机字符串，如 `sk_abc123def456...`
- 存储：仅存 SHA-256 hash，明文只在创建时展示一次
- OpenClaw skill 通过 API Key 鉴权调用 Gateway

### 5.3 新用户引导

微信 OAuth 注册后自动完成：
1. 创建账户（openid、昵称、头像）
2. 生成唯一邀请码（6-8位字母数字）
3. 生成首个 API Key
4. 展示一键复制文案，用户复制后发送给 ClawBot 即可完成配置

**一键复制文案示例**：

```
请帮我安装 open-stocki 金融分析工具，并设置我的 API Key：

1. 安装：npx clawhub install open-stocki --force
2. 设置环境变量：STOCKI_API_KEY=sk_abc123def456...

安装完成后，我想试一下：A股今天行情怎么样？
```

用户将此文案发送给 ClawBot，ClawBot（OpenClaw agent）即可自动完成 skill 安装和 API Key 配置。

## 6. 额度机制

### 6.1 Instant 模式（1.0 支持）

| 项目 | 规则 |
|---|---|
| 基础额度 | 5 次/天，每日零点（北京时间）重置 |
| 邀请奖励 | 每成功邀请 1 人，每日额度永久 +3 次 |
| 额度上限 | 暂不设上限 |
| 超额处理 | 返回友好提示 + 分享引导文案 |

**超额响应示例**：
> 今日免费查询次数已用完。分享 OpenStocki 给朋友，每邀请 1 位新用户可永久增加 3 次/天额度：https://stocki.com.cn/r/YOUR_CODE

### 6.2 Quant 模式（1.0 预留）

- 按 LLM token 消耗计量
- 1.0 不开放，仅在数据模型和 API 中预留字段
- 后端记录每次 instant 调用的实际 token 消耗，用于成本分析

## 7. 分享裂变

### 7.1 机制

```
User asks question -> OpenStocki answers -> footer auto-appends share short link
  -> Friend clicks link -> H5 share page (analysis + signup CTA)
  -> New user registers via ClawBot -> invite code bound
  -> Both sides get quota reward
```

### 7.2 分享内容

每次 instant 回答末尾自动附加一行：

```
--
Analysis by OpenStocki | Try free: https://stocki.com.cn/r/{invite_code}
```

### 7.3 分享页（H5）

短链接 `https://stocki.com.cn/r/{invite_code}` 打开后展示：
- OpenStocki 品牌介绍（简短）
- 注册引导：关注 ClawBot 公众号
- 邀请码自动填充

### 7.4 邀请奖励

| 角色 | 奖励 |
|---|---|
| 邀请人 | 每日额度永久 +3 次 |
| 被邀请人 | 获得基础 5 次/天额度（与普通注册相同） |

邀请关系不可更改，一个用户只能被邀请一次。

## 8. API 设计

### 8.1 鉴权 API（/auth）

| 接口 | 方法 | 说明 |
|---|---|---|
| `/auth/wechat` | GET | 发起微信 OAuth，重定向到微信授权页 |
| `/auth/wechat/callback` | GET | 微信回调，换取 openid，创建/登录账户，返回 session token |
| `/auth/token/refresh` | POST | 刷新 session token |

### 8.2 业务 API（/v1）

| 接口 | 方法 | 鉴权 | 说明 |
|---|---|---|---|
| `/v1/instant` | POST | API Key | 提交 instant 查询，扣减额度，调用 LangGraph instant agent，返回回答 |
| `/v1/quant` | POST | API Key | 提交 quant 分析（异步），创建 task，调用 LangGraph quant agent |
| `/v1/tasks` | GET | API Key | 列出用户的 quant 任务 |
| `/v1/tasks/{task_id}` | GET | API Key | 查询任务状态（读取 COS status.json）+ 结果文件列表 |
| `/v1/tasks/{task_id}/files/{path}` | GET | API Key | 下载任务结果文件（从 COS 代理） |

**请求**：
```json
{
  "question": "A股半导体行业前景?",
  "timezone": "Asia/Shanghai"
}
```

**响应**：
```json
{
  "answer": "...(格式化后的回答)...",
  "share_url": "https://stocki.com.cn/s/abc123",
  "usage": {
    "used_today": 3,
    "daily_quota": 5
  }
}
```

### 8.3 用户 API（/user）

| 接口 | 方法 | 鉴权 | 说明 |
|---|---|---|---|
| `/user/me` | GET | Session | 当前用户信息、额度、邀请码 |
| `/user/usage` | GET | Session | 用量统计（今日、历史） |
| `/user/api-keys` | GET/POST/DELETE | Session | 管理 API Key |
| `/user/invitations` | GET | Session | 邀请记录列表 |

### 8.4 分享 API（/share）

| 接口 | 方法 | 鉴权 | 说明 |
|---|---|---|---|
| `/share/{id}` | GET | 无 | 渲染分享页（SSR HTML） |
| `/share/create` | POST | API Key | 创建分享内容（Gateway 调用时自动创建） |

## 9. OpenClaw Skill 改动

### 9.1 变更点

PoC 版 `stocki-instant.py` 直连 Stocki 引擎。1.0 改为：

```
stocki-instant.py -> OpenStocki Gateway /v1/instant (API Key auth) -> Stocki Engine
```

### 9.2 Skill 环境变量

| 变量 | 说明 |
|---|---|
| `STOCKI_API_KEY` | 用户的 API Key（在 H5 管理页生成） |
| `STOCKI_GATEWAY_URL` | Gateway 地址（默认 `https://api.stocki.com.cn`） |

### 9.3 回答格式

Script 输出格式不变（WeChat 友好格式），Gateway 在返回时自动附加分享链接。Skill 的 SKILL.md 要求 OpenClaw agent：
1. 展示 OpenStocki 回答（保持原有 post-processing 规则）
2. 展示分享链接（回答末尾）
3. 额度不足时展示引导文案

## 10. H5 页面

### 10.1 页面列表

| 页面 | 路径 | 说明 |
|---|---|---|
| 登录页 | `/login` | 微信 OAuth 一键登录 |
| 首页/仪表盘 | `/dashboard` | 今日用量、剩余额度、快速入口 |
| 邀请页 | `/invite` | 展示邀请码、分享按钮、邀请记录 |
| API Key 管理 | `/keys` | 创建/查看/吊销 Key |
| 分享页 | `/s/{id}` | 公开页面，展示分析内容 + 注册引导 |
| 邀请落地页 | `/r/{invite_code}` | 公开页面，品牌介绍 + 注册引导 |

### 10.2 技术方案

- 轻量 H5 SPA（Vue 或纯 HTML + Tailwind）
- 微信 JS-SDK 集成（OAuth、分享能力）
- Gateway 提供 SSR 分享页（SEO + 微信卡片预览）

## 11. 数据模型

```
users           (openid, phone, nickname, avatar, invite_code, invited_by, daily_quota)
api_keys        (user_id, key_hash, key_prefix, name, is_active)
usage_log       (user_id, mode, query_text, response_id, token_count)
daily_usage     (user_id, date, used_count) -- fast quota lookup
invitations     (inviter_id, invitee_id, rewarded)
shared_answers  (short_id, user_id, query, answer, view_count)
```

## 12. 1.0 范围与排除

### 1.0 包含

- [x] API Gateway（FastAPI）：鉴权、额度、代理、用量记录
- [x] 微信 OAuth 登录 + 账户创建
- [x] API Key 生成与管理
- [x] Instant 模式额度（5次/天 + 邀请奖励）
- [x] 分享链接自动生成 + H5 分享页
- [x] 邀请码机制 + 额度奖励
- [x] H5 管理页（仪表盘、邀请、Key 管理）
- [x] OpenClaw skill 对接 Gateway
- [x] PostgreSQL 数据存储

### 1.0 不包含

- [ ] H5 端直接提问（聊天界面）
- [ ] Quant 模式开放（仅预留数据结构）
- [ ] 微信小程序
- [ ] 付费机制
- [ ] 手机号登录（仅微信 OAuth）
- [ ] 多语言支持

## 13. 成功指标

| 指标 | 目标 |
|---|---|
| 注册用户数 | 验证注册流程跑通 |
| 日活跃查询数 | 观察真实使用频率 |
| 分享转化率 | 分享链接点击 → 注册的比例 |
| 邀请率 | 有多少用户主动分享 |
| 额度消耗分布 | 大部分用户是否够用 |
