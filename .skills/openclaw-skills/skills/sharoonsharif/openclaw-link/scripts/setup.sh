#!/bin/bash
# ClawLink Setup — One command to get your agent mesh running
# Usage: bash setup.sh [server|client|both]

set -e

MODE="${1:-both}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════════════╗"
echo "║          🔗 ClawLink Setup                   ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Mode: $MODE                                 "
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found."
    exit 1
fi

# Install dependencies
echo "[1/3] Installing dependencies..."
pip install aiohttp requests 2>/dev/null || pip install --user aiohttp requests 2>/dev/null || {
    pip install aiohttp requests --break-system-packages 2>/dev/null
}

# Optional: mDNS support
echo "[2/3] Installing mDNS support (optional)..."
pip install zeroconf 2>/dev/null || pip install --user zeroconf 2>/dev/null || {
    pip install zeroconf --break-system-packages 2>/dev/null || echo "  (mDNS skipped — LAN auto-discovery won't work, but HTTP is fine)"
}

echo "[3/3] Setup complete!"
echo ""

if [ "$MODE" = "server" ] || [ "$MODE" = "both" ]; then
    echo "Start the relay server with:"
    echo "  python3 $SCRIPT_DIR/server.py"
    echo ""
    echo "Options:"
    echo "  --port 9077       Custom port (default: 9077)"
    echo "  --host 0.0.0.0    Bind to all interfaces"
    echo "  --no-mdns         Disable LAN broadcast"
    echo ""
fi

if [ "$MODE" = "client" ] || [ "$MODE" = "both" ]; then
    echo "Connect an agent with:"
    echo "  python3 $SCRIPT_DIR/client.py register --name 'my-agent' --caps 'code,search'"
    echo ""
    echo "Or scan for relays on your LAN:"
    echo "  python3 $SCRIPT_DIR/client.py scan"
    echo ""
fi

if [ "$MODE" = "both" ]; then
    echo "Quick start (run in separate terminals):"
    echo "  Terminal 1:  python3 $SCRIPT_DIR/server.py"
    echo "  Terminal 2:  python3 $SCRIPT_DIR/client.py register --name agent-a --caps 'code,search'"
    echo "  Terminal 3:  python3 $SCRIPT_DIR/client.py register --name agent-b --caps 'write,review'"
    echo ""
    echo "Then delegate a task:"
    echo "  python3 $SCRIPT_DIR/client.py delegate --to <agent-b-id> --task 'Review my code'"
fi
