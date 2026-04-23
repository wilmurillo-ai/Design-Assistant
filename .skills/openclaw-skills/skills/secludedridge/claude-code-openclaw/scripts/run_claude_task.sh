#!/usr/bin/env bash
set -euo pipefail

PROMPT=""
PROMPT_FILE=""
CWD=""
TIMEOUT_SEC="1800"
PERMISSION_MODE="bypassPermissions"
NOTIFY_TARGET="telegram:778877450"
NOTIFY_ACCOUNT="sage4coder"

# Progress notification (event-driven / rate-limited)
NOTIFY_PROGRESS=0
NOTIFY_INTERVAL_SEC=180
NOTIFY_LINES=12
NOTIFY_MAX_UPDATES=20

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt) PROMPT="${2:-}"; shift 2 ;;
    --prompt-file) PROMPT_FILE="${2:-}"; shift 2 ;;
    --cwd) CWD="${2:-}"; shift 2 ;;
    --timeout) TIMEOUT_SEC="${2:-1800}"; shift 2 ;;
    --permission-mode) PERMISSION_MODE="${2:-bypassPermissions}"; shift 2 ;;

    --notify-target) NOTIFY_TARGET="${2:-}"; shift 2 ;;
    --notify-account) NOTIFY_ACCOUNT="${2:-}"; shift 2 ;;

    --notify-progress) NOTIFY_PROGRESS=1; shift ;;
    --no-notify-progress) NOTIFY_PROGRESS=0; shift ;;
    --notify-interval) NOTIFY_INTERVAL_SEC="${2:-180}"; shift 2 ;;
    --notify-lines) NOTIFY_LINES="${2:-12}"; shift 2 ;;
    --notify-max) NOTIFY_MAX_UPDATES="${2:-20}"; shift 2 ;;

    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -n "$PROMPT_FILE" ]]; then
  if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "ERROR: prompt file not found: $PROMPT_FILE" >&2
    exit 2
  fi
  PROMPT="$(cat "$PROMPT_FILE")"
fi

if [[ -z "$PROMPT" ]]; then
  echo "Missing --prompt or --prompt-file" >&2
  exit 2
fi

if [[ -n "$CWD" ]]; then
  cd "$CWD"
fi

# Defensive defaults for numeric inputs
[[ "$NOTIFY_INTERVAL_SEC" =~ ^[0-9]+$ ]] || NOTIFY_INTERVAL_SEC=180
[[ "$NOTIFY_LINES" =~ ^[0-9]+$ ]] || NOTIFY_LINES=12
[[ "$NOTIFY_MAX_UPDATES" =~ ^[0-9]+$ ]] || NOTIFY_MAX_UPDATES=20
(( NOTIFY_INTERVAL_SEC > 0 )) || NOTIFY_INTERVAL_SEC=180
(( NOTIFY_LINES > 0 )) || NOTIFY_LINES=12
(( NOTIFY_MAX_UPDATES > 0 )) || NOTIFY_MAX_UPDATES=20

CLAUDE_CMD=(claude -p --permission-mode "$PERMISSION_MODE" "$PROMPT")
OUTPUT_FILE=$(mktemp)

cleanup() {
  rm -f "$OUTPUT_FILE"
}
trap cleanup EXIT

# In headless environments, force a PTY when possible to avoid claude CLI hangs.
if command -v script >/dev/null 2>&1; then
  printf -v CLAUDE_CMD_STR '%q ' "${CLAUDE_CMD[@]}"
  EXEC_CMD=(script -q -c "$CLAUDE_CMD_STR" /dev/null)
else
  EXEC_CMD=("${CLAUDE_CMD[@]}")
fi

CAN_NOTIFY=0
if command -v openclaw >/dev/null 2>&1 && [[ -n "$NOTIFY_ACCOUNT" ]] && [[ -n "$NOTIFY_TARGET" ]]; then
  CAN_NOTIFY=1
fi

# If messaging is unavailable, skip progress monitor to avoid useless background work.
if (( CAN_NOTIFY == 0 )); then
  NOTIFY_PROGRESS=0
fi

send_notify() {
  local msg="$1"
  if (( CAN_NOTIFY == 1 )); then
    openclaw message send --account "$NOTIFY_ACCOUNT" --target "$NOTIFY_TARGET" --message "$msg" >/dev/null 2>&1 || true
  fi
}

strip_ansi() {
  sed -r 's/\x1B\[[0-9;]*[mK]//g' | tr -d '\r' | grep -v '\[?25h' | grep -v '\[?2004' || true
}

progress_monitor() {
  local cmd_pid="$1"
  local updates=0
  local last_lines=0
  local last_digest=""

  while kill -0 "$cmd_pid" >/dev/null 2>&1; do
    # Sleep in 1s chunks so we can stop quickly after task exits.
    local slept=0
    while (( slept < NOTIFY_INTERVAL_SEC )); do
      kill -0 "$cmd_pid" >/dev/null 2>&1 || return 0
      sleep 1
      slept=$((slept + 1))
    done

    local current_lines
    current_lines=$(wc -l < "$OUTPUT_FILE" 2>/dev/null || echo 0)
    (( current_lines > 0 )) || continue
    (( current_lines > last_lines )) || continue

    local chunk
    chunk=$(tail -n "$NOTIFY_LINES" "$OUTPUT_FILE" | strip_ansi)
    [[ -n "${chunk// }" ]] || { last_lines=$current_lines; continue; }

    local digest
    digest=$(printf '%s' "$chunk" | cksum | awk '{print $1":"$2}')
    if [[ "$digest" == "$last_digest" ]]; then
      last_lines=$current_lines
      continue
    fi

    if (( updates >= NOTIFY_MAX_UPDATES )); then
      if (( updates == NOTIFY_MAX_UPDATES )); then
        send_notify "🔕 **Claude Code 过程推送已达上限**（$NOTIFY_MAX_UPDATES 条）。任务仍在运行，完成后会推送最终结果。"
      fi
      updates=$((updates + 1))
      last_lines=$current_lines
      last_digest="$digest"
      continue
    fi

    updates=$((updates + 1))
    send_notify "⏳ **Claude Code 执行中**（进度 #$updates）
工作目录：
\`\`\`text
$(pwd)
\`\`\`
最近日志：
\`\`\`text
$chunk
\`\`\`"

    last_lines=$current_lines
    last_digest="$digest"
  done
}

if (( NOTIFY_PROGRESS == 1 )); then
  send_notify "🚀 **Claude Code 任务已启动**
- 模式: headless
- 权限: $PERMISSION_MODE
- 进度推送间隔: ${NOTIFY_INTERVAL_SEC}s
- 任务超时: ${TIMEOUT_SEC}s"
fi

# Execute and tee output (background) so we can monitor progress without tight polling.
set +e
if command -v timeout >/dev/null 2>&1; then
  (timeout "$TIMEOUT_SEC" "${EXEC_CMD[@]}" 2>&1 | tee "$OUTPUT_FILE") &
else
  ("${EXEC_CMD[@]}" 2>&1 | tee "$OUTPUT_FILE") &
fi
RUN_PID=$!

MONITOR_PID=""
if (( NOTIFY_PROGRESS == 1 )); then
  progress_monitor "$RUN_PID" &
  MONITOR_PID=$!
fi

wait "$RUN_PID"
EXIT_CODE=$?

if [[ -n "$MONITOR_PID" ]]; then
  wait "$MONITOR_PID" || true
fi
set -e

# Final summary
SUMMARY=$(tail -n 25 "$OUTPUT_FILE" | strip_ansi | tail -n 15)

STATUS_ICON="✅"
if [ "$EXIT_CODE" -ne 0 ]; then
  STATUS_ICON="❌"
fi

send_notify "$STATUS_ICON **Claude Code 任务执行结束** (Exit: $EXIT_CODE)
摘要日志：
\`\`\`text
$SUMMARY
\`\`\`"

exit "$EXIT_CODE"
