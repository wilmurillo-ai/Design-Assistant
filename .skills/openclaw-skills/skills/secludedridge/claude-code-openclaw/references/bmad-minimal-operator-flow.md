# BMad Minimal Operator Flow

Use this file when you want the **shortest reliable operator checklist**.

## 1. Determine the path

- Official BMad role/trigger → `run_bmad_persona.py`
- Direct slash workflow → `claude_code_run.py`
- One-shot headless task → `run_claude_task.sh`

## 2. Before running on a BMad repo

Inspect:
- `_bmad/_config/bmad-help.csv`
- `.claude/commands/`

## 3. Default implementation loop

1. SM → `CS`
2. DEV → `DS`
3. DEV → `CR`
4. Fixes → `DS`
5. Epic complete → SM → `ER`

## 4. Prompt minimum

Include only:
- exact role/trigger or workflow
- target story/file/repo
- completion criteria
- default interaction policy

Default interaction policy:
- Continue / C
- no A / P
- no YOLO unless explicitly authorized

## 5. Completion rule

Trust artifacts over terminal behavior:
- target file exists
- story/sprint status advanced
- tests passed when required

## 6. Feedback rule

When a clear result arrives:
- send a short status summary immediately
- add details only if needed

## 7. Never do this

- raw `claude -p`
- tmux as default path
- ad-hoc background polling loops
- multi-workflow prompts in one run
