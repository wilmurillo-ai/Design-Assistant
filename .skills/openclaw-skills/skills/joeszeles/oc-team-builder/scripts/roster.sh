#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
AGENCY_DIR="${OPENCLAW_AGENCY_DIR:-$PROJECT_DIR/reference/agency-agents-main}"
WORKSPACE_DIR="${OPENCLAW_DATA_DIR:-$PROJECT_DIR/.openclaw}"

usage() {
  cat <<'USAGE'
Usage: roster.sh [OPTIONS]

List available agents across all three rosters.

Options:
  -r, --roster ROSTER   Filter by roster: core, agency, research, all (default: all)
  -d, --division DIV    Filter agency division (engineering, design, marketing, etc.)
  -s, --search QUERY    Case-insensitive search across agent names and descriptions
  -v, --verbose         Show full agent descriptions
  -j, --json            Output as JSON
  -h, --help            Show this help
USAGE
}

roster="all"
division=""
search=""
verbose=false
json_out=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -r|--roster)    roster="${2-}"; shift 2 ;;
    -d|--division)  division="${2-}"; shift 2 ;;
    -s|--search)    search="${2-}"; shift 2 ;;
    -v|--verbose)   verbose=true; shift ;;
    -j|--json)      json_out=true; shift ;;
    -h|--help)      usage; exit 0 ;;
    *)              echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

print_core_roster() {
  local agents=()
  for ws in "$WORKSPACE_DIR"/workspace*/; do
    [ -d "$ws" ] || continue
    local name=$(basename "$ws")
    name="${name#workspace-}"
    [ "$name" = "workspace" ] && name="ceo"
    local soul="$ws/SOUL.md"
    local desc=""
    if [ -f "$soul" ]; then
      desc=$(head -5 "$soul" | grep -i "description:" | head -1 | sed 's/.*description:\s*//' || echo "")
    fi
    [ -z "$desc" ] && desc="Core agent"
    if [ -n "$search" ]; then
      echo "$name $desc" | grep -iq "$search" || continue
    fi
    if $json_out; then
      agents+=("{\"name\":\"$name\",\"roster\":\"core\",\"workspace\":\"$ws\",\"description\":\"$desc\"}")
    elif $verbose; then
      printf "  %-12s %-50s %s\n" "$name" "$desc" "$ws"
    else
      printf "  %-12s %s\n" "$name" "$desc"
    fi
  done
  if $json_out; then
    local IFS=','
    echo "[${agents[*]}]"
  fi
}

print_agency_roster() {
  local agents=()
  local dirs=()
  if [ -n "$division" ]; then
    dirs=("$AGENCY_DIR/$division")
  else
    for d in "$AGENCY_DIR"/*/; do
      local bn=$(basename "$d")
      case "$bn" in
        .github|examples|strategy) continue ;;
        *) dirs+=("$d") ;;
      esac
    done
  fi
  for d in "${dirs[@]}"; do
    [ -d "$d" ] || continue
    local div=$(basename "$d")
    local first=true
    for f in "$d"/*.md; do
      [ -f "$f" ] || continue
      local bn=$(basename "$f" .md)
      local name=$(head -5 "$f" | grep -i "^name:" | head -1 | sed 's/^name:\s*//' || echo "$bn")
      local desc=$(head -5 "$f" | grep -i "^description:" | head -1 | sed 's/^description:\s*//' || echo "")
      if [ -n "$search" ]; then
        echo "$name $desc $div" | grep -iq "$search" || continue
      fi
      if $json_out; then
        name=$(echo "$name" | sed 's/"/\\"/g')
        desc=$(echo "$desc" | sed 's/"/\\"/g')
        agents+=("{\"name\":\"$name\",\"roster\":\"agency\",\"division\":\"$div\",\"file\":\"$f\",\"description\":\"$desc\"}")
      else
        if $first; then
          printf "\n  [%s]\n" "$div"
          first=false
        fi
        if $verbose; then
          printf "    %-30s %s\n" "$name" "$desc"
        else
          printf "    %s\n" "$name"
        fi
      fi
    done
  done
  if $json_out; then
    local IFS=','
    echo "[${agents[*]}]"
  fi
}

print_research_roster() {
  if $json_out; then
    echo '[{"name":"Research Lab","roster":"research","description":"Autonomous experiment loops with metric-driven optimization"}]'
  else
    printf "  %-20s %s\n" "Research Lab" "Autonomous experiment loops — metric-driven optimization"
    printf "  %-20s %s\n" "  Capabilities:" "Baseline → Modify → Measure → Keep/Discard cycles"
    printf "  %-20s %s\n" "  Activation:" "Read TEAM-RESEARCH.md for experiment protocol"
  fi
}

if [ "$roster" = "all" ] || [ "$roster" = "core" ]; then
  $json_out || echo "=== CORE TEAM ==="
  print_core_roster
fi

if [ "$roster" = "all" ] || [ "$roster" = "agency" ]; then
  $json_out || echo -e "\n=== AGENCY DIVISION (55+ Specialists) ==="
  print_agency_roster
fi

if [ "$roster" = "all" ] || [ "$roster" = "research" ]; then
  $json_out || echo -e "\n=== RESEARCH LAB ==="
  print_research_roster
fi
