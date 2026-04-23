# HTTP 契约（生产版 v2 建议）

## 新增目标

在原有 Telegram -> moderation core 契约上，增加 trace_id 和更稳定的日志串联能力。

## 请求建议

```json
{
  "platform": "telegram",
  "scene": "group_message",
  "id": 345,
  "trace_id": "tg-345-20260320014100",
  "title": "",
  "content": "加V了解一下",
  "imgs": [],
  "videos": [],
  "other": {
    "chat_id": -1001234567890,
    "message_id": 345,
    "user_id": 777,
    "username": "spam_user"
  }
}
```

## 响应建议

```json
{
  "id": 345,
  "trace_id": "tg-345-20260320014100",
  "audit_status": "reject",
  "is_pass": 0,
  "risk_level": "high",
  "reason": "存在联系方式和明显引流话术",
  "hit_rules": ["contact_info", "advertising"],
  "action": "reject"
}
```

## 原则

- Telegram 接入层负责生成 trace_id
- 审核核心应尽量原样回传 trace_id
- 所有审计日志、review 记录、动作结果都使用同一个 trace_id
