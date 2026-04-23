#!/usr/bin/env bash
set -euo pipefail

# Default to official domain to avoid security scanner warnings
BASE_URL="${LG_AGENT_BASE_URL:-https://lg-data.cc}"

if [[ -n "${LG_AGENT_TOKEN:-}" ]]; then
  curl -sS "${BASE_URL}/agent/skills" \
    -H "Authorization: Bearer ${LG_AGENT_TOKEN}" \
    -H "Accept: application/json"
  exit 0
fi

# fallback: session mode
: "${LG_AGENT_COOKIE_HEADER:?LG_AGENT_COOKIE_HEADER is required when LG_AGENT_TOKEN is not set}"
curl -sS "${BASE_URL}/agent/skills" \
  -H "Cookie: ${LG_AGENT_COOKIE_HEADER}" \
  -H "Accept: application/json"
