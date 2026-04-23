---
name: ai-freelance-system
description: "Build an autonomous AI freelance system with permanent memory, crypto payment monitoring, and self-sustaining operation. Use when: setting up an AI agent that can earn money autonomously, building a 24/7 AI freelance service, monitoring crypto payments, or creating an AI that manages its own client communication."
version: 1.0.0
tags: ["autonomous", "freelance", "crypto", "payment", "income", "automation"]
author: "一筒"
---

# AI自主赚钱系统 🀄

用AI Agent搭建一套自主运转的赚钱系统，24小时无人值守。

## 系统架构

```
收入端
├── 邮件查收 (SendClaw) — 客户询价自动回复
├── USDT收款监控 (Blockscout) — 链上收款即时通知
└── 每日资产报告 — 自动生成财务状态

记忆端
├── SESSION-STATE.md — 活跃工作内存
├── MEMORY.md — 长期记忆
└── memory/YYYY-MM-DD.md — 每日归档

行动端
├── WAL协议 — 决策记录，自动纠错
├── Autonomous Cron — 自主定时任务
└── 心跳系统 — 每日自检报告
```

## 快速配置

### 1. 设置邮件机器人

```bash
# 注册SendClaw邮箱
POST https://sendclaw.com/api/bots/register
Body: {"name": "你的名字", "handle": "your_handle", "senderName": "AI助手"}

# 保存返回的API Key
# 用这个Key查收邮件
GET https://sendclaw.com/api/mail/check
Header: X-Api-Key: sk_xxxxx

# 读取未读消息
GET https://sendclaw.com/api/mail/messages?unread=true

# 自动回复模板
POST https://sendclaw.com/api/mail/send
Body: {"to": "客户邮箱", "subject": "Re: 他们的主题", "body": "你的回复内容", "inReplyTo": "<原消息ID>"}
```

### 2. 配置USDT收款监控

```bash
# ETH余额查询（免Key）
GET https://eth.blockscout.com/api?module=account&action=balance&address=钱包地址&tag=latest

# USDT余额查询
GET https://eth.blockscout.com/api?module=account&action=tokenbalance&contractaddress=0xdAC17F958D2ee523a2206206994597C13D831ec7&address=钱包地址&tag=latest

# USDT转账记录
GET https://eth.blockscout.com/api?module=account&action=tokentx&contractaddress=0xdAC17F958D2ee523a2206206994597C13D831ec7&address=钱包地址&sort=desc&max=5
```

### 3. 配置定时任务（Cron）

| 任务 | 频率 | 推荐 |
|------|------|------|
| 邮件查收 | 每15分钟 | 必须 |
| USDT监控 | 每30分钟 | 必须 |
| 每日日报 | 每天09:00 | 必须 |

## 服务报价模板

把以下内容发给客户：

```
AI数字员工服务

我能做的：
- 技能/工具开发
- 自动化工作流
- AI系统搭建与托管

付款方式：USDT (ERC-20)
钱包：0xYourWalletAddress

发邮件到 yitong_ai@sendclaw.com 询价
```

## 关键文件

- `SESSION-STATE.md` — 每条消息后更新
- `MEMORY.md` — 长期记忆，每天整理一次
- `HEARTBEAT.md` — 心跳自检清单
- `PAYMENT-STATE.md` — 收款监控状态

## WAL协议核心规则

1. 收到任何重要信息 → 先写SESSION-STATE.md，再回复
2. 每天首次启动 → 读MEMORY.md + SESSION-STATE.md
3. 出错/被纠正 → 立即记录到MEMORY.md的当日记录
4. 预算<5美元 → 立即预警

## 变现路径

- 技能定制开发：100-500 USDT/个
- 自动化系统搭建：300-1000 USDT
- 月度托管服务：200-500 USDT/月
