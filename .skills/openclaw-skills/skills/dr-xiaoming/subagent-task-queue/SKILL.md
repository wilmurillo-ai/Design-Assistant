---
name: task-queue
description: >
  Concurrent task queue management for sub-agent orchestration. Provides a /queue command
  for real-time visibility into active, queued, and completed sub-agent tasks. Use when:
  (1) user sends /queue or /quene to check task status, (2) spawning a sub-agent task that
  should be tracked, (3) managing concurrent workload across multiple sub-agents,
  (4) user asks about task capacity or current workload. Supports configurable concurrency
  limits, automatic FIFO scheduling, typed task categorization, and portable deployment
  across different machines. NOT for: task board/kanban management (use mc-task), simple
  single-step tasks handled in main session, or project-level tracking.
---

# Task Queue

Manage concurrent sub-agent tasks with real-time visibility. Main session stays responsive;
heavy work runs in parallel sub-agents tracked by a queue.

## Setup

Initialize the queue state file on first use:

```bash
cat > /tmp/task-queue.json << 'EOF'
{
  "maxConcurrent": 8,
  "maxSameType": 3,
  "active": [],
  "queued": [],
  "completed": [],
  "stats": { "totalSpawned": 0, "totalCompleted": 0, "totalFailed": 0 },
  "updatedAt": null
}
EOF
```

Adjust `maxConcurrent` by machine:
- Low-end (Mac Mini 16GB): 3-4
- Mid-range (Mac Studio 64GB): 6
- Server (64+ cores, 128GB+): 8

## Commands

| Command | Action |
|---------|--------|
| `/queue` or `/quene` | Show current queue status |
| `/queue clear` | Clear completed task history |
| `/queue kill <Q-ID>` | Terminate a specific task |

## Queue Protocol

### On new task (that needs sub-agent)

1. Generate sequential ID: `Q-001`, `Q-002`, ...
2. Classify type: `research | dev | report | search | translate | analysis | other`
3. Check capacity:
   - `active.length < maxConcurrent` AND same-type count < `maxSameType` → spawn, add to `active`
   - Otherwise → add to `queued`, notify user of position
4. Update `/tmp/task-queue.json`

### On task completion

1. Move from `active` to `completed` (keep last 20)
2. Pop next from `queued` if any, spawn it
3. Update stats
4. Report result to user

### On task failure

1. Record in `completed` with `"result": "failed"` and reason
2. Notify user with suggestion (retry / alternative / manual)
3. Continue dequeuing — failures don't block the queue

### /queue response format

```
📋 任务队列 (活跃 X/8 | 排队 Y)

🔄 运行中：
  Q-001 [research] 海外媒体分析 (3m ago)
  Q-002 [dev] 修复登录bug (1m ago)

⏳ 排队中：
  Q-003 [report] 周报生成

✅ 最近完成：
  Q-000 [search] KOL筛选 → 成功 (5m)
```

If empty: report "全空，随时可以塞活"

## Data Schema

See [references/schema.md](references/schema.md) for the complete JSON structure
of `/tmp/task-queue.json`.

## Dispatch Rules

Decide whether to queue (spawn sub-agent) or handle directly in main session:

**Queue it** (any one triggers):
- Estimated time > 2 minutes
- Batch operations (bulk search, multi-doc processing)
- Development / code tasks
- Deep research or analysis
- Long document generation
- User sends multiple independent tasks at once

**Handle directly** (all true):
- Simple Q&A, chat, confirmations
- Quick lookups (read file, check status)
- 1-2 step operations
- Needs multi-turn clarification first

When uncertain, prefer queuing — better to over-spawn than block the main session.

## Portable Deployment

To deploy on another machine (e.g., Mac with a different OpenClaw agent):

1. Install this skill to the target agent's skills directory
2. Create `/tmp/task-queue.json` with the init template above
3. Adjust `maxConcurrent` for the machine's resources
4. Add `/queue` trigger to the agent's routing config (AGENTS.md or equivalent)
