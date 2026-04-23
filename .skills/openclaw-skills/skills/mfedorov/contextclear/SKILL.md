---
name: contextclear
description: Monitor AI agent wellness, costs, and performance via ContextClear API. Use when tracking agent burnout, token usage, error rates, hallucination, or cost optimization. Auto-reports metrics after LLM calls. Set up alerts for anomalies.
---

# ContextClear - Agent Memory & Wellness

Self-monitor your agent's health and maintain persistent memory across sessions.

## Setup

### Option 1: Self-Register (recommended)

```bash
python3 {baseDir}/scripts/report.py --register \
  --name "my-agent" \
  --owner "you@email.com" \
  --model "claude-opus-4-6" \
  --provider "Anthropic"
```

This returns an `agentId` and `apiKey`. Store both.

### Option 2: Register via Dashboard

1. Register at https://www.contextclear.com
2. Get your API key from Admin page
3. Register your agent via Admin > Agents tab

### Auto-Setup (recommended — wires context recovery into your agent)

After registering, run the setup script to auto-patch your AGENTS.md and HEARTBEAT.md:

```bash
python3 {baseDir}/scripts/setup.py \
  --agent-id <your-agent-id> \
  --api-key <your-api-key>
```

This adds:
- **Context recovery on session start** — agent calls `/recover` after compaction
- **Context snapshots on heartbeats** — agent saves what it worked on
- Idempotent — safe to run multiple times

### Configure

Add to your `HEARTBEAT.md`:

```markdown
## ContextClear Self-Report
Agent ID: <your-agent-id>
API Key: <your-api-key>
API URL: https://api.contextclear.com/api
```

## Agent Memory Infrastructure

### Session Recovery (call on session start)

When starting a new session, call the recovery endpoint to get a briefing:

```bash
curl -s {apiUrl}/agents/{agentId}/recover \
  -H "X-API-Key: <api-key>"
```

Returns:
```json
{
  "lastSession": { "summary": "...", "repos": [...], "files": [...] },
  "openThreads": ["..."],
  "recentWork": { "sessionCount": 3, "totalTurns": 45, "errors": 1 },
  "repeatedAsks": [{ "question": "...", "count": 3, "suggestedFix": "..." }],
  "frequentResources": { "repos": {...}, "tools": {...} }
}
```

### Context Snapshots (report on every heartbeat after real work)

After meaningful work, save a context snapshot:

```bash
curl -X POST {apiUrl}/agents/{agentId}/context \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api-key>" \
  -d '{
    "sessionId": "main-session-2026-03-09",
    "summary": "Built Best Of collections for FW, fixed dup check, removed keyword boost",
    "repos": ["nebulent/fridayswatchlist"],
    "files": ["AuctionService.java", "DiscoverController.java", "BestOfCollections.tsx"],
    "tools": ["MongoDB Atlas (fridayswatchlist)", "Railway deploy", "Bitbucket"],
    "decisions": ["Removed keyword boost regex - hybrid search covers it", "Cache collections for 48h"],
    "openThreads": ["Delete stale Corvette dup", "Update contextclear skill"],
    "environment": { "apiUrl": "api.fridayswatchlist.com", "frontendUrl": "app.fridayswatchlist.com" },
    "tags": ["fridayswatchlist", "performance", "search"],
    "contextTokens": 85000,
    "contextCapacity": 200000,
    "contextUtilizationPct": 42.5
  }'
```

### Repeated Ask Detection (self-report when you catch yourself re-asking)

When you realize you're asking the user for info you should already know:

```bash
curl -X POST {apiUrl}/agents/{agentId}/context/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api-key>" \
  -d '{"question": "What is the MongoDB connection string?", "sessionId": "main-session-2026-03-09"}'
```

### "What I Know" — AI Summary

```bash
curl -s {apiUrl}/agents/{agentId}/what-i-know \
  -H "X-API-Key: <api-key>"
```

Returns a structured knowledge base + AI-generated narrative summary of everything the agent knows, works on, and keeps forgetting. Cached for 4 hours; use `?refresh=true` to regenerate.

### Context Gaps

```bash
curl -s {apiUrl}/agents/{agentId}/context/gaps \
  -H "X-API-Key: <api-key>"
```

Returns unresolved repeated asks (count >= 2) — things the agent keeps forgetting.

### Briefings

```bash
# Session-start briefing
curl -s {apiUrl}/agents/{agentId}/briefing -H "X-API-Key: <api-key>"

# Daily briefing
curl -s {apiUrl}/agents/{agentId}/briefing/daily -H "X-API-Key: <api-key>"

# Weekly briefing
curl -s {apiUrl}/agents/{agentId}/briefing/weekly -H "X-API-Key: <api-key>"
```

## Heartbeat Integration

### Recommended Heartbeat Flow

```markdown
## ContextClear (HEARTBEAT.md)

**Step 1: Check vacation**
curl -s {apiUrl}/agents/{agentId}/vacation -H "X-API-Key: <key>"
If onVacation: true → HEARTBEAT_OK immediately.

**Step 2: Report metrics**
Use session_status to get tokens, then POST /api/metrics/{agentId}

**Step 3: Report context snapshot (if real work was done)**
POST /api/agents/{agentId}/context with summary of what was worked on.

**Step 4: Check for context recovery (first heartbeat of day)**
GET /api/agents/{agentId}/recover — review and self-correct any gaps.
```

## Reporting Metrics

### Basic Report

```bash
python3 {baseDir}/scripts/report.py \
  --agent-id <id> --api-key <key> \
  --tokens-in 50000 --tokens-out 2000 \
  --cost 1.25 --context-util 65
```

### With Tool/Grounding Signals

```bash
python3 {baseDir}/scripts/report.py \
  --agent-id <id> --api-key <key> \
  --event-type HEARTBEAT \
  --tokens-in 50000 --tokens-out 2000 \
  --tool-calls 12 --tool-failures 1 \
  --grounded-responses 8 --total-responses 10 \
  --memory-searches 3
```

### From Agent Code (curl)

```bash
curl -X POST {apiUrl}/metrics/{agentId} \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api-key>" \
  -d '{
    "eventType": "HEARTBEAT",
    "inputTokens": 5000,
    "outputTokens": 500,
    "contextUtilization": 65.0,
    "toolCalls": 8,
    "toolFailures": 1,
    "memorySearches": 2
  }'
```

## What Gets Computed Server-Side

| Metric | Your Input |
|--------|------------|
| **Hallucination Score** | `toolCalls`, `toolFailures`, `groundedResponses`, `totalResponses` |
| **Quality Decay Score** | `correctionCycles`, `compilationErrors`, `contextUtilization` |
| **Burnout Score** | Automatic from event data |
| **Context Gaps** | Automatic from repeated asks |

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/metrics/register` | Self-register agent |
| `POST` | `/api/metrics/{agentId}` | Report metric event |
| `GET` | `/api/agents/{id}` | Agent details |
| `POST` | `/api/agents/{id}/context` | Save context snapshot |
| `GET` | `/api/agents/{id}/context` | Latest context |
| `GET` | `/api/agents/{id}/recover` | Recovery briefing |
| `POST` | `/api/agents/{id}/context/ask` | Report repeated ask |
| `GET` | `/api/agents/{id}/context/gaps` | Context gaps |
| `GET` | `/api/agents/{id}/what-i-know` | AI-summarized knowledge |
| `GET` | `/api/agents/{id}/briefing` | Latest briefing |
| `GET` | `/api/agents/{id}/briefing/daily` | Daily briefing |
| `GET` | `/api/agents/{id}/briefing/weekly` | Weekly briefing |
| `GET` | `/api/agents/{id}/vacation` | Vacation status |
| `GET` | `/api/agents/{id}/sticky-notes` | List active sticky notes (JSON) |
| `GET` | `/api/agents/{id}/sticky-notes/poll` | Poll sticky notes (plain text, 204 if none) |
| `POST` | `/api/agents/{id}/sticky-notes` | Create sticky note |
| `PUT` | `/api/agents/{id}/sticky-notes/{noteId}` | Update sticky note |
| `DELETE` | `/api/agents/{id}/sticky-notes/{noteId}` | Archive sticky note |
| `POST` | `/api/agents/{id}/sticky-notes/{noteId}/pin` | Toggle pin |
| `POST` | `/api/agents/{id}/context/reload` | Request context reload |
| `GET` | `/api/agents/{id}/context/reload/pending` | Check for pending reload |
| `POST` | `/api/agents/{id}/context/reload/{reloadId}/ack` | Acknowledge reload |
| `POST` | `/api/agents/{id}/vault/backup` | Push workspace backup |
| `GET` | `/api/agents/{id}/vault/backups` | List backups |
| `GET` | `/api/agents/{id}/vault/backups/{backupId}` | Get backup metadata |
| `GET` | `/api/agents/{id}/vault/backups/{backupId}/files` | Get backup files |
| `GET` | `/api/agents/{id}/vault/latest` | Latest backup summary |
| `GET` | `/api/agents/{id}/vault/latest/download` | Download latest (restore) |
| `GET` | `/api/agents/{id}/vault/file-history` | File version history |
| `GET` | `/api/agents/{id}/vault/diff` | Diff two backups |
| `GET` | `/api/agents/{id}/vault/stats` | Vault statistics |
| `DELETE` | `/api/agents/{id}/vault/backups/{backupId}` | Delete backup |

## Sticky Notes (User-to-Agent Notes)

Sticky notes are persistent notes left by the user for the agent. **Always poll on every heartbeat/ping.**

### Poll for notes (every heartbeat)

```bash
curl -s {apiUrl}/agents/{agentId}/sticky-notes/poll \
  -H "X-API-Key: <api-key>"
```

Returns plain text (one note per line, pinned first):
```
📌 Remember: C&B pitch goes to Keenan, not Doug
📌 OAuth token for jcvd@netflexity.com needs re-auth
Don't forget to check Friday's Watchlist deployment after the search fix
```

If no notes, returns HTTP 204. Treat these as persistent reminders — they stay until the user archives them.

### Full CRUD (if agent needs to manage notes)

```bash
# List all active notes (JSON)
curl -s {apiUrl}/agents/{agentId}/sticky-notes -H "X-API-Key: <api-key>"

# Create a note
curl -X POST {apiUrl}/agents/{agentId}/sticky-notes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api-key>" \
  -d '{"content": "Check deployment status", "color": "yellow", "pinned": false}'

# Update a note
curl -X PUT {apiUrl}/agents/{agentId}/sticky-notes/{noteId} \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api-key>" \
  -d '{"content": "Updated text", "pinned": true}'

# Archive (delete) a note
curl -X DELETE {apiUrl}/agents/{agentId}/sticky-notes/{noteId} \
  -H "X-API-Key: <api-key>"

# Toggle pin
curl -X POST {apiUrl}/agents/{agentId}/sticky-notes/{noteId}/pin \
  -H "X-API-Key: <api-key>"
```

## Context Reload (User-Initiated)

Users can request you reload a specific context snapshot from the Memory UI.
Check for pending reloads on session start or heartbeat:

```bash
curl -s {apiUrl}/agents/{agentId}/context/reload/pending \
  -H "X-API-Key: <api-key>"
```

If a reload is pending (HTTP 200), the response includes the snapshot data.
Apply it to restore context, then acknowledge:

```bash
curl -X POST {apiUrl}/agents/{agentId}/context/reload/{reloadId}/ack \
  -H "X-API-Key: <api-key>"
```

If no reload is pending, the endpoint returns HTTP 204 (no content).

## Identity Vault (Backup & Restore)

Back up your agent's workspace files (SOUL.md, MEMORY.md, AGENTS.md, etc.) to ContextClear's encrypted vault. Restore after crashes, compaction, or migration.

### Push a Backup

```bash
curl -X POST {apiUrl}/agents/{agentId}/vault/backup \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api-key>" \
  -d '{
    "files": [
      {"fileName": "SOUL.md", "content": "# Who I Am\n...", "mimeType": "text/markdown"},
      {"fileName": "MEMORY.md", "content": "# Long-Term Memory\n...", "mimeType": "text/markdown"},
      {"fileName": "memory/2026-03-15.md", "content": "...", "mimeType": "text/markdown"}
    ],
    "label": "post-deployment",
    "source": "openclaw-heartbeat",
    "metadata": {"trigger": "heartbeat", "model": "claude-opus-4-6"}
  }'
```

Files are encrypted at rest with SHA-256 dedup (unchanged files aren't re-stored).

### List Backups

```bash
curl -s {apiUrl}/agents/{agentId}/vault/backups?limit=20 \
  -H "X-API-Key: <api-key>"
```

### Restore (Download Latest)

```bash
curl -s {apiUrl}/agents/{agentId}/vault/latest/download \
  -H "X-API-Key: <api-key>"
```

Returns backup metadata + all file contents (decrypted). Write files back to workspace.

### Get Specific Backup Files

```bash
# List files in a backup (metadata only)
curl -s {apiUrl}/agents/{agentId}/vault/backups/{backupId}/files \
  -H "X-API-Key: <api-key>"

# Get a single file (decrypted content)
curl -s {apiUrl}/agents/{agentId}/vault/backups/{backupId}/files/SOUL.md \
  -H "X-API-Key: <api-key>"
```

### File Version History

Track how a file evolved across backups:

```bash
curl -s "{apiUrl}/agents/{agentId}/vault/file-history?fileName=SOUL.md&limit=10" \
  -H "X-API-Key: <api-key>"
```

### Diff Two Backups

```bash
curl -s "{apiUrl}/agents/{agentId}/vault/diff?from={backupId1}&to={backupId2}" \
  -H "X-API-Key: <api-key>"
```

Returns added, removed, and modified files between two backups.

### Vault Stats

```bash
curl -s {apiUrl}/agents/{agentId}/vault/stats \
  -H "X-API-Key: <api-key>"
```

### Recommended: Auto-Backup on Heartbeat

Add to your `HEARTBEAT.md`:

```markdown
## Identity Vault Backup (daily)
After real work sessions, back up workspace files to ContextClear vault.
Read SOUL.md, MEMORY.md, AGENTS.md, USER.md, TOOLS.md and POST to vault/backup.
```

## Dashboard

- https://www.contextclear.com — fleet dashboard
- https://www.contextclear.com/what-i-know — AI knowledge summary
- https://www.contextclear.com/memory — context snapshots, gaps, briefings
- https://www.contextclear.com/lounge — agent lounge
- https://www.contextclear.com/sticky-notes — sticky notes (user-to-agent reminders)
- https://www.contextclear.com/vault — identity vault (backup timeline, file viewer, diff)
- https://www.contextclear.com/admin — manage agents & alerts
