#!/usr/bin/env bash
set -euo pipefail

# Default to official domain to avoid security scanner warnings
BASE_URL="${LG_AGENT_BASE_URL:-https://lg-data.cc}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <list-mine|list-all|approve|reject> [id] [json-body]" >&2
  exit 1
fi

ACTION="$1"

auth_headers() {
  if [[ -n "${LG_AGENT_TOKEN:-}" ]]; then
    echo "Authorization: Bearer ${LG_AGENT_TOKEN}"
    return
  fi
  : "${LG_AGENT_COOKIE_HEADER:?LG_AGENT_COOKIE_HEADER is required when LG_AGENT_TOKEN is not set}"
  echo "Cookie: ${LG_AGENT_COOKIE_HEADER}"
}

csrf_header_if_needed() {
  if [[ -n "${LG_AGENT_TOKEN:-}" ]]; then
    return
  fi
  : "${LG_AGENT_CSRF_TOKEN:?LG_AGENT_CSRF_TOKEN is required when LG_AGENT_TOKEN is not set}"
  echo "X-CSRF-Token: ${LG_AGENT_CSRF_TOKEN}"
}

AUTH_HEADER=$(auth_headers)
CSRF_HEADER=$(csrf_header_if_needed || true)

case "$ACTION" in
  list-mine)
    curl -sS "${BASE_URL}/api/agent/approvals?mine=true" \
      -H "$AUTH_HEADER" \
      -H "Accept: application/json"
    ;;
  list-all)
    curl -sS "${BASE_URL}/api/agent/approvals?mine=false" \
      -H "$AUTH_HEADER" \
      -H "Accept: application/json"
    ;;
  approve|reject)
    if [[ $# -lt 2 ]]; then
      echo "Usage: $0 ${ACTION} <approvalId> [json-body]" >&2
      exit 1
    fi
    ID="$2"
    BODY="${3:-{\"reason\":\"${ACTION} via script\"}}"
    if [[ -n "$CSRF_HEADER" ]]; then
      curl -sS "${BASE_URL}/api/agent/approvals/${ID}/${ACTION}" \
        -X POST \
        -H "$AUTH_HEADER" \
        -H "$CSRF_HEADER" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        --data "${BODY}"
    else
      curl -sS "${BASE_URL}/api/agent/approvals/${ID}/${ACTION}" \
        -X POST \
        -H "$AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        --data "${BODY}"
    fi
    ;;
  *)
    echo "Unsupported action: ${ACTION}" >&2
    exit 1
    ;;
esac
