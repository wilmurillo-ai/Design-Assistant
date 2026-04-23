#!/bin/bash

# WebChat Enhancer - One-Command Installer
# Run this command to install:
#   curl -sL https://raw.githubusercontent.com/yjin94606-art/webchat-enhancer/main/skills/webchat-enhancer/install.sh | bash

set -e

echo "🎉 Installing WebChat Enhancer..."

# Step 1: Install the skill
echo "📦 Installing skill..."
clawhub install webchat-enhancer --yes 2>/dev/null || clawhub update webchat-enhancer --yes 2>/dev/null || echo "Skill already installed"

# Step 2: Open GreasyFork for one-click script install
echo "🌐 Opening GreasyFork for script installation..."
open "https://greasyfork.org/zh-CN/scripts/571337-webchat-enhancer"

# Step 3: Show completion
echo ""
echo "✅ Done!"
echo ""
echo "📋 Next steps:"
echo "   1. Click the green 'Install' button on GreasyFork"
echo "   2. Open WebChat: http://127.0.0.1:18789"
echo ""
