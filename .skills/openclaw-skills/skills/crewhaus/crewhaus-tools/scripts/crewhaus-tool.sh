#!/usr/bin/env bash
# CrewHaus Tools API helper
# Usage: bash crewhaus-tool.sh <slug> '<json-body>'
#        bash crewhaus-tool.sh list

set -euo pipefail

API_BASE="https://crewhaus.ai/api/tools"

slug="${1:-}"
body="${2:-}"

if [ -z "$slug" ]; then
  echo "Usage: crewhaus-tool.sh <slug> '<json-body>'"
  echo "       crewhaus-tool.sh list"
  echo ""
  echo "Tools: json-formatter, base64-encoder, uuid-generator, hash-generator,"
  echo "       case-converter, url-encoder, html-entity-encoder, timestamp-converter,"
  echo "       word-counter, jwt-decoder, password-generator, lorem-ipsum-generator,"
  echo "       text-diff, percentage-calculator, regex-tester"
  exit 1
fi

if [ "$slug" = "list" ]; then
  curl -sL "$API_BASE" | python3 -m json.tool 2>/dev/null || curl -sL "$API_BASE"
  exit 0
fi

if [ -z "$body" ]; then
  echo "Error: JSON body required. Example:"
  echo "  crewhaus-tool.sh uuid-generator '{\"count\":5}'"
  exit 1
fi

result=$(curl -sL -X POST "$API_BASE/$slug" \
  -H "Content-Type: application/json" \
  -d "$body")

# Pretty-print if python3 available, otherwise raw
echo "$result" | python3 -m json.tool 2>/dev/null || echo "$result"
