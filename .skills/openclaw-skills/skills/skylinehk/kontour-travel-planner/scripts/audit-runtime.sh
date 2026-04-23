#!/usr/bin/env bash
# Runtime safety audit for kontour-travel-planner scripts.
# Fails if suspicious network/exec primitives are found in runtime scripts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGETS=("$SCRIPT_DIR/plan.sh" "$SCRIPT_DIR/export-gmaps.sh" "$SCRIPT_DIR/gen-airports.py")

PATTERN='\b(curl|wget|ssh|scp)\b|requests\.|urllib\.request|fetch\(|axios|eval\(|exec\(|os\.system|subprocess\.'

echo "[audit] scanning runtime scripts for risky primitives..."
if rg -n -e "$PATTERN" "${TARGETS[@]}"; then
  echo "[audit] FAIL: suspicious pattern(s) detected." >&2
  exit 1
fi

echo "[audit] PASS: no risky runtime patterns found."
