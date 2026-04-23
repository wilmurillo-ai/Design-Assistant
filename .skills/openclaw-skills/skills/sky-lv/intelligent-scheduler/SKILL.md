---
description: Context-aware intelligent scheduler for AI agents — time zone handling, priority queues, conflict resolution, and adaptive scheduling
keywords: openclaw, skill, automation, ai-agent, scheduler, task-scheduling, priority-queue, timezone, conflict-resolution, calendar
name: intelligent-scheduler
triggers: intelligent scheduler, task scheduling, priority queue, calendar management, schedule optimization, conflict resolution
---

# intelligent-scheduler

> Context-aware intelligent scheduler — handle time zones, prioritize tasks, resolve conflicts, and optimize schedules for AI agents.

## Skill Metadata

- **Slug**: intelligent-scheduler
- **Version**: 1.0.0
- **Description**: Context-aware scheduling system for AI agents. Handles multi-timezone scheduling, priority-based task queues, conflict detection and resolution, and adaptive schedule optimization based on agent workload and user preferences.
- **Category**: automation
- **Trigger Keywords**: `scheduler`, `task scheduling`, `priority queue`, `calendar`, `conflict resolution`, `timezone`, `schedule optimization`

---

## Capabilities

### 1. Schedule Tasks
\`\`\`bash
node scheduler.js add "Review PR #42" --time "14:00" --tz "Asia/Shanghai" --priority high
node scheduler.js add "Deploy v2.0" --time "2024-03-15 09:00" --tz "America/New_York" --depends "Review PR #42"
\`\`\`

### 2. Priority Queue Management
\`\`\`bash
node scheduler.js queue --sort priority
node scheduler.js queue --filter today
node scheduler.js promote "Urgent hotfix" --to critical
\`\`\`

Priority levels: `critical` > `high` > `medium` > `low` > `deferred`

### 3. Conflict Detection
\`\`\`bash
node scheduler.js check-conflicts --date 2024-03-15
# Output: CONFLICT: "Team standup" (09:00-09:30) overlaps "Client call" (09:15-10:00)
\`\`\`

### 4. Timezone Conversion
\`\`\`bash
node scheduler.js convert "14:00 Asia/Shanghai" --to "America/New_York"
# Output: 01:00 EDT (next day)
\`\`\`

### 5. Smart Rescheduling
\`\`\`bash
node scheduler.js auto-reschedule --fill-gaps --respect-priority
\`\`\`
Automatically moves tasks to fill schedule gaps while respecting priorities and dependencies.

---

## Configuration

\`\`\`json
// .scheduler/config.json
{
  "timezone": "Asia/Shanghai",
  "workHours": { "start": "09:00", "end": "18:00" },
  "bufferMinutes": 15,
  "rules": [
    "No meetings before 10:00 on Mondays",
    "Reserve Friday afternoons for deep work",
    "Critical tasks always scheduled first"
  ]
}
\`\`\`

## Use Cases

1. **Agent Task Management**: Schedule and prioritize agent tasks
2. **Meeting Coordination**: Handle multi-timezone meeting scheduling
3. **Cron Job Optimization**: Space out automated tasks to avoid resource contention
4. **Deadline Management**: Track and prioritize tasks by deadline proximity
5. **Work-Life Balance**: Enforce work hours and break scheduling
