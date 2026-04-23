# OpenClaw-Native open-stocki Skill Design (v1 — Instant Only)

## Context

Redesign the open-stocki OpnClaw skill from scratch for OpenClaw agents. The previous version was shaped around Claude Code's MCP model. This version targets OpenClaw's `exec`-based tool execution model directly, using the raw Stocki agent service at `https://stocki-agent-test.miti.chat/`.

v1 scope: **instant mode only** (quick financial Q&A).

## Architecture

```
open-stocki/
├── SKILL.md                      # Skill metadata + usage guide (~80 lines)
└── scripts/
    └── stocki-instant.py         # Wrapper script (~50 lines)
```

**Flow:**
```
OpenClaw agent
  → exec "python3 {baseDir}/scripts/stocki-instant.py 'A股半导体?'"
       │
       ├── langgraph_sdk.get_client(url)
       ├── client.threads.create()  → new disposable thread
       ├── RemoteGraph("StockiAgent").ainvoke({query, time_prompt, agent_type:"instant"})
       └── print(response["answer"])  → stdout → OpenClaw reads result
```

## Key Design Decisions

- **No open_stocki package dependency** — script uses `langgraph_sdk` + `langgraph` directly (3 SDK calls total)
- **New thread per call** — stateless, no persistent thread tracking
- **Stdout for answers** — OpenClaw reads exec output directly
- **Stderr for errors** — structured error messages to stderr
- **Exit codes:** 0 = success, 1 = auth error, 2 = service error

## SKILL.md Sections

- Frontmatter: name, description, requires (python3, STOCKI_USER_API_KEY), pip install
- When to USE / NOT to USE
- Single usage example with `{baseDir}/scripts/stocki-instant.py`
- Error handling (3 cases: auth_missing, stocki_unavailable, timezone_invalid)
- Output rules (verbatim, language matching)

## stocki-instant.py Interface

```
Usage: python3 stocki-instant.py <question> [--timezone Asia/Shanghai]

Stdin:  not used
Stdout: markdown answer from Stocki
Stderr: error messages
Exit:   0 success, 1 auth error, 2 service error
```

## Dependencies

- `langgraph-sdk>=0.1.0`
- `langgraph>=0.2.0`

## Future (v2)

- Add quant mode: `stocki-quant.py` (create task, submit run, poll status)
- Add report download: `stocki-report.py`
- Potentially extract shared config if multiple scripts need it
