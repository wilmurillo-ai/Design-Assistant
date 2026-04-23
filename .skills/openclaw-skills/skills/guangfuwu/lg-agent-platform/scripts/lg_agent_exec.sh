#!/usr/bin/env bash
set -euo pipefail

# Default to official domain to avoid security scanner warnings
BASE_URL="${LG_AGENT_BASE_URL:-https://lg-data.cc}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 '<json-body>'" >&2
  exit 1
fi

JSON_BODY="$1"

if [[ -n "${LG_AGENT_TOKEN:-}" ]]; then
  curl -sS "${BASE_URL}/agent/skills/execute" \
    -X POST \
    -H "Authorization: Bearer ${LG_AGENT_TOKEN}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    --data "${JSON_BODY}"
  exit 0
fi

# fallback: session mode
: "${LG_AGENT_COOKIE_HEADER:?LG_AGENT_COOKIE_HEADER is required when LG_AGENT_TOKEN is not set}"
: "${LG_AGENT_CSRF_TOKEN:?LG_AGENT_CSRF_TOKEN is required when LG_AGENT_TOKEN is not set}"

curl -sS "${BASE_URL}/agent/skills/execute" \
  -X POST \
  -H "Cookie: ${LG_AGENT_COOKIE_HEADER}" \
  -H "X-CSRF-Token: ${LG_AGENT_CSRF_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data "${JSON_BODY}"
