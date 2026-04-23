#!/usr/bin/env bash
#
# Tozil OpenClaw Hook Installer
# Installs the Tozil cost tracking hook into OpenClaw
#

set -euo pipefail

HOOK_DIR="$HOME/.openclaw/hooks/tozil"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Tozil hook for OpenClaw..."

# Create hook directory
mkdir -p "$HOOK_DIR"

# Copy files
cp "$SCRIPT_DIR/handler.js" "$HOOK_DIR/"
cp "$SCRIPT_DIR/sync_costs.js" "$HOOK_DIR/"

echo "✅ Files copied to $HOOK_DIR"

# Check for API key
if [ -z "${TOZIL_API_KEY:-}" ]; then
    echo "⚠️  Don't forget to set TOZIL_API_KEY in your environment!"
    echo "   Get your key at: https://agents.tozil.dev"
    echo ""
    echo "   export TOZIL_API_KEY=tz_xxxxxxxxxxxxxxxxxx"
fi

echo ""
echo "Next steps:"
echo "1. Set TOZIL_API_KEY environment variable"
echo "2. Run: openclaw hooks enable tozil"
echo "3. Run: openclaw gateway restart"
echo ""
echo "Hook installed successfully! 🎉"