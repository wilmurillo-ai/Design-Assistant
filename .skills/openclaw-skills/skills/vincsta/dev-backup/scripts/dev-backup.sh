#!/usr/bin/env bash
set -euo pipefail

# dev-backup: snapshot a named project for safe rollback
# Usage: dev-backup <project-name> [--project-dir PATH] [--output-dir PATH]
#
# Creates a numbered snapshot of a project, prefixed with the project name
# so you can distinguish backups across different apps.
#
# Examples:
#   dev-backup my-app                     # uses current dir as project dir
#   dev-backup my-app --project-dir /path # explicit project dir
#   dev-backup another-project --project-dir ~/projects/another-project
#
# Snapshots are named: <project>-snapshot-1, <project>-snapshot-2, …
# A .latest symlink always points to the newest snapshot.

# Project name is mandatory
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <project-name> [--project-dir PATH] [--output-dir PATH]"
  echo "Example: $0 my-app --project-dir /home/user/projects/my-app"
  exit 1
fi

PROJECT_NAME="$1"
shift

PROJECT_DIR="${PROJECT_DIR:-.}"
OUTPUT_DIR="${OUTPUT_DIR:-$(dirname "$PROJECT_DIR")/backups}"
PREFIX="${PROJECT_NAME}-snapshot"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir) PROJECT_DIR="$2"; shift 2 ;;
    --output-dir)  OUTPUT_DIR="$2";     shift 2 ;;
    --help|-h)
      echo "Usage: $0 <project-name> [--project-dir PATH] [--output-dir PATH]"
      exit 0
      ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# Resolve to absolute paths
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
OUTPUT_DIR="$(mkdir -p "$OUTPUT_DIR" && cd "$OUTPUT_DIR" && pwd)"

# Find next number for THIS project
NEXT=1
if ls "$OUTPUT_DIR/${PREFIX}-"* 1>/dev/null 2>&1; then
  HIGHEST=$(ls "$OUTPUT_DIR" | grep "^${PROJECT_NAME}-snapshot-" | sed "s/^${PROJECT_NAME}-snapshot-//;s/-.*//" | sort -rn | head -1)
  if [[ "$HIGHEST" =~ ^[0-9]+$ ]]; then
    NEXT=$((HIGHEST + 1))
  fi
fi

SNAPSHOT_NAME="${PREFIX}-${NEXT}"
SNAPSHOT_DIR="${OUTPUT_DIR}/${SNAPSHOT_NAME}"

echo "==> Creating dev-backup: ${SNAPSHOT_NAME}"
echo "    Project: ${PROJECT_NAME}"
echo "    Source:  ${PROJECT_DIR}"
echo "    Target:  ${SNAPSHOT_DIR}"

# Copy with rsync
if command -v rsync &>/dev/null; then
  rsync -a --delete \
    --exclude '.git' --exclude 'node_modules' --exclude '.vite' \
    --exclude '.cache' --exclude '*.log' --exclude '.env' \
    --exclude 'backups' \
    "${PROJECT_DIR}/" "${SNAPSHOT_DIR}/"
else
  mkdir -p "$SNAPSHOT_DIR"
  tar -C "$(dirname "$PROJECT_DIR")" -cf - "$(basename "$PROJECT_DIR")" | tar -C "$SNAPSHOT_DIR" -xf -
fi

# Size report
TOTAL_SIZE=$(du -sh "$SNAPSHOT_DIR" 2>/dev/null | cut -f1 || echo "?")
echo "==> Snapshot created: ${SNAPSHOT_DIR} (${TOTAL_SIZE})"

# Update .latest symlink
LATEST="${OUTPUT_DIR}/.latest"
rm -f "$LATEST"
ln -s "$SNAPSHOT_NAME" "$LATEST"

echo "Done. Latest backup: ${LATEST}"
echo "To restore: cp -r ${SNAPSHOT_DIR}/ <your-app-dir>/"
