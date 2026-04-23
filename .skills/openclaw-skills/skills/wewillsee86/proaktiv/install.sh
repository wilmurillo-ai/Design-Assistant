#!/usr/bin/env bash
# ============================================================
# Proactive v1.0.18 — Installer
# ============================================================

set -e

echo "Proactive v1.0.18 Installer"
echo "==========================="

# --- CONFIG ---
TARGET_DIR="/data/.openclaw/skills/proaktiv"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"

# --- STEP 1: Create directory ---
echo "[1/6] Creating directory structure..."
mkdir -p "$TARGET_DIR"

# --- STEP 2: Copy scripts ---
echo "[2/6] Copying scripts..."
cp "$REPO_DIR/proaktiv_check.py"     "$TARGET_DIR/"
cp "$REPO_DIR/interest_evolve.py"   "$TARGET_DIR/"
cp "$REPO_DIR/feedback_update.py"   "$TARGET_DIR/"

# --- STEP 3: Copy templates ---
echo "[3/6] Copying templates..."
mkdir -p "$TARGET_DIR/templates"
cp "$REPO_DIR/templates/proaktiv_state.json"  "$TARGET_DIR/"
cp "$REPO_DIR/templates/interest_graph.json" "$TARGET_DIR/"
cp "$REPO_DIR/templates/social_knowledge.json" "$TARGET_DIR/"

# --- STEP 4: Copy topic templates ---
echo "[4/6] Copying topic templates..."
cp "$REPO_DIR/TOPIC_TEMPLATES.md" "$TARGET_DIR/"

# --- STEP 5: Prompt for Telegram Chat ID ---
echo "[5/6] Telegram Chat ID..."
echo ""
echo "  To send you pings, Proactive needs your Telegram chat ID."
echo "  Find it by messaging @userinfobot on Telegram."
echo ""
read -p "  Enter your Telegram chat ID (number): " TELEGRAM_CHAT_ID

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "  SKIPPED — set OPENCLAW_TELEGRAM_NR manually in $TARGET_DIR/.env"
else
    echo "OPENCLAW_TELEGRAM_NR=$TELEGRAM_CHAT_ID" > "$TARGET_DIR/.env"
    chmod 600 "$TARGET_DIR/.env"
    echo "  Saved to $TARGET_DIR/.env"
fi

# --- STEP 6: Make scripts executable ---
echo "[6/6] Making scripts executable..."
chmod +x "$TARGET_DIR/proaktiv_check.py"
chmod +x "$TARGET_DIR/interest_evolve.py"
chmod +x "$TARGET_DIR/feedback_update.py"

# --- Set up OpenClaw Cron job ---
echo ""
echo "Setting up OpenClaw Cron job (every 30 min)..."

"$OPENCLAW_BIN" cron list 2>/dev/null | grep -q "PROAKTIV" && \
  "$OPENCLAW_BIN" cron list 2>/dev/null | grep "PROAKTIV" | awk '{print $1}' | while read id; do \
    "$OPENCLAW_BIN" cron remove "$id" 2>/dev/null; done || true

(
  export OPENCLAW_TELEGRAM_NR
  "$OPENCLAW_BIN" cron add \
    --name "PROAKTIV-30min" \
    --cron "*/30 * * * *" \
    --tz "Europe/Berlin" \
    --session "isolated" \
    --no-deliver \
    --system-event "[SYSTEM-TRIGGER: PROAKTIV_CHECK | ambient_context=auto]" \
    2>/dev/null
) && echo "  PROAKTIV-30min cron registered" || \
  echo "  Could not register cron — run manually."

echo ""
echo "==========================="
echo "Proactive skill installed successfully!"
echo ""
echo "IMPORTANT:"
echo "1. If you skipped the chat ID, create:"
echo "   $TARGET_DIR/.env"
echo "   with: OPENCLAW_TELEGRAM_NR=YOUR_CHAT_ID"
echo ""
echo "2. Restart: openclaw gateway restart"
echo ""
echo "3. To activate the session, send your agent a message:"
echo "   'Hello' or 'Ping' in the chat!"
echo ""
echo "The routing instructions are sent automatically with each trigger."
echo "No global files are modified. All data stays in \$TARGET_DIR."
echo "==========================="
