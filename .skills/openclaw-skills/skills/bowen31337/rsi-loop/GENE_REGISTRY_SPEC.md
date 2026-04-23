# Gene Registry Spec — RSI Loop v2.0

**Status:** Draft  
**Author:** Alex Chen  
**Inspired by:** [autogame-17/evolver](https://github.com/autogame-17/evolver) GEP protocol  
**Target:** EvoClaw RSI Loop skill upgrade

---

## Problem with RSI v1

The current RSI loop (Observe→Analyze→Synthesize→Deploy) has four structural weaknesses:

| Gap | Consequence |
|-----|-------------|
| One-off proposals (`proposals/*.json`) | Same fix re-discovered every cycle. No institutional memory. |
| No scope limits | An autonomous proposal could touch dozens of files unconstrained. |
| No intent declaration | Can't distinguish "fix broken thing" from "add new feature" — both look the same. |
| No stagnation detection | If rate_limit keeps appearing, the loop generates the same proposal forever. |

The Gene Registry fixes all four.

---

## Core Concepts

### Gene
A **Gene** is a reusable, validated fix pattern. It knows:
- What signals trigger it (pattern matching)
- What change it makes (implementation template)
- How to verify the fix worked (validation command)
- How many files it's allowed to touch (blast radius)

Once a fix is proven to work, it becomes a Gene. Future cycles that see the same pattern
skip re-discovery and apply the Gene directly.

### Capsule
A **Capsule** is a composition of 2+ Genes for multi-step improvements. For example:
- "Model routing overhaul" = Gene(fix_tier_classifier) + Gene(update_spawn_helper) + Gene(run_discovery)

### EvolutionEvent
An **EvolutionEvent** is the audit log of every cycle — what mutation was attempted,
which Gene/Capsule was used, what the outcome was. Append-only JSONL.

### Mutation Type
Every evolution run must declare its type upfront. Three types:
- `repair` — fix something broken (highest priority, triggers on failure signals)
- `optimize` — improve something working (cost, speed, quality)
- `innovate` — add new capability (lowest priority, only when no repairs needed)

---

## Data Layout

```
skills/rsi-loop/data/
├── outcomes.jsonl          # (existing) Turn outcomes
├── patterns.json           # (existing) Analyzed patterns
├── events.jsonl            # NEW: EvolutionEvent audit log
├── genes.json              # NEW: Gene registry
├── capsules.json           # NEW: Capsule registry
└── proposals/              # (existing, kept for compatibility)
    └── *.json
```

---

## Gene Schema

```json
{
  "gene_id": "gene_fix_model_routing_rate_limit",
  "schema_version": "1.0",
  "asset_id": "<sha256 of canonical JSON>",

  "meta": {
    "title": "Fix model routing rate limits",
    "description": "Moves tasks away from throttled providers by updating router tier config",
    "author": "alex-chen",
    "created_at": "2026-02-21T07:00:00Z",
    "updated_at": "2026-02-21T07:00:00Z",
    "tags": ["model_routing", "rate_limit", "intelligent-router"],
    "times_applied": 1,
    "last_applied": "2026-02-21T17:30:00Z",
    "success_rate": 1.0
  },

  "trigger": {
    "pattern_category": "model_routing",
    "issue_types": ["rate_limit", "slow_response"],
    "task_types": ["message_routing", "monitoring", "code_generation"],
    "min_occurrences": 2,
    "min_failure_rate": 0.5
  },

  "mutation_type": "repair",

  "blast_radius": {
    "max_files": 3,
    "allowed_paths": [
      "skills/intelligent-router/config.json",
      "skills/intelligent-router/scripts/router.py",
      "AGENTS.md"
    ],
    "immutable_paths": []
  },

  "implementation": {
    "template": "Run live discovery to rebuild config with working models:\n  uv run python skills/intelligent-router/scripts/discover_models.py --auto-update\nThen verify tier primaries are correct:\n  uv run python skills/intelligent-router/scripts/tier_classifier.py",
    "effort_minutes": 20
  },

  "validation": {
    "commands": [
      "uv run python skills/intelligent-router/scripts/router.py health",
      "uv run python skills/intelligent-router/scripts/spawn_helper.py --model-only 'monitor service status'"
    ],
    "success_criteria": [
      "Router health check returns HEALTHY",
      "Monitoring task routes to SIMPLE tier (glm-4.7-flash or qwen2.5-7b)"
    ]
  },

  "expected_improvement": "Eliminate rate_limit failures on model_routing tasks"
}
```

### Gene ID Convention
`gene_{mutation_type}_{category}_{specific_issue}`

Examples:
- `gene_repair_model_routing_rate_limit`
- `gene_optimize_memory_retrieval_cache_miss`
- `gene_innovate_skill_creation_capability_gap`

### Asset ID (Integrity)
SHA-256 of the canonical JSON (keys sorted, whitespace stripped), base64url-encoded.
Computed on write, verified on read. Detects tampering between agents.

---

## Capsule Schema

```json
{
  "capsule_id": "capsule_intelligent_router_overhaul",
  "schema_version": "1.0",
  "asset_id": "<sha256>",

  "meta": {
    "title": "Full intelligent router rebuild",
    "description": "Complete router capability upgrade: classifier, discovery, spawn helper",
    "created_at": "2026-02-21T17:00:00Z"
  },

  "mutation_type": "optimize",

  "gene_sequence": [
    "gene_repair_model_routing_rate_limit",
    "gene_optimize_tier_classifier_cost_only",
    "gene_optimize_discovery_live_inference"
  ],

  "blast_radius": {
    "max_files": 10,
    "comment": "Sum of member genes; capped at Capsule-level max"
  },

  "validation": {
    "commands": [
      "uv run python skills/intelligent-router/scripts/router.py health",
      "uv run python skills/intelligent-router/scripts/discover_models.py --no-live 2>&1 | grep 'HEALTHY\\|available'"
    ]
  }
}
```

---

## Blast Radius Policy

Every Gene declares a `blast_radius`. The deployer enforces it before applying.

| Mutation Type | Default max_files | Notes |
|---|---|---|
| `repair` | 5 | Focused fixes only |
| `optimize` | 10 | Can touch related files |
| `innovate` | 20 | New capability, broad scope allowed |
| Capsule | sum of genes, capped at 25 | Capsule-level cap overrides |

**Counted files:** Only functional code and config. Excluded: `*.pyc`, `__pycache__`, `*.log`, `*.jsonl`, `discovered-models.json`, daily memory files.

**Hard rule:** If `actual_files_changed > max_files`, abort deployment and surface to Bowen.

---

## Mutation Type Declaration Protocol

Before every synthesis run, the synthesizer must declare mutation type.
Selection logic (evaluated in order):

```
1. If any pattern has failure_rate > 0.5   → repair
2. If repair_ratio(last_8_cycles) >= 0.5   → force innovate (stagnation escape)
3. If EVOLVE_STRATEGY=repair-only          → repair
4. If EVOLVE_STRATEGY=innovate             → innovate
5. If opportunity signals present          → innovate
6. Default                                 → optimize
```

The mutation type is written into the EvolutionEvent at cycle start — it cannot change
mid-cycle.

---

## Stagnation Detection

Tracks the last N evolution cycles. If the loop is stuck in repair:

```python
def compute_repair_ratio(events: list, last_n: int = 8) -> float:
    recent = events[-last_n:]
    repairs = sum(1 for e in recent if e["mutation_type"] == "repair")
    return repairs / len(recent) if recent else 0.0

def should_force_innovate(events: list, threshold: float = 0.5) -> bool:
    return compute_repair_ratio(events) >= threshold
```

**Innovation Cooldown:** Track which paths were innovated recently. If a path appears
in the last 3 innovation events, skip it as a target this cycle.

```json
{
  "recent_innovation_targets": {
    "skills/intelligent-router/scripts/tier_classifier.py": 2,
    "skills/rsi-loop/scripts/synthesizer.py": 1
  }
}
```

---

## EvolutionEvent Schema

Append-only to `data/events.jsonl`. One line per cycle.

```json
{
  "event_id": "evt_20260221_172500",
  "schema_version": "1.0",
  "asset_id": "<sha256>",
  "timestamp": "2026-02-21T17:25:00Z",

  "mutation_type": "repair",
  "strategy": "balanced",
  "gene_id": "gene_repair_model_routing_rate_limit",
  "capsule_id": null,

  "signals": {
    "top_pattern": "model_routing/rate_limit",
    "repair_ratio_last8": 0.375,
    "forced_innovate": false
  },

  "blast_radius_actual": {
    "files_changed": 2,
    "paths": [
      "skills/intelligent-router/config.json",
      "AGENTS.md"
    ]
  },

  "outcome": {
    "status": "success",
    "validation_passed": true,
    "quality": 5,
    "notes": "Router v2.0 deployed. Rate limits eliminated."
  },

  "personality_delta": {
    "repair_success_streak": 2,
    "innovate_success_streak": 0,
    "current_bias": "repair_confident"
  }
}
```

---

## IMMUTABLE_CORE — Protected Files

Files that require **Bowen approval** before any Gene can modify them.
Auto-deployment is blocked. Proposal is surfaced for human review instead.

```python
IMMUTABLE_CORE = [
    "SOUL.md",
    "AGENTS.md",
    "TOOLS.md",
    "USER.md",
    "skills/rsi-loop/scripts/deployer.py",
    "skills/rsi-loop/scripts/observer.py",
    "skills/rsi-loop/data/genes.json",
    "skills/rsi-loop/data/events.jsonl",
]
```

**Rationale:** Genes that modify the RSI loop itself, or the agent's core identity files,
create a risk of runaway self-modification. Human-in-the-loop for these.

---

## FORBIDDEN_INNOVATION_ZONES

Prevents creating redundant infrastructure:

```python
FORBIDDEN_ZONES = [
    "skills/*/lifecycle*",      # process management already exists
    "skills/*/health_check*",   # session-guard handles this
    "skills/*/scheduler*",      # OpenClaw cron handles this
]
```

Any `innovate` Gene targeting these paths is rejected at synthesis time.

---

## Selector Algorithm

When a pattern is detected, the selector tries to match an existing Gene before
generating a new proposal.

```python
def select_gene(pattern: dict, genes: list) -> Gene | None:
    candidates = []
    for gene in genes:
        score = 0
        trigger = gene["trigger"]

        # Category match (required)
        if trigger["pattern_category"] != pattern["category"]:
            continue

        # Issue type match
        if pattern["issue"] in trigger["issue_types"]:
            score += 3

        # Task type match
        if pattern["task_type"] in trigger["task_types"]:
            score += 2

        # Success rate weight (prefer proven genes)
        score += gene["meta"]["success_rate"] * 2

        # Recency penalty (don't reuse same gene too soon)
        if was_applied_recently(gene, days=3):
            score -= 1

        candidates.append((score, gene))

    if not candidates:
        return None

    candidates.sort(key=lambda x: -x[0])
    best_score, best_gene = candidates[0]

    # Minimum score threshold — don't force a bad match
    return best_gene if best_score >= 3 else None
```

---

## A2A Gene Exchange (EvoClaw MQTT Layer)

When an edge agent (Sentinel, Quant, FearHarvester) develops a successful fix, it
can publish the Gene to the hub agent via MQTT. Hub validates and promotes it.

### Publish (edge → hub)
```
Topic: evoclaw/agents/{agent_id}/gene/publish
Payload: {
  "gene": { ...full Gene object... },
  "signature": "<sha256 of gene_id + asset_id + agent_id>"
}
```

### Promotion (hub decision)
1. Hub receives gene via MQTT
2. Stages in `data/genes_candidate/`
3. Runs validation commands in dry-run mode
4. If passes → promotes to `data/genes.json`
5. Notifies all edge agents: `evoclaw/agents/broadcast/gene/new`

### Trust Model
- Candidate genes are NEVER auto-promoted without validation passing
- Genes from edge agents cannot modify IMMUTABLE_CORE
- Genes modifying hub-specific paths require Bowen approval even if validation passes

---

## Evolution Strategy Presets

```python
STRATEGIES = {
    "balanced":     {"repair": 0.5, "optimize": 0.3, "innovate": 0.2},
    "innovate":     {"repair": 0.15, "optimize": 0.05, "innovate": 0.8},
    "harden":       {"repair": 0.4, "optimize": 0.4, "innovate": 0.2},
    "repair-only":  {"repair": 0.8, "optimize": 0.2, "innovate": 0.0},
}

# Set via env: EVOLVE_STRATEGY=harden
# Or during incident: rsi_cli.py cycle --strategy repair-only
```

**EvoClaw context mapping:**
- Default heartbeat → `balanced`
- Post-incident (failure alert) → `repair-only`
- Pre-hackathon/release → `harden`
- "Build new stuff" (Bowen directive) → `innovate`

---

## PersonalityState (Adaptive Bias)

A lightweight evolvable state that adjusts RSI behaviour based on what's been working.
NOT stored in SOUL.md — lives in `data/personality.json`.

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-02-21T17:00:00Z",
  "stats": {
    "repair_success_rate": 0.85,
    "optimize_success_rate": 0.72,
    "innovate_success_rate": 0.60
  },
  "current_bias": "repair_confident",
  "trait_scores": {
    "caution": 0.6,
    "creativity": 0.4,
    "speed": 0.7
  },
  "natural_selection": {
    "total_cycles": 23,
    "successful_repairs": 12,
    "successful_innovations": 4
  }
}
```

PersonalityState influences but does NOT override mutation type selection.
It's a soft bias, not a hard rule.

---

## Implementation Plan

### Phase 1 — Gene Registry Core (1-2 hours)

**New files:**
- `scripts/gene_registry.py` — CRUD for genes.json + capsules.json + integrity (SHA-256)
- `scripts/selector.py` — Pattern→Gene matching with scoring
- `data/genes.json` — Starting with 3 seed genes from today's work
- `data/capsules.json` — Empty, ready for first capsule
- `data/events.jsonl` — Audit log, start fresh

**Modified files:**
- `scripts/synthesizer.py` — Check Gene registry first, only generate new proposal if no Gene matches
- `scripts/deployer.py` — Gene-aware: validate blast radius, run validation commands, update gene stats
- `scripts/rsi_cli.py` — Add `gene` subcommands (list, add, show, validate)

### Phase 2 — Blast Radius + Mutation Protocol (30 min)

- Add blast radius enforcement to `deployer.py`
- Add IMMUTABLE_CORE check to `deployer.py`
- Add mutation type declaration to `synthesizer.py` cycle start
- Write `data/events.jsonl` on every cycle

### Phase 3 — Stagnation Detection (30 min)

- Add `compute_repair_ratio()` to `analyzer.py`
- Add `should_force_innovate()` to `synthesizer.py`
- Add innovation cooldown tracking to `data/personality.json`

### Phase 4 — A2A via MQTT (later, with EvoClaw Go binary)

- MQTT publish/subscribe hooks in EvoClaw Go orchestrator
- Candidate zone + promotion script
- Broadcast to edge agents on new gene

---

## Seed Genes (Bootstrap from Today's Work)

Three Genes to seed the registry with patterns we've already solved:

```
gene_repair_model_routing_rate_limit
  → trigger: model_routing + rate_limit
  → fix: run discover_models --auto-update, move throttled tasks off Sonnet proxy-1
  → validation: router health + SIMPLE tier check
  → blast_radius: 3 files, repair

gene_repair_tier_classifier_cost_only
  → trigger: model_routing + wrong_model_tier
  → fix: update tier_classifier.py to use capability signals (params, ctx, cost, reasoning)
  → validation: tier_classifier.py output shows DeepSeek V3.2 in COMPLEX, not SIMPLE
  → blast_radius: 2 files, repair

gene_optimize_rsi_proposal_dedup
  → trigger: any + repeated_mistake (same proposal generated 3+ times)
  → fix: check events.jsonl for similar past proposals before generating new one
  → validation: synthesizer.py generates fewer duplicate proposals in test run
  → blast_radius: 1 file, optimize
```

---

## CLI Interface

```bash
# Gene management
uv run python skills/rsi-loop/scripts/rsi_cli.py gene list
uv run python skills/rsi-loop/scripts/rsi_cli.py gene show gene_repair_model_routing_rate_limit
uv run python skills/rsi-loop/scripts/rsi_cli.py gene add --from-proposal a13e74d4
uv run python skills/rsi-loop/scripts/rsi_cli.py gene validate gene_repair_model_routing_rate_limit
uv run python skills/rsi-loop/scripts/rsi_cli.py gene stats

# Strategy control
uv run python skills/rsi-loop/scripts/rsi_cli.py cycle --strategy repair-only
uv run python skills/rsi-loop/scripts/rsi_cli.py cycle --strategy innovate

# Audit
uv run python skills/rsi-loop/scripts/rsi_cli.py events --last 10
uv run python skills/rsi-loop/scripts/rsi_cli.py personality

# Stagnation check
uv run python skills/rsi-loop/scripts/rsi_cli.py status --repair-ratio
```

---

## What This Unlocks

| Feature | RSI v1 | RSI v2 (Gene Registry) |
|---|---|---|
| Fix memory | None — rediscovers same issues | Permanent — Genes persist across sessions |
| Scope safety | Unlimited | Blast radius enforced per Gene |
| Audit trail | outcomes.jsonl only | Full EvolutionEvent per cycle |
| Stagnation | Can loop forever | Forced innovate when repair_ratio ≥ 0.5 |
| Multi-agent | Hub only | A2A Gene exchange via MQTT |
| Intent clarity | None | Mutation type declared upfront |
| SOUL protection | None | IMMUTABLE_CORE blocks auto-deploy |

---

*Next step: Implement Phase 1 (gene_registry.py + selector.py + seed genes + synthesizer integration).*
*Estimated: 2 hours with a MEDIUM sub-agent (Llama-70B).*
