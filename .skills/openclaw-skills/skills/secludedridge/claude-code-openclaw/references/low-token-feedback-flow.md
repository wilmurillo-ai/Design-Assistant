# Low-Token Feedback Flow

Use this file when tuning orchestration for lower token burn.

## Core principles

1. Prefer event-driven completion over polling.
2. Keep prompts short.
3. Keep hook logs compact.
4. Keep completion summaries short.
5. Do not push large run metadata back into the parent session.

## Preferred execution

- One-shot analysis/review → `run_claude_task.sh`
- Interactive workflow → `claude_code_run.py`
- Official BMad role delivery → `run_bmad_persona.py`

## Main token leaks to avoid

- repeated long terminal polling
- repeated long progress summaries
- duplicate Stop / SessionEnd / TaskCompleted notifications
- prompts that paste PRD / architecture / prior history unnecessarily
- verbose completion callbacks that dump run internals

## Practical rules

- one workflow per run
- shortest legal slash-first prompt
- structured context files instead of repeated prose
- check `summary.json`, `events.jsonl`, `user-update.txt` before asking the model to re-explain state
- prefer a short completion summary first, detailed interpretation second
