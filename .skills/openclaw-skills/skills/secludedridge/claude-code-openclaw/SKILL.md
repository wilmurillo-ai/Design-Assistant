---
name: claude-code-openclaw
description: "Delegate implementation, review, and official BMad agent-driven workflows to local Claude Code. Use for: (1) substantial coding/refactoring/review work, (2) repos with `_bmad/` where BMad roles like SM/DEV/PM/Architect/QA/TEA should be invoked through the installed agent commands, (3) direct slash workflows such as `/bmad-bmm-*`, `/bmad-tea-*`, `/speckit.*`, or `/opsx:*`, and (4) one-shot headless Claude Code tasks." 
---

# Claude Code Operator (OpenClaw)

Use local Claude Code as the implementation engine. Keep the orchestration disciplined, evidence-based, and aligned with the repo's installed BMad tooling.

## Supported execution paths

Use exactly one of these paths:

1. **One-shot headless task** → `scripts/run_claude_task.sh`
2. **Direct slash workflow** → `scripts/claude_code_run.py`
3. **Official BMad agent persona** → `scripts/run_bmad_persona.py`

Never use:
- raw `claude -p`
- tmux as the default Claude carrier
- ad-hoc `exec(background:true)` + poll loops
- hand-written generic persona prompts when `run_bmad_persona.py` can express the task

## Preferred orchestration pattern

Prefer the **Spawn and Yield** pattern when ACP is available:
- start the Claude task with `sessions_spawn`
- pass `--notify-parent-session`
- immediately `sessions_yield`
- let completion wake the parent session

If ACP is unavailable, use the supported local runner above. Do not invent a fourth path.

## Core role

You are the Project Owner and orchestration layer.

- Let Claude Code / BMad agents do the implementation work.
- Absorb routine elicitation and make the decision yourself.
- Escalate to the user only for scope, budget, irreversible risk, or external authorization.
- Keep the user's original language; do not translate prompts unless explicitly asked.

## BMad operating rules

For repos that contain `_bmad/`, treat BMad as the **project operating system**, not as loose inspiration.

Before running anything, inspect the repo's actual installed capability set:
- `_bmad/_config/bmad-help.csv`
- `.claude/commands/`
- or `scripts/run_bmad_persona.py --cwd <repo> --list`

### Default implementation loop

Use the official implementation cycle unless there is a deliberate reason not to:
1. **SM → CS**
2. **DEV → DS**
3. **DEV → CR**
4. If fixes are needed, back to **DS**
5. Epic complete → **SM → ER**

### When to use direct workflows instead

Use direct `/bmad-bmm-*` or `/bmad-tea-*` workflows when:
- the user explicitly asks for that workflow
- you are recovering a specific interrupted step
- you need precise single-step monitoring or retry behavior

Default to official agent-driven delivery when the user wants “real BMad” execution.

## How to invoke Claude Code

### 1) One-shot headless task

Use for bounded tasks such as review, summary, targeted fix, or analysis.

```bash
scripts/run_claude_task.sh --prompt "<structured task>"
```

## 2) Direct slash workflow

Use for a specific installed workflow.

Rules:
- first non-empty line must be a slash command
- one workflow per run
- keep the prompt minimal

Example:

```bash
scripts/claude_code_run.py \
  --mode interactive \
  --cwd <repo> \
  --workflow bmad-bmm-code-review \
  --prompt-file <prompt.txt>
```

## 3) Official BMad agent persona

Use for role-correct BMad execution.

Prefer the wrapper:

```bash
scripts/run_bmad_persona.py \
  --cwd <repo> \
  --persona sm \
  --trigger CS \
  --story-id 4-1-agent-api-auth-and-security
```

You may also pass an installed workflow command name as the trigger when recovering or matching a user-facing command exactly, for example `--trigger bmad-bmm-create-story`.

More examples:

```bash
scripts/run_bmad_persona.py --cwd <repo> --persona pm --trigger CP
scripts/run_bmad_persona.py --cwd <repo> --persona architect --trigger CA
scripts/run_bmad_persona.py --cwd <repo> --persona dev --trigger DS --story-id 4-1-agent-api-auth-and-security --story-path _bmad-output/implementation-artifacts/story-4-1-agent-api-auth-and-security.md
scripts/run_bmad_persona.py --cwd <repo> --persona dev --trigger CR --story-id 4-1-agent-api-auth-and-security
```

`run_bmad_persona.py` will:
- read `_bmad/_config/bmad-help.csv`
- resolve trigger → agent → installed command → workflow
- generate a legal slash-first prompt
- bind the correct workflow for orchestrator artifact rules
- auto-enable artifact-based stop for major artifact-producing flows

## Prompt rules

Keep prompts short and structured.

Always include only what is needed:
- the exact workflow or agent trigger for this run
- target files or story identifiers
- completion criteria
- default interaction policy

For BMad prompts, default to:
- `Continue / C`
- no `Advanced Elicitation / A`
- no `Party Mode / P`
- no `YOLO / Y` unless explicitly authorized

Do not paste long PRD / architecture / history into the prompt when files already exist. Prefer file paths and targets.

## Completion criteria

Trust artifacts over terminal vibes.

For BMad, prefer:
- expected output file exists
- story status / sprint-status advanced correctly
- review output exists
- tests actually ran and passed when implementation or review requires it

Do not treat spinner activity, transcript growth, or exit code alone as success.

## Token discipline

Conserve tokens aggressively:
- use the shortest legal slash-first prompt
- prefer structured context files over repeated prose
- keep hooks and event summaries compact
- keep completion updates terse and action-oriented
- avoid re-injecting large run metadata into the parent session

## Read these references as needed

- `references/bmad-agent-trigger-cheatsheet.md` — official role/trigger matrix
- `references/bmad-method-integration.md` — BMad operating guidance in OpenClaw
- `references/bmad-v6-agent-workflow-map.md` — broader agent/workflow map
- `references/bmad-prompt-templates.md` — prompt templates
- `references/spec-driven-workflow.md` — Spec Kit / OpenSpec flows
- `references/claude-orchestrator-ops.md` — operational troubleshooting and recovery commands
- `references/claude-orchestrator-profiles.yaml` — workflow/profile behavior
- `references/claude-orchestration-control-plane.md` — deep architecture notes; read only when modifying the control plane itself

## Resource files

Primary runtime:
- `scripts/run_claude_task.sh`
- `scripts/claude_code_run.py`
- `scripts/run_bmad_persona.py`
- `scripts/claude_orchestrator.py`

Core runtime support:
- `scripts/claude_artifact_probe.py`
- `scripts/claude_checkpoint.py`
- `scripts/claude_workflow_adapter.py`
- `scripts/claude_watchdog.py`
- `scripts/install_claude_hooks.py`
- `scripts/claude_hook_event_logger.py`
- `scripts/claude_dispatch_update.py`

Ops / recovery tools:
- `scripts/ops/claude_run_report.py`
- `scripts/ops/claude_latest_run_report.py`
- `scripts/ops/claude_reconcile_runs.py`
- `scripts/ops/claude_recover_run.py`
- `scripts/ops/claude_user_update.py`

Dev / maintenance tools:
- `scripts/dev/claude_acceptance_check.py`
- `scripts/dev/claude_v2_smoke.py`
- `scripts/dev/claude_event_summary.py`

When improving this skill, prioritize fixes that remove false-progress signals and ensure artifact-complete runs actually terminate and finalize cleanly.
