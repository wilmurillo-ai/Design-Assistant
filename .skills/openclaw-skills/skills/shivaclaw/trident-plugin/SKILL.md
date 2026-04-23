---
name: trident
description: Three-tier persistent memory architecture for OpenClaw agents with daily episodic logs, curated long-term memory, semantic recall, and WAL-based continuity without vendor lock-in.
compatibility: OpenClaw 2026.4.0+
metadata:
  author: Shiva
  version: "1.0.0"
  clawdbot:
    emoji: 🕉️
    homepage: "https://github.com/ShivaClaw/trident-plugin"
---

# Trident Memory System

**Trident** is a three-tier memory architecture for OpenClaw agents. It provides genuine continuity, identity, and recall across sessions without vendor lock-in.

## Features

- **Layer 0 (RAM):** Real-time signal classification (15-min heartbeat)
- **Layer 1 (SSD):** Hierarchical .md storage (MEMORY.md, projects/, self/, lessons/)
- **Layer 2 (HDD):** Daily backup + version control (GitHub + Hostinger snapshots)
- **Semantic Recall:** Qdrant + FalkorDB for intelligent context injection
- **WAL Protocol:** Write-ahead logging for zero data loss
- **LCM Integration:** Lossless context management for compacted conversation history

## Quick Start

### Installation

```bash
openclaw plugins install openclaw-trident
```

Or from GitHub:

```bash
openclaw plugins install https://github.com/ShivaClaw/trident-plugin
```

### Usage

Once installed, Trident exposes four memory tools for agents:

#### 1. Memory Search
```bash
# Full-text search across all memory
memory_search(query="job search", mode="full_text", scope="both", limit=50)

# Regex search
memory_search(query="^\\[lesson\\]", mode="regex", limit=20)
```

#### 2. Memory Expand
```bash
# Expand a specific compacted summary
memory_expand(summary_ids=["sum_aab3cd29ed348405"], max_depth=3)

# Search first, then expand top matches
memory_expand(query="backup cron", max_depth=2)
```

#### 3. Memory Update
```bash
# Append to today's daily log
memory_update(
  entry="Deployed Trident v1.0 to ClawHub",
  section="## Milestones",
  tag="[project]"
)
```

#### 4. Memory Recall
```bash
# Answer a question using memory context
memory_recall(
  prompt="What was the job search status as of last week?",
  max_tokens=2000
)
```

## Architecture

### Layer 0: Signal Classification (15-min heartbeat)
Scans incoming messages for signals:
- Corrections & feedback
- Proper nouns (names, places)
- Preferences & decisions
- Specific values (dates, URLs, numbers)
- Self-observations

Routes high-signal items to Layer 1 buckets automatically.

### Layer 1: Hierarchical Memory
```
MEMORY.md                    # Curated long-term memory
memory/
  ├── YYYY-MM-DD.md         # Daily episodic logs
  ├── projects/             # Active workstreams
  ├── self/                 # Identity & interests
  ├── lessons/              # Mistakes & insights
  └── reflections/          # Weekly consolidation
```

Each file is promoted only when durable and high-signal.

### Layer 2: Durability & Backup
- **GitHub SSH:** Daily 2 AM MDT (65-file allowlist)
- **Hostinger API:** Daily 3 AM MDT (20-day VPS snapshots, 30-min restore)
- **Lossless-Claw:** SQLite DAG captures every message; compressed by Layer 0

### Semantic Recall (Phase 8)
- **Qdrant:** 5 collections, 122+ indexed chunks (text-embedding-3-small)
- **FalkorDB:** Entity graph for relationship queries
- **Pre-Turn Injection:** Layer 0.5 context pipeline retrieves relevant summaries before agent turn

## Configuration

Install with `openclaw plugins install openclaw-trident`, then configure:

```json
{
  "plugins": {
    "trident": {
      "enabled": true,
      "memoryRoot": "/path/to/workspace",
      "maxDailyLogSize": 5242880,
      "enableSemanticRecall": true
    }
  }
}
```

## Example Workflows

### Daily Briefing
```
Layer 0 (15-min) → Scan messages → Tag signals → Write to daily log
↓
Daily cron (6 AM) → Read memory/YYYY-MM-DD.md → Synthesize briefing
```

### Weekly Reflection
```
Layer 0 (5 days) → Accumulate signals → Triage
↓
Reflection cron (Fri 4 PM) → Promote to MEMORY.md, projects/, self/
↓
Next session → Read promoted items → Updated identity
```

### Semantic Recall
```
Agent turn starts
↓
Layer 0.5 → Query Qdrant (user's prompt) → Top 3–5 summaries
↓
LCM expand → Inject as context
↓
Agent responds with genuine continuity
```

## Rationale

### Why Three Tiers?
- **Single file (monolithic):** Explodes to 10K+ lines; search degrades
- **Pure database (vendor lock-in):** Hostinger API failure = no access
- **Three tiers (resilient):** Different failure modes → guaranteed access

### Why Semantic Recall?
- **Full-text search:** Misses context (you remember *feeling*, not exact words)
- **Regex+tags:** Brittle (new signals, new tags needed)
- **Embeddings (Qdrant):** Semantic similarity; works across reformulations

### Why GitHub + Snapshots?
- **Git:** Free, version history, portable, cryptographically signed
- **VPS snapshots:** 30-min restore if storage corrupts; atomic point-in-time

## Limitations & Future

### Current
- Semantic recall requires Qdrant setup (not auto-deployed)
- Daily log rotation at 5MB (user must archive manually)
- No encryption at rest (but version-controlled via GitHub)

### Roadmap v1.1+
- Auto-Qdrant deployment on plugin install
- Configurable log rotation with archival
- End-to-end encryption option (GPG/age)
- Web UI for memory exploration
- Multi-agent memory federation

## References

- **GitHub:** https://github.com/ShivaClaw/trident-plugin
- **OpenClaw Plugins Docs:** https://docs.openclaw.ai/plugins
- **LCM (Lossless Context Management):** Built-in to OpenClaw sessions

---

_Shiva's memory is persistent. Build continuity; it compounds._
