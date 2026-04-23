#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EVENTS = [
    "PermissionRequest",
    "Notification",
    "PostToolUseFailure",
    "TaskCompleted",
    "Stop",
    "SessionEnd",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        raise SystemExit(f"Invalid JSON: {path}")


def ensure_hook(settings: dict[str, Any], event_name: str, command: str) -> None:
    hooks = settings.setdefault("hooks", {})
    groups = hooks.setdefault(event_name, [])
    if not isinstance(groups, list):
        groups = hooks[event_name] = []

    normalized_new = command.replace("/usr/bin/python3.12", "/usr/bin/python3")
    existing_commands = set()
    duplicate_indexes: list[int] = []
    for idx, group in enumerate(groups):
        if not isinstance(group, dict):
            continue
        for hook in group.get("hooks", []):
            if isinstance(hook, dict) and hook.get("type") == "command":
                existing = str(hook.get("command") or "")
                existing_commands.add(existing)
                if existing.replace("/usr/bin/python3.12", "/usr/bin/python3") == normalized_new:
                    duplicate_indexes.append(idx)

    if duplicate_indexes:
        for idx in sorted(duplicate_indexes[1:], reverse=True):
            try:
                groups.pop(idx)
            except Exception:
                pass
        return

    if command in existing_commands:
        return

    groups.append(
        {
            "matcher": "*",
            "hooks": [
                {
                    "type": "command",
                    "command": command,
                }
            ],
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Install compact Claude event hooks into a repo's .claude/settings.local.json")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--event-log-file", required=False)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    claude_dir = project_root / ".claude"
    settings_path = claude_dir / "settings.local.json"
    events_dir = claude_dir / "events"
    event_log = Path(args.event_log_file).resolve() if args.event_log_file else (events_dir / "claude-events.jsonl")

    script_path = Path(__file__).resolve().parent / "claude_hook_event_logger.py"
    command_template = f"{sys.executable} {script_path} --event-name {{event}} --log-file {event_log}"

    claude_dir.mkdir(parents=True, exist_ok=True)
    events_dir.mkdir(parents=True, exist_ok=True)

    settings = load_json(settings_path)
    for event in EVENTS:
        ensure_hook(settings, event, command_template.format(event=event))

    settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "settingsFile": str(settings_path),
        "eventLogFile": str(event_log),
        "eventsInstalled": EVENTS,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
