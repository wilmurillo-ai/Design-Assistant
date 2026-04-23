#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: experiment.sh [OPTIONS] <project-dir>

Run autoresearch-style experiment loops on any project with a measurable metric.
Adapted from Karpathy's autoresearch framework.

Options:
  --setup              Initialize experiment (create branch, run baseline, init ledger)
  --run                Run one experiment cycle (modify → run → measure → keep/discard)
  --status             Show experiment ledger and current best
  --ledger FILE        Ledger file path (default: results.tsv in project dir)
  --metric-cmd CMD     Command to extract metric (default: grep "^val_bpb:" run.log)
  --run-cmd CMD        Command to run experiment (default: uv run train.py > run.log 2>&1)
  --in-scope FILE      File the agent can modify (default: train.py)
  --budget SECS        Time budget per experiment in seconds (default: 300)
  --tag TAG            Experiment branch tag (default: date-based)
  -h, --help           Show this help

Examples:
  # LLM training (autoresearch default)
  experiment.sh --setup /path/to/autoresearch
  experiment.sh --run /path/to/autoresearch

  # Custom project
  experiment.sh --setup /path/to/project \
    --run-cmd "python benchmark.py > run.log 2>&1" \
    --metric-cmd "grep '^accuracy:' run.log" \
    --in-scope "config.py" \
    --budget 120

  # Check progress
  experiment.sh --status /path/to/project
USAGE
}

action=""
project_dir=""
ledger=""
metric_cmd='grep "^val_bpb:" run.log'
run_cmd='uv run train.py > run.log 2>&1'
in_scope="train.py"
budget=300
tag=$(date +%b%d | tr '[:upper:]' '[:lower:]')

while [[ $# -gt 0 ]]; do
  case "$1" in
    --setup)      action="setup"; shift ;;
    --run)        action="run"; shift ;;
    --status)     action="status"; shift ;;
    --ledger)     ledger="${2-}"; shift 2 ;;
    --metric-cmd) metric_cmd="${2-}"; shift 2 ;;
    --run-cmd)    run_cmd="${2-}"; shift 2 ;;
    --in-scope)   in_scope="${2-}"; shift 2 ;;
    --budget)     budget="${2-}"; shift 2 ;;
    --tag)        tag="${2-}"; shift 2 ;;
    -h|--help)    usage; exit 0 ;;
    -*)           echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    *)            project_dir="$1"; shift ;;
  esac
done

if [ -z "$project_dir" ]; then
  echo "Error: project directory required" >&2
  usage >&2
  exit 1
fi

if [ -z "$action" ]; then
  echo "Error: specify --setup, --run, or --status" >&2
  usage >&2
  exit 1
fi

[ -z "$ledger" ] && ledger="$project_dir/results.tsv"

do_setup() {
  echo "=== Experiment Setup ==="
  echo "Project: $project_dir"
  echo "In-scope file: $in_scope"
  echo "Run command: $run_cmd"
  echo "Metric command: $metric_cmd"
  echo "Time budget: ${budget}s per experiment"
  echo ""

  if [ ! -d "$project_dir" ]; then
    echo "Error: project directory does not exist: $project_dir" >&2
    exit 1
  fi

  if [ ! -f "$project_dir/$in_scope" ]; then
    echo "Warning: in-scope file not found: $project_dir/$in_scope" >&2
  fi

  cd "$project_dir"

  branch="autoresearch/$tag"
  if git rev-parse --verify "$branch" >/dev/null 2>&1; then
    echo "Branch $branch already exists. Checking out..."
    git checkout "$branch"
  else
    echo "Creating branch: $branch"
    git checkout -b "$branch"
  fi

  if [ ! -f "$ledger" ]; then
    echo -e "commit\tmetric\tstatus\tdescription" > "$ledger"
    echo "Initialized ledger: $ledger"
  fi

  echo ""
  echo "=== Running Baseline ==="
  echo "Command: $run_cmd"
  echo "Budget: ${budget}s"
  echo ""

  start_time=$(date +%s)
  eval "$run_cmd" || true
  end_time=$(date +%s)
  elapsed=$((end_time - start_time))

  metric=$(eval "$metric_cmd" 2>/dev/null | head -1 | awk '{print $NF}' || echo "")

  if [ -z "$metric" ]; then
    echo "WARNING: No metric extracted. Run may have crashed."
    echo "Check run.log for errors: tail -50 $project_dir/run.log"
    commit=$(git rev-parse --short HEAD)
    echo -e "$commit\t0.000000\tcrash\tbaseline (crashed)" >> "$ledger"
  else
    commit=$(git rev-parse --short HEAD)
    echo -e "$commit\t$metric\tkeep\tbaseline" >> "$ledger"
    echo ""
    echo "=== Baseline Established ==="
    echo "Metric: $metric"
    echo "Time: ${elapsed}s"
    echo "Commit: $commit"
  fi
}

do_run() {
  if [ ! -f "$ledger" ]; then
    echo "Error: no ledger found. Run --setup first." >&2
    exit 1
  fi

  cd "$project_dir"

  best_metric=$(tail -n +2 "$ledger" | grep "keep" | tail -1 | awk -F'\t' '{print $2}')
  if [ -z "$best_metric" ]; then
    echo "Error: no baseline metric in ledger. Run --setup first." >&2
    exit 1
  fi

  echo "=== Experiment Run ==="
  echo "Current best metric: $best_metric"
  echo "In-scope file: $in_scope"
  echo ""

  before_commit=$(git rev-parse --short HEAD)

  echo "Running experiment..."
  start_time=$(date +%s)
  timeout $((budget * 2)) bash -c "$run_cmd" || true
  end_time=$(date +%s)
  elapsed=$((end_time - start_time))

  metric=$(eval "$metric_cmd" 2>/dev/null | head -1 | awk '{print $NF}' || echo "")

  if [ -z "$metric" ]; then
    echo "CRASH — no metric extracted"
    commit=$(git rev-parse --short HEAD)
    echo -e "$commit\t0.000000\tcrash\texperiment crashed" >> "$ledger"
    echo "Reverting to $before_commit..."
    git checkout -- "$in_scope" 2>/dev/null || true
    return
  fi

  improved=$(awk "BEGIN {print ($metric < $best_metric) ? 1 : 0}")
  commit=$(git rev-parse --short HEAD)

  if [ "$improved" -eq 1 ]; then
    echo "IMPROVED: $metric (was $best_metric)"
    echo -e "$commit\t$metric\tkeep\texperiment (improved)" >> "$ledger"
    git add "$in_scope" 2>/dev/null && git commit -m "autoresearch: metric $metric" --quiet 2>/dev/null || true
    echo "Change kept and committed."
  else
    echo "NO IMPROVEMENT: $metric (best: $best_metric)"
    echo -e "$commit\t$metric\tdiscard\texperiment (no improvement)" >> "$ledger"
    git checkout -- "$in_scope" 2>/dev/null || true
    echo "Change discarded."
  fi

  echo ""
  echo "Time: ${elapsed}s"
}

do_status() {
  if [ ! -f "$ledger" ]; then
    echo "No ledger found at $ledger"
    echo "Run --setup first."
    exit 1
  fi

  total=$(tail -n +2 "$ledger" | wc -l | tr -d ' ')
  kept=$(tail -n +2 "$ledger" | grep -c "keep" || echo "0")
  discarded=$(tail -n +2 "$ledger" | grep -c "discard" || echo "0")
  crashed=$(tail -n +2 "$ledger" | grep -c "crash" || echo "0")
  best=$(tail -n +2 "$ledger" | grep "keep" | sort -t$'\t' -k2 -n | head -1 | awk -F'\t' '{print $2}')

  echo "=== Experiment Status ==="
  echo "Project: $project_dir"
  echo "Total experiments: $total"
  echo "  Kept: $kept"
  echo "  Discarded: $discarded"
  echo "  Crashed: $crashed"
  echo "Best metric: ${best:-N/A}"
  echo ""
  echo "=== Ledger ==="
  cat "$ledger"
}

case "$action" in
  setup)  do_setup ;;
  run)    do_run ;;
  status) do_status ;;
esac
