#!/usr/bin/env python3
"""
RSI Loop — OpenClaw Shim

Bridges the gap between OpenClaw (no native RSI) and the RSI Loop skill.
Scans OpenClaw session logs for structural errors and auto-feeds aggregated
outcomes into RSI.

Key design principles:
- Parse JSONL structurally, don't regex raw text
- Only flag system-level errors, not tool output content
- Aggregate by (session, issue_type) to avoid flooding
- One summary event per (session, issue) with count + samples

Usage:
    uv run python skills/rsi-loop/scripts/openclaw_shim.py scan
    uv run python skills/rsi-loop/scripts/openclaw_shim.py scan --since 1h
    uv run python skills/rsi-loop/scripts/openclaw_shim.py watch
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).parent.parent
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SKILL_DIR / "data"
SHIM_STATE_FILE = DATA_DIR / "openclaw_shim_state.json"

# OpenClaw session log location
OPENCLAW_SESSION_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

# Maximum sample errors to include in a summary event
MAX_SAMPLES = 3
# Maximum events to log per scan (across all sessions)
MAX_EVENTS_PER_SCAN = 50


# ── Structural detectors ────────────────────────────────────────────────────────
# Each detector receives a parsed JSONL entry and returns (issue_type, detail) or None.

def detect_tool_validation_error(entry: dict) -> tuple[str, str] | None:
    """Detect tool validation errors (isError=true with validation messages)."""
    msg = entry.get("message", {})
    if not msg.get("role") == "toolResult":
        return None
    if not entry.get("message", {}).get("isError", False) and \
       not entry.get("message", {}).get("details", {}).get("isError", False):
        # Check both locations for isError
        if msg.get("isError") is not True and \
           msg.get("details", {}).get("isError") is not True:
            return None
    
    # It's an actual tool error (isError=true)
    content_parts = msg.get("content", [])
    text = ""
    if isinstance(content_parts, list):
        text = " ".join(p.get("text", "") for p in content_parts if isinstance(p, dict))
    elif isinstance(content_parts, str):
        text = content_parts
    
    tool_name = msg.get("toolName", "unknown")
    
    if "Validation failed" in text:
        return "tool_validation_error", f"Tool '{tool_name}': validation failed"
    if "not found" in text.lower() and tool_name.startswith("<"):
        return "tool_not_found", f"Tool '{tool_name}': not found (malformed tool call)"
    
    return "tool_error", f"Tool '{tool_name}' error: {text[:100]}"


def detect_is_error_tool_result(entry: dict) -> tuple[str, str] | None:
    """Detect tool results where isError is true at the message level."""
    msg = entry.get("message", {})
    if msg.get("role") != "toolResult":
        return None
    if msg.get("isError") is not True:
        return None
    
    tool_name = msg.get("toolName", "unknown")
    content_parts = msg.get("content", [])
    text = ""
    if isinstance(content_parts, list):
        text = " ".join(p.get("text", "") for p in content_parts if isinstance(p, dict))
    elif isinstance(content_parts, str):
        text = content_parts

    # Already handled by detect_tool_validation_error
    if "Validation failed" in text or (tool_name.startswith("<") and "not found" in text.lower()):
        return None

    return "tool_error", f"Tool '{tool_name}' failed: {text[:100]}"


def detect_context_reset(entry: dict) -> tuple[str, str] | None:
    """Detect session/context resets (system-level type fields)."""
    entry_type = entry.get("type", "")
    if entry_type in ("context_reset", "session_reset"):
        return "session_reset", f"Session reset: {entry_type}"
    # Check for compaction events
    if entry_type == "compaction" or entry.get("customType") == "compaction":
        return "context_loss", "Context compacted"
    if entry_type == "custom" and entry.get("customType") == "context-reset":
        return "session_reset", "Context reset via custom event"
    return None


def detect_model_fallback(entry: dict) -> tuple[str, str] | None:
    """Detect model fallback/unknown model events."""
    entry_type = entry.get("type", "")
    
    # model_change with error or fallback indicators
    if entry_type == "model_change":
        data = entry.get("data", {})
        if data.get("fallback") or data.get("error"):
            return "model_fallback", f"Model fallback: {data.get('modelId', '?')}"
    
    # System messages about unknown models
    if entry_type == "system" or entry.get("type") == "error":
        text = str(entry.get("message", ""))
        if isinstance(entry.get("message"), dict):
            text = str(entry["message"].get("content", ""))
        if "unknown model" in text.lower() or "model not found" in text.lower():
            return "model_fallback", f"Unknown model: {text[:100]}"
    
    return None


def detect_rate_limit(entry: dict) -> tuple[str, str] | None:
    """Detect rate limiting from system-level error responses."""
    # Check details field for HTTP status codes
    msg = entry.get("message", {})
    if not isinstance(msg, dict):
        return None
    
    details = msg.get("details", {})
    if isinstance(details, dict):
        status = details.get("status") or details.get("statusCode") or details.get("code")
        if status == 429 or str(status) == "429":
            return "rate_limit", f"Rate limited (429): {details.get('message', '')[:80]}"
        error = str(details.get("error", ""))
        if "rate limit" in error.lower() or "quota exceeded" in error.lower():
            return "rate_limit", f"Rate limit: {error[:100]}"
    
    # System-level error entries
    if entry.get("type") == "error":
        text = str(entry.get("error", entry.get("message", "")))
        if "429" in text or "rate limit" in text.lower():
            return "rate_limit", f"Rate limit: {text[:100]}"
    
    return None


def detect_timeout(entry: dict) -> tuple[str, str] | None:
    """Detect timeouts from system-level events (not tool output content)."""
    entry_type = entry.get("type", "")
    
    # System error entries about timeouts
    if entry_type == "error":
        text = str(entry.get("error", entry.get("message", "")))
        if "timeout" in text.lower() or "timed out" in text.lower() or "deadline exceeded" in text.lower():
            return "timeout", f"System timeout: {text[:100]}"
    
    # Tool results with timeout in details (not content)
    msg = entry.get("message", {})
    if isinstance(msg, dict) and msg.get("role") == "toolResult":
        details = msg.get("details", {})
        if isinstance(details, dict):
            error = str(details.get("error", ""))
            status = str(details.get("status", ""))
            if "timeout" in error.lower() or status == "timeout":
                tool_name = msg.get("toolName", "unknown")
                return "timeout", f"Tool '{tool_name}' timed out: {error[:80]}"
    
    return None


# All structural detectors, in priority order
DETECTORS = [
    detect_tool_validation_error,
    detect_is_error_tool_result,
    detect_context_reset,
    detect_model_fallback,
    detect_rate_limit,
    detect_timeout,
]

# Issue type metadata
ISSUE_META = {
    "tool_validation_error": {"task_type": "tool_call", "success": False, "quality": 1},
    "tool_not_found": {"task_type": "tool_call", "success": False, "quality": 1},
    "tool_error": {"task_type": "tool_call", "success": False, "quality": 2},
    "session_reset": {"task_type": "session_management", "success": False, "quality": 1},
    "context_loss": {"task_type": "session_management", "success": True, "quality": 3},
    "model_fallback": {"task_type": "model_routing", "success": False, "quality": 3},
    "rate_limit": {"task_type": "api_call", "success": False, "quality": 2},
    "timeout": {"task_type": "tool_call", "success": False, "quality": 2},
    # User request dropped due to session reset or end-of-session without response
    "incomplete_task": {"task_type": "message_routing", "success": False, "quality": 1},
}


def load_shim_state() -> dict:
    """Load last scan state."""
    if SHIM_STATE_FILE.exists():
        with open(SHIM_STATE_FILE) as f:
            return json.load(f)
    return {"last_scan_ts": 0, "last_scan_iso": "", "events_logged": 0}


def save_shim_state(state: dict):
    """Save scan state."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SHIM_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def parse_since(since_str: str) -> float:
    """Parse time duration string like '1h', '30m', '2d' to epoch."""
    now = time.time()
    match = re.match(r"(\d+)([hmds])", since_str)
    if not match:
        return now - 3600
    value, unit = int(match.group(1)), match.group(2)
    multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return now - (value * multiplier.get(unit, 3600))


def scan_session_file(log_file: Path, is_active: bool = False) -> list[tuple[str, str, str]]:
    """Scan a single session JSONL file. Returns [(issue_type, detail, timestamp), ...].

    Args:
        log_file: Path to the JSONL session log.
        is_active: True if this is the currently active session. Used to suppress
                   false positives from in-flight user messages at end-of-file.
    """
    hits = []
    try:
        entries: list[dict] = []
        with open(log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        # ── Pass 1: structural detectors (stateless, existing logic) ─────────
        for entry in entries:
            for detector in DETECTORS:
                result = detector(entry)
                if result:
                    issue_type, detail = result
                    ts = entry.get("timestamp", "")
                    hits.append((issue_type, detail, ts))
                    break  # first matching detector wins

        # ── Pass 2: stateful dropped-request detection ────────────────────────
        # Detect user messages that were never answered before a session reset
        # or before the session ended (covers the "address it" class of bugs).
        _RESET_TYPES = {"context_reset", "session_reset", "compaction"}
        _RESET_CUSTOM = {"context-reset", "compaction"}
        pending_user: tuple[str, str] | None = None  # (text_preview, timestamp)

        for entry in entries:
            et = entry.get("type", "")

            if et == "message":
                msg = entry.get("message", {})
                role = msg.get("role", "")
                if role == "user":
                    content = msg.get("content", [])
                    text = ""
                    if isinstance(content, list):
                        text = " ".join(
                            p.get("text", "") for p in content
                            if isinstance(p, dict) and p.get("type") == "text"
                        )
                    pending_user = (text.strip()[:80], entry.get("timestamp", ""))
                elif role == "assistant":
                    pending_user = None  # request was answered

            elif et in _RESET_TYPES or (
                et == "custom" and entry.get("customType", "") in _RESET_CUSTOM
            ):
                # Session reset while a user message was waiting for a response
                if pending_user:
                    text, ts = pending_user
                    hits.append((
                        "incomplete_task",
                        f"Request dropped at session reset: '{text[:60]}'",
                        ts,
                    ))
                    pending_user = None

        # End-of-file: pending user message that was never answered.
        # Only flag for closed (non-active) sessions that had at least one prior
        # assistant response — avoids flagging brand-new sessions or in-flight turns.
        if pending_user and not is_active:
            had_responses = any(
                e.get("type") == "message"
                and e.get("message", {}).get("role") == "assistant"
                for e in entries
            )
            if had_responses:
                text, ts = pending_user
                hits.append((
                    "incomplete_task",
                    f"Request at end of closed session (no response): '{text[:60]}'",
                    ts,
                ))

    except Exception as e:
        print(f"Error scanning {log_file}: {e}", file=sys.stderr)
    return hits


def aggregate_hits(all_hits: dict[str, list[tuple[str, str, str]]]) -> list[dict]:
    """
    Aggregate raw hits into summary events.
    
    all_hits: {session_filename: [(issue_type, detail, timestamp), ...]}
    
    Returns aggregated events grouped by (session, issue_type).
    """
    # Group: (session_file, issue_type) -> list of (detail, timestamp)
    groups: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    
    for session_file, hits in all_hits.items():
        for issue_type, detail, ts in hits:
            groups[(session_file, issue_type)].append((detail, ts))
    
    events = []
    for (session_file, issue_type), occurrences in groups.items():
        meta = ISSUE_META.get(issue_type, {
            "task_type": "unknown", "success": False, "quality": 2
        })
        
        count = len(occurrences)
        samples = [occ[0] for occ in occurrences[:MAX_SAMPLES]]
        first_ts = occurrences[0][1] if occurrences else ""
        
        detail_str = samples[0] if samples else issue_type
        if count > 1:
            detail_str += f" (seen {count} times in this session)"
        
        events.append({
            "source": "openclaw",
            "task_type": meta["task_type"],
            "success": meta["success"],
            "quality": meta["quality"],
            "issues": [issue_type],
            "error_message": detail_str[:200],
            "notes": f"Shim: {count}x {issue_type} in {session_file}",
            "tags": ["shim", "auto-detected", issue_type],
            "samples": samples,
            "count": count,
        })
    
    # Sort by count descending so most frequent issues are logged first
    events.sort(key=lambda e: e["count"], reverse=True)
    
    # Cap total events
    return events[:MAX_EVENTS_PER_SCAN]


def scan_session_logs(since_ts: float) -> list[dict]:
    """Scan OpenClaw session JSONL files for structural errors, return aggregated events."""
    if not OPENCLAW_SESSION_DIR.exists():
        print(f"Session dir not found: {OPENCLAW_SESSION_DIR}", file=sys.stderr)
        return []

    all_hits: dict[str, list[tuple[str, str, str]]] = {}

    # Determine which file is the active session (most recently modified, within last 5 min)
    active_cutoff = time.time() - 300  # 5 minutes
    candidate_files = []
    for log_file in OPENCLAW_SESSION_DIR.glob("*.jsonl"):
        try:
            candidate_files.append((log_file.stat().st_mtime, log_file))
        except OSError:
            pass
    active_file: Path | None = None
    if candidate_files:
        newest_mtime, newest_file = max(candidate_files, key=lambda x: x[0])
        if newest_mtime >= active_cutoff:
            active_file = newest_file

    for log_file in sorted(OPENCLAW_SESSION_DIR.glob("*.jsonl")):
        try:
            mtime = log_file.stat().st_mtime
            if mtime < since_ts:
                continue
        except OSError:
            continue

        is_active = (log_file == active_file)
        hits = scan_session_file(log_file, is_active=is_active)
        if hits:
            all_hits[log_file.name] = hits

    return aggregate_hits(all_hits)


def scan_gateway_logs(since_ts: float) -> list[dict]:
    """Scan gateway logs for system-level errors."""
    log_paths = [
        Path.home() / ".openclaw" / "gateway.log",
        Path.home() / ".openclaw" / "gateway.err",
    ]
    
    all_hits: dict[str, list[tuple[str, str, str]]] = {}
    
    for log_path in log_paths:
        if not log_path.exists():
            continue
        try:
            if log_path.stat().st_mtime < since_ts:
                continue
        except OSError:
            continue
        
        hits = []
        try:
            with open(log_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Gateway logs may be plain text - look for specific system errors
                    lower = line.lower()
                    if "unknown model" in lower:
                        hits.append(("model_fallback", f"Gateway: {line[:100]}", ""))
                    elif "rate limit" in lower or "429" in line:
                        hits.append(("rate_limit", f"Gateway: {line[:100]}", ""))
        except Exception as e:
            print(f"Error scanning {log_path}: {e}", file=sys.stderr)
        
        if hits:
            all_hits[log_path.name] = hits
    
    return aggregate_hits(all_hits)


def log_events(events: list[dict]) -> int:
    """Feed events into RSI auto-observe."""
    logged = 0
    for event in events:
        try:
            sys.path.insert(0, str(SCRIPT_DIR))
            from auto_observe import auto_observe
            result = auto_observe(event)
            if result:
                logged += 1
        except Exception as e:
            print(f"Error logging event: {e}", file=sys.stderr)
    return logged


def cmd_scan(args):
    """Scan logs and feed into RSI."""
    state = load_shim_state()

    if args.since:
        since_ts = parse_since(args.since)
    elif state["last_scan_ts"] > 0:
        since_ts = state["last_scan_ts"]
    else:
        since_ts = time.time() - 3600

    since_iso = datetime.fromtimestamp(since_ts, tz=timezone.utc).isoformat()
    print(f"Scanning since: {since_iso}")

    events = []
    events.extend(scan_session_logs(since_ts))
    events.extend(scan_gateway_logs(since_ts))

    if not events:
        print("No new events detected.")
    else:
        print(f"Found {len(events)} aggregated events:")
        for e in events:
            issues = e.get("issues", [])
            count = e.get("count", 1)
            print(f"  [{issues[0] if issues else '?'}] x{count} — {e.get('notes', '')[:70]}")

        if not args.dry_run:
            logged = log_events(events)
            print(f"\nLogged {logged}/{len(events)} events to RSI.")
            state["events_logged"] = state.get("events_logged", 0) + logged
        else:
            print("\n(dry-run: not logging)")

    state["last_scan_ts"] = time.time()
    state["last_scan_iso"] = datetime.now(timezone.utc).isoformat()
    save_shim_state(state)


def cmd_watch(args):
    """Continuous scan mode."""
    interval = args.interval or 300
    print(f"Watching for events every {interval}s. Ctrl+C to stop.")

    while True:
        try:
            cmd_scan(args)
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped.")
            break


def main():
    parser = argparse.ArgumentParser(description="RSI Loop — OpenClaw Shim")
    sub = parser.add_subparsers(dest="command")

    scan_parser = sub.add_parser("scan", help="Scan logs once")
    scan_parser.add_argument("--since", help="Time window (e.g., 1h, 30m, 2d)")
    scan_parser.add_argument("--dry-run", action="store_true", help="Don't log events")

    watch_parser = sub.add_parser("watch", help="Continuous scanning")
    watch_parser.add_argument("--interval", type=int, help="Scan interval in seconds")
    watch_parser.add_argument("--since", help="Initial time window")
    watch_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "watch":
        cmd_watch(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
