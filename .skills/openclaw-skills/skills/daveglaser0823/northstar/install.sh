#!/usr/bin/env bash
# Northstar - Root install shim
# Delegates to scripts/install.sh (the actual installer)
# This file exists so both of these work:
#   curl -fsSL .../main/install.sh | bash
#   curl -fsSL .../main/scripts/install.sh | bash

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$INSTALL_DIR/scripts/install.sh" ]; then
    exec "$INSTALL_DIR/scripts/install.sh" "$@"
else
    # Fallback: fetch from GitHub if running via curl | bash
    echo "Fetching Northstar installer..."
    curl -fsSL "https://raw.githubusercontent.com/Daveglaser0823/northstar-skill/main/scripts/install.sh" | bash
fi
