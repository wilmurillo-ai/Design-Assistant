#!/usr/bin/env bash
set -euo pipefail

# 5GC detached runner
# 用法:
#   ./run-5gc-detached.sh <label> -- <actual command...>
# 示例:
#   ./run-5gc-detached.sh bulk-ue -- node skills/5gc/scripts/5gc.js ue edit --project XW_S5GC_1 --set-msisdn 8613888888888

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <label> -- <command...>" >&2
  exit 1
fi

LABEL="$1"
shift
if [ "$1" != "--" ]; then
  echo "Usage: $0 <label> -- <command...>" >&2
  exit 1
fi
shift

ROOT="/home/dotouch/.openclaw/workspace/skills/5gc/test_results"
mkdir -p "$ROOT"
TS="$(date +%Y%m%d-%H%M%S)"
LOG="$ROOT/${TS}-${LABEL}.log"
PIDFILE="$ROOT/${TS}-${LABEL}.pid"
CMD=("$@")

{
  echo "[$(date '+%F %T')] label=$LABEL"
  echo "[$(date '+%F %T')] cwd=$(pwd)"
  printf '[%s] cmd=' "$(date '+%F %T')"
  printf '%q ' "${CMD[@]}"
  echo
} >> "$LOG"

# 尽量脱离当前聊天 exec 生命周期
nohup setsid "${CMD[@]}" >> "$LOG" 2>&1 < /dev/null &
PID=$!
echo "$PID" > "$PIDFILE"

echo "started"
echo "label=$LABEL"
echo "pid=$PID"
echo "log=$LOG"
echo "pidfile=$PIDFILE"
