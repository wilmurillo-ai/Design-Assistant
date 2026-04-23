# Telegram Progress Notify

Use this only when direct progress push is actually needed for a long headless task.

## Applies to
- `scripts/run_claude_task.sh`

## Main options
- `--notify-progress`
- `--notify-interval <sec>`
- `--notify-lines <n>`
- `--notify-max <n>`
- `--notify-account <id>`
- `--notify-target <target>`

## Recommendation

Default to sparse updates.

- normal long task: `--notify-interval 180`
- very long task: `--notify-interval 300`
- reduce noise with lower `--notify-max`

## Token note

Direct script-side progress pushes are cheaper than repeatedly asking the model to summarize runtime logs.
