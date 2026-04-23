# 审核日志落库说明（中文）

## 目标

给 Telegram 审核接入层补齐可追踪、可复盘、可人工复核的基础日志能力。

## 建议记录什么

建议至少记录：
- trace_id
- chat_id
- message_id
- user_id
- username
- audit_status
- risk_level
- action
- reason
- offense_count
- action_result
- created_at

## 为什么要落库

如果只删消息、不留日志，后续会遇到这些问题：
- 管理员不知道为什么删了
- 用户申诉时无法回查
- 无法分析误判率
- 无法分析哪个群、哪类规则问题最多

## action_result 建议

建议至少区分：
- `pending`
- `success`
- `failed`
- `skipped`

## review 建议

review 不应只发管理员群，最好也落库。

这样可以：
- 后台查看待复核记录
- 后续做状态流转
- 审计谁处理过哪条 review

## trace_id 建议

trace_id 用来串联：
- Telegram webhook 收到的事件
- 调用审核核心的请求
- Telegram 动作执行结果
- 审核日志记录

推荐格式：

```text
tg-<message_id>-<YYYYMMDDHHMMSS>
```
