# Decay Algorithm — Formal Memory Lifecycle Rules

Complete specification for autonomous memory decay. Runs weekly via `decay_sweep.py`, classifies facts as hot/warm/cold, updates summaries.

---

## Overview

Memory decay prevents the graveyard problem: old, irrelevant facts cluttering your agent's context.

**Principle (GAM-RAG, arXiv:2603.01783):** Kalman-inspired updates apply rapid changes to uncertain signals (new facts) and conservative refinement to stable signals (frequently-used facts).

**Applied to decay:** New facts age quickly; established facts resist aging.

---

## Classification Rules

Every fact has three states based on age and usage:

### Hot (Recently Active)

**Condition:** `effective_age < 7 days`

**Characteristics:**
- Accessed within last 7 days
- Prominent in summaries
- High retrieval priority
- Frequently referenced

**Example:**
- Fact: "Ship v1.2 by end of sprint"
- Last accessed: 2 days ago
- Access count: 5
- Effective age: 2 - 0 = 2 days
- Status: **Hot** (< 7 days)

**In summaries:** Always included, top priority

**In retrieval:** Highest priority, fetch first

---

### Warm (Moderately Active)

**Condition:** `7 <= effective_age < 30 days`

**Characteristics:**
- Accessed 8–30 days ago
- Still relevant but less urgent
- Included in summaries but lower priority
- Retrieved on-demand, not by default

**Example:**
- Fact: "Q2 roadmap focuses on API performance"
- Last accessed: 20 days ago
- Access count: 3
- Effective age: 20 - 0 = 20 days
- Status: **Warm** (8–30 days)

**In summaries:** Included, lower section, lower prominence

**In retrieval:** Moderate priority, fetch after hot

---

### Cold (Inactive/Archived)

**Condition:** `effective_age >= 30 days`

**Characteristics:**
- Accessed 30+ days ago
- Archived, not active
- Removed from summaries
- Kept in storage for historical record
- Only retrieved if explicitly searching history

**Example:**
- Fact: "Experimented with Rust for CLI (didn't pursue)"
- Last accessed: 60 days ago
- Access count: 1
- Effective age: 60 - 0 = 60 days
- Status: **Cold** (>= 30 days)

**In summaries:** Not included (removed by decay_sweep)

**In retrieval:** Low priority, only on explicit historical search

---

## Resistance Formula

Not all facts age equally. Frequently-used facts resist decay.

### Formula

```
effective_age = days_since_last_access - (14 if accessCount > 5 else 0)
```

### Interpretation

- **Base age:** Days since last access
- **Resistance bonus:** +14 days if accessed more than 5 times
- **Meaning:** Facts with accessCount > 5 are "stable" and get bonus time before cooling

### Why This Works (GAM-RAG)

Kalman filtering principle: **stable signals resist change, uncertain signals update quickly.**

- **New facts** (accessCount = 0–5) → uncertain → age at normal rate
- **Established facts** (accessCount > 5) → stable → resist decay via bonus

### Examples

#### Example 1: New Fact, Not Accessed Much

```
Fact: "User wants to explore GraphQL" (from yesterday's conversation)
Last accessed: 1 day ago
Access count: 1 (mentioned once)
Effective age: 1 - 0 = 1 day
Status: Hot (< 7)
```

This fact is hot because it's new. Even though it's only been referenced once, it's recent enough to be relevant.

#### Example 2: Frequently-Used Fact, Older

```
Fact: "Revenue model is subscription"
Last accessed: 22 days ago
Access count: 12 (referenced in many decisions)
Effective age: 22 - 14 = 8 days
Status: Warm (8-30, not cold!)
```

This fact is warm (not cold) because it's been referenced 12 times. The +14 day bonus prevents it from aging into cold.

**Without resistance:** Would be warm (22 days → warm)  
**With resistance:** Still warm (effective 8 days → warm)

#### Example 3: Old, Never Referenced

```
Fact: "Evaluated tool X in March" (now June)
Last accessed: 90 days ago
Access count: 0
Effective age: 90 - 0 = 90 days
Status: Cold (>= 30)
```

This fact is cold because it's old and never referenced. It's archived (kept in storage, not in summary).

---

## Classification Algorithm

```
def classify_fact(fact):
    days_since_access = (now - fact.lastAccessed).days
    access_count = fact.accessCount
    
    # Apply resistance bonus for frequently-used facts
    resistance_bonus = 14 if access_count > 5 else 0
    effective_age = days_since_access - resistance_bonus
    
    # Classify
    if effective_age < 7:
        fact.status = "active"  # Hot
    elif effective_age < 30:
        fact.status = "warm"     # Warm
    else:
        fact.status = "cold"     # Cold
    
    return fact
```

---

## Weekly Decay Sweep

Decay sweep (`decay_sweep.py`) runs weekly (default: Sunday 2 AM).

### Process

1. **Scan all items.json** under `life/` (PARA structure)
2. **For each fact:**
   - Calculate days_since_access
   - Apply resistance bonus (if accessCount > 5)
   - Classify as hot/warm/cold
   - Update status field
3. **Rewrite summary.md:**
   - Include hot facts (first section)
   - Include warm facts (second section)
   - Exclude cold facts (note count in summary)
   - Keep cold facts in items.json (never delete)
4. **Output:**
   - "X facts cooled, Y facts reactivated, Z summaries updated"

### Example Output

```
$ decay_sweep.py --base-path life/
3 facts cooled, 1 fact reactivated, 2 summaries updated
```

**Meaning:**
- 3 facts moved from warm → cold (not in this summary anymore)
- 1 fact moved from cold → warm (got referenced, came back to life)
- 2 summary.md files were rewritten

---

## Summary Rewriting

After classification, summaries are regenerated.

### Before Decay

```markdown
# Summary
- Revenue model is subscription (referenced 100 times, very relevant)
- Experimented with Rust (old experiment, not pursuing)
- User wants GraphQL (recent request, high priority)
- Q2 roadmap: API performance (moderate priority)
```

### After Decay (Hot + Warm Only)

```markdown
# Summary

## Active (Hot)
- User wants GraphQL (recent request, high priority)
- Revenue model is subscription (referenced 100 times, very relevant)

## Warm (Older)
- Q2 roadmap: API performance (moderate priority)

## Archived
(1 cold fact in items.json, see there for history)
```

**Effect:** Summary is shorter, focused on what's relevant now. Cold facts are kept (never deleted) but not cluttering.

---

## No Deletion, Only Status Change

**Critical rule:** Facts are never deleted from `items.json`.

Only the status field changes:
- `active` → `warm` → `cold` (normal aging)
- `cold` → `warm` → `active` (re-referenced)
- Manual: `* → superseded` (human marks as obsolete, but fact stays)

**Why:** Full audit trail. You can search history, understand old decisions, trace reasoning.

---

## Re-Activation (Cold → Warm)

If you reference an old fact, it comes back to life.

**Example:**
```
Fact: "We evaluated Rust in Q1" (cold, 180 days old, accessCount=0)

Day 200: You ask agent: "Should we reconsider Rust?"
Agent retrieves the fact, increments accessCount to 1, updates lastAccessed

Next decay sweep:
  effective_age = 200 - 0 = 200 days → But accessCount=1
  Status changes: cold → cold (still cold because now 200 days old)
  
Day 215: You reference it again in discussion (accessCount=2)
Next decay:
  effective_age = 215 - 0 = 215 → cold
  But if you keep referencing it (accessCount > 5), it gets bonus
```

Facts can resurrect from cold if they become relevant again.

---

## Decay Schedule

Default: **Weekly, Sunday at 2 AM**

Configurable via cron: Edit `decay-sweep-cron.json` schedule field.

**Why Sunday night?** Low activity time, won't interfere with work.

**Alternative schedules:**
- `0 2 * * 0` — Every Sunday at 2 AM
- `0 2 * * 1-5` — Every weekday at 2 AM (if you prefer frequent decay)
- `0 23 * * 0` — Sunday at 11 PM (sync with nightly extraction)

---

## Cost of Decay

**Computational:** Near-zero (just file I/O + hash comparison)

**Tokens:** Zero (decay_sweep.py has no LLM calls; it's pure logic)

**Storage:** Minimal (only status field changes, facts never deleted)

**Summary:** Decay is extremely cheap to run, so run it frequently (weekly or even daily) without worry.

---

## Monitoring Decay

Check decay output weekly:

```bash
# After decay run (or manual trigger)
$ openclaw cron logs decay-sweep

# Manual trigger for testing
$ decay_sweep.py --base-path life/ --dry-run
# Preview without writing changes

# Check fact statuses
$ grep '"status"' life/*/items.json | sort | uniq -c
# Shows distribution of active/warm/cold
```

---

## Research Backing

**GAM-RAG (arXiv:2603.01783):** Kalman-inspired updates on uncertain vs. stable signals. Directly maps to:
- New facts (uncertain) → fast age decay
- Frequent facts (stable) → resistance bonus

**SuperLocalMemory (arXiv:2603.02240):** Local-first storage with full provenance. Decay never deletes; only status changes. Historical audit trail preserved.

**MemPO (arXiv:2603.00680):** Self-managed memory. Agent autonomously applies decay (you don't manually prune). Reduces complexity 67–73%.

---

## Troubleshooting Decay

### Facts aging too fast

1. Check lastAccessed field: Is it being bumped correctly when facts are used?
2. Check accessCount: Is it being incremented?
3. Verify decay_sweep is running: Check logs
4. Manually fix: Edit items.json directly if needed

### Summaries not updating

1. Verify summary.md files exist: `ls life/*/summary.md`
2. Check decay logs: `openclaw cron logs decay-sweep`
3. Manually rewrite: `decay_sweep.py --base-path life/` (non-dry-run mode)

### Cold facts should come back

1. Reference the fact (accessCount bumps)
2. Wait for next decay sweep (weekly)
3. Check status field: should move from cold → warm if accessCount > 5

