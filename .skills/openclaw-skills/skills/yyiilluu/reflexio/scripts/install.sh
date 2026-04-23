#!/usr/bin/env bash
# openclaw-embedded install.sh — plugin installation.
#
# Default install is minimal: link the plugin, copy workspace files, and stop.
# Host-wide side effects (enabling active-memory, registering cron, restarting
# gateway) are behind explicit opt-in flags so reviewers / shared installs can
# audit blast radius.
#
# Flags (all default off):
#   --enable-active-memory   Enable the active-memory plugin host-wide.
#   --enable-cron            Register the daily 3am consolidation cron.
#   --restart-gateway        Restart the openclaw gateway when done.
#   --all                    Shortcut for all three of the above.
#   -h, --help               Show this help and exit.
#
# After install, the SKILL.md bootstrap still guides per-agent configuration
# (active-memory targeting, .reflexio/ extraPath) at first use.
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"

ENABLE_ACTIVE_MEMORY=0
ENABLE_CRON=0
RESTART_GATEWAY=0

die() { echo "error: $*" >&2; exit 1; }
info() { echo "==> $*"; }
note() { echo "    $*"; }

usage() {
  sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --enable-active-memory) ENABLE_ACTIVE_MEMORY=1 ;;
    --enable-cron)          ENABLE_CRON=1 ;;
    --restart-gateway)      RESTART_GATEWAY=1 ;;
    --all)
      ENABLE_ACTIVE_MEMORY=1
      ENABLE_CRON=1
      RESTART_GATEWAY=1
      ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown flag: $1 (see --help)" ;;
  esac
  shift
done

# 1. Prereq checks
info "Checking prerequisites..."
command -v openclaw >/dev/null || die "openclaw CLI required but not found on PATH"
command -v node >/dev/null     || die "node required but not found on PATH"

# 2. Install the plugin (hooks are registered programmatically from index.ts)
# `plugins install --link <path>` rejects `--force`, so we uninstall any prior
# registration first to make the install idempotent.
info "Installing plugin..."
openclaw plugins uninstall --force reflexio-embedded 2>/dev/null || true
openclaw plugins install --link "$PLUGIN_DIR"
# plugins install auto-enables by default. If ever it stops doing so, fall
# back to an explicit enable.
openclaw plugins enable reflexio-embedded 2>/dev/null || true

# 3. Copy main SKILL.md and consolidate command
info "Copying skills to workspace..."
mkdir -p "$OPENCLAW_HOME/workspace/skills/reflexio-embedded"
cp "$PLUGIN_DIR/SKILL.md" "$OPENCLAW_HOME/workspace/skills/reflexio-embedded/"
cp -r "$PLUGIN_DIR/commands/reflexio-consolidate" "$OPENCLAW_HOME/workspace/skills/"

# 4. Copy agent definitions
info "Copying agent definitions..."
mkdir -p "$OPENCLAW_HOME/workspace/agents"
cp "$PLUGIN_DIR/agents/reflexio-extractor.md"     "$OPENCLAW_HOME/workspace/agents/"
cp "$PLUGIN_DIR/agents/reflexio-consolidator.md"  "$OPENCLAW_HOME/workspace/agents/"

# 5. Copy prompts and scripts (referenced by agents at runtime)
info "Copying prompts and scripts..."
mkdir -p "$OPENCLAW_HOME/workspace/plugins/reflexio-embedded"
cp -r "$PLUGIN_DIR/prompts" "$OPENCLAW_HOME/workspace/plugins/reflexio-embedded/"
cp -r "$PLUGIN_DIR/scripts" "$OPENCLAW_HOME/workspace/plugins/reflexio-embedded/"
chmod +x "$OPENCLAW_HOME/workspace/plugins/reflexio-embedded/scripts/"*.sh

# 6. active-memory — opt-in
if [[ "$ENABLE_ACTIVE_MEMORY" -eq 1 ]]; then
  info "Enabling active-memory plugin (host-wide)..."
  openclaw plugins enable active-memory || \
    echo "warning: active-memory enable failed — may already be enabled or unavailable"
else
  note "active-memory not enabled (host-wide change skipped)."
  note "To enable later:  openclaw plugins enable active-memory"
  note "Or re-run this installer with --enable-active-memory."
fi

# 7. Cron — opt-in
if [[ "$ENABLE_CRON" -eq 1 ]]; then
  info "Registering daily consolidation cron (3am)..."
  # Remove any pre-existing entry so reinstalls don't accumulate duplicates
  # (`openclaw cron add` appends rather than replacing by name).
  openclaw cron rm reflexio-embedded-consolidate 2>/dev/null || true
  openclaw cron add \
    --name reflexio-embedded-consolidate \
    --cron "0 3 * * *" \
    --session isolated \
    --agent reflexio-consolidator \
    --message "Run your full-sweep consolidation workflow now. Follow your system prompt in full." \
    || echo "warning: cron registration failed — you can register it manually with the same flags"
else
  note "Daily consolidation cron not registered."
  note "To register later, re-run this installer with --enable-cron, or run:"
  note "  openclaw cron add --name reflexio-embedded-consolidate \\"
  note "    --cron \"0 3 * * *\" --session isolated \\"
  note "    --agent reflexio-consolidator \\"
  note "    --message \"Run your full-sweep consolidation workflow now.\""
fi

# 8. Gateway restart — opt-in
if [[ "$RESTART_GATEWAY" -eq 1 ]]; then
  info "Restarting openclaw gateway..."
  openclaw gateway restart
else
  note "Gateway not restarted — run 'openclaw gateway restart' when convenient"
  note "(or re-run this installer with --restart-gateway)."
fi

# 9. Verify
info "Verification:"
if openclaw plugins inspect reflexio-embedded 2>/dev/null | grep -q "Status: loaded"; then
  info "  ✓ plugin registered and loaded"
else
  echo "  ⚠ plugin did not reach 'loaded' status; run 'openclaw plugins inspect reflexio-embedded' to debug"
fi
if [[ "$ENABLE_CRON" -eq 1 ]]; then
  if openclaw cron list 2>/dev/null | grep -q reflexio-embedded-consolidate; then
    info "  ✓ cron registered"
  else
    echo "  ⚠ cron not visible in 'openclaw cron list'"
  fi
fi

info "Installation complete."
info "On first use, the SKILL.md bootstrap will guide per-agent configuration (active-memory targeting, extraPath registration, embedding provider)."
info "See SECURITY.md for the full list of side effects and privacy tradeoffs."
