#!/usr/bin/env bash
set -euo pipefail

# SerpAPI Search Script
# Usage: search.sh <query> [options]
#
# Engines: google (default), google_news, google_local
# Options: --engine, --country, --lang, --location, --num, --json, --api-key

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE="google"
COUNTRY="us"
LANG="en"
LOCATION=""
NUM=10
RAW_JSON=false
API_KEY="${SERPAPI_API_KEY:-}"
QUERY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --engine)   ENGINE="$2"; shift 2 ;;
    --country)  COUNTRY="$2"; shift 2 ;;
    --lang)     LANG="$2"; shift 2 ;;
    --location) LOCATION="$2"; shift 2 ;;
    --num)      NUM="$2"; shift 2 ;;
    --json)     RAW_JSON=true; shift ;;
    --api-key)  API_KEY="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: search.sh <query> [--engine google|google_news|google_local] [--country br] [--lang pt] [--location 'São Paulo'] [--num 10] [--json]"
      exit 0
      ;;
    *) QUERY="${QUERY:+$QUERY }$1"; shift ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "Error: query is required" >&2
  exit 1
fi

# Resolve API key
if [[ -z "$API_KEY" ]]; then
  SKILL_ENV="$(dirname "$SCRIPT_DIR")/.env"
  [[ -f "$SKILL_ENV" ]] && API_KEY=$(grep -E "^SERPAPI_API_KEY=" "$SKILL_ENV" 2>/dev/null | cut -d= -f2- || true)
  [[ -z "$API_KEY" && -f "$HOME/.config/serpapi/api_key" ]] && API_KEY=$(cat "$HOME/.config/serpapi/api_key")
fi

if [[ -z "$API_KEY" ]]; then
  echo "Error: No API key. Set SERPAPI_API_KEY or create ~/.config/serpapi/api_key" >&2
  exit 1
fi

# Delegate the actual HTTP fetch to Python so the API key never appears
# in the process list (curl URL args are visible to all users via `ps aux`).
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

SERPAPI_API_KEY="$API_KEY" python3 - "$ENGINE" "$QUERY" "$COUNTRY" "$LANG" "$NUM" "${LOCATION}" "$TMPFILE" << 'PYEOF'
import os, sys, json, urllib.request, urllib.parse

engine, query, country, lang, num, location, outfile = sys.argv[1:]

params = {
    "engine": engine,
    "q": query,
    "api_key": os.environ["SERPAPI_API_KEY"],
    "gl": country,
    "hl": lang,
}
if engine == "google":
    params["num"] = num
if location:
    params["location"] = location

url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
try:
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
except Exception as e:
    print(f"Request failed: {e}", file=sys.stderr)
    sys.exit(1)

with open(outfile, "w") as f:
    json.dump(data, f)
PYEOF

# Check error
ERROR=$(python3 -c "import json;d=json.load(open('$TMPFILE'));print(d.get('error',''))" 2>/dev/null || echo "")
if [[ -n "$ERROR" ]]; then
  echo "SerpAPI Error: $ERROR" >&2
  exit 1
fi

if [[ "$RAW_JSON" == true ]]; then
  cat "$TMPFILE"
  exit 0
fi

# Format
python3 "$SCRIPT_DIR/format.py" "$TMPFILE" "$ENGINE"
