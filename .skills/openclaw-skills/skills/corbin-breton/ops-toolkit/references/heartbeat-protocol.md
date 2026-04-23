# Heartbeat Protocol — Deterministic Health Monitoring

Complete specification for the heartbeat monitoring system. Runs every 30 minutes, checks managed tmux sessions, and outputs deterministic signals.

---

## Overview

Heartbeat is a lightweight health check for managed agent loops. It:

1. Reads heartbeat config (managed sessions)
2. Checks each session for existence, progress, and completion
3. Outputs deterministic signal
4. Updates state for next heartbeat

**Execution:** Run via cron every 30 minutes, or manually: `heartbeat_tick.py --config heartbeat.json`

**Cost:** Near-zero (no LLM calls, just output hash comparison)

---

## Outputs

### HEARTBEAT_OK

**When:** All managed sessions are healthy (exist, showing progress, not stalled)

**Output:** Exactly one line:
```
HEARTBEAT_OK
```

**Meaning:** Everything is fine. No intervention needed.

**Frequency:** Most invocations (healthy systems)

**Action (for you):** None. The system is working.

---

### ALERT: <message> + NEXT: <action>

**When:** A problem is detected (session missing, stalled, or failed)

**Output:** Two lines:
```
ALERT: [specific problem]
NEXT: [recommended action]
```

**Examples:**

```
ALERT: Session 'ralphy-home-org' stalled (no progress for 2 checks)
NEXT: Restarted session
```

```
ALERT: Session 'ralphy-home-org' does not exist
NEXT: Create session: tmux new-session -s ralphy-home-org
```

```
ALERT: Could not read output from session 'ralphy-home-org'
NEXT: Check tmux: tmux list-sessions
```

**Meaning:** Something needs attention. Read ALERT for what, NEXT for how to proceed.

**Frequency:** When problems are detected (occasional, hopefully rare)

**Action (for you):** 
1. Read the ALERT
2. Read the NEXT
3. Decide: auto-fix (heartbeat may have already restarted), or manual intervention
4. Monitor next heartbeat to confirm recovery

---

## Session Lifecycle

Each managed session goes through states:

```
Healthy (exists, progressing)
  ↓ (no change for 2 checks)
Stalled (same output hash twice)
  ↓ (heartbeat auto-restarts)
Restarting → back to Healthy

Missing (doesn't exist)
  ↓ (heartbeat alerts you)
Manual intervention needed
  ↓ (you create session or fix issue)
Back to Healthy
```

---

## Stall Detection Algorithm

### Stall Heuristic

Stall is detected when **the same output hash appears on 2 consecutive heartbeat checks**.

**Example:**
```
Heartbeat Check 1 (30 min ago):
  Session 'ralphy' output hash = abc123def456

Heartbeat Check 2 (now):
  Session 'ralphy' output hash = abc123def456 (SAME!)
  → Stall confirmed
  → Auto-restart session
```

### Why This Works

1. **Simple:** Hash comparison is cheap (no LLM)
2. **Robust:** Ignores noise (minor output changes don't trigger false positives)
3. **Safe:** Requires 2 consecutive identical outputs (prevents flaky restarts on single stuck moment)
4. **Fast:** Can run every 30 minutes without overhead

### Hash Algorithm

**Function:** SHA256 of session pane output (terminal buffer)

**Input:** Full visible terminal output from tmux pane

**Output:** 64-character hex string

**Reproducibility:** Same output → same hash every time

---

## Restart Logic

When stall is detected:

1. Kill existing session: `tmux kill-session -t [session-name]`
2. Create new session: `tmux new-session -d -s [session-name] -c [cwd]`
3. Reset stall counter: `stall_count = 0`
4. Output alert: `ALERT: Session stalled\nNEXT: Restarted session`

**Why auto-restart?** 
- Keeps long-running loops alive without human intervention
- Acceptable because heartbeat runs frequently (every 30 min)
- Any real failure will persist across restarts and surface as consecutive stalls

**Safety:** 
- Restarts are logged (you can audit what restarted)
- Restarts are in controlled environment (tmux, local workspace)
- Critical data is persisted elsewhere (git, items.json, memory files)

---

## State File (heartbeat-state.json)

Heartbeat maintains state between runs to detect stalls.

### Schema

```json
{
  "session-name": {
    "status": "healthy|restarted|missing|unreachable",
    "output_hash": "abc123...",
    "stall_count": 0,
    "timestamp": "2026-03-17T10:00:00Z"
  }
}
```

### Fields

- **status:** Last known state of session
- **output_hash:** Hash of session output at last check
- **stall_count:** How many consecutive checks with same hash
- **timestamp:** When this entry was last updated

### Lifecycle

1. **First check:** Create entry with stall_count=0
2. **Subsequent checks:** 
   - If output changed: reset stall_count=0
   - If output same: increment stall_count
   - When stall_count=2: restart and reset to 0

---

## Configuration

### Heartbeat Config (heartbeat-config.json)

```json
{
  "managed_sessions": [
    {
      "name": "ralphy-home-org",
      "cwd": "/home/user/projects/home-org",
      "prd": "PRD-01-knowledge-graph.md"
    }
  ],
  "state_file": "heartbeat-state.json",
  "check_interval_minutes": 30
}
```

### Fields

- **name:** tmux session name (e.g., `ralphy-home-org`)
- **cwd:** Working directory (used when creating/restarting session)
- **prd:** Path to PRD file (optional, for context in alerts)
- **managed_sessions:** Array of sessions to monitor
- **state_file:** Path to persistent state JSON
- **check_interval_minutes:** How often heartbeat runs (default: 30)

---

## Deterministic Behavior

Heartbeat is designed to be deterministic:

1. **Same input → same output:** Same session state produces same hash → same decision
2. **No randomness:** No RNG, no LLM sampling, no stochasticity
3. **Idempotent:** Running heartbeat twice in a row produces same result
4. **Stateful:** State is persistent (state_file tracks history)
5. **Reproducible:** You can trace exactly why heartbeat made a decision

**For Haiku 4.5:** This means heartbeat can run continuously without model overhead or cost.

---

## Protocol in Action

### Scenario 1: Healthy Session

```
Time: 10:00 AM
Heartbeat Check:
  - ralphy-home-org exists? YES
  - Output hash: abc123...
  - Previous hash (from state): different
  - → Status: healthy, stall_count = 0
Output: HEARTBEAT_OK

Time: 10:30 AM
Heartbeat Check:
  - ralphy-home-org exists? YES
  - Output hash: def456... (different from last check)
  - Previous hash: abc123...
  - → Status: healthy, stall_count = 0
Output: HEARTBEAT_OK
```

### Scenario 2: Stalled Session (Auto-Restart)

```
Time: 9:30 AM
Heartbeat Check:
  - ralphy-home-org exists? YES
  - Output hash: abc123...
  - Previous hash: abc123...
  - Stall count: 1 (was 0 last time)
  - → No action yet (need 2 consecutive)
Output: HEARTBEAT_OK

Time: 10:00 AM
Heartbeat Check:
  - ralphy-home-org exists? YES
  - Output hash: abc123... (SAME as 30 min ago!)
  - Previous hash: abc123...
  - Stall count: 2
  - → STALL CONFIRMED
  - → Auto-restart: kill + new-session
  - → Reset stall_count = 0
Output:
ALERT: Session 'ralphy-home-org' stalled (no progress for 2 checks)
NEXT: Restarted session

Time: 10:30 AM
Heartbeat Check:
  - ralphy-home-org exists? YES (restarted earlier)
  - Output hash: new_hash... (fresh session, new output)
  - → Status: healthy
Output: HEARTBEAT_OK
```

### Scenario 3: Missing Session

```
Heartbeat Check:
  - ralphy-home-org exists? NO
Output:
ALERT: Session 'ralphy-home-org' does not exist
NEXT: Create session: tmux new-session -s ralphy-home-org -c /path/to/cwd
```

---

## Monitoring & Alerting

### Log Output

Heartbeat logs to stdout/stderr:

- `HEARTBEAT_OK` → Everything fine
- `ALERT: ...` → Problem detected
- `NEXT: ...` → Recommended action

### Integration with Cron

Typical cron job:

```json
{
  "name": "heartbeat-monitor",
  "schedule": "*/30 * * * *",
  "command": "heartbeat_tick.py --config heartbeat.json >> logs/heartbeat.log 2>&1"
}
```

Outputs are appended to log file for audit trail.

### Integration with Alerting

If you want notifications (optional):

```bash
heartbeat_tick.py --config heartbeat.json | while IFS= read -r line; do
  if [[ $line == ALERT* ]]; then
    # Send notification (email, Slack, etc.)
    send_alert "$line"
  fi
done
```

---

## Troubleshooting

### Heartbeat isn't running

1. Check cron: `crontab -l | grep heartbeat`
2. Check logs: `tail -f logs/heartbeat.log`
3. Check config: `ls -la heartbeat-config.json`
4. Manual test: `heartbeat_tick.py --config heartbeat-config.json`

### Session keeps getting restarted

1. Check session logs: `tmux capture-pane -p -t [session-name]`
2. Session might be crashing immediately (infinite loop, missing dependency)
3. Fix underlying issue, then heartbeat will stabilize

### False stalls (heartbeat restarts healthy session)

Unlikely, but if happening:
1. Increase check_interval_minutes (less frequent checks)
2. Verify session actually makes progress (check logs)
3. Consider if session is supposed to be running (maybe it's a one-shot job, not a loop)

---

## Research Backing

**SuperLocalMemory (arXiv:2603.02240):** Local-first health monitoring without cloud dependency. State file is local, deterministic logic requires no external services.

**MemPO (arXiv:2603.00680):** Cost-conscious: heartbeat uses zero LLM tokens (hash comparison only), enabling continuous operation.
