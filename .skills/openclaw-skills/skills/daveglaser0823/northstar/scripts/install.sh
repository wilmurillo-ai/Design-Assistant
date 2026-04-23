#!/usr/bin/env bash
# Northstar Installer
# Installs the Northstar skill and configures it for use with OpenClaw.

set -e

SKILL_DIR="$HOME/.clawd/skills/northstar"
SCRIPTS_DIR="$SKILL_DIR/scripts"
CONFIG_DIR="$SKILL_DIR/config"
BIN_DIR="$HOME/.local/bin"

echo "Installing Northstar Daily Business Briefing..."
echo ""

# Create directories
mkdir -p "$SCRIPTS_DIR" "$CONFIG_DIR" "$BIN_DIR"

# Copy scripts
INSTALL_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$INSTALL_SRC/northstar.py" "$SCRIPTS_DIR/northstar.py"
chmod +x "$SCRIPTS_DIR/northstar.py"

# Copy Pro module (always included; gated by tier config, not install)
if [ -f "$INSTALL_SRC/northstar_pro.py" ]; then
    cp "$INSTALL_SRC/northstar_pro.py" "$SCRIPTS_DIR/northstar_pro.py"
    echo "  ✓ Pro module installed (Pro features require tier: pro in config)"
fi

# Copy config example (don't overwrite existing config)
CONFIG_EXAMPLE="$(cd "$INSTALL_SRC/.." && pwd)/config/northstar.json.example"
if [ -f "$CONFIG_EXAMPLE" ]; then
    cp "$CONFIG_EXAMPLE" "$CONFIG_DIR/northstar.json.example"
    if [ ! -f "$CONFIG_DIR/northstar.json" ]; then
        cp "$CONFIG_EXAMPLE" "$CONFIG_DIR/northstar.json"
        echo "  ✓ Config created at: $CONFIG_DIR/northstar.json"
        echo "    Edit it with your API keys before running."
    else
        echo "  ✓ Config already exists (not overwritten): $CONFIG_DIR/northstar.json"
    fi
fi

# Create wrapper script in ~/.local/bin (no sudo required)
WRAPPER="$BIN_DIR/northstar"
cat > "$WRAPPER" << 'WRAPPER_EOF'
#!/usr/bin/env bash
exec python3 "$HOME/.clawd/skills/northstar/scripts/northstar.py" "$@"
WRAPPER_EOF
chmod +x "$WRAPPER"
echo "  ✓ Installed: $WRAPPER"

# Check PATH
if echo "$PATH" | grep -q "$BIN_DIR"; then
    echo "  ✓ $BIN_DIR is in your PATH"
else
    echo ""
    echo "  ⚠️  Add to your PATH to use 'northstar' command:"
    echo "     echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc"
    echo ""
    echo "  Or run directly: python3 ~/.clawd/skills/northstar/scripts/northstar.py <command>"
fi

# Install Python dependencies
echo ""
echo "Checking Python dependencies..."
python3 -c "import stripe" 2>/dev/null || {
    echo "  Installing stripe..."
    # macOS Homebrew Python requires --break-system-packages or --user + that flag
    pip3 install --user --break-system-packages stripe -q 2>/dev/null || \
    pip3 install --user stripe -q 2>/dev/null || \
    pip3 install stripe -q 2>/dev/null || {
        echo "  ⚠️  Could not auto-install stripe. Install manually:"
        echo "     pip3 install --user --break-system-packages stripe"
        echo "  Then re-run: northstar test"
    }
}
python3 -c "import stripe" 2>/dev/null && echo "  ✓ Dependencies ready" || echo "  ⚠️  stripe package not found - see above"

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit your config: $CONFIG_DIR/northstar.json"
echo "  2. Add your Stripe API key (and Shopify if needed)"
echo "  3. Test it: northstar test"
echo "  4. Schedule it (optional): add to OpenClaw cron"
echo "     0 6 * * * northstar run"
echo ""
echo "Docs: See SKILL.md in the northstar skill directory"
