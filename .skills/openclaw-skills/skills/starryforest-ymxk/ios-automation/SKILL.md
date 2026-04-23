---
name: ios-automation
description: Control iOS automation via StarryForest Agent Mail API. Use when creating alarms, reminders, memos, calendar events, focus modes, music playback, or journal entries on iOS. Sends structured JSON commands via email (126 to Hotmail) to trigger iOS Shortcuts automation.
metadata:
  openclaw:
    emoji: "⚙️"
    requires:
      python: ">=3.8"
    install: []
---
---

# iOS Automation via Agent Mail

Send structured commands to iOS Shortcuts automation via email using StarryForest Agent Mail API v1.

## Overview

This skill enables OpenClaw to control iOS automation through email:
1. Build JSON command with one or more actions
2. Send email from `starryforest_ymxk@126.com` to `starryforest_ymxk@hotmail.com`
3. iOS Shortcuts receives email and executes actions

## Skill Structure

```
ios-automation/
├── SKILL.md
├── scripts/
│   ├── init.py              # StarryForestAgent class
│   ├── send_agent_mail.py   # Command-line tool
│   ├── examples.py          # Usage examples
│   ├── quickstart.sh        # Quick start script
│   └── verify_automation.py # Configuration verification
└── references/
    └── StarryForest Agent Mail API v1 使用说明.md  # API docs
```

## Quick Start

### Import the module

```python
import sys
import os

# Get skill directory
skill_dir = os.path.join(os.path.expanduser('~/.openclaw/workspace/skills/ios-automation/scripts'))
sys.path.insert(0, skill_dir)

from __init__ import StarryForestAgent
```

### Single action

```python
import sys
import os
skill_dir = os.path.join(os.path.expanduser('~/.openclaw/workspace/skills/ios-automation/scripts'))
sys.path.insert(0, skill_dir)

from __init__ import send_reminder

send_reminder(
    title="测试提醒",
    to_email="starryforest_ymxk@hotmail.com",
    due="2026-02-07 15:00",
    notes="来自 OpenClaw",
    priority="中"
)
```

### Multiple actions (recommended)

```python
import sys
import os
skill_dir = os.path.join(os.path.expanduser('~/.openclaw/workspace/skills/ios-automation/scripts'))
sys.path.insert(0, skill_dir)

from __init__ import StarryForestAgent

agent = StarryForestAgent("126")

agent.create_alarm(
    time="07:30",
    label="晨练",
    repeat=["Monday", "Wednesday", "Friday"]
)

agent.create_reminder(
    title="喝水",
    due="2026-02-07 15:00",
    priority="中"
)

agent.create_memo(
    title="备忘录",
    content="这是一条测试备忘录"
)

# Send all actions in one email
agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送")
```

## Seven Action Types

### 1. Create Alarm (创建闹钟)

```python
agent.create_alarm(
    time="07:30",           # HH:mm format
    label="晨练",           # Optional
    enabled=True,           # Optional, default True
    repeat=["Monday", "Wednesday", "Friday"]  # Optional, full English names
)
```

**Repeat values**: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`

### 2. Create Reminder (创建提醒事项)

```python
agent.create_reminder(
    title="测试提醒",                  # Required
    due="2026-02-07 15:00",           # Optional, YYYY-MM-DD HH:mm
    notes="来自 OpenClaw",            # Optional
    priority="中"                     # Optional: 高/中/低
)
```

### 3. Create Memo (创建备忘录)

```python
agent.create_memo(
    title="备忘录标题",    # Required
    content="备忘录内容"   # Required
)
```

### 4. Create Calendar Event (创建日历日程)

```python
agent.create_calendar_event(
    title="会议",                      # Required
    start="2026-02-07 10:00",         # Required, YYYY-MM-DD HH:mm
    end="2026-02-07 11:00",           # Optional, YYYY-MM-DD HH:mm
    location="会议室",                 # Optional
    notes="备注",                      # Optional
    all_day=False                     # Optional, default False
)
```

### 5. Focus Mode (专注模式)

```python
agent.focus_mode(
    name="工作",                      # Required: 工作/个人/睡眠
    on=True,                         # Required: True=开启, False=关闭
    until="2026-02-07 18:00"         # Optional, YYYY-MM-DD HH:mm
)
```

### 6. Play Music (播放音乐)

```python
agent.play_music(
    play=True,                       # Required: True=播放, False=暂停
    playlist="每日推荐"               # Required: 每日推荐/私人漫游
)
```

### 7. Write Journal (写日记)

```python
agent.write_journal(
    title="日记",                    # Required
    date="2026-02-07",              # Required, YYYY-MM-DD
    content="今天的日记内容"          # Required
)
```

## Time Format Rules

| Field Type | Format | Example | Usage |
|-----------|--------|---------|-------|
| Time point | `YYYY-MM-DD HH:mm` | `2026-02-07 15:00` | Reminder due, calendar start/end, focus until |
| Alarm time | `HH:mm` | `07:30` | Alarm time |
| Date only | `YYYY-MM-DD` | `2026-02-07` | Journal date |

## Email Configuration (CRITICAL)

For iOS automation to trigger successfully:

- **Sender**: MUST use `starryforest_ymxk@126.com` (account="126")
- **Receiver**: MUST send to `starryforest_ymxk@hotmail.com`
- **Subject**: MUST contain "自动化推送"
- **Token**: Auto-generated as "starryforest_agent"

## Convenience Functions

For single actions, use convenience functions:

```python
import sys
import os
skill_dir = os.path.join(os.path.expanduser('~/.openclaw/workspace/skills/ios-automation/scripts'))
sys.path.insert(0, skill_dir)

from __init__ import (
    send_alarm,
    send_reminder,
    send_memo,
    send_calendar_event,
    send_focus_mode,
    send_music,
    send_journal
)

# Example
send_reminder(
    title="测试",
    to_email="starryforest_ymxk@hotmail.com",
    due="2026-02-07 15:00",
    priority="中"
)
```

## Complete Example

```python
import sys
import os

# Add skill scripts to path
skill_dir = os.path.join(os.path.expanduser('~/.openclaw/workspace/skills/ios-automation/scripts'))
sys.path.insert(0, skill_dir)

from __init__ import StarryForestAgent

# Initialize with 126 account
agent = StarryForestAgent("126")

# Add multiple actions
agent.create_alarm(
    time="07:30",
    label="晨练",
    repeat=["Monday", "Wednesday", "Friday"]
)

agent.create_reminder(
    title="喝水提醒",
    due="2026-02-07 15:00",
    notes="每天八杯水",
    priority="中"
)

agent.create_calendar_event(
    title="团队会议",
    start="2026-02-07 14:00",
    end="2026-02-07 15:00",
    location="会议室A",
    notes="项目进度讨论"
)

agent.focus_mode(
    name="工作",
    on=True,
    until="2026-02-07 18:00"
)

agent.write_journal(
    title="日记",
    date="2026-02-07",
    content="今天完成了 iOS 自动化集成测试"
)

# Send all actions in one email
agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送")
```

## Notes

1. **Always use `account="126"`** for automation triggering
2. **Email subject must contain "自动化推送"** for iOS to process
3. **Batch operations recommended** - use `StarryForestAgent` class to send multiple actions in one email
4. **Time zones**: All times are local time (Asia/Shanghai), no timezone conversion needed
5. **Unique ID**: Auto-generated in format `agent-YYYYMMDD-HHMMSS-UUID`

## API Reference

- **Full API docs**: `references/StarryForest Agent Mail API v1 使用说明.md`
- **Module source**: `scripts/init.py`
- **Examples**: `scripts/examples.py`
