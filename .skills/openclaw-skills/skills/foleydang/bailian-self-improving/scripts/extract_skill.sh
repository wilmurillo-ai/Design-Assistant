#!/usr/bin/env bash
# =====================================================
# Bailian Skill Extraction Script
# Usage: ./extract_skill.sh <messages_json> [existing_skills_json]
# Config: config.json in same directory (or use DASHSCOPE_API_KEY env)
# =====================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../config.json"

# Default values
DEFAULT_ENDPOINT="https://dashscope.aliyuncs.com/api/v2/apps/memory/skills/extract"
DEFAULT_TIMEOUT=30

# Load config from file if exists
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        # Use jq to parse JSON config
        if command -v jq &> /dev/null; then
            CONFIG_API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
            CONFIG_ENDPOINT=$(jq -r '.endpoint // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
            CONFIG_TIMEOUT=$(jq -r '.timeout // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
        else
            # Fallback: simple grep for api_key if jq not available
            CONFIG_API_KEY=$(grep -o '"api_key"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*:.*"\([^"]*\)"/\1/' || echo "")
        fi
    fi
}

# Get API key (config file takes priority over env)
get_api_key() {
    if [ -n "${CONFIG_API_KEY:-}" ]; then
        echo "$CONFIG_API_KEY"
    elif [ -n "${DASHSCOPE_API_KEY:-}" ]; then
        echo "$DASHSCOPE_API_KEY"
    else
        return 1
    fi
}

# Get endpoint (config file takes priority over env, then default)
get_endpoint() {
    if [ -n "${CONFIG_ENDPOINT:-}" ]; then
        echo "$CONFIG_ENDPOINT"
    elif [ -n "${DASHSCOPE_ENDPOINT:-}" ]; then
        echo "$DASHSCOPE_ENDPOINT"
    else
        echo "$DEFAULT_ENDPOINT"
    fi
}

# Get timeout
get_timeout() {
    if [ -n "${CONFIG_TIMEOUT:-}" ]; then
        echo "$CONFIG_TIMEOUT"
    elif [ -n "${DASHSCOPE_TIMEOUT:-}" ]; then
        echo "$DASHSCOPE_TIMEOUT"
    else
        echo "$DEFAULT_TIMEOUT"
    fi
}

# Load configuration
load_config

# Get API key
if ! API_KEY=$(get_api_key); then
    echo "Error: DASHSCOPE_API_KEY not set" >&2
    echo "  Set environment variable: export DASHSCOPE_API_KEY='your-key'" >&2
    echo "  Or configure in: $CONFIG_FILE" >&2
    exit 1
fi

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <messages_json> [existing_skills_json]" >&2
    echo "  messages_json: JSON array of conversation messages" >&2
    echo "  existing_skills_json: Optional JSON array of existing skills" >&2
    exit 1
fi

MESSAGES="$1"
EXISTING_SKILLS="${2:-}"
ENDPOINT=$(get_endpoint)
TIMEOUT=$(get_timeout)

# Build request body
if [ -n "$EXISTING_SKILLS" ]; then
    REQUEST_BODY=$(cat <<EOF
{
  "messages": $MESSAGES,
  "existing_skills": $EXISTING_SKILLS
}
EOF
)
else
    REQUEST_BODY=$(cat <<EOF
{
  "messages": $MESSAGES
}
EOF
)
fi

# Call API
RESPONSE=$(curl -s -w "\n%{http_code}" \
    --max-time "$TIMEOUT" \
    -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "$REQUEST_BODY" 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
    echo "Error: API returned HTTP $HTTP_CODE" >&2
    echo "$BODY" >&2
    exit 1
fi

# Output result
echo "$BODY"