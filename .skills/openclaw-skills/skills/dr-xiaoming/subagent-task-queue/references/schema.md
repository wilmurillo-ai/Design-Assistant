# Queue State Schema

## /tmp/task-queue.json

```json
{
  "maxConcurrent": 8,
  "maxSameType": 3,
  "active": [
    {
      "id": "Q-001",
      "task": "Task description",
      "type": "research|dev|report|search|translate|analysis|other",
      "sessionId": "subagent-session-id",
      "startedAt": "2026-03-26T07:30:00Z",
      "status": "running"
    }
  ],
  "queued": [
    {
      "id": "Q-002",
      "task": "Task description",
      "type": "research",
      "queuedAt": "2026-03-26T07:31:00Z"
    }
  ],
  "completed": [
    {
      "id": "Q-001",
      "task": "Task description",
      "type": "research",
      "startedAt": "2026-03-26T07:30:00Z",
      "completedAt": "2026-03-26T07:35:00Z",
      "result": "success|failed",
      "summary": "One-line result summary"
    }
  ],
  "stats": {
    "totalSpawned": 0,
    "totalCompleted": 0,
    "totalFailed": 0
  },
  "updatedAt": "2026-03-26T07:30:00Z"
}
```

## Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `maxConcurrent` | number | Max simultaneous sub-agents |
| `maxSameType` | number | Max sub-agents of the same type |
| `active[].id` | string | Sequential ID (Q-NNN) |
| `active[].task` | string | Human-readable task description |
| `active[].type` | enum | Task category for concurrency grouping |
| `active[].sessionId` | string | OpenClaw sub-agent session ID |
| `active[].startedAt` | ISO 8601 | When the sub-agent was spawned |
| `queued[].queuedAt` | ISO 8601 | When the task entered the queue |
| `completed[].result` | enum | "success" or "failed" |
| `completed[].summary` | string | Brief outcome description |
| `stats.*` | number | Lifetime counters |

## Capacity Rules

- Total active ≤ `maxConcurrent`
- Active of same `type` ≤ `maxSameType`
- Completed list capped at 20 (oldest evicted)
- Queue is FIFO — first in, first out
