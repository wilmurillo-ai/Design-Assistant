#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

FILES=(
  "scripts/plan.sh"
  "scripts/export-gmaps.sh"
  "scripts/gen-airports.py"
)

echo "== SHA256 checksums =="
for file in "${FILES[@]}"; do
  shasum -a 256 "$file"
done

echo
echo "== Static risky-pattern scan =="
PATTERN='eval\(|exec\(|\b(bash|sh)\s+-c\b|\bpython3?\s+-c\b|os\.system|os\.popen|subprocess\.(Popen|run|call|check_output)\([^\n]*shell\s*=\s*True|curl\s|wget\s|requests\.|urllib\.request|socket\.'
if rg -n --pcre2 "$PATTERN" "${FILES[@]}"; then
  echo ""
  echo "FAIL: risky patterns detected in runtime scripts."
  exit 1
fi

echo "PASS: no risky execution or network-client patterns detected in runtime scripts."
