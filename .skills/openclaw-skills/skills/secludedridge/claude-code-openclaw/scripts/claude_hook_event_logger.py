#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_nested(obj: dict[str, Any], *keys: str) -> Any:
    cur: Any = obj
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def compact_text(value: Any, limit: int = 240) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\n", " ").strip()
    if not text:
        return None
    return text if len(text) <= limit else text[: limit - 1] + "…"


def build_summary(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    tool_name = payload.get("tool_name") or payload.get("toolName")
    command = get_nested(payload, "tool_input", "command") or get_nested(payload, "toolInput", "command")
    file_path = get_nested(payload, "tool_input", "file_path") or get_nested(payload, "tool_input", "path")
    message = payload.get("message") or get_nested(payload, "notification", "message")

    record: dict[str, Any] = {
        "ts": utc_now(),
        "event": event_name,
        "tool": tool_name,
        "command": compact_text(command, limit=120),
        "path": compact_text(file_path, limit=120),
        "message": compact_text(message, limit=120),
        "cwd": compact_text(payload.get("cwd") or payload.get("working_directory") or payload.get("workingDirectory"), limit=120),
    }

    if event_name == "PermissionRequest":
        record["kind"] = "needs-approval"
        record["summary"] = compact_text(command, limit=100) or compact_text(message, limit=100) or compact_text(tool_name, limit=100) or "permission requested"
    elif event_name in {"TaskCompleted", "Stop", "SessionEnd"}:
        record["kind"] = "completed"
        record["summary"] = compact_text(message, limit=100) or f"{event_name}"
    elif event_name in {"Notification", "SubagentStop", "SubagentStart", "SessionStart"}:
        record["kind"] = "notification"
        record["summary"] = compact_text(message, limit=100) or f"{event_name}"
    elif event_name == "PostToolUseFailure":
        record["kind"] = "tool-failure"
        record["summary"] = compact_text(command, limit=100) or compact_text(message, limit=100) or compact_text(tool_name, limit=100) or "tool failure"
    else:
        record["kind"] = "activity"
        record["summary"] = compact_text(command, limit=100) or compact_text(message, limit=100) or compact_text(tool_name, limit=100) or event_name

    return {k: v for k, v in record.items() if v not in (None, "")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Append compact Claude hook events to a JSONL file")
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--log-file", required=False)
    parser.add_argument("--dedupe-window-sec", type=int, default=30)
    args = parser.parse_args()

    raw = os.sys.stdin.read().strip()
    payload: dict[str, Any] = {}
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                payload = parsed
            else:
                payload = {"raw": parsed}
        except json.JSONDecodeError:
            payload = {"raw": raw}

    log_file = args.log_file or os.environ.get("CLAUDE_HOOKS_EVENT_LOG")
    if not log_file:
        return 0

    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = build_summary(args.event_name, payload)

    if path.exists() and args.event_name in {"Stop", "SessionEnd", "TaskCompleted"}:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines[-20:]):
                if not line.strip():
                    continue
                prev = json.loads(line)
                if not isinstance(prev, dict):
                    continue
                if prev.get("event") not in {"Stop", "SessionEnd", "TaskCompleted"}:
                    continue
                prev_ts = parse_ts(prev.get("ts"))
                now_ts = parse_ts(record.get("ts"))
                if prev_ts and now_ts and now_ts - prev_ts <= timedelta(seconds=args.dedupe_window_sec):
                    if prev.get("summary") == record.get("summary"):
                        return 0
                    break
                break
        except Exception:
            pass

    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
