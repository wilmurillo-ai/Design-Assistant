#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from claude_artifact_probe import probe_completion
from claude_run_registry import RunRegistry, TERMINAL_STATES, pid_alive


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def infer_artifact_completion(state: dict[str, Any], summary: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
    summary_complete = summary.get("artifactComplete")
    summary_probe = summary.get("artifactProbe") if isinstance(summary.get("artifactProbe"), dict) else None
    if summary_complete is True:
        return True, summary_probe

    repo = state.get("repo") or summary.get("repo")
    workflow = state.get("workflow") or summary.get("workflow")
    if not repo or not workflow:
        return False, summary_probe

    story_id = state.get("storyId") or summary.get("storyId")
    story_path_raw = state.get("storyPath") or summary.get("storyPath")
    profiles_file_raw = state.get("profilesFile") or summary.get("profilesFile")

    try:
        probe = probe_completion(
            repo=Path(str(repo)).resolve(),
            workflow=str(workflow),
            story_id=str(story_id) if story_id else None,
            story_path=Path(str(story_path_raw)).resolve() if story_path_raw else None,
            profiles_file=Path(str(profiles_file_raw)).resolve() if profiles_file_raw else None,
        )
        return bool(probe.get("complete")), probe
    except Exception as exc:
        return False, {"complete": False, "reasons": [f"artifact-probe-error: {exc}"]}


def recommended_state(state: dict[str, Any], summary: dict[str, Any], idle_timeout_s: int) -> dict[str, Any]:
    current_state = str(state.get("state") or "unknown")
    pid = int(state.get("pid") or 0)
    pid_is_alive = pid_alive(pid)

    last_progress = parse_ts(state.get("lastProgressAt") or state.get("updatedAt"))
    progress_source = state.get("lastProgressSource")
    age_s = None
    if last_progress:
        age_s = int((utc_now() - last_progress).total_seconds())

    checkpoint_ts = parse_ts(state.get("checkpointTs") or summary.get("checkpointTs"))
    checkpoint_age_s = None
    if checkpoint_ts:
        checkpoint_age_s = int((utc_now() - checkpoint_ts).total_seconds())
    checkpoint_required = bool(state.get("checkpointRequired") or summary.get("checkpointRequired"))

    artifact_complete, artifact_probe = infer_artifact_completion(state, summary)
    terminal = current_state in TERMINAL_STATES
    orphaned = (not terminal) and (not pid_is_alive)

    evidence = {
        "checkpointFresh": checkpoint_age_s is not None and checkpoint_age_s <= idle_timeout_s,
        "artifactSignalFresh": progress_source == "artifact-change" and age_s is not None and age_s <= idle_timeout_s,
        "hookSignalFresh": progress_source == "hook-log-growth" and age_s is not None and age_s <= idle_timeout_s,
        "checkpointSignalFresh": progress_source == "checkpoint" and age_s is not None and age_s <= idle_timeout_s,
        "transcriptSignalFresh": progress_source == "transcript-growth" and age_s is not None and age_s <= idle_timeout_s,
    }

    missing_checkpoint_signal = checkpoint_required and checkpoint_ts is None
    stuck = (not terminal) and pid_is_alive and age_s is not None and age_s > idle_timeout_s and not evidence["checkpointFresh"]

    fix_to = None
    reason = None
    if terminal and current_state != "needs_input":
        fix_to = current_state
        reason = "already-terminal"
    elif artifact_complete:
        fix_to = "completed"
        reason = "artifact-complete"
    elif terminal and current_state == "needs_input":
        fix_to = current_state
        reason = "already-terminal"
    elif orphaned:
        fix_to = "orphaned"
        reason = "pid-dead"
    elif stuck:
        fix_to = "stuck"
        reason = "idle-timeout-missing-checkpoint" if missing_checkpoint_signal else "idle-timeout-no-fresh-checkpoint"

    return {
        "state": current_state,
        "pid": pid,
        "pidAlive": pid_is_alive,
        "idleAgeSeconds": age_s,
        "idleTimeoutSeconds": idle_timeout_s,
        "checkpointAgeSeconds": checkpoint_age_s,
        "checkpointRequired": checkpoint_required,
        "lastProgressSource": progress_source,
        "stuck": stuck,
        "orphaned": orphaned,
        "terminal": terminal,
        "artifactComplete": artifact_complete,
        "artifactProbe": artifact_probe,
        "evidence": evidence,
        "recommendedState": fix_to,
        "reason": reason,
    }


def reconcile(state_file: Path, idle_timeout_s: int, apply_fix: bool) -> dict[str, Any]:
    state = load_json(state_file)
    run_dir = state_file.parent
    summary_file = run_dir / "summary.json"
    summary = load_json(summary_file)
    evaluation = recommended_state(state, summary, idle_timeout_s)

    result = {
        **evaluation,
        "stateFile": str(state_file),
        "summaryFile": str(summary_file),
        "applied": False,
    }

    if not apply_fix or not evaluation.get("recommendedState"):
        return result

    current_state = str(state.get("state") or "unknown")
    target_state = str(evaluation["recommendedState"])
    if target_state == current_state:
        return result

    repo = state.get("repo")
    if not repo:
        return result

    registry_base = state_file.parents[2]
    registry = RunRegistry(registry_base)
    lock_path = registry.repo_lock_path(repo)
    handle = registry.open_run(run_dir, lock_path=lock_path)
    registry.append_event(handle, "watchdog_reconcile", fromState=current_state, toState=target_state, reason=evaluation.get("reason"))

    effective_summary = dict(summary) if isinstance(summary, dict) else {}
    if evaluation.get("artifactComplete") is not None:
        effective_summary["artifactComplete"] = evaluation.get("artifactComplete")
    if evaluation.get("artifactProbe") is not None:
        effective_summary["artifactProbe"] = evaluation.get("artifactProbe")
    if target_state == "completed":
        effective_summary.setdefault("finalState", "completed")

    registry.finalize(
        handle,
        state=target_state,
        exit_code=effective_summary.get("exitCode") if isinstance(effective_summary, dict) else None,
        summary=effective_summary or None,
    )
    result["applied"] = True
    result["newState"] = target_state
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate or reconcile whether a Claude orchestrator run is stuck/orphaned")
    parser.add_argument("--state-file", required=True)
    parser.add_argument("--idle-timeout-s", type=int, default=120)
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    result = reconcile(Path(args.state_file), args.idle_timeout_s, args.fix)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    for key, value in result.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
