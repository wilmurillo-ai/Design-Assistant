# Open Stocki OpnClaw Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create an OpnClaw skill (`open-stocki`) with SKILL.md + two helper scripts, publishable to ClawHub, that teaches OpenClaw agents how to use the Stocki financial analyst integration.

**Architecture:** Single `open-stocki/` skill directory containing a SKILL.md (frontmatter + workflow docs + tool reference) and two Python scripts that use `open_stocki.StockiClient` directly for background status polling and report saving.

**Tech Stack:** Python 3.12, `open_stocki` client library, OpnClaw skill format (YAML frontmatter + markdown)

---

### Task 1: Create skill directory and SKILL.md

**Files:**
- Create: `open-stocki/SKILL.md`

**Step 1: Create the skill directory**

```bash
mkdir -p open-stocki/scripts
```

**Step 2: Write SKILL.md**

Write `open-stocki/SKILL.md` with the following complete content:

````markdown
---
name: open-stocki
description: "Financial analysis via Stocki agent. Use for market Q&A, quantitative analysis, backtesting, and sector deep-dives. Supports instant queries (quick answers) and async quant runs (long-running analysis tasks up to 30 minutes with background status tracking)."
homepage: https://repo.miti.chat/wangzhikun/open_stocki
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": {
          "bins": ["python3.12"],
          "env": ["STOCKI_USER_API_KEY"],
          "os": ["darwin", "linux"]
        },
        "primaryEnv": "STOCKI_USER_API_KEY",
        "install": [
          {
            "id": "pip",
            "kind": "pip",
            "packages": ["langgraph-sdk>=0.1.0", "langgraph>=0.2.0"],
            "label": "Install Stocki dependencies (pip)"
          }
        ]
      }
  }
---

# Open Stocki — Financial Analyst Agent

Integrates the Stocki financial analyst (a remote LangGraph-based service) for instant Q&A and async quantitative analysis. The `open_stocki` Python package is the sole interface — all LangGraph SDK details are encapsulated.

## When to USE

- Quick market questions, price checks, news lookups → **instant mode**
- Backtesting, strategy analysis, quantitative modeling, sector deep-dives → **quant mode**
- Anything the user calls "analysis", "research", or "深度分析" → **quant mode**
- Downloading a past quant analysis as a local markdown report

## When NOT to USE

- General web search or non-financial questions
- Local file operations unrelated to Stocki reports
- Real-time trading or order execution (Stocki is analysis-only)

## Setup

### 1. Set environment variable

```bash
export STOCKI_USER_API_KEY="your-key-here"  # add to ~/.zshrc or ~/.bashrc
```

### 2. Install the client

```bash
git clone https://repo.miti.chat/wangzhikun/open_stocki.git
cd open_stocki && pip3.12 install -r requirements.txt
```

Ensure `open_stocki` is importable (add the repo root to `PYTHONPATH` or install it).

### 3. Configure MCP server (for Claude Code integration)

Add to `.claude/settings.json` or `.mcp.json`:

```json
{
  "mcpServers": {
    "stocki": {
      "command": "python3.12",
      "args": ["/path/to/open_stocki/stocki_mcp_server.py"],
      "env": { "STOCKI_USER_API_KEY": "${STOCKI_USER_API_KEY}" }
    }
  }
}
```

## Mode Selection

| Signal | Mode | Action |
|--------|------|--------|
| Quick question, price, news | **Instant** | `client.instant.query(question)` |
| "Analysis", "research", "深度分析", backtesting | **Quant** | Create task → submit run → poll status |
| Ambiguous | **Ask user** | "Quick answer or full quantitative analysis?" |

## Core Workflow: Instant Query

No task setup needed. Uses a persistent per-user thread.

```python
from open_stocki import StockiClient
import asyncio

client = StockiClient()
result = asyncio.run(client.instant.query("A股半导体行业前景?", timezone="Asia/Shanghai"))
print(result.answer)   # markdown response
print(result.cot_id)   # chain-of-thought ID (optional)
```

## Core Workflow: Quant Analysis

Quant runs are async and can take up to 30 minutes.

### Step 1: Create a task

```python
task = await client.tasks.create("半导体行业深度分析")
# task.task_id  — UUID string
# task.name     — the name you chose
```

**Task naming rules:**
- Concise topic in the user's language, no dates
- Examples: `"A股半导体行业分析"`, `"US Macro Outlook"`, `"BTC Quant Strategy"`
- Names must be unique per user (server returns `task_name_conflict` on duplicates)
- On conflict: use a more specific name or resume the existing task

### Step 2: Submit the quant run

```python
run = await client.runs.submit(task.task_id, "半导体量化分析", timezone="Asia/Shanghai")
# run.run_id        — UUID string
# run.status        — "queued" at submission time
# run.queue_position — 1 (next to execute)
```

### Step 3: Monitor status

Use the bundled `scripts/stocki-status-poll.py` for background monitoring:

```bash
python3.12 scripts/stocki-status-poll.py <task_id> <run_id> --interval 60 --timeout 1800
```

Or check manually:

```python
status = await client.runs.status(task.task_id, run.run_id)
# status.status — "queued" | "running" | "success" | "error"
# On success: the answer is in the run status response
```

### Step 4: Download report

Use the bundled `scripts/stocki-report-save.py`:

```bash
python3.12 scripts/stocki-report-save.py "半导体行业深度分析" --output report.md
```

Or programmatically:

```python
report = await client.tasks.export_report(task.task_id)
# report.content  — full markdown report
# report.filename — suggested filename
```

## Tool Reference

### Instant

| Method | Description | Timeout |
|--------|-------------|---------|
| `client.instant.query(query, timezone="Asia/Shanghai")` | Quick financial Q&A on persistent thread | 120s |

Returns `InstantResult(answer: str, cot_id: str | None)`

### Tasks

| Method | Description | Timeout |
|--------|-------------|---------|
| `client.tasks.create(name, description="")` | Create named quant project | 30s |
| `client.tasks.list()` | List all tasks (up to 200, sorted by updated_at desc) | 30s |
| `client.tasks.get_history(task_id, page=1)` | Paginated history (10 runs/page = 20 messages) | 300s |
| `client.tasks.export_report(task_id)` | Extract last AI analysis as markdown | 300s |

### Runs

| Method | Description | Timeout |
|--------|-------------|---------|
| `client.runs.submit(task_id, query, timezone="Asia/Shanghai")` | Submit async quant run (returns immediately) | 30s |
| `client.runs.status(task_id, run_id)` | Check run status (call once, never loop) | 120s |

**Status lifecycle:** `queued → running → success | error`

### Files (v1 stubs — not yet available)

| Method | Status |
|--------|--------|
| `client.files.upload()` | Raises `NotImplementedError` |
| `client.files.list_reports()` | Returns `[]` |
| `client.files.get_report()` | Raises `NotImplementedError` |

## Error Handling

All errors are subclasses of `StockiError` with a `.code` field and `.to_dict()` method.

| Error code | Meaning | Action |
|------------|---------|--------|
| `auth_missing` | `STOCKI_USER_API_KEY` not set | Show: `export STOCKI_USER_API_KEY='your-key-here'` |
| `auth_invalid` | Key rejected | Contact Stocki team to reissue |
| `stocki_unavailable` | API unreachable / timeout | Retry in a few minutes |
| `task_not_found` | Invalid `task_id` | Call `client.tasks.list()` to find valid tasks |
| `task_name_conflict` | Duplicate task name | Use a different name or resume existing task |
| `run_not_found` | Invalid `run_id` | Verify `task_id`, resubmit run |
| `run_error` | Quant run failed server-side | Report error verbatim, offer to resubmit |
| `report_not_found` | No AI messages in task history | Run a quant analysis first |
| `rate_limited` | Too many requests | Wait; check `details.retry_after` |
| `timezone_invalid` | Bad IANA timezone | Retry with `timezone="Asia/Shanghai"` |

## Output Rules

- **Present answers verbatim** — do not paraphrase, summarize, or editorialize
- **Timezone:** Always pass `timezone="Asia/Shanghai"` (Beijing time) explicitly; it controls how "today", "this week" are interpreted
- **Language:** Respond in the user's language; if Stocki's response is in a different language, add a label (e.g., "Stocki's response (in Chinese):")
- **Follow-up:** You may add context or suggest follow-up questions after presenting the answer

## Bundled Scripts

### stocki-status-poll.py

Background poller for long-running quant analyses.

```bash
python3.12 scripts/stocki-status-poll.py <task_id> <run_id> [--interval 60] [--timeout 1800]
```

- Polls `client.runs.status()` every `--interval` seconds (default: 60)
- On `success`: prints the answer to stdout and exits 0
- On `error`: prints the error message to stderr and exits 1
- On timeout (default: 1800s / 30 min): exits 2
- On `queued`/`running`: prints brief status line and continues polling

### stocki-report-save.py

Download and save a quant analysis report as local markdown.

```bash
python3.12 scripts/stocki-report-save.py <task_name> [--output path.md]
```

- Resolves task name → `task_id` via `client.tasks.list()` (case-insensitive substring match)
- Calls `client.tasks.export_report(task_id)`
- Writes markdown to `--output` (default: `<task_name>.md` in current directory)
- Multiple matches: prints all matches with timestamps and exits 1
- No match: prints available tasks and exits 1
````

**Step 3: Verify SKILL.md is well-formed**

```bash
head -20 open-stocki/SKILL.md
wc -l open-stocki/SKILL.md
```

Expected: frontmatter starts with `---`, file is ~300-400 lines.

**Step 4: Commit**

```bash
git add open-stocki/SKILL.md
git commit -m "feat: add open-stocki OpnClaw skill SKILL.md"
```

---

### Task 2: Write stocki-status-poll.py script

**Files:**
- Create: `open-stocki/scripts/stocki-status-poll.py`

**Step 1: Write the script**

Write `open-stocki/scripts/stocki-status-poll.py` with the following content:

```python
#!/usr/bin/env python3.12
"""
Poll a Stocki quant run until it completes or times out.

Usage:
    python3.12 stocki-status-poll.py <task_id> <run_id> [--interval 60] [--timeout 1800]

Exit codes:
    0 — success (answer printed to stdout)
    1 — error (error message printed to stderr)
    2 — timeout (polling exceeded --timeout seconds)
"""

import argparse
import asyncio
import sys
import time

# Ensure open_stocki is importable from the repo root
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from open_stocki import StockiClient, StockiError


async def poll(task_id: str, run_id: str, interval: int, timeout: int) -> int:
    client = StockiClient()
    start = time.monotonic()

    while True:
        elapsed = time.monotonic() - start
        if elapsed >= timeout:
            print(
                f"Timeout: polling exceeded {timeout}s for run {run_id}",
                file=sys.stderr,
            )
            return 2

        try:
            status = await client.runs.status(task_id, run_id)
        except StockiError as e:
            print(f"Error: {e.message}", file=sys.stderr)
            return 1

        if status.status == "success":
            # Fetch the latest history to get the answer
            try:
                hist = await client.tasks.get_history(task_id, page=1)
                if hist.total_pages > 1:
                    hist = await client.tasks.get_history(task_id, page=hist.total_pages)
                ai_msgs = [m for m in reversed(hist.messages) if m["role"] == "ai" and m["content"].strip()]
                if ai_msgs:
                    print(ai_msgs[0]["content"])
                else:
                    print(f"Run {run_id} succeeded (no answer text found)")
            except StockiError:
                print(f"Run {run_id} succeeded (could not fetch answer)")
            return 0

        if status.status == "error":
            msg = status.error_message or status.error or "Unknown error"
            print(f"Run failed: {msg}", file=sys.stderr)
            return 1

        # queued or running — print status and wait
        remaining = timeout - elapsed
        pos = f" (queue position: {status.queue_position})" if status.queue_position else ""
        print(
            f"[{int(elapsed)}s] Status: {status.status}{pos} — "
            f"next check in {min(interval, int(remaining))}s",
            file=sys.stderr,
        )
        await asyncio.sleep(min(interval, remaining))


def main():
    parser = argparse.ArgumentParser(description="Poll a Stocki quant run until completion.")
    parser.add_argument("task_id", help="Task UUID")
    parser.add_argument("run_id", help="Run UUID")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between polls (default: 60)")
    parser.add_argument("--timeout", type=int, default=1800, help="Max seconds to poll (default: 1800)")
    args = parser.parse_args()

    exit_code = asyncio.run(poll(args.task_id, args.run_id, args.interval, args.timeout))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
```

**Step 2: Make it executable**

```bash
chmod +x open-stocki/scripts/stocki-status-poll.py
```

**Step 3: Verify syntax**

```bash
python3.12 -c "import ast; ast.parse(open('open-stocki/scripts/stocki-status-poll.py').read()); print('OK')"
```

Expected: `OK`

**Step 4: Commit**

```bash
git add open-stocki/scripts/stocki-status-poll.py
git commit -m "feat: add stocki-status-poll.py background poller script"
```

---

### Task 3: Write stocki-report-save.py script

**Files:**
- Create: `open-stocki/scripts/stocki-report-save.py`

**Step 1: Write the script**

Write `open-stocki/scripts/stocki-report-save.py` with the following content:

```python
#!/usr/bin/env python3.12
"""
Download a Stocki quant analysis report and save as local markdown.

Usage:
    python3.12 stocki-report-save.py <task_name> [--output path.md]

Resolves task name to task_id via substring match (case-insensitive).
On multiple matches, prints options and exits 1.

Exit codes:
    0 — success (report saved)
    1 — error
"""

import argparse
import asyncio
import sys

# Ensure open_stocki is importable from the repo root
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from open_stocki import StockiClient, StockiError


async def save_report(task_name: str, output: str | None) -> int:
    client = StockiClient()

    # Resolve task name to task_id
    try:
        tasks = await client.tasks.list()
    except StockiError as e:
        print(f"Error listing tasks: {e.message}", file=sys.stderr)
        return 1

    query = task_name.lower()
    matches = [t for t in tasks if query in t.name.lower()]

    if not matches:
        print(f"No task matching '{task_name}'. Available tasks:", file=sys.stderr)
        for t in tasks:
            print(f"  - {t.name} (updated: {t.updated_at})", file=sys.stderr)
        return 1

    if len(matches) > 1:
        print(f"Multiple tasks match '{task_name}':", file=sys.stderr)
        for t in matches:
            print(f"  - {t.name} (id: {t.task_id[:8]}..., updated: {t.updated_at})", file=sys.stderr)
        print("Please use a more specific name.", file=sys.stderr)
        return 1

    task = matches[0]

    # Export report
    try:
        report = await client.tasks.export_report(task.task_id)
    except StockiError as e:
        print(f"Error exporting report: {e.message}", file=sys.stderr)
        return 1

    # Write to file
    out_path = output or report.filename
    Path(out_path).write_text(report.content, encoding="utf-8")
    print(f"Report saved to {out_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Download a Stocki analysis report as markdown.")
    parser.add_argument("task_name", help="Task name (case-insensitive substring match)")
    parser.add_argument("--output", "-o", help="Output file path (default: <task_name>.md)")
    args = parser.parse_args()

    exit_code = asyncio.run(save_report(args.task_name, args.output))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
```

**Step 2: Make it executable**

```bash
chmod +x open-stocki/scripts/stocki-report-save.py
```

**Step 3: Verify syntax**

```bash
python3.12 -c "import ast; ast.parse(open('open-stocki/scripts/stocki-report-save.py').read()); print('OK')"
```

Expected: `OK`

**Step 4: Commit**

```bash
git add open-stocki/scripts/stocki-report-save.py
git commit -m "feat: add stocki-report-save.py report download script"
```

---

### Task 4: Validate the complete skill package

**Files:**
- Verify: `open-stocki/SKILL.md`, `open-stocki/scripts/stocki-status-poll.py`, `open-stocki/scripts/stocki-report-save.py`

**Step 1: Verify directory structure**

```bash
find open-stocki -type f | sort
```

Expected:
```
open-stocki/SKILL.md
open-stocki/scripts/stocki-report-save.py
open-stocki/scripts/stocki-status-poll.py
```

**Step 2: Verify SKILL.md frontmatter is valid YAML**

```bash
python3.12 -c "
import yaml
with open('open-stocki/SKILL.md') as f:
    content = f.read()
# Extract frontmatter between --- markers
parts = content.split('---', 2)
meta = yaml.safe_load(parts[1])
assert meta['name'] == 'open-stocki'
assert 'STOCKI_USER_API_KEY' in meta['metadata']['openclaw']['requires']['env']
print('Frontmatter OK')
print(f'Name: {meta[\"name\"]}')
print(f'Description: {meta[\"description\"][:60]}...')
"
```

Expected: `Frontmatter OK` with correct name and description.

**Step 3: Verify both scripts parse without errors**

```bash
python3.12 -c "import ast; ast.parse(open('open-stocki/scripts/stocki-status-poll.py').read()); print('poll OK')"
python3.12 -c "import ast; ast.parse(open('open-stocki/scripts/stocki-report-save.py').read()); print('report OK')"
```

Expected: Both print `OK`.

**Step 4: Verify scripts show help**

```bash
cd /Users/zhikun/code/open_stocki && python3.12 open-stocki/scripts/stocki-status-poll.py --help
cd /Users/zhikun/code/open_stocki && python3.12 open-stocki/scripts/stocki-report-save.py --help
```

Expected: Each shows usage info with arguments and options.

**Step 5: Check file count and size**

```bash
wc -l open-stocki/SKILL.md open-stocki/scripts/*.py
```

Expected: SKILL.md ~300-400 lines, scripts ~80-100 lines each.

**Step 6: Commit validation pass**

No commit needed — this is a verification task.

---

### Task 5: Final commit with all files

**Step 1: Check overall status**

```bash
git status
```

**Step 2: If not already committed individually, commit all skill files together**

```bash
git add open-stocki/
git commit -m "feat: add open-stocki OpnClaw skill for ClawHub publishing

Includes SKILL.md with full Stocki integration guide (instant + quant
workflows, 7-tool reference, error handling) and two helper scripts:
- stocki-status-poll.py: background poller for long-running quant runs
- stocki-report-save.py: download and save analysis reports as markdown"
```
