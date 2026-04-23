---
name: meaningful-chunker
description: "Graph-based code intelligence API. Query any indexed codebase for architecture understanding, debugging, refactor safety analysis, and design principle mapping. Returns structured analysis with ranked chunks, execution paths, root-cause chains, and answer synthesis. Use when asked to analyze codebases, explain what a component does, trace a bug to its source, assess whether a change is safe, or understand the design principles governing a system."
version: 1.2.2
metadata:
  openclaw:
    emoji: "🧠"
    homepage: "https://github.com/DaymyanDogg/Meaningful-Chunker"
    requires:
      env:
        - CHUNKER_API_URL
        - CHUNKER_API_KEY
    primaryEnv: CHUNKER_API_KEY
---

# Meaningful Chunker — Code Intelligence API

A graph-based code analysis system that scans any codebase once, builds a semantic graph of all components and their relationships, then answers natural-language queries against that graph. Returns structured, ranked results with explanation — not raw file dumps.

---

## ⚠️ Required First Step

You MUST scan a codebase before using any query endpoints.

If you skip this, all queries will fail with a `no_scan_loaded` error.

Always start with `POST /scan`. See the **Scanning a Codebase** section below.

---

## 🔐 Authentication Required

All endpoints except `/health` and `/status` require an API key.

Include this header in every request:

```
x-api-key: YOUR_API_KEY
```

Without this header, requests return `401 Unauthorized`. Set your key as `CHUNKER_API_KEY` in your agent's environment.

---

## Setup

Two environment variables are required before using this skill:

```
CHUNKER_API_URL   — Base URL of the hosted API.
                    Example: https://meaningful-chunker-production.up.railway.app
CHUNKER_API_KEY   — Your API key. Get a free key instantly at:
                    https://meaningful-chunker-production.up.railway.app/register/free
                    (100 queries/month, resets each calendar month, no credit card required)
                    Upgrade to Pro (2,000/month) at /upgrade.
```

Full OpenAPI spec available at: `$CHUNKER_API_URL/docs`

---

## When to Use This Skill

Use one of the four query endpoints depending on intent:

| Intent | Endpoint | Example query |
|---|---|---|
| Understand what something does | `/query/architecture` | "What does the authentication module do?" |
| Trace a bug or failure | `/query/debug` | "Why is the login function failing?" |
| Assess safety of a change | `/query/refactor` | "Can I safely change the database connector?" |
| Understand design principles | `/query/philosophy` | "What principle governs error handling here?" |

All four endpoints accept the same request body and return the same response shape.

---

## 🚀 30-Second Quick Start

1. Scan a repo:
POST /scan with {"repo_url": "https://github.com/owner/repo"}

2. Wait until:
GET /status → "ready": true

3. Query:
POST /query/architecture with {"query": "What does X do?"}

## Scanning a Codebase

---

### Scan a GitHub repo (recommended)

```bash
curl -s -X POST $CHUNKER_API_URL/scan \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CHUNKER_API_KEY" \
  -d '{"repo_url": "https://github.com/owner/repo"}'
```

The system clones the repo, builds the graph, and deletes the local clone automatically.
Supports any public GitHub, GitLab, or git URL — including `/tree/main` branch URLs.
Repos larger than 300MB are rejected with a clear error.

### Scan a local path (self-hosted instances only)

```bash
curl -s -X POST $CHUNKER_API_URL/scan \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CHUNKER_API_KEY" \
  -d '{"project_path": "/path/to/project"}'
```

### Check scan progress

```bash
curl $CHUNKER_API_URL/status
```

When `"ready": true` the graph is built and all query endpoints are available. Scanning typically takes 5–30 seconds depending on repo size.

---

## How to Query

### Request format

```bash
curl -s -X POST $CHUNKER_API_URL/query/architecture \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CHUNKER_API_KEY" \
  -d '{"query": "What does the payment processor do?"}'
```

Replace `/query/architecture` with the appropriate endpoint for your intent.

### Optional: session continuity

Pass a `session_id` to maintain context across related queries. The system remembers what you asked recently and biases results toward the same area of the codebase.

```bash
curl -s -X POST $CHUNKER_API_URL/query/debug \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CHUNKER_API_KEY" \
  -d '{"query": "Why is the checkout flow failing?", "session_id": "my-investigation-001"}'
```

---

## ⚡ Quick Read Guide

For fastest results, read the response in this order:

1. `answer_summary` — one sentence telling you what the key component is and why it matters. Start here every time.
2. `primary_path` — the execution chain (`A → B → C`). Shows how things connect structurally.
3. CENTER tier chunks — the exact matches. These ARE the answer.
4. EPIPHANY tier chunks — critical cross-system connections. Don't skip these.
5. `next_step` — actionable follow-up already computed for you.

Everything else (BREAKTHROUGH, RELEVANT) is supporting context. Read it when you need depth, skip it when you don't.

---

## Understanding the Response

### Top-level synthesis fields

```
answer_summary      — One-sentence synthesis. Start here. Tells you what the
                      key component is, its role, and why it matters.

system_explanation  — What the relevant subsystem does as a whole. Multiple
                      components explained together.

primary_path        — The execution chain: "A → B → C". Shows how components
                      connect structurally. Most useful for debugging.

query_profile       — Which intent was detected (architecture/debug/refactor_risk/
                      philosophy). Confirms the system understood your query.

confidence          — "high" / "medium" / "low". Trust signal before reading context.

next_step           — Actionable follow-up. What to look at next.
```

### Debug-specific fields (present on `/query/debug` responses)

```
root_cause_analysis.execution_timeline    — Call chain with [FAILING_CHUNK] bracketed
root_cause_analysis.root_cause_hypotheses — Ranked suspects with confidence + check instructions
root_cause_analysis.top_suspect           — Single highest-suspicion chunk with specific check
```

### Refactor-specific fields (present on `/query/refactor` responses)

```
structural_authority.change_risk   — "untouchable" / "sensitive" / "local"
structural_authority.blast_radius  — How many chunks/files break if this changes
top_risks                          — Top 5 most dangerous chunks in the whole codebase
```

### Context tiers

```
CENTER       (score=100)  — Exact match. This IS what you asked about.
EPIPHANY     (score≥99)   — Critical cross-component connection. Don't skip these.
BREAKTHROUGH (score≥82)   — Direct structural dependency. Important context.
RELEVANT     (score≥70)   — Meaningful but peripheral. Useful for broader understanding.
```

Each chunk includes:
- `name` — component identifier
- `type` — class / function / method / module_code / etc.
- `file` — source file path
- `summary` — one-line description
- `why_matched` — how the system found this chunk
- `neighbors` — adjacent components in the graph
- `explanation` (CENTER/EPIPHANY only) — roles, primary reason, importance summary

---

## Example: Architecture Query

```bash
curl -s -X POST $CHUNKER_API_URL/query/architecture \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CHUNKER_API_KEY" \
  -d '{"query": "What does the UserAuthenticator do?"}'
```

Read: `answer_summary` → `primary_path` → CENTER `explanation.roles` → BREAKTHROUGH `neighbors`

---

## Example: Debug Query

```bash
curl -s -X POST $CHUNKER_API_URL/query/debug \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CHUNKER_API_KEY" \
  -d '{"query": "Why is the login flow not working?"}'
```

Read: `root_cause_analysis.top_suspect` → `execution_timeline` → `root_cause_hypotheses[0]`

---

## Example: Refactor Safety Query

```bash
curl -s -X POST $CHUNKER_API_URL/query/refactor \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CHUNKER_API_KEY" \
  -d '{"query": "Can I safely change the database connection handler?"}'
```

Read: `structural_authority.change_risk` → `blast_radius` → `advice` → `top_risks`

---

## Relevance Tiers — Scoring Reference

| Tier | Score | What it means |
|---|---|---|
| CENTER | 100 | Exact match — this IS the answer |
| EPIPHANY | ≥99 | Critical cross-system connection |
| BREAKTHROUGH | ≥82 | Direct structural dependency |
| RELEVANT | ≥70 | Meaningful peripheral context |

Results capped at: CENTER×3, EPIPHANY×5, BREAKTHROUGH×6, RELEVANT×5. Max 19 chunks per response.

---

## Checking API Health

These endpoints are always open — no API key required:

```bash
curl $CHUNKER_API_URL/health
```

Returns `{"status": "ok"}` when the system is up and a project is indexed.

```bash
curl $CHUNKER_API_URL/status
```

Returns current graph stats: chunk count, edge count, cluster count, shortcut count, last scan time.

---

## ⚠️ Common Issues

- "no_scan_loaded" → You forgot to run /scan
- 401 Unauthorized → Missing x-api-key header

---

## Notes

- Queries are natural language — no special syntax required. "Why is X broken?" works as well as "explain the architecture of X."
- The system is language-agnostic: Python, C++, JSON, Markdown, and plain text files are all indexed.
- Session memory persists within an API session (same `session_id`). Cross-session long-term focus is tracked via insight memory — frequently queried components surface higher automatically.
- Repo scans maintain memory during the active service lifecycle. The same repo URL will accumulate focus signals across queries until the service restarts.
- Large repos (10k+ files) may take up to 2 minutes to scan. Poll `/status` to check progress.
