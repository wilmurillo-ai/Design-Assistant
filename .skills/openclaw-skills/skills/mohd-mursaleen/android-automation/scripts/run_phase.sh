#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$(cd "${SCRIPT_DIR}/../runtime" && pwd)"

if [[ -x "${RUNTIME_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${RUNTIME_DIR}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python is required but neither python3 nor python is available in PATH." >&2
  exit 1
fi

if ! "${PYTHON_BIN}" - <<'PY' >/dev/null 2>&1
import importlib
for module_name in ("dotenv", "PIL"):
    importlib.import_module(module_name)
PY
then
  echo "Runtime dependencies are not installed for ${PYTHON_BIN}. Run ${SCRIPT_DIR}/setup_runtime.sh first." >&2
  exit 1
fi

exec "${PYTHON_BIN}" "${SCRIPT_DIR}/run_phase.py" "$@"
