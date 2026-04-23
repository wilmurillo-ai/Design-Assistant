# Open Stocki OpnClaw Skill Design

## Context

Build an OpnClaw skill (`open-stocki`) publishable to ClawHub that teaches the OpenClaw agent how to use the Stocki financial analyst integration — 7 MCP tools for instant Q&A and async quantitative analysis.

## Approach

Single SKILL.md + two helper scripts. Matches the standard OpnClaw skill pattern (github, weather, coding-agent all use single SKILL.md) with scripts for background automation.

## Directory Layout

```
open-stocki/
├── SKILL.md                     # Main skill file (~350 lines)
└── scripts/
    ├── stocki-status-poll.py    # Background status poller
    └── stocki-report-save.py    # Report download + save
```

## SKILL.md Structure

### Frontmatter

```yaml
name: open-stocki
description: "Financial analysis via Stocki agent..."
homepage: https://repo.miti.chat/wangzhikun/open_stocki
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins: ["python3.12"]
      env: ["STOCKI_USER_API_KEY"]
      os: ["darwin", "linux"]
    primaryEnv: "STOCKI_USER_API_KEY"
```

### Body Sections

1. **When to USE / NOT to USE** — mode selection (instant vs quant)
2. **Setup** — MCP server registration, env var config
3. **Core Workflow: Instant Queries** — direct `stocki_instant_query`
4. **Core Workflow: Quant Analysis** — task create → run submit → status poll → report
5. **Tool Reference** — 7 tools with signatures and returns
6. **Task Naming** — conventions for generating task names
7. **Error Handling** — per-error-code behavior table
8. **Output Rules** — verbatim answers, language, timezone defaults

## Scripts

### stocki-status-poll.py

- Usage: `python3.12 scripts/stocki-status-poll.py <task_id> <run_id> [--interval 60] [--timeout 1800]`
- Polls `client.runs.status()` at configurable interval
- Exit 0 on success (prints answer), 1 on error, 2 on timeout
- Reads `STOCKI_USER_API_KEY` from env

### stocki-report-save.py

- Usage: `python3.12 scripts/stocki-report-save.py <task_name> [--output path.md]`
- Resolves task name → task_id via `client.tasks.list()`
- Calls `client.tasks.export_report(task_id)`
- Writes markdown to `--output` (default: `<task_name>.md`)
- Exit 0 on success, 1 on error

Both scripts import `open_stocki.StockiClient` directly (requires open_stocki on PYTHONPATH).

## Design Decisions

- **Single SKILL.md** — all 7 tools fit under 500 lines; no need for references/ split
- **Scripts for automation** — background polling and report saving are deterministic tasks better handled by scripts than inline agent reasoning
- **No MCP dependency in scripts** — scripts use `open_stocki` client directly, avoiding the MCP server layer
- **Requires python3.12** — matches the open_stocki project requirement
