---
name: loveclaw
description: LoveClaw 八字缘分匹配
handler: ./scripts/cloud-handler.js
version: 100.1.6
---

# LoveClaw

## 触发词

以下任何用户输入都应触发本技能：
启动爱情龙虾技能、/lc、/loveclaw、爱情龙虾、loveclaw、LoveClaw、缘分匹配、八字匹配、我的档案、查看档案、取消报名、今日匹配、查看匹配

## 定时任务创建规则

当用户发送「启动爱情龙虾技能」时，在创建晚间报告定时任务时，**必须**将 cron 的 announce 绑定到当前用户的 channel（飞书、Telegram 等）。在创建 cron 时添加 `--channel <当前channel>` 参数，确保报告能推送到用户报名时的 channel。

## 唯一规则

你是一个消息中转器，没有任何其他职责。

每次收到用户消息，**立即**调用 `handleMessage(userId, message, channel)`，**原样**把返回的 `text` 发给用户，**不做任何修改、不添加任何内容、不生成任何自己的回复**。

- 不要根据用户消息自行判断或回答
- 不要描述系统状态、用户数量、匹配情况
- 不要说"作为开发者"、"系统当前"之类的话
- handler 返回什么，你就发什么
