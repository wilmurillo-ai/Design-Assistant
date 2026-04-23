#!/usr/bin/env bash
set -euo pipefail

base="https://skills.sh/bookingdesk-ai/kontour-travel-planner/kontour-travel-planner"
stamp="$(date +%s)"

fetch() {
  curl -fsSL "$1" || true
}

listing="$(fetch "$base?nocache=$stamp")"
ath="$(fetch "$base/security/agent-trust-hub?nocache=$stamp")"
socket="$(fetch "$base/security/socket?nocache=$stamp")"
snyk="$(fetch "$base/security/snyk?nocache=$stamp")"

listing_version="VERSION_DELTA_UNOBSERVABLE_STATIC"
if echo "$listing" | grep -Eiq "version[:[:space:]]*[0-9]+\.[0-9]+\.[0-9]+"; then
  listing_version="VERSION_TOKEN_FOUND_STATIC"
fi

ath_verdict="INCONCLUSIVE_STATIC"
if echo "$ath" | grep -Eiq "Risk Level:[[:space:]]*SAFE"; then
  ath_verdict="SAFE"
fi

# Extract a stable ATH reason signature so pre/post runs can detect reason text drift.
ath_reason_lines="$(echo "$ath" | grep -Eo "\[SAFE\]:[^\n]+" || true)"
ath_reason_hash="UNAVAILABLE"
if [ -n "$ath_reason_lines" ]; then
  ath_reason_hash="$(printf "%s" "$ath_reason_lines" | shasum -a 256 | awk '{print $1}')"
fi

socket_verdict="INCONCLUSIVE_STATIC"
if echo "$socket" | grep -Eiq "\b(pass|safe|fail|malicious|risk level)\b"; then
  socket_verdict="VERDICT_TOKEN_PRESENT_STATIC"
fi

snyk_verdict="INCONCLUSIVE_STATIC"
if echo "$snyk" | grep -Eiq "\bPass\b"; then
  snyk_verdict="PASS"
fi

clawhub_listing="$(fetch "https://clawhub.ai/skylinehk/kontour-travel-planner?nocache=$stamp")"
clawhub_version="VERSION_DELTA_UNOBSERVABLE_STATIC"
clawhub_state="STATIC_CONTENT_PARTIAL"
if echo "$clawhub_listing" | grep -Eiq "version[:[:space:]]*[0-9]+\.[0-9]+\.[0-9]+"; then
  clawhub_version="VERSION_TOKEN_FOUND_STATIC"
fi
if echo "$clawhub_listing" | grep -Eiq "Loading skill"; then
  clawhub_state="DYNAMIC_LOADING_GATE"
fi

printf "listing_version_static=%s\n" "$listing_version"
printf "ath_verdict=%s\n" "$ath_verdict"
printf "ath_reason_hash=%s\n" "$ath_reason_hash"
printf "socket_verdict=%s\n" "$socket_verdict"
printf "snyk_verdict=%s\n" "$snyk_verdict"
printf "clawhub_version_static=%s\n" "$clawhub_version"
printf "clawhub_state=%s\n" "$clawhub_state"
