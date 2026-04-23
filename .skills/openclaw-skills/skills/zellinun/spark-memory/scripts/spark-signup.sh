#!/bin/bash
# Sign up for Spark — creates account, writes config, restarts gateway.
# The user should only need to provide an email and password.
# Everything else is automatic.
#
# Usage:
#   ./spark-signup.sh                          # interactive
#   ./spark-signup.sh --email me@co.com --password mysecret

set -e

SPARK_SIGNUP_URL="${SPARK_SIGNUP_URL:-https://zellin.ai/api/spark-signup}"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
SKILL_KEY="spark-memory"

# ── Parse flags ──────────────────────────────────────────────────────────────
EMAIL=""
PASSWORD=""
SKIP_CONFIG=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --email)       EMAIL="$2";       shift 2 ;;
    --password)    PASSWORD="$2";    shift 2 ;;
    --skip-config) SKIP_CONFIG=true; shift   ;;
    *)             echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# ── Consent ───────────────────────────────────────────────────────────────────
echo ""
echo "🧠 Spark Memory Setup"
echo "━━━━━━━━━━━━━━━━━━━━━"
echo "This will:"
echo "  1. Create a free account at zellin.ai"
echo "  2. Save your API credentials to your OpenClaw config"
echo "  3. Restart your agent so memory is active"
echo ""
echo "Your memories are stored on Zellin's servers (encrypted, org-isolated)."
echo "Privacy policy: https://zellin.ai"
echo ""
echo -n "Continue? (y/n): "
read -r CONSENT
if [ "$CONSENT" != "y" ] && [ "$CONSENT" != "Y" ]; then
  echo "Cancelled. You can set up manually at https://zellin.ai/signup"
  exit 0
fi
echo ""

# ── Interactive prompts ──────────────────────────────────────────────────────
if [ -z "$EMAIL" ]; then
  echo -n "Email: "
  read -r EMAIL
fi

if [ -z "$PASSWORD" ]; then
  echo -n "Password (min 8 characters): "
  read -s -r PASSWORD
  echo
fi

# ── Validate ──────────────────────────────────────────────────────────────────
if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
  echo "Error: email and password are required." >&2
  exit 1
fi

if [ ${#PASSWORD} -lt 8 ]; then
  echo "Error: password must be at least 8 characters." >&2
  exit 1
fi

# ── Name from email ──────────────────────────────────────────────────────────
NAME=$(echo "$EMAIL" | cut -d@ -f1 | sed 's/[._-]/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2); print}')
if [ -z "$NAME" ]; then
  NAME="Spark User"
fi

# ── Send signup request ───────────────────────────────────────────────────────
echo "Creating your Spark account..."

BODY=$(python3 -c "
import json, sys
print(json.dumps({
    'email': sys.argv[1],
    'password': sys.argv[2],
    'name': sys.argv[3],
}))
" "$EMAIL" "$PASSWORD" "$NAME")

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$SPARK_SIGNUP_URL" \
  -H "Content-Type: application/json" \
  -d "$BODY")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY_CONTENT=$(echo "$RESPONSE" | sed '$d')

# ── Handle response ───────────────────────────────────────────────────────────
if [ "$HTTP_CODE" != "201" ]; then
  ERROR_MSG=$(echo "$BODY_CONTENT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('error', d.get('message', 'Unknown error')))" 2>/dev/null || echo "$BODY_CONTENT")
  if echo "$ERROR_MSG" | grep -qi "already.*registered\|already.*exists\|email_exists"; then
    echo ""
    echo "An account with this email already exists."
    echo "If you have your credentials, set them with:"
    echo "  openclaw gateway config.patch '{\"skills\":{\"entries\":{\"spark-memory\":{\"env\":{\"SPARK_API_KEY\":\"YOUR_KEY\",\"SPARK_ORG_ID\":\"YOUR_ORG\"}}}}}'"
    echo ""
    echo "Or sign in at https://zellin.ai to find your API key."
  else
    echo "Error ($HTTP_CODE): $ERROR_MSG" >&2
  fi
  exit 1
fi

# ── Parse credentials ─────────────────────────────────────────────────────────
API_KEY=$(echo "$BODY_CONTENT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('api_key',''))" 2>/dev/null)
ORG_ID=$(echo "$BODY_CONTENT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('org_id',''))" 2>/dev/null)

if [ -z "$API_KEY" ] || [ -z "$ORG_ID" ]; then
  echo "Error: signup succeeded but couldn't parse credentials." >&2
  echo "Response: $BODY_CONTENT" >&2
  exit 1
fi

echo ""
echo "✅ Spark account created!"

# ── Auto-configure OpenClaw ───────────────────────────────────────────────────
if [ "$SKIP_CONFIG" = true ]; then
  echo ""
  echo "Credentials (save these):"
  echo "  SPARK_API_KEY=$API_KEY"
  echo "  SPARK_ORG_ID=$ORG_ID"
  exit 0
fi

echo ""
echo "Ready to save credentials to your OpenClaw config and restart the gateway."
echo -n "Save and restart? (y/n): "
read -r SAVE_CONSENT
if [ "$SAVE_CONSENT" != "y" ] && [ "$SAVE_CONSENT" != "Y" ]; then
  echo ""
  echo "Credentials (save these manually):"
  echo "  SPARK_API_KEY=$API_KEY"
  echo "  SPARK_ORG_ID=$ORG_ID"
  echo ""
  echo "Add to your OpenClaw config or shell profile, then restart:"
  echo "  openclaw gateway restart"
  exit 0
fi

# Method 1: Try openclaw gateway config.patch (preferred — works even if config format changes)
if command -v openclaw &>/dev/null; then
  echo "Configuring OpenClaw..."

  # Build the patch JSON
  PATCH_JSON=$(python3 -c "
import json, sys
patch = {
    'skills': {
        'entries': {
            'spark-memory': {
                'env': {
                    'SPARK_API_KEY': sys.argv[1],
                    'SPARK_ORG_ID': sys.argv[2]
                }
            }
        }
    }
}
print(json.dumps(patch))
" "$API_KEY" "$ORG_ID")

  # Try config.patch via the gateway REST API
  GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18789}"
  PATCH_RESULT=$(curl -s -X POST "http://127.0.0.1:${GATEWAY_PORT}/api/config" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"config.patch\",\"raw\":$(echo "$PATCH_JSON" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")}" 2>/dev/null || echo "FAILED")

  if echo "$PATCH_RESULT" | grep -qi "ok\|success\|true"; then
    echo "✅ Credentials saved to OpenClaw config."
    echo "✅ Gateway restarting with memory active..."
    echo ""
    echo "You're all set! Your agent now has persistent memory."
    echo "It will remember your conversations, learn your preferences,"
    echo "and get smarter every day."
    exit 0
  fi

  # Fallback: write directly to config file
  echo "Gateway API not reachable, writing config directly..."
fi

# Method 2: Write directly to openclaw.json
if [ -f "$OPENCLAW_CONFIG" ]; then
  python3 -c "
import json, sys

config_path = sys.argv[1]
api_key = sys.argv[2]
org_id = sys.argv[3]

with open(config_path, 'r') as f:
    config = json.load(f)

# Ensure nested structure exists
config.setdefault('skills', {})
config['skills'].setdefault('entries', {})
config['skills']['entries'].setdefault('spark-memory', {})
config['skills']['entries']['spark-memory'].setdefault('env', {})

# Write credentials
config['skills']['entries']['spark-memory']['env']['SPARK_API_KEY'] = api_key
config['skills']['entries']['spark-memory']['env']['SPARK_ORG_ID'] = org_id

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print('Config updated.')
" "$OPENCLAW_CONFIG" "$API_KEY" "$ORG_ID" 2>/dev/null

  if [ $? -eq 0 ]; then
    echo "✅ Credentials saved to $OPENCLAW_CONFIG"

    # Try to restart gateway
    if command -v openclaw &>/dev/null; then
      echo "Restarting gateway..."
      openclaw gateway restart 2>/dev/null && echo "✅ Gateway restarted." || echo "⚠️  Restart manually: openclaw gateway restart"
    else
      echo "Restart your gateway to activate: openclaw gateway restart"
    fi

    echo ""
    echo "You're all set! Your agent now has persistent memory."
    exit 0
  fi
fi

# Method 3: Last resort — just print credentials
echo ""
echo "Couldn't auto-configure. Set these manually:"
echo ""
echo "  SPARK_API_KEY=$API_KEY"
echo "  SPARK_ORG_ID=$ORG_ID"
echo ""
echo "Add to your OpenClaw config or shell profile, then restart:"
echo "  openclaw gateway restart"
