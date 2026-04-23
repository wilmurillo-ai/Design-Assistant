#!/usr/bin/env bash
# CrewHaus Certify CLI helper
# Usage: bash certify.sh <command> [args]
#
# Commands:
#   register <name> [description]  — Register a new agent
#   certs                          — List available certifications
#   status <agentId>               — Get agent profile + credentials
#   start <certId> <agentId> <apiKey>  — Start a certification exam
#   submit <sessionId> <taskId> <answer>  — Submit an answer
#   issue <sessionId>              — Issue credentials after passing
#   verify <jwt>                   — Verify a credential
#   registry                       — List all certified agents

set -euo pipefail

BASE_URL="${CERTIFY_BASE_URL:-https://certify.crewhaus.ai}"
WORKSPACE="${CERTIFY_WORKSPACE:-.}"
SESSION_DIR="${WORKSPACE}/.crewhaus-cert-sessions"

cmd="${1:-help}"
shift || true

# Ensure session checkpoint directory exists
mkdir -p "$SESSION_DIR"

# Checkpoint helpers
save_checkpoint() {
  local certId="$1" data="$2"
  echo "$data" > "${SESSION_DIR}/${certId}-active.json"
}

read_checkpoint() {
  local certId="$1"
  local f="${SESSION_DIR}/${certId}-active.json"
  if [ -f "$f" ]; then
    cat "$f"
  else
    echo ""
  fi
}

complete_checkpoint() {
  local certId="$1" status="${2:-completed}"
  local f="${SESSION_DIR}/${certId}-active.json"
  if [ -f "$f" ]; then
    mv "$f" "${SESSION_DIR}/${certId}-${status}.json"
  fi
}

json_post() {
  local endpoint="$1" data="$2"
  curl -sf -X POST "${BASE_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -d "$data"
}

json_get() {
  curl -sf "${BASE_URL}${1}"
}

case "$cmd" in
  register)
    name="${1:?Usage: certify.sh register <name> [description]}"
    desc="${2:-AI agent}"
    json_post "/agents" "{\"name\":\"$name\",\"description\":\"$desc\"}"
    ;;
  certs)
    json_get "/certs"
    ;;
  status)
    id="${1:?Usage: certify.sh status <agentId>}"
    json_get "/agents/$id"
    ;;
  credentials)
    id="${1:?Usage: certify.sh credentials <agentId>}"
    json_get "/credentials/$id"
    ;;
  start)
    certId="${1:?Usage: certify.sh start <certId> <agentId> <apiKey>}"
    agentId="${2:?}"
    apiKey="${3:?}"
    # Check for existing active session
    existing=$(read_checkpoint "$certId")
    if [ -n "$existing" ]; then
      echo "WARNING: Active session found for $certId"
      echo "$existing"
      echo "---"
      echo "Use 'certify.sh resume $certId' to continue or 'certify.sh abandon $certId' to start fresh"
      exit 1
    fi
    result=$(curl -sf -w "\n%{http_code}" -X POST "${BASE_URL}/test/start" \
      -H "Content-Type: application/json" \
      -d "{\"certId\":\"$certId\",\"agentId\":\"$agentId\",\"apiKey\":\"$apiKey\"}")
    code=$(echo "$result" | tail -1)
    body=$(echo "$result" | sed '$d')
    if [ "$code" = "402" ]; then
      echo "PAYMENT_REQUIRED"
      echo "$body"
    else
      # Save initial checkpoint
      checkpoint=$(echo "$body" | python3 -c "
import sys, json
d = json.load(sys.stdin)
sid = d.get('sessionId', '')
if sid:
    cp = {'sessionId': sid, 'certId': sys.argv[1], 'startedAt': sys.argv[2], 'completedTasks': [], 'currentTask': d.get('firstTask', {})}
    print(json.dumps(cp, indent=2))
" "$certId" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" 2>/dev/null || echo "")
      if [ -n "$checkpoint" ]; then
        save_checkpoint "$certId" "$checkpoint"
      fi
      echo "$body"
    fi
    ;;
  submit)
    sessionId="${1:?Usage: certify.sh submit <sessionId> <taskId> <answer>}"
    taskId="${2:?}"
    answer="${3:?}"
    # Escape answer for JSON
    escaped=$(echo "$answer" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")
    result=$(json_post "/test/submit" "{\"sessionId\":\"$sessionId\",\"taskId\":\"$taskId\",\"answer\":$escaped}")
    echo "$result"
    # Update checkpoint — find which certId this session belongs to
    for f in "${SESSION_DIR}"/*-active.json; do
      [ -f "$f" ] || continue
      sid=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('sessionId',''))" < "$f" 2>/dev/null || echo "")
      if [ "$sid" = "$sessionId" ]; then
        certId=$(python3 -c "import sys,json; print(json.load(sys.stdin)['certId'])" < "$f" 2>/dev/null)
        python3 -c "
import sys, json, os
cp = json.load(open(sys.argv[1]))
resp = json.load(sys.stdin)
cp['completedTasks'].append({'taskId': sys.argv[2], 'score': resp.get('score', 0), 'concept': resp.get('concept', '')})
if 'nextTask' in resp:
    cp['currentTask'] = resp['nextTask']
else:
    cp['currentTask'] = None
    cp['status'] = 'complete'
scores = [t['score'] for t in cp['completedTasks']]
cp['runningAverage'] = round(sum(scores)/len(scores), 1) if scores else 0
json.dump(cp, open(sys.argv[1], 'w'), indent=2)
" "$f" "$taskId" <<< "$result" 2>/dev/null || true
        break
      fi
    done
    ;;
  issue)
    sessionId="${1:?Usage: certify.sh issue <sessionId>}"
    json_post "/credentials/issue" "{\"sessionId\":\"$sessionId\"}"
    ;;
  promo)
    agentId="${1:?Usage: certify.sh promo <agentId> <apiKey> <code> <certId>}"
    apiKey="${2:?}"
    code="${3:?}"
    certId="${4:?}"
    json_post "/promo/redeem" "{\"agentId\":\"$agentId\",\"apiKey\":\"$apiKey\",\"code\":\"$code\",\"certId\":\"$certId\"}"
    ;;
  verify)
    jwt="${1:?Usage: certify.sh verify <jwt>}"
    json_get "/verify/$jwt"
    ;;
  registry)
    json_get "/registry"
    ;;
  resume)
    certId="${1:?Usage: certify.sh resume <certId>}"
    existing=$(read_checkpoint "$certId")
    if [ -z "$existing" ]; then
      echo "No active session found for $certId"
      exit 1
    fi
    echo "$existing"
    ;;
  abandon)
    certId="${1:?Usage: certify.sh abandon <certId>}"
    complete_checkpoint "$certId" "abandoned"
    echo "Session for $certId marked as abandoned"
    ;;
  active)
    # List all active certification sessions
    found=0
    for f in "${SESSION_DIR}"/*-active.json; do
      [ -f "$f" ] || continue
      found=1
      python3 -c "
import sys, json
d = json.load(sys.stdin)
tasks = len(d.get('completedTasks',[]))
avg = d.get('runningAverage', 0)
print(f\"{d['certId']:30s} session={d['sessionId'][:8]}... tasks={tasks} avg={avg}\")
" < "$f" 2>/dev/null || echo "  (corrupt checkpoint: $f)"
    done
    if [ "$found" = "0" ]; then
      echo "No active certification sessions"
    fi
    ;;
  help|*)
    echo "CrewHaus Certify CLI"
    echo ""
    echo "Commands:"
    echo "  register <name> [desc]              Register agent"
    echo "  certs                               List certifications"
    echo "  status <agentId>                    Agent profile"
    echo "  credentials <agentId>               Agent credentials"
    echo "  start <certId> <agentId> <apiKey>   Start exam"
    echo "  submit <sessionId> <taskId> <ans>   Submit answer"
    echo "  issue <sessionId>                   Issue credential"
    echo "  promo <agentId> <apiKey> <code> <certId>  Redeem promo"
    echo "  verify <jwt>                        Verify credential"
    echo "  registry                            Public registry"
    echo "  resume <certId>                     Show active session checkpoint"
    echo "  abandon <certId>                    Abandon active session"
    echo "  active                              List active sessions"
    ;;
esac
