#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REVIEW_LOG_DIR="${OPENCLAW_DATA_DIR:-$HOME/.openclaw}/team-reviews"

usage() {
  cat <<'USAGE'
Usage: review.sh [OPTIONS]

Run the Team Builder QA review workflow on deliverables.

Options:
  -t, --task TASK       Task description (required)
  -c, --criteria FILE   File containing acceptance criteria (one per line)
  -p, --pass PASS       Review pass: evidence (Pass 1), reality (Pass 2), both (default)
  -s, --score           Output machine-readable scores
  -o, --output FILE     Write review to file (default: stdout + log)
  -h, --help            Show this help

Example:
  review.sh --task "Portfolio dashboard" --pass evidence
  review.sh --task "Silver strategy optimization" --criteria criteria.txt --pass both
USAGE
}

task=""
criteria_file=""
pass="both"
score_mode=false
output=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--task)      task="${2-}"; shift 2 ;;
    -c|--criteria)  criteria_file="${2-}"; shift 2 ;;
    -p|--pass)      pass="${2-}"; shift 2 ;;
    -s|--score)     score_mode=true; shift ;;
    -o|--output)    output="${2-}"; shift 2 ;;
    -h|--help)      usage; exit 0 ;;
    *)              echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [ -z "$task" ]; then
  echo "Error: --task required" >&2
  usage >&2
  exit 1
fi

mkdir -p "$REVIEW_LOG_DIR"
timestamp=$(date +%Y-%m-%d-%H%M%S)
log_file="$REVIEW_LOG_DIR/review-${timestamp}.md"

criteria=()
if [ -n "$criteria_file" ] && [ -f "$criteria_file" ]; then
  while IFS= read -r line; do
    [ -n "$line" ] && criteria+=("$line")
  done < "$criteria_file"
fi

generate_evidence_template() {
  echo "## Evidence Collector — Pass 1"
  echo ""
  echo "### Task: $task"
  echo "### Date: $(date '+%Y-%m-%d %H:%M')"
  echo ""
  echo "### Verification Checklist"
  echo "- [ ] Code compiles / runs without errors"
  echo "- [ ] No console errors or warnings"
  echo "- [ ] All dependencies resolved"
  echo ""
  echo "### Acceptance Criteria"
  if [ ${#criteria[@]} -gt 0 ]; then
    for c in "${criteria[@]}"; do
      echo "- [ ] $c — verified: [evidence needed]"
    done
  else
    echo "- [ ] [Define acceptance criteria] — verified: [evidence needed]"
    echo "- [ ] [Define acceptance criteria] — verified: [evidence needed]"
    echo "- [ ] [Define acceptance criteria] — verified: [evidence needed]"
  fi
  echo ""
  echo "### Visual Verification (UI work)"
  echo "- [ ] Desktop viewport (1920x1080)"
  echo "- [ ] Tablet viewport (768x1024)"
  echo "- [ ] Mobile viewport (375x667)"
  echo ""
  echo "### Edge Cases"
  echo "- [ ] Empty state (no data)"
  echo "- [ ] Error state (API failure)"
  echo "- [ ] Large data set (performance)"
  echo ""
  echo "### Issues Found"
  echo "1. [Category] — [Severity: Critical/High/Medium/Low]"
  echo "   Expected: [what should happen]"
  echo "   Actual: [what actually happens]"
  echo "   Fix: [specific instruction]"
  echo ""
  echo "### Evidence"
  echo "- [Screenshot/log/output references]"
  echo ""
  echo "### Verdict: [PASS / FAIL]"
}

generate_reality_template() {
  echo "## Reality Checker — Pass 2 (Final Gate)"
  echo ""
  echo "### Task: $task"
  echo "### Date: $(date '+%Y-%m-%d %H:%M')"
  echo ""
  echo "### Specification Match"
  echo "- [ ] Deliverable matches what was requested"
  echo "- [ ] No requirements missed"
  echo "- [ ] No unrequested features added (scope creep)"
  echo ""
  echo "### Quality Rating"
  echo "- [ ] D: Major issues, not functional"
  echo "- [ ] C: Functional but rough, needs significant work"
  echo "- [ ] B: Good, meets requirements, minor polish needed"
  echo "- [ ] A: Excellent, exceeds expectations, production ready"
  echo ""
  echo "### Production Readiness"
  echo "- [ ] Handles errors gracefully"
  echo "- [ ] Performance acceptable"
  echo "- [ ] No hardcoded values that should be configurable"
  echo "- [ ] Security considerations addressed"
  echo ""
  echo "### What Works"
  echo "- [Positive finding with evidence]"
  echo ""
  echo "### What Needs Work"
  echo "- [Issue with specific fix instruction]"
  echo ""
  echo "### Decision"
  echo "- [ ] SHIP IT — production ready"
  echo "- [ ] REVISE — send back with specific fix list"
  echo "- [ ] ESCALATE — fundamental approach needs rethinking"
}

run_review() {
  echo "# Team Builder Review"
  echo "# Task: $task"
  echo "# Generated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""

  case "$pass" in
    evidence)
      generate_evidence_template
      ;;
    reality)
      generate_reality_template
      ;;
    both)
      generate_evidence_template
      echo ""
      echo "---"
      echo ""
      generate_reality_template
      ;;
  esac

  echo ""
  echo "---"
  echo "## Retry Protocol"
  echo "- Attempt 1 fails → specific fix instructions back to developer"
  echo "- Attempt 2 fails → updated fix instructions, flag recurring issues"
  echo "- Attempt 3 fails → escalate to CEO with root cause analysis"
}

if [ -n "$output" ]; then
  run_review | tee "$log_file" > "$output"
  echo "" >&2
  echo "Review written to: $output" >&2
  echo "Log saved to: $log_file" >&2
else
  run_review | tee "$log_file"
  echo "" >&2
  echo "Log saved to: $log_file" >&2
fi
