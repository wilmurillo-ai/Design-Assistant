---
name: skill-garden
description: "Automatically improves installed skills through passive usage observation and periodic batch analysis. Activates after any skill is used, or when you say grow / improve skill / analyze skills. Uses a three-layer token-efficient architecture: lightweight structured logging after each skill use, weekly isolated-agent batch analysis, and targeted SKILL.md edits for high-confidence improvements. Designed to be invisible - runs passively, accumulates evidence, improves skills over time. Handles its own cron scheduling, dashboard generation, and proposal tracking. Use whenever you want skills to get better automatically through use."
---

# 🌿 Skill Garden — Skill Evolution Engine

> *"Every skill should get better the more you use it."*

## Philosophy

Skill Garden treats skill improvement as a **continuous, invisible process** — not a special operation. It runs passively in the background, accumulating observations from every skill invocation, then periodically synthesizes them into concrete improvements.

**Key design principles:**
- **Token-efficient:** Lightweight structured logs, batch processing, no real-time overhead
- **User-in-control:** High-confidence changes auto-apply; uncertain ones ask first
- **Transparent:** Every change is explained, nothing happens silently without explanation
- **Self-contained:** Manages its own memory, dashboard, proposals, and cron schedule

## Three-Layer Architecture

```
Layer 1 — Passive Observation (near-zero token cost)
  Every skill invocation → 1-line structured log entry
  Abnormal outcomes (FAIL/SLOW) → detailed log with evidence

Layer 2 — Weekly Batch Analysis (isolated agent, ~5-15 min)
  Read all accumulated logs
  Run evaluation engine across 6 dimensions
  Generate specific improvement proposals

Layer 3 — Targeted Modification (low frequency, high precision)
  Confidence ≥ 90% → apply immediately, notify user
  Confidence 70–89% → apply with [experimental] tag
  Confidence 50–69% → write to proposals, ask user
  Confidence < 50% → log as observation only
```

## When This Skill Activates

**Trigger 1 — After every skill use (automatic, passive):**
When any skill finishes executing, immediately log the outcome using the format in `references/usage_tracker.md`. This is the most important layer — it costs almost nothing and feeds everything else.

**Trigger 2 — On user request:**
- "grow this skill" / "improve skill" / "optimize skill"
- "why did this fail" / "analyze this skill"
- "run skill analysis" / "check my skills"
- "skill health" / "skill dashboard"

**Trigger 3 — On schedule (automatic, every Sunday 20:00):**
An isolated agent runs `batch_analyze.py` and `generate_report.py`, applies high-confidence improvements, and sends you a summary.

## Layer 1: Passive Observation

After any skill finishes (any outcome: OK, FAIL, PARTIAL, SLOW, SKIP), immediately write a structured log. Use `log_insight.py` or write directly to the skill's `references/usage_log.md`.

### Log Entry Format

**For OK outcomes with nothing notable (minimal tokens):**
```markdown
## YYYY-MM-DD HH:MM
Trigger: [trigger in ≤10 words]
Outcome: OK
Signal: [one-line finding or "No issues"]
```

**For PARTIAL, FAIL, SLOW outcomes (always log all fields):**
```markdown
## YYYY-MM-DD HH:MM

### Trigger
[What the user asked for, ≤10 words]

### Outcome
OK | PARTIAL | FAIL | SLOW | SKIP

### Signal
[One specific phrase: what this tells us about the skill]
Examples:
  - "Covered: standard use case works perfectly"
  - "Missing: error handling for network timeouts"
  - "Ambiguous: step 3 could be interpreted two ways"
  - "Outdated: API version in skill doesn't match current"

### Evidence
[1-2 sentences. Quote or paraphrase exact output/error. Be specific.]

### Flags
[Comma-separated tags: [new_trigger] [missing_coverage] [confusing_step]
 [outdated_info] [token_heavy] [edge_case] [user_workaround_used]
 [config_stale] [api_change] [Covered] [success_boost]]
```

### Using log_insight.py

```bash
# Quick OK log (minimal)
python3 ~/.openclaw/workspace/skills/skill-garden/scripts/log_insight.py \
  --skill github-trending-summary \
  --trigger "daily top 5 repos" \
  --outcome OK \
  --signal "Covered: standard case"

# Detailed failure log
python3 ~/.openclaw/workspace/skills/skill-garden/scripts/log_insight.py \
  --skill banxuebang-helper \
  --trigger "check homework" \
  --outcome FAIL \
  --signal "Missing: semester selector not dynamic" \
  --evidence "Config hardcoded to 2024-2025 but API shows 2025-2026 is current." \
  --flags "missing_coverage,config_stale" \
  --mark-landmark "SkillImproved"
```

**Rule of thumb:** If you had to pause, reconsider, or work around something — log it with full detail. If it just worked perfectly — log minimally. The goal is signal, not noise.

## Layer 2: Weekly Batch Analysis

Run manually or wait for the Sunday cron trigger.

### Manual Trigger

Say: **"run skill analysis"** or **"grow all skills"**

The analysis does the following in order:

1. **Scan all skills** — read every `references/usage_log.md`
2. **Evaluate each skill** across 6 dimensions (see `references/evaluation_engine.md`)
3. **Generate proposals** — for each skill with score below threshold
4. **Apply high-confidence changes** — auto-edit SKILL.md for confident improvements
5. **Update dashboard** — rewrite `references/dashboard.md`
6. **Notify user** — send summary message

### Running Scripts Directly

```bash
# Full batch analysis (evaluate all skills, generate proposals)
python3 ~/.openclaw/workspace/skills/skill-garden/scripts/batch_analyze.py

# Analyze one skill only
python3 ~/.openclaw/workspace/skills/skill-garden/scripts/batch_analyze.py --skill github-trending-summary

# Dry run (proposals only, don't apply)
python3 ~/.openclaw/workspace/skills/skill-garden/scripts/batch_analyze.py --dry-run --min-confidence 70

# Generate/refresh dashboard
python3 ~/.openclaw/workspace/skills/skill-garden/scripts/generate_report.py

# Output as JSON (for integrations)
python3 ~/.openclaw/workspace/skills/skill-garden/scripts/generate_report.py --output json
```

## Layer 3: Applying Improvements

### The Six Evaluation Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **Coverage** | 30% | Does the skill's description match how it's actually used? |
| **Completeness** | 25% | Are all necessary steps present? Do FAIL events reveal missing coverage? |
| **Clarity** | 20% | Are steps unambiguous? Are there [confusing_step] or [user_workaround_used] flags? |
| **Currency** | 15% | Is the information still accurate? Are there [outdated_info] or [config_stale] flags? |
| **Efficiency** | 10% | Is it unnecessarily verbose or token-heavy? |

See `references/evaluation_engine.md` for the full evaluation algorithm, scoring thresholds, and confidence calibration guide.

### Applying an Edit to SKILL.md

When a proposal meets the confidence threshold:

1. Read the current SKILL.md
2. Identify the exact text to replace using `edit` tool
3. Write the improved version
4. Add a brief changelog note at the top of the edit:
   ```markdown
   <!-- Auto-improved by Skill Garden: YYYY-MM-DD
        Reason: [confidence]% confidence — [evidence summary] -->
   ```
5. Update `references/improvement_proposals.md` to mark as applied
6. Notify the user with a summary of what changed

### Editing Checklist

Before applying any edit:
- [ ] Change is specific and testable (not vague advice)
- [ ] New text is more concrete than old text (examples > statements)
- [ ] If adding a step, verify it doesn't contradict existing steps
- [ ] If removing text, verify no other part of the skill depends on it
- [ ] If changing description, verify all log triggers are now covered
- [ ] Change addresses the flagged evidence, not just the symptom

## Dashboard

The dashboard (`references/dashboard.md`) shows:
- Overall skill ecosystem health
- Per-skill scores across all 6 dimensions
- Recent signals and flags
- Pending proposals
- Weekly outcome distribution
- Recent landmark events

Regenerate with:
```bash
python3 ~/.openclaw/workspace/skills/skill-garden/scripts/generate_report.py
```

## Cron Setup

Set up a weekly Sunday 20:00 analysis run:

```bash
openclaw cron add \
  --name "Skill Garden Weekly Analysis" \
  --schedule '{"kind":"cron","expr":"0 20 * * 0","tz":"Asia/Shanghai"}' \
  --sessionTarget isolated \
  --payload '{"kind":"agentTurn","message":"Run full skill analysis: execute batch_analyze.py then generate_report.py and notify me of any improvements applied.","timeoutSeconds":900}'
```

Or manually trigger with:
```
grow all skills
```

## Reference Files

| File | Purpose |
|------|---------|
| `references/usage_tracker.md` | Full logging schema, log rotation, landmark events |
| `references/evaluation_engine.md` | Scoring algorithm, thresholds, confidence calibration |
| `references/improvement_examples.md` | Real improvement examples with full context |
| `references/dashboard.md` | Auto-generated growth dashboard (don't edit manually) |
| `references/master_log.md` | Grower's own lightweight master log |
| `scripts/log_insight.py` | CLI for writing log entries |
| `scripts/batch_analyze.py` | Core analysis engine |
| `scripts/generate_report.py` | Dashboard generator |

## Examples in Context

### Example 1: Passive Log — Skill Works Perfectly

**User:** "给我推荐一首今天听的歌"
**Skill:** `daily-song-recommender` — succeeds, email sent
**Your action:** Write one-line abbreviated log:
```markdown
## 2026-04-22 09:15
Trigger: daily song recommendation
Outcome: OK
Signal: Covered: standard use case, no issues
```

### Example 2: Passive Log — Skill Fails Due to Missing Coverage

**User:** "查一下这周的数学作业"
**Skill:** `banxuebang-helper` — API error: semester field stale
**Your action:** Write full structured log:
```markdown
## 2026-04-22 21:30

### Trigger
banxuebang: check math homework

### Outcome
FAIL

### Signal
Missing: semester config hardcoded, not dynamic

### Evidence
API returned {"code": 500, "msg": "semester not found"}.
Config in skill has "2024-2025下学期" but actual is "2025-2026下学期".

### Flags
[missing_coverage] [config_stale]
```

### Example 3: Passive Log — New Trigger Not in Description

**User:** "爬一下GitHub今日热榜发到我邮箱"
**Skill:** `github-trending-summary` — works, but user's phrasing not in description
**Your action:** Write log with [new_trigger] flag:
```markdown
## 2026-04-22 10:00

### Trigger
github-trending-summary: crawl and email

### Outcome
OK

### Signal
Covered: but user said "爬" not in description triggers

### Evidence
Skill handled it fine, but description doesn't mention "爬" as a trigger phrase.

### Flags
[new_trigger]
```

### Example 4: User Requests Analysis

**User:** "run skill analysis"
**Your action:**
1. Run `batch_analyze.py --dry-run`
2. Read the proposals from output
3. Apply high-confidence changes (≥90%) via `edit` tool
4. Run `generate_report.py` to refresh dashboard
5. Message user: "Found N improvement(s) — applied X automatically, Y need your review"

### Example 5: Weekly Cron Fires (Sunday 20:00)

**Isolated agent runs full cycle:**
1. `batch_analyze.py` scans all 20 installed skills
2. Finds `github-trending-summary`: 1 [new_trigger] flag, coverage 66%
3. Generates proposal with 65% confidence → written to proposals
4. Updates dashboard
5. You receive: "🌿 Weekly analysis done. github-trending-summary needs description update (65% confidence — needs more data to auto-apply). Review?"
