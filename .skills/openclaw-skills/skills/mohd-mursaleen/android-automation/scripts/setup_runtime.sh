#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$(cd "${SCRIPT_DIR}/../runtime" && pwd)"

if [[ -x "${RUNTIME_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${RUNTIME_DIR}/.venv/bin/python"
else
  if command -v python3 >/dev/null 2>&1; then
    HOST_PYTHON="python3"
  elif command -v python >/dev/null 2>&1; then
    HOST_PYTHON="python"
  else
    echo "Python is required but neither python3 nor python is available in PATH." >&2
    exit 1
  fi

  "${HOST_PYTHON}" -m venv "${RUNTIME_DIR}/.venv"
  PYTHON_BIN="${RUNTIME_DIR}/.venv/bin/python"
fi

"${PYTHON_BIN}" -m pip install --upgrade pip
"${PYTHON_BIN}" -m pip install -r "${RUNTIME_DIR}/requirements.txt"

if [[ ! -f "${RUNTIME_DIR}/.env" && -f "${RUNTIME_DIR}/.env.example" ]]; then
  cp "${RUNTIME_DIR}/.env.example" "${RUNTIME_DIR}/.env"
fi

echo "Runtime ready at ${RUNTIME_DIR}"
