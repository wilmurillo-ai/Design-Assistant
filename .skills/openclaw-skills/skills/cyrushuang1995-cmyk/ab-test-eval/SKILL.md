---
name: ab-test-eval
description: "Run A/B evaluation tests for any skill using subagents. Use when the user wants to test, benchmark, or compare a skill's effectiveness — e.g. 'test this skill', 'run evals', 'AB test the skill', 'benchmark this skill'. Automatically spawns with-skill and without-skill subagents, grades assertions, and generates a benchmark report."
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "bins": ["jq"]
          }
      }
  }
---

# AB Test Eval — Skill Benchmarking via Subagents

Evaluate any skill by spawning parallel subagents: one with the skill loaded, one without. Compare results against predefined assertions to measure the skill's actual impact.

## Workflow Overview

1. **Define evals** — write test prompts and assertions
2. **Spawn subagents** — with-skill vs without-skill, in parallel
3. **Wait for results** — `sessions_yield` until all complete
4. **Grade** — check each assertion against outputs
5. **Benchmark** — aggregate pass rates and summarize

---

## Step 1: Prepare Directory Structure

```
<skill-dir>/evals/evals.json          # Test prompts
<skill-dir>/<skill>-workspace/
  iteration-1/
    eval-1/
      with_skill/outputs/              # Skill-guided output
      without_skill/outputs/           # Baseline output
      eval_metadata.json               # Prompt + assertions
      grading.json                     # Grading results
    eval-2/ ...
    benchmark.json                     # Aggregated results
    benchmark.md                       # Human-readable summary
```

Create directories upfront:

```bash
SKILL_DIR="path/to/skill"
SKILL_NAME="my-skill"
WORKSPACE="${SKILL_DIR}/${SKILL_NAME}-workspace/iteration-1"
mkdir -p "${WORKSPACE}"/eval-{1,2,3}/{with_skill,without_skill}/outputs
```

---

## Step 2: Define Eval Cases

Save to `<skill-dir>/evals/evals.json`:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "A realistic user request that should trigger the skill",
      "expected_output": "What the correct approach looks like",
      "files": []
    },
    {
      "id": 2,
      "prompt": "Another test case covering a different aspect",
      "expected_output": "Expected behavior description",
      "files": []
    }
  ]
}
```

Guidelines for good eval prompts:
- Write as a real user would — casual, specific, with context
- Cover different aspects of the skill (not just happy path)
- Include edge cases where the skill's traps/gotchas matter
- 3-5 evals is usually enough for a first iteration

---

## Step 3: Spawn Subagents

For each eval, spawn **two** subagents in the same turn — with-skill and without-skill. The maximum concurrent subagents is 5, so batch accordingly.

### With-skill subagent

```
sessions_spawn:
  label: eval-N-with-skill
  mode: run
  runTimeoutSeconds: 120
  task: |
    Execute this task:
    - Skill path: <absolute-path-to-skill>/SKILL.md
    - Read the skill file first, then follow its guidance.
    - Task: <eval prompt>
    - Input files: <eval files or "none">
    - Save outputs to: <workspace>/eval-N/with_skill/outputs/commands.md
    - DO NOT actually run commands (no auth/runtime available).
      Instead, document exactly what commands/steps you would run,
      in what order, based on the skill instructions.
```

### Without-skill subagent (baseline)

```
sessions_spawn:
  label: eval-N-without-skill
  mode: run
  runTimeoutSeconds: 120
  task: |
    Execute this task WITHOUT reading any skill files:
    - Task: <eval prompt>
    - Use the relevant CLI/API tool.
    - Input files: <eval files or "none">
    - Save outputs to: <workspace>/eval-N/without_skill/outputs/commands.md
    - DO NOT actually run commands (no auth/runtime available).
      Instead, document exactly what commands/steps you would run,
      in what order, and explain your approach.
```

### Batch spawning pattern

```
# Round 1: spawn eval-1 + eval-2 (4 subagents, within limit)
sessions_spawn eval-1-with-skill
sessions_spawn eval-1-without-skill
sessions_spawn eval-2-with-skill
sessions_spawn eval-2-without-skill

# Wait for completions via sessions_yield
# Round 2: spawn eval-3 (2 subagents)
sessions_spawn eval-3-with-skill
sessions_spawn eval-3-without-skill
```

After spawning, call `sessions_yield` to wait for results. Subagents auto-announce on completion.

---

## Step 4: Handle Results

Each completed subagent sends a notification. Key things to check:

1. **Status** — `completed successfully` vs `timed out`. Timed-out subagents may still have partial output saved to files.
2. **Output files** — always verify the output file was actually written, regardless of status.
3. **Timing data** — the notification includes `total_tokens` and `duration_ms`. Save to `timing.json` in the run directory if tracking performance.

```json
{
  "total_tokens": 22900,
  "duration_ms": 51000,
  "total_duration_seconds": 51.0
}
```

---

## Step 5: Grade Assertions

For each eval, write `eval_metadata.json`:

```json
{
  "eval_id": 1,
  "eval_name": "descriptive-kebab-case-name",
  "prompt": "The eval prompt",
  "assertions": [
    {
      "text": "Description of what the correct approach should do",
      "expected": true
    }
  ]
}
```

Then read both outputs and grade each assertion, saving to `grading.json`:

```json
{
  "eval_id": 1,
  "eval_name": "descriptive-kebab-case-name",
  "grading": {
    "with_skill": {
      "assertions": [
        {
          "text": "Description of what was checked",
          "passed": true,
          "evidence": "Quote or reference from the output proving it"
        }
      ]
    },
    "without_skill": {
      "assertions": [
        {
          "text": "Description of what was checked",
          "passed": false,
          "evidence": "What went wrong or was missing"
        }
      ]
    }
  }
}
```

**Tips for good assertions:**
- Focus on the skill's unique knowledge (CLI flags, gotchas, parameter formats) — things the baseline wouldn't know
- Each assertion should be independently verifiable from the output
- 3-5 assertions per eval is sufficient
- The `evidence` field is important for human review — quote the exact command or explain the gap

---

## Step 6: Generate Benchmark

Write `benchmark.json` manually (the aggregate script may not always work):

```json
{
  "skill_name": "my-skill",
  "model": "model-id-from-session",
  "date": "ISO-date",
  "evals": [
    {
      "eval_id": 1,
      "eval_name": "name",
      "configurations": {
        "with_skill": {
          "pass_rate": 1.0,
          "assertions_passed": 4,
          "assertions_total": 4,
          "details": "Brief summary"
        },
        "without_skill": {
          "pass_rate": 0.25,
          "assertions_passed": 1,
          "assertions_total": 4,
          "details": "Brief summary"
        }
      }
    }
  ],
  "summary": {
    "with_skill": { "pass_rate": 0.85, "total_assertions": 20, "passed": 17 },
    "without_skill": { "pass_rate": 0.15, "total_assertions": 20, "passed": 3 },
    "delta": 0.70
  }
}
```

Then present the summary table to the user:

| Eval | With Skill | Without Skill |
|------|-----------|---------------|
| eval-1 | X/Y (Z%) | X/Y (Z%) |
| ... | ... | ... |
| **Total** | **X/Y** | **X/Y** |

---

## Iteration Loop

If results aren't satisfactory:

1. Improve the skill based on failed assertions
2. Rerun into `iteration-2/` directory
3. Compare against `iteration-1/`
4. Repeat until pass rate is acceptable

Focus improvements on the assertions that failed — those represent the skill's weak points.

---

## Quick Reference

| Step | Action |
|------|--------|
| Prepare | `mkdir -p` workspace + eval dirs |
| Define | Write `evals.json` with prompts |
| Spawn | `sessions_spawn` x2 per eval (with/without skill) |
| Wait | `sessions_yield`, handle notifications |
| Grade | Write `grading.json` per eval |
| Benchmark | Aggregate into `benchmark.json` |
| Report | Present summary table |
| Iterate | Fix skill → `iteration-N+1/` |
