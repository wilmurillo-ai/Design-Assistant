# MEMORY.md — Skill Garden Self-Record

> Skill Garden's own persistent memory. Updated after batch analysis runs and when significant events occur.

## Identity
- **Name:** Skill Garden (formerly "Skill Auto-Grower")
- **Slug:** skill-garden
- **Created:** 2026-04-22
- **Purpose:** Make all installed skills improve automatically through passive usage observation

## Design Philosophy

**Three-layer token-efficient architecture:**
- Layer 1: Passive observation — ~50-100 tokens per OK log, ~150-300 per FAIL log
- Layer 2: Weekly batch analysis — isolated agent, doesn't affect main session cost
- Layer 3: Targeted edits — only when confidence ≥ 90%

**Core insight:** Improvement quality depends entirely on log consistency. Structured abbreviated format (Trigger/Outcome/Signal/Flags) captures signal at ~15% of natural language token cost.

## Architecture

```
~/.openclaw/workspace/skills/skill-garden/
├── SKILL.md                          ← Entry point (human-readable documentation)
├── MEMORY.md                         ← Self-record (this file)
├── references/
│   ├── usage_tracker.md             ← Logging schema + rotation rules
│   ├── evaluation_engine.md          ← Scoring algorithm + confidence calibration
│   ├── improvement_examples.md        ← Real improvement cases with full context
│   ├── dashboard.md                  ← Auto-generated growth dashboard
│   ├── master_log.md                 ← Skill-level outcome summaries
│   └── improvement_proposals.md       ← Pending/in-progress proposals
└── scripts/
    ├── log_insight.py               ← CLI logger (piping-friendly)
    ├── batch_analyze.py              ← Core analysis engine (14KB, fully rewritten)
    └── generate_report.py           ← Dashboard generator
```

## Formula Changes (v2)

**v1 bugs fixed in v2:**

1. **Completeness formula** — was `(OK / non_FAIL) × 100`. If 5 OK + 5 FAIL → 5/5 = 100% (wrong, inflated). Now `(OK + PARTIAL) / attempted × 100` where attempted = OK + PARTIAL + FAIL + SLOW.

2. **Coverage scoring** — was purely keyword overlap (too crude). Now uses `[new_trigger]` flags as primary signal, keyword overlap only as secondary heuristic when fewer than 3 logs exist.

3. **Efficiency penalty** — was `×15` per [token_heavy], now `×20` to match evaluation_engine.md.

4. **Confidence calibration** — now calibrated per-dimension with clear ranges matching the evaluation engine guide.

## Key Invariants

- Skill never modifies another skill's SKILL.md without at least 1 log entry supporting the change
- SKIP outcomes are excluded from completeness calculation (skill wasn't attempted)
- Completeness and coverage use different signals (coverage = description match; completeness = success rate given coverage)
- Confidence < 50% never generates a proposal — logged only in master_log.md

## Current State (2026-04-22)

- **Cron job:** Weekly Sunday 20:00 (Asia/Shanghai), isolated agent
- **Skills tracked:** 20
- **Log entries so far:** 1 (github-trending-summary, 2026-04-22)
- **Pending proposals:** 0 (insufficient data yet — github-trending-summary has 65% coverage confidence, needs ≥50% to propose, but only 1 log entry)

## Landmark Events

| Date | Event | Detail |
|------|-------|--------|
| 2026-04-22 | Skill born | Renamed from "skill-auto-grower" → "skill-garden" |
| 2026-04-22 | Formula v2 | Fixed completeness, coverage, and efficiency formulas |
| 2026-04-22 | Batch engine | batch_analyze.py fully rewritten with corrected formulas |
| 2026-04-22 | Weekly cron | Set for Sundays 20:00 (Asia/Shanghai) |

## Known Limitations

1. **Coverage heuristic is approximate** — keyword overlap doesn't understand semantic intent. With enough logs, [new_trigger] flags become the real signal.

2. **Can't detect improvements requiring new tools** — SKILL.md text and structure only. Can't autonomously add new API integrations.

3. **Confidence is still calibrated by rule-of-thumb** — as real improvement data accumulates, the confidence ranges should be empirically refined.

4. **Log compaction not yet automated** — when usage_log.md exceeds 500 lines, must manually compact. The `log_insight.py --compact` flag is planned.
