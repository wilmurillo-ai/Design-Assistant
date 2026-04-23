#!/bin/bash
# cmd-exec wrapper script
# Usage: ./exec.sh '<json_request>' OR ./exec.sh --server [options]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD_EXEC="${SCRIPT_DIR}/../assets/cmd_exec_linux"

if [ ! -f "$CMD_EXEC" ]; then
    echo '{"error": "cmd_exec_linux binary not found"}'
    exit 1
fi

# Server mode
if [ "$1" = "--server" ]; then
    shift
    exec "$CMD_EXEC" -server "$@"
fi

# CLI mode - pass JSON request
if [ -n "$1" ]; then
    echo "$1" | "$CMD_EXEC"
else
    # Read from stdin
    "$CMD_EXEC"
fi