#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="${1:-$ROOT_DIR/dist}"
mkdir -p "$OUT_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cp -R "$ROOT_DIR" "$TMP_DIR/lg-agent-platform"
rm -rf "$TMP_DIR/lg-agent-platform/dist"
rm -f "$TMP_DIR/lg-agent-platform/package.sh"

(cd "$TMP_DIR" && zip -r "$OUT_DIR/lg-agent-platform.skill" lg-agent-platform >/dev/null)

echo "Created: $OUT_DIR/lg-agent-platform.skill"
