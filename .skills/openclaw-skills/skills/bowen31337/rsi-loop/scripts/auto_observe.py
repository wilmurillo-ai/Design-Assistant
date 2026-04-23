#!/usr/bin/env python3
"""
RSI Loop - Auto Observer
Post-task hook that accepts structured JSON about completed tasks,
auto-classifies them, logs to outcomes.jsonl, and detects recurring patterns.

Usage:
    echo '{"task":"code_generation","success":false,"error_msg":"empty response","source":"openclaw"}' | \
        uv run python skills/rsi-loop/scripts/auto_observe.py

    uv run python skills/rsi-loop/scripts/auto_observe.py --input '{"task":"...","success":true}'
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from observer import (
    TASK_TYPES, ISSUE_TYPES, SOURCES, HIGH_SEVERITY_ISSUES,
    log_outcome, load_outcomes, DATA_DIR,
)

# ── Error message → issue type mapping ─────────────────────────────────────────
ERROR_CLASSIFIERS = [
    (["empty response", "returned empty", "no output", "null response"], "empty_response"),
    (["rate limit", "429", "too many requests", "quota exceeded"], "rate_limit"),
    (["context limit", "session reset", "context_length", "max_tokens"], "session_reset"),
    (["context lost", "compaction", "lost context", "missing context"], "context_loss"),
    (["fallback", "model unavailable", "switched model"], "model_fallback"),
    (["wrong model", "expensive model", "premium model"], "cost_overrun"),
    (["tool error", "tool failed", "function call error"], "tool_error"),
    (["timeout", "timed out", "deadline exceeded"], "slow_response"),
    (["hydration", "wake detection", "missed wake"], "hydration_fail"),
    (["wal", "write-ahead", "forgot wal"], "wal_miss"),
    (["missing tool", "unknown tool", "no such tool"], "missing_tool"),
    (["incomplete", "partial", "unfinished"], "incomplete_task"),
    (["wrong output", "incorrect", "bad result"], "wrong_output"),
    (["repeated mistake", "same error again"], "repeated_mistake"),
]

# ── Task description → task type mapping ───────────────────────────────────────
TASK_CLASSIFIERS = [
    (["code gen", "write code", "implement", "create function", "coding"], "code_generation"),
    (["debug", "fix bug", "troubleshoot", "error fix"], "code_debug"),
    (["review", "code review", "pr review"], "code_review"),
    (["architecture", "design", "system design"], "architecture_design"),
    (["file", "read file", "write file", "edit file"], "file_ops"),
    (["search", "web search", "google", "lookup"], "web_search"),
    (["memory", "remember", "recall", "retrieve"], "memory_retrieval"),
    (["skill", "create skill", "new skill"], "skill_creation"),
    (["cron", "schedule", "timer", "periodic"], "cron_management"),
    (["api", "integration", "webhook", "endpoint"], "api_integration"),
    (["data", "analysis", "analyze data", "parse"], "data_analysis"),
    (["message", "send message", "notify", "route"], "message_routing"),
    (["infra", "server", "deploy", "ops", "infrastructure"], "infrastructure_ops"),
    (["doc", "documentation", "readme", "write doc"], "documentation"),
    (["monitor", "check", "health", "status"], "monitoring"),
    (["trade", "trading", "blockchain", "crypto"], "trading"),
]


def classify_issues(error_msg: str, existing_issues: list | None = None) -> list[str]:
    """Auto-classify issues from error message text."""
    issues = list(existing_issues or [])
    if not error_msg:
        return issues

    lower = error_msg.lower()
    for keywords, issue_type in ERROR_CLASSIFIERS:
        if any(kw in lower for kw in keywords):
            if issue_type not in issues:
                issues.append(issue_type)

    return [i for i in issues if i in ISSUE_TYPES]


def classify_task(description: str, existing_task: str | None = None) -> str:
    """Auto-classify task type from description."""
    if existing_task and existing_task in TASK_TYPES and existing_task != "unknown":
        return existing_task

    if not description:
        return existing_task or "unknown"

    lower = description.lower()
    for keywords, task_type in TASK_CLASSIFIERS:
        if any(kw in lower for kw in keywords):
            return task_type

    return existing_task or "unknown"


def detect_recurrence(issues: list[str], source: str, days: int = 7, threshold: int = 3) -> list[dict]:
    """Check if any of the given issues have recurred >= threshold times in the last N days."""
    if not issues:
        return []

    outcomes = load_outcomes()
    cutoff = time.time() - (days * 86400)

    # Count recent occurrences per issue
    issue_counts: dict[str, int] = {}
    for o in outcomes:
        try:
            ts = datetime.fromisoformat(o["ts"]).timestamp()
            if ts < cutoff:
                continue
        except Exception:
            continue
        for issue in o.get("issues", []):
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

    flags = []
    for issue in issues:
        # Count includes the one we're about to log (+1)
        count = issue_counts.get(issue, 0) + 1
        if count >= threshold:
            flags.append({
                "issue": issue,
                "count": count,
                "days": days,
                "severity": "high" if issue in HIGH_SEVERITY_ISSUES else "normal",
            })

    return flags


def auto_observe(input_data: dict) -> dict:
    """
    Process a structured task outcome and log it.

    Expected input fields:
        task (str): Task type or description (auto-classified if not exact match)
        success (bool): Whether the task succeeded
        error_msg (str): Raw error message (optional)
        source (str): Platform source (openclaw, evoclaw, cron, subagent, etc.)
        quality (int): Quality 1-5 (auto-inferred if not provided)
        model (str): Model used (optional)
        duration_ms (int): Duration in milliseconds (optional)
        issues (list[str]): Explicit issues (optional, auto-classified from error_msg)
        tags (list[str]): Tags (optional)
        notes (str): Additional notes (optional)
        description (str): Task description for auto-classification (optional)
        agent_id (str): Agent ID (optional, default "main")
        session_id (str): Session ID (optional)

    Returns:
        dict with: record, recurrence_flags
    """
    # Extract fields with defaults
    success = input_data.get("success", True)
    error_msg = input_data.get("error_msg", "")
    source = input_data.get("source", "manual")
    quality = input_data.get("quality", 0)
    description = input_data.get("description", "")

    # Auto-classify task type
    # Trust pre-classified task_type from shim/upstream if it's already set and valid
    _pre_classified = input_data.get("task_type", "")
    if _pre_classified and _pre_classified in TASK_TYPES and _pre_classified != "unknown":
        task_type = _pre_classified
    else:
        task_type = classify_task(
            description or input_data.get("task", ""),
            _pre_classified or input_data.get("task"),
        )

    # Auto-classify issues from error message
    issues = classify_issues(error_msg, input_data.get("issues"))

    # Auto-infer quality if not provided
    if not quality:
        if not success:
            quality = 1 if any(i in HIGH_SEVERITY_ISSUES for i in issues) else 2
        else:
            quality = 4 if not issues else 3

    # Detect recurrence BEFORE logging (so we count existing + this one)
    recurrence_flags = detect_recurrence(issues, source)

    # Log the outcome
    record = log_outcome(
        task_type=task_type,
        success=success,
        quality=quality,
        model=input_data.get("model", ""),
        duration_ms=input_data.get("duration_ms", 0),
        issues=issues,
        tags=input_data.get("tags", []),
        notes=input_data.get("notes", ""),
        session_id=input_data.get("session_id", ""),
        agent_id=input_data.get("agent_id", "main"),
        source=source,
        error_msg=error_msg,
    )

    return {
        "record": record,
        "recurrence_flags": recurrence_flags,
    }


def main():
    parser = argparse.ArgumentParser(description="RSI Auto-Observer - Post-task hook")
    parser.add_argument("--input", "-i", help="JSON string with task outcome data")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
    args = parser.parse_args()

    # Read from --input or stdin
    if args.input:
        input_data = json.loads(args.input)
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print("Error: No input provided. Use --input or pipe JSON to stdin.", file=sys.stderr)
            sys.exit(1)
        input_data = json.loads(raw)

    result = auto_observe(input_data)

    if not args.quiet:
        record = result["record"]
        print(f"Logged: {record['id']} | {record['source']} | {record['task_type']} | "
              f"success={record['success']} | quality={record['quality']} | "
              f"issues={record.get('issues', [])}")

        if result["recurrence_flags"]:
            print("\n⚠️  RECURRING PATTERNS DETECTED:")
            for flag in result["recurrence_flags"]:
                severity = "🔴" if flag["severity"] == "high" else "🟡"
                print(f"  {severity} {flag['issue']}: {flag['count']}x in {flag['days']} days")

    # Output JSON for programmatic consumption
    if args.quiet:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
