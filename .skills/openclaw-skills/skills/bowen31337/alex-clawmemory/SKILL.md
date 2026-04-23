---
name: clawmemory
description: Sovereign agent memory engine — self-hosted, privacy-first SQLite store with LLM-based fact extraction (GLM-4.7), hybrid BM25+vector search, contradiction resolution, and OpenClaw plugin for auto-capture/auto-recall. Use when storing structured facts from conversations, querying agent memory semantically, or wiring persistent memory into an OpenClaw agent.
version: 1.0.0
---

# ClawMemory Skill

Sovereign agent memory engine — self-hosted, privacy-first. All data stays local (SQLite) with optional Turso cloud sync.

**Repo:** https://github.com/clawinfra/clawmemory  
**Server port:** `localhost:7437`  
**Last verified:** 2026-03-28

---

## ✅ VERIFIED WORKING PATTERNS (copy-paste ready)

### Start the server

```bash
cd /tmp/clawmemory && ./clawmemory serve --config config.json
# OR with defaults (SQLite at ./clawmemory.db, port 7437, Ollama at localhost:11434)
./clawmemory serve
```

**Guard rules:**
- Ollama must be running for vector search — if not, BM25-only mode activates automatically (no crash)
- Server binds `localhost:7437` by default — not exposed externally
- First run auto-runs migrations (safe to restart)

### Store a fact manually

```bash
curl -s -X POST http://localhost:7437/facts \
  -H "Content-Type: application/json" \
  -d '{"text": "User prefers Python over Go for scripting", "category": "preference", "importance": 0.8}'
```

### Search memory

```bash
# Hybrid BM25 + vector (best quality)
curl -s "http://localhost:7437/search?q=python+preference&limit=5" | python3 -m json.tool

# BM25-only (fast, no Ollama needed)
curl -s "http://localhost:7437/search?q=python+preference&limit=5&mode=bm25" | python3 -m json.tool
```

### Extract facts from a conversation turn (auto-capture)

```bash
curl -s -X POST http://localhost:7437/extract \
  -H "Content-Type: application/json" \
  -d '{
    "turns": [
      {"role": "user", "content": "I always deploy to Hetzner, never AWS."},
      {"role": "assistant", "content": "Got it, using Hetzner for deployments."}
    ]
  }' | python3 -m json.tool
```

### Get user profile

```bash
curl -s http://localhost:7437/profile | python3 -m json.tool
```

### Forget a fact

```bash
curl -s -X DELETE http://localhost:7437/facts/<fact-id>
```

---

## OpenClaw Plugin (TypeScript) — Auto-wire

The plugin at `plugin/` auto-injects memory pre-turn and auto-captures post-turn.

```bash
cd /tmp/clawmemory/plugin && npm install && npm run build
# Copy plugin/dist/ to OpenClaw plugins dir and enable in config
```

Plugin config in `openclaw.config.json`:
```json
{
  "plugins": [
    {
      "id": "clawmemory",
      "path": "./plugins/clawmemory/dist/index.js",
      "config": {
        "serverUrl": "http://localhost:7437",
        "maxContextFacts": 10,
        "minImportance": 0.3
      }
    }
  ]
}
```

**What it does automatically:**
- **Pre-turn:** searches memory for relevant facts → injects as `[Memory context]` block into system prompt
- **Post-turn:** sends conversation turn to `/extract` → stores new facts

---

## Config Reference (config.json)

```json
{
  "server": { "host": "localhost", "port": 7437 },
  "store": {
    "sqlitePath": "./clawmemory.db",
    "tursoUrl": "",
    "tursoToken": ""
  },
  "extractor": {
    "endpoint": "http://localhost:8080/v1",
    "model": "glm-4.7",
    "apiKey": "placeholder"
  },
  "embed": {
    "ollamaUrl": "http://localhost:11434",
    "model": "qwen2.5:7b"
  },
  "decay": {
    "halfLifeDays": 30,
    "minImportance": 0.1,
    "intervalMinutes": 60
  }
}
```

**Key tunables:**
- `extractor.endpoint` → point at any OpenAI-compatible endpoint (GLM-4.7, local Ollama, Anthropic proxy)
- `embed.model` → `mxbai-embed-large` gives better separability than `qwen2.5:7b` for security classification tasks
- `decay.halfLifeDays` → reduce to 7 for short-lived contexts (task sessions), increase to 90 for long-term persona facts

---

## ❌ KNOWN BROKEN / DO NOT USE

- **Turso sync with empty token** — set `tursoUrl: ""` to disable; non-empty URL with empty token causes silent write failures
- **Ollama `llama3.2-vision` for embeddings** — wrong dimensionality, breaks vector search index; use `qwen2.5:7b` or `mxbai-embed-large`
- **Multi-statement SQL migrations** — `go-libsql` can't handle them; each migration must be a single statement

---

## Build from source

```bash
git clone https://github.com/clawinfra/clawmemory /tmp/clawmemory
cd /tmp/clawmemory
go build ./...  # produces ./clawmemory binary
go test ./... -timeout 120s  # all tests should pass
```

**CI status:** `main` branch — golangci-lint v2 requires action@v7 (fixed 2026-03-28, commit `877384b`)

---

## API Reference (quick)

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| POST | `/facts` | `{text, category, importance}` | Store a fact directly |
| POST | `/extract` | `{turns: [{role,content}]}` | LLM-extract + store facts from conversation |
| GET | `/search` | `?q=<query>&limit=N&mode=bm25|hybrid` | Search memory |
| GET | `/profile` | — | Get synthesized user profile |
| DELETE | `/facts/:id` | — | Soft-delete a fact (sets importance=0) |
| POST | `/forget` | `{query}` | Find + soft-delete facts matching query |

Categories: `person`, `preference`, `fact`, `skill`, `relationship`, `event`, `goal`

---

## Integration with OpenClaw workspace

ClawMemory replaces manual `memory/YYYY-MM-DD.md` writes for structured facts. Daily notes remain the primary context store for narrative/decisions; ClawMemory handles queryable structured facts (preferences, skills, relationships).

**When to use ClawMemory vs daily notes:**
- Daily notes: decisions, decisions-with-context, URLs shared, task state → still use these
- ClawMemory: `User prefers X`, `User's email is Y`, `Project Z uses Go` → queryable atomic facts
