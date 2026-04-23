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

from claude_orchestrator import read_tail_text
from claude_watchdog import recommended_state


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def build_report(run_dir: Path, idle_timeout_s: int) -> dict[str, Any]:
    state = load_json(run_dir / "state.json")
    summary = load_json(run_dir / "summary.json")
    eval_data = recommended_state(state, summary, idle_timeout_s)
    events_file = run_dir / "events.jsonl"
    last_events = []
    if events_file.exists():
        lines = events_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in lines[-8:]:
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    last_events.append(item)
            except json.JSONDecodeError:
                continue
    workflow_context_file = state.get("workflowContextFile") or summary.get("workflowContextFile")
    if not workflow_context_file:
        fallback = run_dir / "workflow-context.json"
        if fallback.exists():
            workflow_context_file = str(fallback)

    expected_artifacts = state.get("expectedArtifacts") or summary.get("expectedArtifacts")
    if not expected_artifacts:
        checkpoint = summary.get("checkpoint") if isinstance(summary.get("checkpoint"), dict) else {}
        expected_artifacts = checkpoint.get("expectedArtifacts") if isinstance(checkpoint, dict) else None

    return {
        "runId": state.get("runId") or run_dir.name,
        "workflow": state.get("workflow"),
        "storyId": state.get("storyId"),
        "state": state.get("state"),
        "pid": state.get("pid"),
        "recommended": eval_data,
        "artifactComplete": eval_data.get("artifactComplete"),
        "lastSeen": state.get("lastSeen"),
        "stage": state.get("stage") or summary.get("stage"),
        "progressExcerpt": state.get("progressExcerpt") or summary.get("progressExcerpt"),
        "checkpointTs": state.get("checkpointTs") or summary.get("checkpointTs"),
        "lastProgressSource": state.get("lastProgressSource"),
        "workflowContextFile": workflow_context_file,
        "expectedArtifacts": expected_artifacts,
        "resumeId": summary.get("resumeId"),
        "uiState": summary.get("uiState"),
        "recoveryHint": summary.get("recoveryHint"),
        "transcriptTail": read_tail_text(run_dir / "transcript.log", max_bytes=3000)[-1200:],
        "lastEvents": last_events,
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a concise report for a Claude orchestrator run")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--idle-timeout-s", type=int, default=180)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    report = build_report(Path(args.run_dir).resolve(), args.idle_timeout_s)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"runId={report['runId']}")
    print(f"workflow={report['workflow']}")
    print(f"storyId={report['storyId']}")
    print(f"state={report['state']}")
    recommended = report.get("recommended") or {}
    for key in ["pidAlive", "idleAgeSeconds", "checkpointAgeSeconds", "checkpointRequired", "lastProgressSource", "stuck", "orphaned", "recommendedState", "reason"]:
        print(f"{key}={recommended.get(key)}")
    print(f"artifactComplete={report.get('artifactComplete')}")
    print(f"stage={report.get('stage')}")
    print(f"progressExcerpt={report.get('progressExcerpt')}")
    print(f"checkpointTs={report.get('checkpointTs')}")
    print(f"workflowContextFile={report.get('workflowContextFile')}")
    if report.get("lastEvents"):
        print("lastEvents=")
        for item in report["lastEvents"]:
            print("  - " + json.dumps(item, ensure_ascii=False))
    tail = report.get("transcriptTail") or ""
    if tail.strip():
        print("transcriptTail=")
        print(tail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
