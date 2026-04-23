#!/bin/bash
set -e

# ClawHub publish script for ClawRecipes
# Usage: ./scripts/publish-clawhub.sh [version]

VERSION=${1:-$(node -p "require('./package.json').version")}

echo "Publishing ClawRecipes v$VERSION to ClawHub..."

# Check if logged in
if ! clawhub status >/dev/null 2>&1; then
    echo "❌ Not logged in to ClawHub. Run:"
    echo "   clawhub login --token <your-token> --no-browser"
    exit 1
fi

# Publish
echo "🚀 Publishing to ClawHub..."
clawhub publish . --version "$VERSION"

echo "✅ Published ClawRecipes v$VERSION to ClawHub!"
echo ""
echo "Install via:"
echo "  openclaw plugins install clawhub:clawrecipes"