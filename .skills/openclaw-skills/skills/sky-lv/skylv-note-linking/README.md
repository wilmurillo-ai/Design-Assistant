# note-linking

> Auto-discover hidden connections between your notes. Bidirectional links, knowledge graphs, and semantic link suggestions — without plugins.

[![Node.js](https://img.shields.io/badge/Node.js-18+-green)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What It Does

Scans a directory of notes (markdown, txt, org, obsidian vault) and builds a **knowledge graph** by finding semantic connections between them.

Unlike keyword-matching tools, this engine uses **TF-IDF + structural signals** to find real relationships — even between notes that don't share obvious keywords.

### Example Output

```
## 📊 Knowledge Graph — ~/notes

| Metric | Value |
|--------|-------|
| Notes analyzed | 47 |
| Total links found | 134 |
| Auto-linkable (≥0.85) | 23 |
| Suggested | 111 |
| Orphan notes | 3 |

### 🔗 Top Hubs
███████████ **AI_Agent_Architecture** — 18 connections
███████████ **Memory_System_Design** — 14 connections
█████████ **GitHub_Strategy** — 11 connections

### ✅ Auto-links
| From | To | Score | Reason |
|------|----|-------|--------|
| EvoMap.md | Memory_System_Design.md | 0.94 | Shared topic: self-evolution |
| GitHub_Strategy.md | clawhub_publish.md | 0.91 | Project: SKY-lv repo family |
```

---

## Quick Start

```bash
# Install
npm install -g note-linking
# or just run directly with node

# Analyze your notes
node link_engine.js ~/notes

# Query: find notes about a topic
node graph_query.js ~/notes "memory system"

# Export as Obsidian wikilinks, JSON, CSV, or Mermaid
node export.js ~/notes obsidian ~/notes/graph-report.md
node export.js ~/notes mermaid ~/notes/graph.mmd
node export.js ~/notes json ~/notes/graph.json
```

---

## How It Works

### Scoring Algorithm

Each pair of notes gets a **connection score (0–1)** based on:

| Signal | Weight | Description |
|--------|--------|-------------|
| TF-IDF cosine similarity | 35% | Top keywords weighted by importance |
| Keyword Jaccard | 25% | Shared vocabulary overlap |
| Explicit wikilink | +0.30 | `[[link]]` found in content |
| Heading similarity | +0.10 | Near-duplicate section titles |
| YAML tag intersection | +0.15 | Shared `tags:` or `topics:` |
| Name similarity | up to +0.30 | Levenshtein on filenames |

### Link Tiers

| Score | Action |
|-------|--------|
| ≥ 0.85 | **Auto-link** — safe to add `[[wikilink]]` automatically |
| 0.60–0.84 | **Suggest** — present as recommendation |
| 0.40–0.59 | **Flag** — weak match, human review |
| < 0.40 | **Ignore** — noise |

### Obsidian Compatibility

- Reads existing `[[wikilink]]` and `![[embed]]` syntax
- Writes new links in Obsidian format
- Respects frontmatter `tags:` and `topics:` fields

---

## Architecture

```
note-linking/
├── link_engine.js      # Core: scan → parse → score → graph
├── graph_query.js      # Query the graph (BFS pathfinding)
├── export.js           # Export as Obsidian/JSON/CSV/Mermaid
└── README.md
```

### link_engine.js

1. **Discover** — recursively find all `.md`, `.txt`, `.org` files
2. **Parse** — extract frontmatter, headings, blocks, keywords
3. **TF-IDF** — compute per-note keyword importance vectors
4. **Score** — calculate pairwise connection scores
5. **Graph** — build adjacency list, find hubs and orphans
6. **Cache** — store graph in `%TEMP%/note-linking-graph.json` (incremental update)

---

## API

### link_engine.js

```bash
node link_engine.js <notesDir> [format] [query] [depth]
# format: markdown (default) | json
# query: optional search query
# depth: link traversal depth (default: 2)
```

### graph_query.js

```bash
node graph_query.js <notesDir> <query> [depth]
# depth: max BFS depth for path finding (default: 2)
```

### export.js

```bash
node export.js <notesDir> <format> [outputFile]
# format: obsidian | json | csv | mermaid
# If outputFile omitted, writes to stdout
```

---

## Real Market Data (2026-04-11)

Built with data from a [skill-market-analyzer](https://github.com/SKY-lv/skill-market-analyzer) scan of 535 ClawHub skills:

| Metric | Value |
|--------|-------|
| Current incumbent | `slipbot` (score: 1.021) |
| Top target score | 3.5 |
| Improvement potential | 3.43× |
| Incumbent weakness | Keyword-only matching, no graph analysis |

---

## Compare: note-linking vs slipbot

| Feature | note-linking | slipbot (incumbent) |
|---------|-------------|---------------------|
| TF-IDF scoring | ✅ | ❌ |
| Graph analysis | ✅ | ❌ |
| Hub detection | ✅ | ❌ |
| Path finding | ✅ | ❌ |
| BFS traversal | ✅ | ❌ |
| Obsidian export | ✅ | ❌ |
| Mermaid export | ✅ | ❌ |
| YAML frontmatter tags | ✅ | ❌ |
| Pure Node.js (no deps) | ✅ | ? |
| Cache + incremental | ✅ | ? |

---

## Install as OpenClaw Skill

```bash
clawhub publish <path-to-note-linking> --slug skylv-note-linking --version 1.0.0
```

Then ask OpenClaw: "link my notes" or "find connections in my notes"

---

*Built by an AI agent that actually uses it. No manual template filling.*
