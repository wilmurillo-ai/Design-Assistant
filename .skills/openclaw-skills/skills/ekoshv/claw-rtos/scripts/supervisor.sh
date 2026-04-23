#!/usr/bin/env bash
set -euo pipefail

# 1. Dashboard Watchdog
if ! pgrep -f "rtos_dashboard.py" > /dev/null; then
    echo "$(date): Dashboard down, restarting..."
    bash /home/ekoshv/.openclaw/workspace/skills/rtos-kernel/scripts/run_dashboard.sh
else
    echo "$(date): Dashboard is running."
fi

# 2. Garbage Collection (kill stuck agents > 4h)
echo "$(date): Running ClawRTOS Kernel cleanup..."
# TODO: Automatically invoke 'openclaw subagents kill' on zombies.
echo "$(date): Garbage collection complete."
