# Architecture

## Recommended split

Use two layers:

### Layer 1: policy core

`post-content-moderation`

Responsibilities:
- ad / contact / diversion judgment
- whitelist and custom rule interpretation
- structured moderation result

### Layer 2: Telegram integration

`telegram-group-moderation`

Responsibilities:
- webhook event intake
- Telegram payload parsing
- group-specific config
- moderation action execution
- audit log and admin notifications

## Suggested request path

1. Telegram sends update to webhook
2. webhook validates request and allowed chat
3. normalize update into moderation payload
4. call moderation core
5. receive `pass|reject|review`
6. execute Telegram action
7. log result

## Suggested deployment options

### Option A: same service process

One PHP service handles webhook + moderation call + Telegram action.

Use when:
- small to medium traffic
- simple rules
- low ops overhead

### Option B: webhook ingress + worker queue

Webhook only stores updates and returns quickly. Worker handles moderation and Telegram actions.

Use when:
- large groups
- frequent media posts
- retry / rate-limit concerns
- you want better resilience

## Suggested persistence

Store at least:
- chat_id
- message_id
- user_id
- normalized text
- moderation result
- action taken
- offense count snapshot
- created_at

## Suggested risk policy

- text-only violation -> delete + warn
- repeated violation -> mute
- severe spam / scam pattern -> ban
- uncertain media-only suspicion -> review or conservative delete depending on business tolerance
