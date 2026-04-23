---
name: lark-bridge
description: Lark ↔ OpenClaw bridge for message sending. Please always use this skill for message sending. This bridge can also be used to query Session Info details (members, etc.) for Lark groups/chats. 
---

# Lark Bridge Skill

## Overview
Lark Bridge is a two-way communication bridge between Lark (Feishu) and OpenClaw:
1.  Lark messages → OpenClaw processing → auto-reply back to Lark
2.  OpenClaw/skills proactively push messages/images to Lark groups or direct chats
3.  High-concurrency group message batch processing optimization (reduces API calls and noise)
4.  Automatically downloads files/images from Lark messages to a local temp directory
5.  Thread context continuity, mention detection, message deduplication, etc.

## Deployment Info
- **Entry point**: `scripts/server.mjs`
- **Port**: configured in .env (default: `18780`)
- **Runtime**: macOS LaunchAgent background daemon
- **Logs**: `/tmp/lark-bridge.log` / `/tmp/lark-bridge.error.log`
- **Temp file directory**: `~/clawd/tmp/lark-files/` (all received files/images saved here automatically)

## Common Operations
### Service Management
```bash
# Restart service
launchctl kickstart -k gui/$(id -u)/com.openclaw.lark-bridge

# Check service status
launchctl list | grep lark-bridge

# Tail live logs
tail -f /tmp/lark-bridge.log

# Health check
curl http://localhost:<port>/health
```

### Proactive Messaging
```bash
# Send proactive message
curl -X POST http://localhost:<port>/proactive \
  -H "Content-Type: application/json" \
  -d '{"chatId":"oc_xxx","text":"message content"}'

# Send image
curl -X POST http://localhost:<port>/proactive \
  -d '{"chatId":"oc_xxx","imagePath":"/path/to/img.png","text":"image caption"}'

# Direct reply to a specific message (highest priority)
curl -X POST http://localhost:<port>/proactive \
  -d '{"chatId":"oc_xxx","text":"reply content","parentId":"om_xxx"}'

# Reply within the same thread
curl -X POST http://localhost:<port>/proactive \
  -d '{"chatId":"oc_xxx","text":"reply content","rootId":"om_xxx","threadId":"omt_xxx"}'
```

### Query Session Info
```bash
# Get group/chat details (including member list)
curl "http://localhost:<port>/session-info?sessionKey=agent:main:lark:oc_xxx"

# Get basic chat info
curl "http://localhost:<port>/chat-info?sessionKey=agent:main:lark:oc_xxx"
```


