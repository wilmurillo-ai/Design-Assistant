#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from ops.claude_run_report import build_report


def load_state(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def find_latest_run(registry_dir: Path, workflow: str | None, story_id: str | None) -> Path | None:
    runs_dir = registry_dir / "runs"
    if not runs_dir.exists():
        return None

    candidates: list[Path] = []
    for run_dir in runs_dir.iterdir():
        state_file = run_dir / "state.json"
        if not state_file.exists():
            continue
        state = load_state(state_file)
        if workflow and state.get("workflow") != workflow:
            continue
        if story_id and state.get("storyId") != story_id:
            continue
        candidates.append(run_dir)

    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Report latest orchestrator run (optionally filtered by workflow/story)")
    parser.add_argument("--registry-dir", required=False, help="Path to .claude/orchestrator or .claude/runs")
    parser.add_argument("--cwd", default=".", help="Current working directory")
    parser.add_argument("--workflow")
    parser.add_argument("--story-id")
    parser.add_argument("--idle-timeout-s", type=int, default=180)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    if args.registry_dir:
        registry_base = Path(args.registry_dir).resolve()
        if registry_base.name == "runs":
            registry_base = registry_base.parent
    else:
        registry_base = Path(args.cwd).resolve() / ".claude" / "orchestrator"

    latest = find_latest_run(registry_base, args.workflow, args.story_id)
    if not latest:
        if args.format == "json":
            print(json.dumps({"found": False}, ensure_ascii=False, indent=2))
        else:
            print("found=False")
        return 1

    report = build_report(latest, args.idle_timeout_s)
    report["found"] = True
    report["runDir"] = str(latest)

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"found=True")
    print(f"runDir={latest}")
    print(f"runId={report.get('runId')}")
    print(f"workflow={report.get('workflow')}")
    print(f"storyId={report.get('storyId')}")
    print(f"state={report.get('state')}")
    rec = report.get("recommended") or {}
    print(f"recommendedState={rec.get('recommendedState')}")
    print(f"reason={rec.get('reason')}")
    print(f"checkpointRequired={rec.get('checkpointRequired')}")
    print(f"artifactComplete={report.get('artifactComplete')}")
    print(f"stage={report.get('stage')}")
    print(f"progressExcerpt={report.get('progressExcerpt')}")
    print(f"checkpointTs={report.get('checkpointTs')}")
    print(f"lastProgressSource={report.get('lastProgressSource')}")
    print(f"workflowContextFile={report.get('workflowContextFile')}")
    print(f"uiState={report.get('uiState')}")
    print(f"resumeId={report.get('resumeId')}")
    print(f"recoveryHint={report.get('recoveryHint')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
