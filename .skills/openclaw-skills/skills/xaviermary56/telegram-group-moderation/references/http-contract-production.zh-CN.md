# HTTP 契约（生产版建议）

## 目标

统一 Telegram 接入层与审核核心之间的 HTTP 请求/响应结构，避免每个项目都临时拼字段。

## 请求建议

### URL

```text
POST /moderation/telegram/message-audit
```

### Headers

```text
Content-Type: application/json
Authorization: Bearer <token>
X-Request-Id: <trace_id>
```

### Body 示例

```json
{
  "platform": "telegram",
  "scene": "group_message",
  "id": 345,
  "trace_id": "tg-345-20260320004500",
  "title": "",
  "content": "加V了解一下",
  "imgs": [],
  "videos": [],
  "other": {
    "chat_id": -1001234567890,
    "chat_type": "supergroup",
    "chat_title": "Example Group",
    "message_id": 345,
    "user_id": 777,
    "username": "spam_user",
    "display_name": "Promo Bot",
    "raw_has_photo": false,
    "raw_has_video": false,
    "forwarded": false,
    "edited": false
  }
}
```

## 响应建议

```json
{
  "id": 345,
  "trace_id": "tg-345-20260320004500",
  "audit_status": "reject",
  "is_pass": 0,
  "risk_level": "high",
  "reason": "存在联系方式和明显引流话术",
  "hit_rules": ["contact_info", "advertising"],
  "hit_fields": ["content"],
  "hit_positions": ["content"],
  "action": "reject"
}
```

## 响应字段要求

至少要求：
- `audit_status`
- `risk_level`
- `reason`

推荐补充：
- `trace_id`
- `hit_rules`
- `hit_fields`
- `hit_positions`
- `action`

## 契约原则

- Telegram 接入层不重复发明审核规则
- 审核核心只负责判断，不直接调用 Telegram API
- Telegram 接入层根据审核结果自行决定 delete / warn / mute / ban / review

## 错误处理建议

审核核心异常时，建议返回明确错误码，避免 Telegram 接入层误判为通过。

例如：

```json
{
  "error": true,
  "code": "UPSTREAM_TIMEOUT",
  "message": "moderation core timeout"
}
```

然后在 Telegram 接入层按业务策略：
- review
- 或保守拦截
