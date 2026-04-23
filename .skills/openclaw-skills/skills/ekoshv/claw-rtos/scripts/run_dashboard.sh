#!/usr/bin/env bash
set -euo pipefail

# Define variables
VENV="/home/ekoshv/.openclaw/workspace/.venvs/rtos-kernel"
export PYTHONPATH="/home/ekoshv/.openclaw/workspace/skills/rtos-kernel/scripts"

# Choose python path
# Priority: dedicated rtos env > default system python
if [ -f "$VENV/bin/python" ]; then
  PY="$VENV/bin/python"
elif [ -f "/home/ekoshv/.local/bin/python3" ]; then
  PY="/home/ekoshv/.local/bin/python3"
else
  PY="python3"
fi

echo "Starting ClawRTOS Monitor with $PY on http://localhost:8085..."
# We use nohup to detach it properly
nohup "$PY" /home/ekoshv/.openclaw/workspace/skills/rtos-kernel/scripts/rtos_dashboard.py > /home/ekoshv/.openclaw/workspace/skills/rtos-kernel/dashboard.log 2>&1 &
echo "Dashboard started (PID: $!)"
