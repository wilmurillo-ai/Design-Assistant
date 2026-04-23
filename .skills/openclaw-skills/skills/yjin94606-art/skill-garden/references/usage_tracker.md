# Usage Tracker — Structured Logging Schema

> The quality of improvement is only as good as the quality of the logs. Structured, consistent logs are the foundation of the whole system.

## Log File Location

Each skill has its own usage log at:
```
~/.openclaw/workspace/skills/<skill-name>/references/usage_log.md
```

If the `references/` directory doesn't exist, create it before writing logs.

## The Master Log (Grower's Own Record)

The Skill Garden also maintains its own lightweight master log at:
```
~/.openclaw/workspace/skills/skill-garden/references/master_log.md
```

This is a summary log — not full entries, just skill-level outcome counts. It powers the dashboard.

## Log Entry Schema (Full)

Write all fields for PARTIAL, FAIL, SLOW outcomes. Write only Trigger + Outcome + Signal for OK outcomes unless something notable happened.

```markdown
## YYYY-MM-DD HH:MM

### Trigger
≤10 words describing what the user asked the skill to do

### Outcome
OK | PARTIAL | FAIL | SLOW | SKIP

### Signal
One specific phrase: what this outcome tells us about the skill
Format: [Positive finding] or [Problem category]: [specific detail]
Examples:
  - "Covered: common use case works perfectly"
  - "Missing: error handling for network timeouts"
  - "Ambiguous: step 3 could be interpreted two ways"
  - "Outdated: API version in skill doesn't match current"

### Evidence
1–2 sentences max. Be specific. Include actual error messages, command outputs, or user behavior.
DO NOT generalize. Quote or paraphrase exact interactions.

### Flags
Comma-separated list of applicable tags:
  [Covered]              — This use case is fully supported
  [new_trigger]           — User asked for something not in the description
  [missing_coverage]      — Skill couldn't handle this case
  [confusing_step]       — A specific step was unclear
  [outdated_info]        — Information in the skill is stale
  [token_heavy]          — The skill used more tokens than necessary
  [edge_case]             — This involved an unusual boundary condition
  [user_workaround_used] — Agent or user worked around the skill
  [config_stale]          — Configuration values are outdated
  [api_change]            — External API behavior changed
  [success_boost]         — An exceptional result worth noting
```

## Abbreviated Log Format (For OK Outcomes With Nothing Notable)

```markdown
## YYYY-MM-DD HH:MM
Trigger: [trigger in ≤10 words]
Outcome: OK
Signal: [one-line finding or "No issues"]
```

**Example:**
```markdown
## 2026-04-22 10:30
Trigger: github-trending-summary: morning top 5
Outcome: OK
Signal: Standard execution, no issues
```

## Master Log Format (Skill Garden's Own Log)

For the master log, use this even more abbreviated format:

```markdown
## YYYY-MM-DD
- skill-name: OK(3) PARTIAL(1) FAIL(0)
- another-skill: OK(5) FAIL(1)
- skill-with-issues: FAIL(2) [proposal: pending]
```

This is updated weekly during batch analysis, not per-session.

## Log Rotation and Pruning

### When to Compact Logs

When a usage_log.md exceeds 500 lines, compress the oldest 50% of entries into a summary format:

```markdown
## Compacted entries: YYYY-MM-DD to YYYY-MM-DD (N entries)
Most common trigger: [trigger phrase] (N times)
Overall outcome distribution: OK(N) PARTIAL(N) FAIL(N)
Key signals: [list of unique signals from this period]
```

Keep the most recent 50% in full detail. Move the compacted summary to `references/usage_archive.md`.

### When to Delete Old Logs

- Logs older than 90 days can be archived or deleted if the skill is stable
- If a skill hasn't been used in 60 days, archive its log and start fresh
- If a skill is deleted/uninstalled, archive its log to `~/.openclaw/workspace/skills/skill-garden/references/archived_logs/`

## Special Event Logging

### Landmark Events (Write to Grower's Own Memory)

For exceptional events, also write a 1-line summary to `memory/skill-garden.md`:

```
## Landmark: YYYY-MM-DD
[Skill name]: [Event type] — [1-line description]
```

Event types:
- `SkillImproved`: A skill's SKILL.md was edited
- `HighConfidenceFail`: A skill failed 3+ times in one week
- `NewSkillInstalled`: A new skill was added to the workspace
- `SkillUninstalled`: A skill was removed
- `ProposalGenerated`: A significant improvement proposal was created
- `ProposalRejected`: User rejected an improvement proposal

### Example Landmark Entry

```markdown
## Landmark: 2026-04-22
banxuebang-helper: SkillImproved — semester config now dynamic
github-trending-summary: HighConfidenceFail — GitHub Search API rate limit not handled (3 fails this week)
```

## Cross-Skill Pattern Detection

Sometimes the same issue appears across multiple skills. The grower's memory should note these as **systemic patterns**:

```markdown
## Systemic Pattern: YYYY-MM-DD
[Pattern]: Multiple skills fail on the same external API error handling
Affected skills: [skill-a], [skill-b], [skill-c]
Proposed fix: Add a references/error_handling_guide.md and reference it from all three
Confidence: 65%
Status: Pending user decision
```

## Log Quality Checklist

Before finalizing any log entry, ask:

- [ ] Is the Trigger ≤ 10 words and specific enough to search for?
- [ ] Is the Signal a concrete observation, not a vague impression?
- [ ] Is the Evidence quoted/paraphrased from actual output, not invented?
- [ ] Are the Flags specific and actionable?
- [ ] Would I be able to make a decision based only on this log entry in 3 months?
