#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from claude_watchdog import reconcile


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch reconcile Claude orchestrator runs under a registry base dir")
    parser.add_argument("--registry-dir", required=True, help="Path to .claude/orchestrator")
    parser.add_argument("--idle-timeout-s", type=int, default=180)
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    registry_dir = Path(args.registry_dir).resolve()
    runs_dir = registry_dir / "runs"
    results = []
    if runs_dir.exists():
        for run_dir in sorted(runs_dir.iterdir()):
            state_file = run_dir / "state.json"
            if state_file.exists():
                results.append(reconcile(state_file, args.idle_timeout_s, args.fix))

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    for item in results:
        print(f"{item.get('stateFile')} :: state={item.get('state')} recommended={item.get('recommendedState')} applied={item.get('applied')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
