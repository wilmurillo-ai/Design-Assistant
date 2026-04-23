---
name: agent-ci
description: Continuous AI testing and agent-driven quality automation for development workflows. Use when setting up agent-based CI/CD integration, implementing autonomous testing patterns, creating specialized QA agent councils, building self-healing test pipelines, or automating quality checks that require reasoning (doc/code mismatches, semantic regressions, dependency drift, test coverage expansion). Applies to projects needing continuous quality checks beyond deterministic CI rules.
---

# Agent CI - Continuous AI for Development Quality

Continuous AI extends CI/CD by applying AI agents to quality tasks that require reasoning, interpretation, and context—work that traditional CI cannot handle because it depends on understanding intent rather than enforcing rules.

## Core Concepts

**Continuous CI vs Continuous AI:**
- CI handles deterministic rules: tests pass/fail, builds succeed/don't, linters flag violations
- Continuous AI handles judgment-heavy tasks: doc/code alignment, semantic changes, dependency drift, performance regressions requiring context

**Key patterns:**
1. Natural-language rules express intent that cannot be reduced to heuristics
2. Agents evaluate repositories continuously (on schedule, PR events, pushes)
3. Outputs are artifacts developers can review (PRs, issues, reports)
4. Developers retain final authority; agents never auto-merge

## When to Use Agent CI

Use agent-based testing when:
- Documentation frequently drifts from implementation
- Test coverage lags behind feature velocity
- Dependencies change behavior without version bumps
- Performance regressions hide in context-dependent code paths
- UI/UX changes need interaction testing at scale
- Translation/localization updates batch too late
- Quality checks require semantic understanding

Do NOT use for:
- Tasks expressible as deterministic rules (use traditional CI)
- Simple lint violations or formatting
- Binary pass/fail validation

## Design Patterns

### Pattern 1: Single-Agent Workflows

Use when a task is linear and self-contained.

**Structure:**
```markdown
on: [trigger]
permissions: read
safe-outputs:
  create-pull-request:
    title-prefix: "[auto] "
---
[Natural-language instruction expressing intent]
```

**Example: Doc/Code Alignment**
```markdown
on: pull_request
permissions: read
safe-outputs:
  create-pull-request:
    title-prefix: "[docs] "
---
Analyze changed functions and compare docstrings to implementation.
For any mismatches:
- Explain the divergence
- Propose concrete fixes (update code OR docs)
- Open a PR with the fix
```

**Best for:**
- Doc/code sync
- Translation updates
- Performance optimization suggestions
- Dependency drift detection

### Pattern 2: Multi-Agent Council

Use when quality requires specialized roles and iteration.

**Structure:**
```
Orchestrator (routes tasks)
  ↓
Phase 1: Analysis (feature analysis, selector mapping)
  ↓
Phase 2: Planning (test plan with priorities)
  ↓
Phase 3: Generation (write test code)
  ↓
Phase 4: Quality Gate (audit for violations)
  ↓
Phase 5: Healing (iterate until passing)
  ↓
Phase 6: Documentation (record results)
```

**Example: QA Council (from OpenObserve)**

Agents:
1. **Analyst** - Extract selectors, map workflows, identify edge cases → Feature Design Doc
2. **Architect** - Create prioritized test plan (P0/P1/P2) → Test Plan
3. **Engineer** - Write Playwright tests following Page Object Model → Test Code
4. **Sentinel** (Quality Gate) - Audit for framework violations, anti-patterns, security issues → BLOCKS if critical
5. **Healer** - Run tests, diagnose failures, fix issues, iterate up to 5x → Passing Tests
6. **Scribe** - Document in test management system → Documentation

**Best for:**
- E2E test automation
- Complex multi-step validation
- Tasks requiring iteration to success
- Quality enforcement with hard gates

**Key insight:** Specialization beats generalization. Bounded agents with clear roles outperform "super agents."

### Pattern 3: Continuous Reporting

Use when synthesis across data sources provides ongoing value.

**Example:**
```markdown
on: schedule (daily)
permissions: read
safe-outputs:
  create-issue:
    title-prefix: "[status] "
---
Analyze repository activity over the last 24 hours:
- Summarize merged PRs and commits
- Highlight emerging bug trends
- Correlate test failures with recent changes
- Surface areas of high churn

Create an issue with the daily report.
```

**Best for:**
- Daily/weekly status digests
- Bug trend analysis
- Churn detection
- Activity summaries for managers

### Pattern 4: Interaction Testing

Use agents as deterministic "play-testers" to validate user flows.

**Example applications:**
- Onboarding flows
- Multi-step forms
- Retry logic
- Input validation
- Accessibility under interaction

**Structure:**
Agents simulate user behavior thousands of times, comparing variants and detecting UX regressions that static analysis cannot catch.

## Implementation Guide

### Step 1: Identify High-Value Targets

Ask:
1. What quality work is repetitive but requires judgment?
2. What checks depend on understanding intent, not just syntax?
3. Where does manual QA lag behind feature velocity?

Common answers:
- Doc/code alignment
- Test coverage gaps
- Dependency drift
- Performance regressions
- Semantic UI changes

### Step 2: Define Safe Outputs

Specify exactly what the agent may produce:

```yaml
safe-outputs:
  create-pull-request:
    title-prefix: "[auto] "
    branch-prefix: "agent-ci/"
  create-issue:
    title-prefix: "[alert] "
  create-comment:
    only-on: pull_request
```

**Default:** Read-only. Agents cannot modify the repo unless explicitly permitted.

### Step 3: Write Natural-Language Rules

Express expectations in plain language that an agent can reason over:

**Good:**
- "Check whether documented behavior matches implementation, explain mismatches, and propose fixes."
- "Flag performance regressions in critical paths by analyzing execution patterns."

**Bad (too vague):**
- "Make the code better."
- "Fix bugs."

**Bad (should be CI):**
- "Check if tests pass." (deterministic)
- "Ensure code is formatted." (lint rule)

### Step 4: Set Guardrails

**Quality gates:** Use blocking audits (like Sentinel) to enforce standards before allowing progress.

**Iteration limits:** Cap retries (e.g., Healer iterates max 5x) to prevent infinite loops.

**Context chaining:** Each agent receives rich context from prior phases to enable intelligent decisions.

**Human review:** Agents produce artifacts for review; they never auto-merge or deploy.

### Step 5: Iterate Based on Real Use

1. Run the workflow on real PRs/features
2. Notice where agents struggle or produce low-quality outputs
3. Refine instructions, add constraints, or split into multiple agents
4. Repeat

**Early insight:** Workflows rarely work perfectly on first try. Collaboration between human and agent refines intent over iterations.

## Real-World Impact Metrics

From production deployments:

**Speed & Efficiency:**
- Feature analysis: 45-60min → 5-10min (6-10x faster)
- Time to first passing test: ~1h → 5min
- RCA and test maintenance: full day → minutes

**Quality & Coverage:**
- Flaky tests: 30-35 → 4-5 (85% reduction)
- Test coverage: 380 → 700+ tests (84% increase)
- Edge case detection: agents consistently identify scenarios humans miss
- Production bugs caught: silent failures discovered during test generation

**Team Velocity:**
- QA contributes automation in feature PRs (no lag)
- Releases ship with E2E tests already written
- Standardized patterns via quality gate enforcement

## Anti-Patterns to Avoid

❌ **One super-agent doing everything** → Use specialized agents with bounded roles

❌ **Agents auto-merging code** → Always require human review

❌ **No quality gates** → Use blocking audits for critical violations

❌ **Vague instructions** → Be specific about intent and constraints

❌ **Ignoring iteration** → Agents rarely succeed on first try; embrace refinement

❌ **Using AI for deterministic tasks** → Save agents for judgment-heavy work; use CI for rules

## Integration Examples

### GitHub Actions Pattern

```yaml
name: Agent CI - Doc Sync
on:
  pull_request:
    paths:
      - 'src/**/*.py'

jobs:
  doc-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check doc/code alignment
        run: |
          # Agent analyzes changes and opens PR if mismatches found
          agent-ci doc-sync --agent-id doc-checker
```

### Cron-Based Pattern (OpenClaw)

```json
{
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "America/Los_Angeles" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run daily test coverage expansion: identify untested code paths, generate tests, open PR."
  },
  "delivery": { "mode": "announce" },
  "sessionTarget": "isolated"
}
```

## Best Practices

✅ **Start small:** Begin with one high-value workflow (e.g., doc/code sync)

✅ **Progressive rollout:** Test on non-critical paths before expanding

✅ **Monitor token costs:** Track agent usage to avoid runaway spend

✅ **Review outputs:** Treat agent PRs like any other code review

✅ **Explicit permissions:** Default to read-only; grant write access sparingly

✅ **Audit trails:** Log all agent activity for debugging and compliance

✅ **Iterate relentlessly:** Refine instructions based on real performance

## Resources

### references/
Detailed guides for specific implementations:

- **council-pattern.md** - Full walkthrough of multi-agent QA council design
- **safe-outputs.md** - Comprehensive guide to permission models and output constraints
- **examples.md** - Real-world workflow examples from production deployments

Read these references when implementing specific patterns or needing deeper context.

---

**Philosophy:** Continuous AI doesn't replace developers or CI—it scales developer judgment across codebases by automating work that requires reasoning, not just rules.
