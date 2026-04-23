# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Stocki is an OpenClaw skill that integrates the Stocki AI financial analyst agent into WeChat via ClawBot. It provides two modes: **instant** (quick Q&A) and **task** (complex quantitative analysis). All scripts call the OpenStocki Gateway HTTP API using Python stdlib only — no pip dependencies.

## Architecture

```
SKILL.md                    # OpenClaw skill definition (frontmatter + docs)
scripts/
├── _gateway.py             # Shared HTTP helper (urllib-based)
├── stocki-instant.py       # POST /v1/instant — quick Q&A
├── stocki-task.py          # Task CRUD (create, list, history)
├── stocki-run.py           # Quant run submit + status check
├── stocki-report.py        # List and download reports
└── stocki-upload.py        # Upload data files to task workspace
docs/plans/                 # Product and system design documents
```

**Key design rule:** All scripts import `_gateway.py` for HTTP requests, auth, and error handling. No external dependencies — only Python stdlib (`urllib.request`, `json`, `argparse`).

## Environment Variables

```bash
export STOCKI_GATEWAY_URL="https://api.stocki.com.cn"
export STOCKI_API_KEY="sk_your_key_here"
```

## Gateway API

Base URL: `$STOCKI_GATEWAY_URL`. Auth: `Authorization: Bearer $STOCKI_API_KEY`.

| Endpoint | Method | Script |
|----------|--------|--------|
| `/v1/instant` | POST | stocki-instant.py |
| `/v1/tasks` | POST/GET | stocki-task.py |
| `/v1/tasks/{id}` | GET | stocki-task.py history |
| `/v1/tasks/{id}/runs` | POST | stocki-run.py submit |
| `/v1/tasks/{id}/runs/{rid}` | GET | stocki-run.py status |
| `/v1/tasks/{id}/reports` | GET | stocki-report.py list |
| `/v1/tasks/{id}/reports/{fn}` | GET | stocki-report.py download |
| `/v1/tasks/{id}/files/upload` | POST | stocki-upload.py |

## Exit Codes

- **0** — Success
- **1** — Auth or client error
- **2** — Service unavailable
- **3** — Rate limited

## Testing Scripts

```bash
# Verify all scripts parse correctly
python3 scripts/stocki-instant.py --help
python3 scripts/stocki-task.py --help
python3 scripts/stocki-run.py --help
python3 scripts/stocki-report.py --help
python3 scripts/stocki-upload.py --help

# Test instant query (requires live Gateway)
python3 scripts/stocki-instant.py "A股今日行情"
```

## Publishing

```bash
# Publish to ClawHub
npx clawhub publish . --slug stocki --version <version> --changelog "..."

# Push to GitHub
git push origin main
```

## Design Documents

- `docs/plans/2026-03-23-openstocki-v1-product-design.md` — Full product spec (auth, quota, viral sharing)
- `docs/plans/2026-03-24-open-stocki-internal-design.md` — Backend architecture (Gateway + LangGraph)
- `docs/plans/2026-03-24-stocki-system-architecture.md` — System overview (3 external paths)
