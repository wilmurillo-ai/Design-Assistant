---
name: agent-ops-toolkit
description: |
  Operational backbone for OpenClaw agents: nightly extraction, morning briefs, heartbeat monitoring,
  PARA knowledge graph scaffold, and Kalman-inspired memory decay. Research-backed with GAM-RAG,
  SuperLocalMemory, Retrieval Bottleneck, and MemPO.
metadata:
  openclaw:
    requires:
      bins: ["python3", "bash"]
    triggers:
      - "set up ops"
      - "agent operations"
      - "nightly extraction"
      - "morning brief"
      - "heartbeat"
      - "memory decay"
      - "ops toolkit"
version: 1.0.0
---

# Agent Ops Toolkit Skill

## Overview

Agent Ops Toolkit sets up the operational backbone for any OpenClaw agent. Five core components work together to keep your agent learning, accountable, and in sync with your schedule:

1. **Nightly Extraction** — Consolidates conversations and decisions into atomic facts
2. **Morning Brief** — Daily priorities and overnight activity summary
3. **Heartbeat Monitoring** — Health checks for managed agent loops (stall detection, auto-restart)
4. **Memory Decay** — Kalman-inspired lifecycle management (hot → warm → cold)
5. **PARA Scaffold** — Ready-to-use knowledge graph structure

**Time to setup:** 5 minutes (wizard-driven)  
**Ongoing maintenance:** ~1 minute/day (morning brief review)  
**Cost:** ~$5–10/month on Claude Haiku extraction models  

All components are research-backed and cost-optimized for 24/7 autonomous operation.

## Setup Wizard

The fastest way to get started:

```bash
clawhub install ops-toolkit
bash scripts/setup_ops.sh
```

The interactive wizard prompts for:

1. **Timezone** (default: `America/New_York`)
   - Used for scheduling nightly extractions and morning briefs

2. **Telegram Chat ID** (optional)
   - Where morning briefs are delivered
   - Leave blank to skip morning brief setup

3. **Agent ID** (default from OpenClaw config)
   - Identifies your agent in logs and cron jobs

4. **Extraction Model** (default: `anthropic/claude-haiku-4-5`)
   - Fast, cheap model for nightly fact extraction
   - Haiku handles structured tasks at 1/60th the cost of Opus

5. **Morning Brief Model** (default: `anthropic/claude-haiku-4-5`)
   - Model for synthesis and summary generation
   - Haiku is sufficient for brief writing; upgrade to Sonnet if you want richer prose

**Output:** Two ready-to-use cron configs (`nightly-extraction-cron.json`, `morning-brief-cron.json`) and your PARA scaffold directories.

Next steps shown on-screen; you manually run the `openclaw cron add` commands (for safety, not auto-executed).

## Component Architecture

### 1. Nightly Extraction (`scripts/heartbeat_tick.py`)

**What it does:**
- Runs on schedule (default: 11 PM in your timezone)
- Reads conversation history from your daily notes
- Extracts key facts, decisions, goals, and learnings
- Writes atomic facts to `life/items.json` with metadata

**Why it matters:**
- Consolidates raw experience into retrievable facts
- Removes burden of manual logging
- Enables decay algorithm to age memories appropriately

**Configuration:** `templates/nightly-extraction-cron.json`

**See also:** `references/memory-schema.md` for items.json spec

### 2. Morning Brief (`scripts/decay_sweep.py`)

**What it does:**
- Runs on schedule (default: 8 AM in your timezone)
- Generates curated summary from hot/warm facts and goals
- Delivers to your Telegram chat (or stdout if unconfigured)
- Shows priorities, overnight activity, risks

**Why it matters:**
- Saves 5 minutes of manual context gathering each morning
- Keeps agent aligned with your goals
- Surfaces newly-cold or risky facts

**Configuration:** `templates/morning-brief-cron.json`

**See also:** `references/decay-algorithm.md` for hot/warm/cold definitions

### 3. Heartbeat Monitoring (`scripts/heartbeat_tick.py`)

**What it does:**
- Runs every 30 minutes (configurable)
- Checks managed tmux sessions for progress or stalls
- Detects when output hasn't changed (stall detection via hash)
- Outputs `HEARTBEAT_OK` if healthy, or `ALERT: <message>` + `NEXT: <action>` if intervention needed

**Why it matters:**
- Autonomous loops can hang without visibility
- Early stall detection prevents silent failures
- Auto-restart capability for managed sessions

**Configuration:** `templates/heartbeat-config.json`

**See also:** `references/heartbeat-protocol.md` for protocol details

### 4. Memory Decay (`scripts/decay_sweep.py`)

**What it does:**
- Runs weekly (default: Sunday at 2 AM)
- Classifies facts as hot/warm/cold based on `lastAccessed` field
- Hot facts (accessed < 7 days) remain prominent in summaries
- Warm facts (8–30 days) lower in priority
- Cold facts (> 30 days) removed from summaries but kept in storage
- Frequently-accessed facts (accessCount > 5) get 14-day resistance bonus

**Why it matters:**
- Without decay, memory becomes a graveyard of irrelevant facts
- Decay surfaces active concerns while preserving historical record
- Access-frequency resistance means "living" facts don't age

**Algorithm:** Inspired by GAM-RAG Kalman principle: "fast warm-up for novel signals, conservative refinement for stable ones"

**See also:** `references/decay-algorithm.md` for formal rules and cite

### 5. PARA Scaffold

**What it does:**
- Creates ready-to-use directory structure for knowledge graph:
  - `projects/` — active initiatives
  - `areas/` — ongoing responsibilities (people, companies, expertise domains)
  - `resources/` — reference material (papers, tools, templates)
  - `archives/` — completed/inactive items

**Why it matters:**
- PARA is battle-tested for long-term personal knowledge management
- Pre-built structure removes decision paralysis
- Atomic facts (`items.json`) naturally organize into PARA entities

**See also:** Your Agent's Memory chapter in the quickstart guide

## Generation Flow

After setup:

1. Wizard generates `nightly-extraction-cron.json` with your timezone, agent ID, model choice
2. Wizard generates `morning-brief-cron.json` with your Telegram chat ID (optional)
3. Wizard creates PARA scaffold: `life/{projects,areas,resources,archives}/`
4. You run: `openclaw cron add < nightly-extraction-cron.json`
5. You run: `openclaw cron add < morning-brief-cron.json`
6. Cron jobs activate on next scheduled tick
7. Nightly: facts extracted, `items.json` updated, summaries rewritten
8. Morning: brief composed and delivered
9. Weekly: decay sweep ages cold facts

**All configs are human-editable.** Change models, timezones, or delivery channels anytime.

## Model Routing (Cost Optimization)

The toolkit uses cost-conscious model selection informed by **MemPO** (arXiv:2603.00680):

| Task | Recommended | Cost | Reasoning |
|------|-------------|------|-----------|
| Nightly extraction | Haiku 4.5 | $0.25/1M | Structured fact extraction, no reasoning |
| Morning brief synthesis | Haiku 4.5 | $0.25/1M | Summary + curation, Haiku sufficient |
| Heartbeat check | Haiku 4.5 | $0.25/1M | Hash comparison, minimal LLM use |
| Decay classification | Haiku 4.5 | $0.25/1M | Rule-based (no LLM needed) |
| **Comparison** | Opus 4 | $15/1M | 60× more expensive for same task |

**Result:** Month of nightly extraction + morning briefs ≈ $5–10 vs $300+ with Opus.

Self-managed memory (MemPO) reduces token usage 67–73%, making this feasible.

## Research Context

All design choices are informed by peer-reviewed research:

### GAM-RAG (arXiv:2603.01783)
**Finding:** Kalman-inspired updates apply rapid changes to uncertain memories, conservative refinement to stable ones.  
**Application:** Decay algorithm — new facts (uncertain) update easily; established facts (stable) resist change via access-count resistance.

### SuperLocalMemory (arXiv:2603.02240)
**Finding:** Local-first, 4-layer progressive architecture with Bayesian trust scoring and provenance tracking.  
**Application:** `items.json` schema includes source, timestamp, accessCount (trust signals); stored locally, never cloud-synced.

### Retrieval Bottleneck (arXiv:2603.02473)
**Finding:** Retrieval quality (which facts you surface) matters 20× more than write sophistication (how fancy your summaries are).  
**Application:** Store raw atomic facts, rely on vector search and decay ranking. Skip expensive summarization.

### MemPO (arXiv:2603.00680)
**Finding:** Self-managed memory reduces token cost 67–73% without sacrificing quality.  
**Application:** Agent autonomously prunes/prioritizes via decay; uses cheap extraction models (Haiku); no expensive fine-tuning.

See `references/research-notes.md` for full citations and deeper design mappings.

## Templates & Scripts

### Templates
- `nightly-extraction-cron.json` — Parameterized with `{{TIMEZONE}}`, `{{AGENT_ID}}`, `{{MODEL}}`
- `morning-brief-cron.json` — Parameterized with `{{TIMEZONE}}`, `{{AGENT_ID}}`, `{{MODEL}}`, `{{DELIVERY_CHANNEL}}`, `{{CHAT_ID}}`
- `heartbeat-config.json` — Default heartbeat configuration
- `life-scaffold/` — PARA directory structure

### Scripts
- `setup_ops.sh` — Interactive wizard (bash)
- `heartbeat_tick.py` — Stall detection + restart logic
- `decay_sweep.py` — Weekly fact lifecycle processor

### References
- `memory-schema.md` — Full `items.json` specification
- `cron-templates.md` — Documented cron configs
- `heartbeat-protocol.md` — Deterministic heartbeat protocol
- `decay-algorithm.md` — Formal decay rules with formula
- `research-notes.md` — Paper citations and mappings

## Quick Start

```bash
# 1. Install the skill
clawhub install ops-toolkit

# 2. Run the setup wizard
bash scripts/setup_ops.sh

# 3. Follow the prompts (timezone, Telegram ID optional, model choice)

# 4. The wizard outputs next steps, e.g.:
# "To activate, run:"
#   openclaw cron add < nightly-extraction-cron.json
#   openclaw cron add < morning-brief-cron.json

# 5. Run those commands manually (wizard doesn't auto-execute for safety)

# 6. Done. Your PARA scaffold is created, crons are scheduled.
```

## What You Get

✓ Automated nightly fact extraction (no more manual logging)  
✓ Morning brief delivered to Telegram (5 mins saved each day)  
✓ Heartbeat monitoring for long-running loops (stall detection)  
✓ Memory decay that keeps facts fresh (no information graveyard)  
✓ PARA scaffold ready for immediate use (no setup decisions)  
✓ Cost-optimized model routing ($5–10/month vs $300+)  
✓ Research-backed architecture (GAM-RAG, MemPO, SuperLocalMemory)

## Support & Troubleshooting

- Cron configs not activating? Check timezone in your OpenClaw config.
- Morning brief not delivering? Verify Telegram chat ID and delivery channel.
- Facts not extracting? Check conversation history format in daily notes.
- Heartbeat not detecting stalls? Review heartbeat config and tmux session names.

See your ops documentation and `references/` subdirectory for detailed troubleshooting.
