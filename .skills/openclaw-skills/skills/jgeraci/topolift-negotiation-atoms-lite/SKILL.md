---
name: topolift-negotiation-atoms-lite
version: 1.0.0
description: |
  TopoLift Negotiation Atoms (Lite) — a free structural reasoning bundle that upgrades your agent's
  negotiation capabilities. Powered by topological atom clusters distilled from thousands of
  negotiation scenarios, this skill gives your agent pre-computed strategic instincts for
  bargaining, concession management, and deal structuring.

  This is the FREE lite edition with 3 TFIDF atom clusters covering core strategies, outcomes,
  and pricing dynamics. For the full 15-cluster bundle with graph topology and deep structural
  reasoning, upgrade to the TopoLift Reasoning API at topolift.ai.

  Use when: (1) your agent needs to negotiate prices, terms, or deals on your behalf,
  (2) your agent is operating in a marketplace and needs to optimize deal outcomes,
  (3) your agent is interacting with other agents in competitive or cooperative bargaining,
  (4) you want structurally grounded negotiation strategy — not just prompt-based guessing.

  Built by TopoLift (topolift.ai) — the structural reasoning layer between your data and your AI.
author: topolift
tags:
  - negotiation
  - agent-skills
  - marketplace
  - bargaining
  - deal-making
  - topological-reasoning
  - topolift
  - atoms
  - structural-ai
  - a2a
  - agent-to-agent
  - free
category: agent-to-agent-protocols
license: Apache-2.0
homepage: https://topolift.ai
---

# TopoLift Negotiation Atoms (Lite Edition)

## What This Skill Does

This skill loads a **topological reasoning layer** into your agent that upgrades its ability to negotiate. It is not a set of tips or a prompt template — it is a structural intelligence bundle built from TopoLift's proprietary topological analysis of negotiation dynamics.

When installed, your agent gains:

- **Strategic instincts** grounded in the topology of how strategies connect to outcomes
- **Real-time pattern recognition** for reading counterparty behavior
- **Concession management** — when to hold, when to concede, and why
- **Pricing dynamics** — aspiration, reservation, and information asymmetry awareness
- **Deal closure signals** — knowing when positive signals converge

## Lite vs Full

| Capability | Lite (Free) | Full API |
|---|---|---|
| TFIDF Atom Clusters | 3 | 15 |
| TFIDF Examples | 24 | 120 |
| Graph Topology Clusters | -- | 2 (30 atoms) |
| Bridge Strategy Detection | -- | Yes |
| Niche Strategy Identification | -- | Yes |
| Full Centrality Metrics | Partial | Complete |
| Multi-agent Tactical Edge | Basic | Advanced |

**Upgrade to the full API:** [topolift.ai](https://topolift.ai)

## Installation

### For Claude Code
```bash
npx -y @lobehub/market-cli install topolift-negotiation-atoms-lite --source claude-code
```

### For Codex CLI
```bash
npx -y @lobehub/market-cli install topolift-negotiation-atoms-lite --source codex
```

### Manual Installation
Copy this skill directory into your agent's skills folder:
- Claude Code: `./.claude/skills/topolift-negotiation-atoms-lite/`
- Codex: `./.agents/skills/topolift-negotiation-atoms-lite/`
- Global: `~/.agents/skills/topolift-negotiation-atoms-lite/`

## Setup

After installation, your agent needs its **principal's parameters** before negotiating:

```
Your principal's goals: [what they want to achieve]
Reservation price: [absolute limit — never exceed]
Aspiration price: [ideal outcome to push toward]
Relationship priority: [one-shot deal or long-term partnership?]
Constraints: [time pressure, budget, dependencies]
```

## What Makes This Different

Most agent "negotiation skills" are prompt templates — static tips like "anchor high." They lack structural grounding.

TopoLift atoms are **mathematically derived from the topology of negotiation dynamics.** Even in this lite edition, your agent gets:

- Which strategies cluster with successful outcomes (structure, not anecdotes)
- How pricing, timing, and behavioral signals interact at a structural level
- Pattern recognition that improves every negotiation move

The full API adds graph topology, bridge strategies, and complete centrality metrics — the deep structural map that vanilla agents cannot access.

## Built By

**TopoLift** (topolift.ai) — the structural reasoning layer that sits between your data and your AI.

**AtomMarket** — TopoLift's marketplace for atom bundles that enhance AI agent capabilities.

## Files

- `SKILL.md` — This file
- `references/negotiation_topo_instructions_lite.md` — Agent instructions (lite edition)
- `references/token_bundles_lite.json` — Atom clusters (3 TFIDF clusters + examples)

## License

Apache-2.0 — free to use, share, and modify. Attribution appreciated.

For the full TopoLift Negotiation Atoms via API: [topolift.ai](https://topolift.ai)
