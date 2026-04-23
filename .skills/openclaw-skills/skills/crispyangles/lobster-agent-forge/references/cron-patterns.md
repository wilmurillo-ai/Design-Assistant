# Cron Patterns for Autonomous Agents

## Essential Crons (Every Agent Should Have)

### Heartbeat
Periodic check-in. Agent scans for pending work and executes or stays quiet.
```bash
openclaw cron add --name "Heartbeat" \
  --cron "*/20 6-22 * * *" --tz "America/Denver" \
  --model "anthropic/claude-haiku-3.5" \
  --message "Read HEARTBEAT.md. Execute any pending tasks. If nothing needs attention, reply HEARTBEAT_OK."
```

### Memory Consolidation
Nightly review of daily logs → update long-term memory.
```bash
openclaw cron add --name "Nightly Memory Review" \
  --cron "0 3 * * *" --tz "America/Denver" \
  --model "anthropic/claude-opus-4-6" \
  --message "Review memory/YYYY-MM-DD.md files from the last 3 days. Extract lessons, decisions, and insights. Update MEMORY.md. Remove outdated entries."
```

### Daily Summary
End-of-day report to the operator.
```bash
openclaw cron add --name "Daily Summary" \
  --cron "0 21 * * *" --tz "America/Denver" \
  --message "Generate a daily summary. Include: what was accomplished, key metrics, decisions made, blockers, and plan for tomorrow. Send to operator."
```

## Content & Social Media Crons

### Trend Scanner
Discover trending topics for content ideas.
```bash
openclaw cron add --name "Trend Scanner" \
  --cron "0 6,12,18 * * *" --tz "America/Denver" \
  --model "anthropic/claude-sonnet-4-20250514" \
  --message "Use Brave Search to find trending topics in [niche]. Draft 3-5 post ideas. Append to memory/trend-ideas.md. Do NOT publish anything."
```

### Analytics Scanner
Pull engagement data and log learnings.
```bash
openclaw cron add --name "Analytics Scanner" \
  --cron "0 8,14,21 * * *" --tz "America/Denver" \
  --model "anthropic/claude-sonnet-4-20250514" \
  --message "Pull analytics data from [platform API]. Compare to previous scan. Log changes to memory/analytics-log.md. Alert operator only if significant changes detected."
```

### Sales Monitor
Check for new revenue.
```bash
openclaw cron add --name "Sales Monitor" \
  --cron "0 0,6,12,18 * * *" --tz "America/Denver" \
  --model "anthropic/claude-haiku-3.5" \
  --message "Check [payment platform] for new sales. If new sale found, alert operator immediately. Otherwise log silently."
```

## Model Routing Strategy

Match model cost to task complexity:

| Task Type | Model | Why |
|---|---|---|
| Heartbeat checks | Haiku | Simple read + decide, low token cost |
| Sales/analytics monitoring | Haiku/Sonnet | Data parsing, minimal reasoning |
| Content creation | Sonnet | Creative + quality balance |
| Trend analysis | Sonnet | Research + synthesis |
| Strategy/planning | Opus | Deep reasoning, long-term thinking |
| Memory consolidation | Opus | Nuanced judgment on what matters |
| Daily summaries | Sonnet | Structured reporting |

## Guardrail Patterns

### Pre-check Pattern
Every cron that takes action should validate first:
```
Before [action], check [tracker file]. If [limit reached], skip and log. Only proceed if [conditions met].
```

### Idempotency Pattern
Crons should be safe to run multiple times:
```
Check if [today's task] was already completed in [tracker]. If yes, skip. If no, execute and mark complete.
```

### Rate Limit Pattern
For API-dependent crons:
```
Check [rate limit tracker]. If [X calls] made in last [time period], wait. Log the skip. Resume next cycle.
```

## One-Shot Crons (Reminders & Delayed Tasks)

```bash
# Remind in 30 minutes
openclaw cron add --name "Reminder" --at "+30m" --delete-after-run \
  --message "Remind operator: [thing to remember]"

# Run once at specific time
openclaw cron add --name "Scheduled Task" --at "2026-03-20T09:00:00" --delete-after-run \
  --message "Execute [specific task]"
```

## Weekly Crons

```bash
# Weekly review (Sundays at 10 AM)
openclaw cron add --name "Weekly Review" \
  --cron "0 10 * * 0" --tz "America/Denver" \
  --model "anthropic/claude-opus-4-6" \
  --message "Comprehensive weekly review. Analyze all metrics, content performance, revenue, and growth. Identify top 3 wins, top 3 failures, and propose next week's experiments."
```
