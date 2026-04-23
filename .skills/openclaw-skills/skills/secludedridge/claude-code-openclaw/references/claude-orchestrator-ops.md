# Claude Orchestrator Ops Runbook

Use this file only when diagnosing or recovering orchestrated Claude runs.

## Latest run

```bash
python3 scripts/ops/claude_latest_run_report.py \
  --registry-dir <repo>/.claude/orchestrator \
  --workflow <workflow> \
  --story-id <story-id> \
  --format text
```

Check:
- `state`
- `recommendedState`
- `stage`
- `progressExcerpt`
- `checkpointTs`

## Single run report

```bash
python3 scripts/ops/claude_run_report.py \
  --run-dir <repo>/.claude/orchestrator/runs/<run-id> \
  --idle-timeout-s 180 \
  --format text
```

## Check context and checkpoint

```bash
cat <repo>/.claude/orchestrator/runs/<run-id>/workflow-context.json
cat <repo>/.claude/orchestrator/runs/<run-id>/checkpoint.json
```

## Reconcile all runs

Dry-run:

```bash
python3 scripts/ops/claude_reconcile_runs.py \
  --registry-dir <repo>/.claude/orchestrator \
  --idle-timeout-s 180 \
  --format text
```

Apply fixes:

```bash
python3 scripts/claude_reconcile_runs.py \
  --registry-dir <repo>/.claude/orchestrator \
  --idle-timeout-s 180 \
  --fix \
  --format text
```

## Recover one run

Print recovery command:

```bash
python3 scripts/ops/claude_recover_run.py \
  --run-dir <repo>/.claude/orchestrator/runs/<run-id>
```

Execute recovery:

```bash
python3 scripts/ops/claude_recover_run.py \
  --run-dir <repo>/.claude/orchestrator/runs/<run-id> \
  --execute
```

## Dry-run completion dispatch

```bash
python3 scripts/claude_dispatch_update.py \
  --run-dir <repo>/.claude/orchestrator/runs/<run-id> \
  --notify-account <account> \
  --notify-target <target> \
  --dry-run
```

## Full acceptance check

```bash
python3 scripts/dev/claude_acceptance_check.py \
  --repo <skill-repo> \
  --registry-dir <repo>/.claude/orchestrator \
  --workflow <workflow> \
  --story-id <story-id> \
  --run-dir <repo>/.claude/orchestrator/runs/<run-id>
```

## Rule of thumb

Trust in this order:
1. artifact files
2. checkpoint / workflow-context
3. summary / run report
4. recent events
5. transcript tail
