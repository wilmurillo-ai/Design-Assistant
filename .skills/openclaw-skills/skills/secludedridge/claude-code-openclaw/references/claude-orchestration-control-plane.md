# Claude Orchestration Control Plane

Read this file only when changing the control plane itself.

## Purpose

The control plane exists to make Claude Code orchestration deterministic, observable, and recoverable.

Primary goals:
- one supported carrier per task type
- structured run state
- artifact-based completion
- checkpoint-based progress
- recoverable stuck/orphaned runs
- compact completion callbacks

## Main components

- `claude_orchestrator.py` — launches and supervises Claude runs
- `claude_run_registry.py` — run registration, state projection, event log
- `claude_workflow_adapter.py` — structured workflow context + prompt injection
- `claude_checkpoint.py` — checkpoint protocol
- `claude_artifact_probe.py` — artifact-based completion rules
- `claude_watchdog.py` — idle/stuck/orphaned diagnosis and reconcile
- `scripts/ops/claude_run_report.py` / `scripts/ops/claude_latest_run_report.py` — reporting
- `scripts/ops/claude_recover_run.py` — recovery command generation/execution
- `claude_dispatch_update.py` — optional final update dispatch
- `scripts/dev/claude_acceptance_check.py` / `scripts/dev/claude_v2_smoke.py` / `scripts/dev/claude_event_summary.py` — maintenance-only tooling, not part of the normal runtime path

## Current design rules

1. Headless work must not reuse the interactive carrier.
2. Interactive work must run through the orchestrator.
3. Completion should prefer artifacts over terminal appearance.
4. Hook/event payloads should stay compact.
5. Parent-session wakeups should receive short summaries, not full run internals.

## State evidence priority

Prefer evidence in this order:
1. expected artifact exists / status advanced
2. checkpoint freshness
3. summary / state projection
4. hook events
5. transcript tail

## Typical failure classes

- startup blocked by trust/bypass/bash approval UI
- artifact produced but run not yet closed
- orphaned run after child/session mismatch
- incorrect prompt carrier (headless vs interactive)
- repo path / story path / workflow mismatch

## What not to do

- reintroduce raw `claude -p` as a default path
- rely on transcript motion alone as progress proof
- dump verbose operational metadata into user-visible completion messages
- add new runner paths without a clear reason
