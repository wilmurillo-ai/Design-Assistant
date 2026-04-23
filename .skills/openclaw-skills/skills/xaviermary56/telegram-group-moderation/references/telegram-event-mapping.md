# Telegram Event Mapping

## Main update types

Handle at least:
- `message`
- `edited_message`
- `channel_post`
- `edited_channel_post`

## Useful Telegram fields

From message-like payloads, extract when present:
- `chat.id`
- `chat.type`
- `chat.title`
- `message_id`
- `from.id`
- `from.username`
- `from.first_name`
- `from.last_name`
- `date`
- `text`
- `caption`
- `entities`
- `caption_entities`
- `photo`
- `video`
- `document`
- `forward_origin` or legacy forward fields
- `reply_to_message`

## Normalized moderation payload

Example normalized payload:

```json
{
  "platform": "telegram",
  "chat_id": -1001234567890,
  "chat_type": "supergroup",
  "chat_title": "Example Group",
  "message_id": 345,
  "user_id": 777,
  "username": "spam_user",
  "display_name": "Promo Bot",
  "text": "加V了解一下",
  "caption": "扫码进群",
  "images": [],
  "videos": [],
  "raw_has_photo": true,
  "raw_has_video": false,
  "forwarded": false,
  "edited": false
}
```

## Normalization rules

- combine `text` and `caption` into the text review surface when policy requires full-message judgment
- preserve original message id and chat id for Telegram action calls
- mark edited messages so you can re-audit them separately
- keep media presence flags even if real media inspection is not enabled
- treat usernames, invite links, and obvious handles as extra evidence when your policy requires it
