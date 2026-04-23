#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
AGENCY_DIR="${OPENCLAW_AGENCY_DIR:-$PROJECT_DIR/reference/agency-agents-main}"

usage() {
  cat <<'USAGE'
Usage: activate.sh [OPTIONS]

Load an agency agent's personality definition for use in delegation.

Options:
  -d, --division DIV   Agency division (engineering, design, marketing, etc.)
  -a, --agent AGENT    Agent slug (e.g., frontend-developer, growth-hacker)
  -f, --file FILE      Direct path to agent .md file
  -l, --list           List available agents in the division
  --personality-only   Output only the personality section (skip metadata)
  -h, --help           Show this help

Example:
  activate.sh --division engineering --agent frontend-developer
  activate.sh --file reference/agency-agents-main/testing/testing-evidence-collector.md
  activate.sh --division testing --list
USAGE
}

division=""
agent=""
file=""
list_mode=false
personality_only=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--division)         division="${2-}"; shift 2 ;;
    -a|--agent)            agent="${2-}"; shift 2 ;;
    -f|--file)             file="${2-}"; shift 2 ;;
    -l|--list)             list_mode=true; shift ;;
    --personality-only)    personality_only=true; shift ;;
    -h|--help)             usage; exit 0 ;;
    *)                     echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if $list_mode; then
  if [ -z "$division" ]; then
    echo "Available divisions:"
    for d in "$AGENCY_DIR"/*/; do
      bn=$(basename "$d")
      case "$bn" in .github|examples|strategy) continue ;; esac
      count=$(find "$d" -name "*.md" -not -name "README*" | wc -l | tr -d ' ')
      printf "  %-25s %s agents\n" "$bn" "$count"
    done
  else
    dir="$AGENCY_DIR/$division"
    if [ ! -d "$dir" ]; then
      echo "Division not found: $division" >&2
      echo "Available: $(ls "$AGENCY_DIR" | grep -v -E '\.github|examples|strategy' | tr '\n' ' ')" >&2
      exit 1
    fi
    echo "Agents in $division:"
    for f in "$dir"/*.md; do
      [ -f "$f" ] || continue
      bn=$(basename "$f" .md)
      name=$(head -5 "$f" | grep -i "^name:" | head -1 | sed 's/^name:\s*//')
      printf "  %-40s (slug: %s)\n" "$name" "${bn#"${division}-"}"
    done
  fi
  exit 0
fi

if [ -n "$file" ]; then
  if [ ! -f "$file" ]; then
    echo "File not found: $file" >&2
    exit 1
  fi
  agent_file="$file"
elif [ -n "$division" ] && [ -n "$agent" ]; then
  agent_file="$AGENCY_DIR/$division/${division}-${agent}.md"
  if [ ! -f "$agent_file" ]; then
    agent_file=$(find "$AGENCY_DIR/$division" -name "*${agent}*" -type f | head -1)
    if [ -z "$agent_file" ] || [ ! -f "$agent_file" ]; then
      echo "Agent not found: $division/$agent" >&2
      echo "Available agents:" >&2
      ls "$AGENCY_DIR/$division"/*.md 2>/dev/null | xargs -I{} basename {} .md >&2
      exit 1
    fi
  fi
else
  echo "Error: provide --division + --agent, or --file" >&2
  usage >&2
  exit 1
fi

agent_name=$(head -5 "$agent_file" | grep -i "^name:" | head -1 | sed 's/^name:\s*//')
agent_desc=$(head -5 "$agent_file" | grep -i "^description:" | head -1 | sed 's/^description:\s*//')

echo "=== ACTIVATED: $agent_name ==="
echo "Source: $agent_file"
echo "Description: $agent_desc"
echo "---"
echo ""

if $personality_only; then
  sed -n '/^#/,$p' "$agent_file"
else
  cat "$agent_file"
fi
