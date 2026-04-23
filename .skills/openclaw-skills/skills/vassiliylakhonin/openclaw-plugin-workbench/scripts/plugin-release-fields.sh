#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-.}"
cd "$REPO_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[error] not a git repository: $(pwd)"
  exit 2
fi

REPO_URL="$(git remote get-url origin 2>/dev/null || true)"
COMMIT="$(git rev-parse HEAD)"
REF="$(git rev-parse --abbrev-ref HEAD)"

cat <<EOF
Source repo: ${REPO_URL:-<set-manually>}
Source commit: $COMMIT
Source ref: $REF
Suggested changelog:
  Release update: publish-ready plugin package with required OpenClaw metadata and preflight-validated manifest.
EOF
