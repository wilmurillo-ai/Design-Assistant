#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_events(path: Path, limit: int) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    events: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
            if isinstance(parsed, dict):
                events.append(parsed)
        except json.JSONDecodeError:
            continue
    return events


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not events:
        return {
            "status": "no-events",
            "eventCount": 0,
            "latest": None,
            "latestApproval": None,
            "latestCompletion": None,
        }

    latest = events[-1]
    latest_approval = next((e for e in reversed(events) if e.get("event") == "PermissionRequest"), None)
    latest_completion = next((e for e in reversed(events) if e.get("event") in {"TaskCompleted", "Stop", "SessionEnd"}), None)

    status = "running"
    if latest.get("event") == "PermissionRequest":
        status = "needs-approval"
    elif latest.get("event") in {"TaskCompleted", "Stop", "SessionEnd"}:
        status = "completed"
    elif latest.get("kind") == "tool-failure":
        status = "tool-failure"

    return {
        "status": status,
        "eventCount": len(events),
        "latest": latest,
        "latestApproval": latest_approval,
        "latestCompletion": latest_completion,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize compact Claude hook events")
    parser.add_argument("--log-file", required=True)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    data = summarize(load_events(Path(args.log_file), args.limit))
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print(f"status={data['status']}")
    print(f"event_count={data['eventCount']}")
    latest = data.get("latest") or {}
    if latest:
        print(f"latest_event={latest.get('event')}")
        print(f"latest_summary={latest.get('summary')}")
    approval = data.get("latestApproval") or {}
    if approval:
        print(f"latest_approval_ts={approval.get('ts')}")
        print(f"latest_approval_summary={approval.get('summary')}")
    completion = data.get("latestCompletion") or {}
    if completion:
        print(f"latest_completion_ts={completion.get('ts')}")
        print(f"latest_completion_summary={completion.get('summary')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
