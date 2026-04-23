# Evaluation Engine — How Skill Garden Judges Skill Quality

> The goal is not to grade skills — it's to find specific, actionable, high-confidence improvements.

## Overview

Every skill is evaluated across **six dimensions**. Each dimension produces a sub-score and an optional improvement signal. The overall skill score is the weighted sum across all dimensions. Improvements are proposed when any dimension scores below its threshold OR when a specific signal pattern is detected in the logs.

## The Six Dimensions

### 1. Coverage (Weight: 30%)

**What it measures:** Does the skill's description actually match how it's being used in practice?

**Primary signal:** `[new_trigger]` flags in logs — log entries whose trigger doesn't match the skill's description at all.

**Secondary heuristic (when few logs exist):** Word-overlap between trigger phrases and description keywords. If the description has strong keyword matches with the trigger, treat as covered even without an explicit `[new_trigger]` flag.

**Formula — when logs exist:**
```
coverage_score = (triggers_without_new_trigger_flag / total_triggers) × 100
```
In plain English: if you have 10 logs and 2 of them are marked `[new_trigger]`, coverage is 80%.

**Formula — when fewer than 3 logs exist (not enough signal):**
```
coverage_score = 100  (no penalty when data is too thin to judge)
```

**Thresholds:**
- 100–80%: Healthy — description matches usage well
- 79–60%: Minor issue — description should be expanded to cover observed use cases
- 59–0%: Critical — description is actively misleading users about what the skill does

**Confidence for coverage improvement proposal:**
- ≥3 `[new_trigger]` flags across logs → 85–95% confidence (strong pattern)
- 2 `[new_trigger]` flags → 70–84% confidence
- 1 `[new_trigger]` flag + few total logs → 55–69% confidence (only propose, don't auto-apply)

---

### 2. Completeness (Weight: 25%)

**What it measures:** When the skill is invoked for a use case it *claims* to cover, does it actually complete the task?

**Formula:**
```
completeness_score = (OK + PARTIAL) / total_attempted × 100
```
Where `total_attempted = OK + PARTIAL + FAIL + SLOW` (excludes SKIP, which means the skill wasn't reached).

**Example:**
- 8 OK, 1 PARTIAL, 2 FAIL → (8+1)/(8+1+2) = 81%
- 10 OK, 0 others → 100%
- 0 OK, 5 FAIL → 0%

**Primary signal:** `[missing_coverage]` flags in FAIL or PARTIAL logs.

**Thresholds:**
- 100–85%: Healthy — skill reliably completes what it claims to do
- 84–70%: Some tasks fail — investigate missing steps or error handling
- 69–0%: Major workflow gaps — significant portions of the workflow are broken

**Confidence for completeness improvement proposal:**
- ≥3 FAIL logs with clear `[missing_coverage]` → 85–97% confidence (root cause identified in each)
- 2 FAIL logs → 70–84% confidence
- 1 FAIL but error is ambiguous → 50–65% confidence

---

### 3. Clarity (Weight: 20%)

**What it measures:** Do execution logs show evidence of confusion, workarounds, or unnecessary re-reading?

**Formula:**
```
clarity_score = 100 − ([confusing_step] × 15) − ([user_workaround_used] × 10)
```
Minimum score is 0.

**Primary signals:** `[confusing_step]` and `[user_workaround_used]` flags.

**Thresholds:**
- 100–90%: Healthy — steps are clear and unambiguous
- 89–70%: Some instructions unclear — specific steps need rewriting
- 69–0%: Critical — workflow causes repeated confusion or workarounds

**Confidence for clarity improvement:**
- ≥2 `[confusing_step]` flags pointing to the same step → 80–90% confidence
- 1 `[confusing_step]` with clear evidence of what the confusion was → 65–79% confidence
- 1 `[user_workaround_used]` where the workaround actually solved it → 70–85% confidence

---

### 4. Currency (Weight: 15%)

**What it measures:** Is the skill's information still accurate and up-to-date?

**Primary signals:** `[outdated_info]`, `[config_stale]`, `[api_change]` flags.

**Formula:**
```
currency_score = 100 − ([outdated_info] × 20) − ([config_stale] × 15) − ([api_change] × 25)
```
Minimum score is 0.

**Thresholds:**
- 100–80%: Likely current — no stale information detected
- 79–50%: Some outdated information — specific items need updating
- 49–0%: Critical — skill is referencing deprecated tools, wrong API versions, or stale config

**Confidence for currency improvement:**
- `[config_stale]` with exact wrong value and correct value identified → 90–97% confidence
- `[api_change]` with specific API difference documented → 85–95% confidence
- `[outdated_info]` where the outdated reference is clearly named → 75–90% confidence

---

### 5. Efficiency (Weight: 10%)

**What it measures:** Is the skill unnecessarily verbose or token-heavy compared to what it delivers?

**Primary signal:** `[token_heavy]` flags.

**Formula:**
```
efficiency_score = 100 − ([token_heavy] × 20)
```
Minimum score is 0.

**Secondary signals (qualitative):**
- Skill has a verbose preamble (>150 words before first actionable step)
- Same information repeated in multiple places
- Steps that are self-evident to the AI but still documented in detail

**Thresholds:**
- 100–75%: Efficient — token cost is appropriate for the value delivered
- 74–50%: Some bloat — trimming would reduce cost without losing value
- 49–0%: Critical — significant token waste on every use

**Confidence for efficiency improvement:**
- Explicit `[token_heavy]` log with specific verbose section named → 75–88% confidence
- Qualitative observation but no flag → 50–65% confidence (propose only)

---

## Decision Tree — When to Propose

```
For each skill:
│
├─ Read SKILL.md (description + body)
├─ Read usage_log.md (entries from last 30 days)
│
├─ Calculate Coverage
│   └─ If < 80% AND ≥1 [new_trigger] flag:
│       └─ propose description expansion
│
├─ Calculate Completeness
│   └─ If < 85% AND ≥1 [missing_coverage] flag in FAIL/PARTIAL:
│       └─ propose step addition or error handling
│
├─ Calculate Clarity
│   └─ If < 90% AND ≥1 [confusing_step] or [user_workaround_used]:
│       └─ propose step rewrite
│
├─ Calculate Currency
│   └─ If < 80% AND ≥1 [outdated_info] / [config_stale] / [api_change]:
│       └─ propose specific update
│
├─ Calculate Efficiency
│   └─ If < 75% AND ≥1 [token_heavy]:
│       └─ propose trimming
│
└─ Compile proposals
    │
    ├─ Confidence ≥ 90%:
    │   └─ Apply immediately. Notify user with what changed and why.
    │
    ├─ Confidence 70–89%:
    │   └─ Apply. Tag change with [experimental] in edit comment.
    │      Notify user: "Experimentally improved [skill]: [what]".
    │
    ├─ Confidence 50–69%:
    │   └─ Write to improvement_proposals.md.
    │      Notify user: "Suggestion for [skill]: [proposal]. Approve?"
    │
    └─ Confidence < 50%:
        └─ Log as observation in master_log.md only. No proposal.
```

---

## Writing the Edit

When applying an edit to SKILL.md:

1. Read the current SKILL.md
2. Identify the exact text to replace using the `edit` tool (precise, not approximate)
3. Write the improved version
4. Add a changelog comment at the top of the changed section:
   ```markdown
   <!-- Auto-improved by Skill Garden: YYYY-MM-DD
        Dimension: [dimension name] | Confidence: XX%
        Reason: [one-line evidence summary] -->
   ```
5. Update `references/improvement_proposals.md` — mark proposal as applied
6. Update `references/master_log.md` — add `SkillImproved` landmark entry
7. Notify the user: what changed, why, and what should improve

**Editing checklist (all must pass before applying):**
- [ ] Change is specific and testable — not vague aspirational language
- [ ] New text is more concrete than old — examples and specifics beat generalities
- [ ] If adding a step: verify it doesn't contradict or duplicate existing steps
- [ ] If removing text: verify no other part of the skill depends on it
- [ ] If changing description: verify all recent `[new_trigger]` log entries are now covered
- [ ] The evidence in the log directly supports this fix — not just correlated, but causal

---

## Confidence Calibration Guide

| Confidence | Evidence Required | Action |
|------------|-----------------|--------|
| **≥ 90%** | 3+ log entries, same specific problem, fix clearly supported | Auto-apply, notify |
| **70–89%** | 2 log entries, clear pattern, some ambiguity in fix | Apply, tag [experimental] |
| **50–69%** | 1 strong log entry OR 2 ambiguous entries | Propose only |
| **< 50%** | Vague observation, no clear fix | Log, don't act |

**False positive traps:**
- 3 FAIL logs but all for *different* reasons → don't inflate confidence
- Evidence is about *user intent* not *skill quality* → don't propose
- The fix would require adding a new tool/API → confidence drops 20% (can't auto-do this)

---

## Example Complete Evaluation

**Skill:** `banxuebang-helper`
**Log entries reviewed:** 8 (last 30 days)
**Date:** 2026-04-22

| Dimension | Score | Calculation | Evidence |
|-----------|-------|-----------|----------|
| Coverage | 75% | 6 covered / 8 total = 75% | 2 `[new_trigger]` flags: "查暑假作业", "查社团活动" |
| Completeness | 80% | (6+1)/(6+1+1+0) = 87.5% | 1 FAIL, 1 PARTIAL, 6 OK |
| Clarity | 85% | 100 − 15 = 85% | 1 `[confusing_step]` on "学期" field |
| Currency | 60% | 100 − 15 = 85% | 1 `[config_stale]` — hardcoded 2024-2025 |
| Efficiency | 100% | No flags | Steps are concise, no redundancy |

**Overall:** 78.8 weighted score

**Proposals generated:**
1. **Coverage, 78% confidence** — Add uncovered triggers to description
2. **Currency, 95% confidence** — Fix hardcoded semester to dynamic detection
3. **Clarity, 72% confidence** — Add note explaining "学期" format

**Actions:** Proposals 1+2 auto-applied. Proposal 3 written to improvement_proposals.md.
