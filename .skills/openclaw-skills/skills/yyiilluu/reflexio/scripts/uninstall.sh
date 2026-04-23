#!/usr/bin/env bash
# openclaw-embedded uninstall.sh — reverses install.sh.
#
# Flags:
#   --purge             Also delete workspace/.reflexio/ user data.
#   --restart-gateway   Restart the openclaw gateway when done.
#   -h, --help          Show this help.
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
PURGE_DATA=0
RESTART_GATEWAY=0

info() { echo "==> $*"; }
note() { echo "    $*"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --purge)           PURGE_DATA=1 ;;
    --restart-gateway) RESTART_GATEWAY=1 ;;
    -h|--help)
      sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "unknown flag: $1 (see --help)" >&2; exit 1 ;;
  esac
  shift
done

info "Disabling plugin..."
openclaw plugins disable reflexio-embedded 2>/dev/null || echo "(already disabled)"

info "Uninstalling plugin..."
openclaw plugins uninstall --force reflexio-embedded 2>/dev/null || echo "(already uninstalled)"

info "Removing cron job..."
openclaw cron rm reflexio-embedded-consolidate 2>/dev/null || echo "(already removed)"

info "Removing skills..."
rm -rf "$OPENCLAW_HOME/workspace/skills/reflexio-embedded"
rm -rf "$OPENCLAW_HOME/workspace/skills/reflexio-consolidate"

info "Removing agent definitions..."
rm -f "$OPENCLAW_HOME/workspace/agents/reflexio-extractor.md"
rm -f "$OPENCLAW_HOME/workspace/agents/reflexio-consolidator.md"

info "Removing plugin resources..."
rm -rf "$OPENCLAW_HOME/workspace/plugins/reflexio-embedded"

if [[ "$PURGE_DATA" -eq 1 ]]; then
  info "Purging .reflexio/ user data per --purge flag..."
  rm -rf "$PWD/.reflexio"
else
  info "User data at .reflexio/ preserved. Use --purge to delete it too."
fi

if [[ "$RESTART_GATEWAY" -eq 1 ]]; then
  info "Restarting openclaw gateway..."
  openclaw gateway restart
else
  note "Gateway not restarted — run 'openclaw gateway restart' when convenient"
  note "(or re-run this uninstaller with --restart-gateway)."
fi

info "Uninstall complete."
