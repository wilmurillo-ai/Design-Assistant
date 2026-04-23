#!/bin/bash
set -e

SKILL_DIR="$HOME/.openclaw/skills"
mkdir -p "$SKILL_DIR"

# Assuming deploy.sh is run from the project root or its own directory
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_LINK="$SKILL_DIR/pm-skill"

ln -sfn "$SOURCE_DIR" "$TARGET_LINK"
echo "Successfully symlinked pm-skill to $TARGET_LINK"
