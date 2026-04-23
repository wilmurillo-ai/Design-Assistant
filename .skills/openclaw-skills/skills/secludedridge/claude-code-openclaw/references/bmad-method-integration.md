# BMad Integration Guide (for claude-code-openclaw)

Use this file when you need the **operating rules** for running BMad correctly inside OpenClaw.

## 1. Start from the repo's installed truth

Do not guess which agents or workflows exist.

Inspect:
- `_bmad/_config/bmad-help.csv`
- `.claude/commands/`
- `scripts/run_bmad_persona.py --cwd <repo> --list`

Use the repo's installed capability set as the source of truth.

## 2. Default execution model

### Preferred paths
1. **One-shot headless task** → `scripts/run_claude_task.sh`
2. **Direct slash workflow** → `scripts/claude_code_run.py`
3. **Official BMad agent role** → `scripts/run_bmad_persona.py`

### Never use
- raw `claude -p`
- tmux as default Claude carrier
- ad-hoc background `exec` + polling loops
- hand-written generic persona prompts when the runner can express the task

## 3. Use BMad as the project operating system

When `_bmad/` exists and the user wants real BMad execution:
- follow the official roles
- follow the official trigger codes
- let the repo's installed commands drive the flow
- do not flatten everything into a few `/bmad-bmm-*` commands unless you are deliberately doing a direct workflow run

## 4. Standard implementation loop

Default implementation cycle:
1. **SM → CS**
2. **DEV → DS**
3. **DEV → CR**
4. If fixes are needed, back to **DS**
5. Epic complete → **SM → ER**

Use **SP** when sprint sequencing is needed.
Use **CC** when the plan meaningfully drifted.

## 5. When to use agent roles vs direct workflows

### Prefer official agent roles when
- the user explicitly wants BMad-native execution
- the task is phase-correct and role-specific
- you want SM / DEV / PM / Architect / QA / TEA to be invoked explicitly

### Prefer direct workflows when
- the user explicitly names a workflow
- you are recovering a specific interrupted step
- you need precise single-step monitoring or retry behavior

## 6. Phase guide

### Analysis
Typical roles/triggers:
- Analyst → `BP`, `MR`, `DR`, `TR`, `CB`, `DP`, `GPC`

### Planning
- PM → `CP`, `VP`, `EP`, `CE`
- UX → `CU`

### Solutioning
- Architect → `CA`, `IR`

### Implementation
- SM → `SP`, `SS`, `CS`, `VS`, `ER`, `CC`
- DEV → `DS`, `CR`
- QA → `QA`
- TEA → `TMT`, `TD`, `TF`, `CI`, `AT`, `TA`, `RV`, `NR`, `TR`

### Builder / meta-workflows
- Agent Builder / Module Builder / Workflow Builder as installed in `bmad-help.csv`

For the full trigger list, see `bmad-agent-trigger-cheatsheet.md`.

## 7. Prompt discipline

Keep prompts minimal:
- exact workflow or role/trigger
- target story/file/repo
- completion criteria
- default interaction policy

Default interaction policy:
- Continue / C
- no Advanced Elicitation / A
- no Party Mode / P
- no YOLO unless explicitly authorized

## 8. Completion discipline

For BMad, trust artifacts over terminal vibes.

Prefer:
- expected file exists
- story status advanced correctly
- sprint-status advanced correctly
- tests actually ran when implementation or review requires them

Do not rely on spinner activity or exit code alone.

## 9. Token discipline

To reduce token waste:
- use shortest legal slash-first prompts
- prefer structured context files over repeated prose
- dedupe completion hooks
- keep completion updates short
- avoid re-injecting large run metadata into the parent session

## 10. Useful companions

- `bmad-agent-trigger-cheatsheet.md`
- `bmad-v6-agent-workflow-map.md`
- `bmad-prompt-templates.md`
- `low-token-feedback-flow.md`
- `claude-orchestrator-ops.md`
