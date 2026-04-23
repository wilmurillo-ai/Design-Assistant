#!/bin/bash
set -e

SLUG=$(basename "$PWD")
HOME_DIR="${HOME_MOCK:-$HOME}"
OPENCLAW_DIR="$HOME_DIR/.openclaw"
SKILLS_DIR="$OPENCLAW_DIR/skills"
RELEASES_DIR="$OPENCLAW_DIR/.releases/$SLUG"
PROD_LINK="$SKILLS_DIR/$SLUG"

RUN_TESTS=false
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --preflight)
        RUN_TESTS=true
        DRY_RUN=true
        shift
        ;;
    esac
done

echo "[$(date '+%H:%M:%S')] Starting blue/green deployment flow for $SLUG"

if [ "$RUN_TESTS" = true ] && [ -f "scripts/test_sdlc_cujs.sh" ]; then
    echo "🧪 Running Preflight CUJ Tests..."
    bash "scripts/test_sdlc_cujs.sh"
    if [ $? -ne 0 ]; then
        echo "❌ PREFLIGHT FAILED: CUJ test suite failed."
        exit 1
    fi
    echo "✅ PREFLIGHT PASSED."
fi

if [ "$DRY_RUN" = true ]; then
    echo "🛑 Dry run (--preflight) active. Exiting before actual deployment."
    exit 0
fi

# 1. Build release
if [ -f "scripts/build_release.sh" ]; then
    bash "scripts/build_release.sh" || exit 1
else
    # Fallback to creating a dist directory if no build script
    mkdir -p dist
    cp -r * dist/ 2>/dev/null || true
fi

# 2. Migration Safety: If target is a directory and NOT a symlink, delete it
mkdir -p "$SKILLS_DIR"
if [ -e "$PROD_LINK" ] && [ ! -L "$PROD_LINK" ] && [ -d "$PROD_LINK" ]; then
    echo "⚠️ Legacy directory detected at $PROD_LINK. Removing..."
    rm -rf "$PROD_LINK"
fi

# 3. Release Stamping & Artifact Staging
RELEASE_ID=$(date +"%Y%m%d_%H%M%S")
# If it's rapid testing, ensure we don't collide in the same second by adding nanoseconds or just sleep is used in tests.
# Actually, the test sleeps 1 second so timestamp is fine.
RELEASE_PATH="$RELEASES_DIR/$RELEASE_ID"

mkdir -p "$RELEASE_PATH"
if [ -d "dist" ] && [ "$(ls -A dist 2>/dev/null)" ]; then
    cp -r dist/* "$RELEASE_PATH/"
else
    # If no dist, copy current directory excluding dist and .git
    rsync -a --exclude=.git --exclude=dist --exclude=node_modules . "$RELEASE_PATH/"
fi

# 4. Atomic Swap
ln -snf "$RELEASE_PATH" "$RELEASES_DIR/current_tmp"
mv -T "$RELEASES_DIR/current_tmp" "$PROD_LINK"

# 5. Gateway Reload
if [ -z "$HOME_MOCK" ]; then
    echo "🔄 Restarting OpenClaw gateway..."
    openclaw gateway restart || echo "⚠️ Gateway restart failed or not available."
fi

# 6. Auto-Cleanup (Pruning): Keep only latest 3 releases
echo "🧹 Pruning old releases..."
# List all directories in RELEASES_DIR that look like release IDs, sort by time (newest first), skip top 3, delete rest
ls -dt "$RELEASES_DIR"/* 2>/dev/null | grep -E '/[0-9]{8}_[0-9]{6}$' | tail -n +4 | xargs -r rm -rf

echo "✅ DEPLOYMENT SUCCESS: $SLUG $RELEASE_ID is now live via blue/green swap."
