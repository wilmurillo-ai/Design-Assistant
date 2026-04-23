#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from claude_run_registry import RunRegistry


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compact(text: str, limit: int = 240) -> str:
    text = " ".join(str(text).strip().split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def checkpoint_path(run_dir: Path) -> Path:
    return run_dir / "checkpoint.json"


def checkpoint_history_path(run_dir: Path) -> Path:
    return run_dir / "checkpoints.jsonl"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def load_checkpoint(run_dir: Path) -> dict[str, Any]:
    data = load_json(checkpoint_path(run_dir), {})
    return data if isinstance(data, dict) else {}


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        item = str(value).strip()
        if not item or item in seen:
            continue
        seen.add(item)
        output.append(item)
    return output


def write_checkpoint(
    *,
    run_dir: Path,
    stage: str,
    message: str,
    expected_artifacts: list[str] | None = None,
    workflow: str | None = None,
    story_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    current = load_checkpoint(run_dir)
    state_file = run_dir / "state.json"
    state = load_json(state_file, {}) if state_file.exists() else {}

    merged_expected = _dedupe_strings(
        [*(current.get("expectedArtifacts") or []), *(expected_artifacts or [])]
    )

    payload = {
        "runId": current.get("runId") or state.get("runId") or run_dir.name,
        "workflow": workflow or current.get("workflow") or state.get("workflow"),
        "storyId": story_id or current.get("storyId") or state.get("storyId"),
        "stage": stage,
        "message": message,
        "updatedAt": utc_now(),
        "expectedArtifacts": merged_expected,
        "details": details or {},
    }
    checkpoint_path(run_dir).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with checkpoint_history_path(run_dir).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")

    if state_file.exists():
        registry = RunRegistry(run_dir.parents[1])
        handle = registry.open_run(run_dir)
        progress_excerpt = compact(f"{stage}: {message}")
        registry.heartbeat(
            handle,
            source="checkpoint",
            stage=stage,
            progressExcerpt=progress_excerpt,
            checkpointTs=payload["updatedAt"],
            checkpointFile=str(checkpoint_path(run_dir)),
            expectedArtifacts=merged_expected,
        )
        registry.append_event(handle, "checkpoint_updated", checkpoint=payload)

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a structured checkpoint for a Claude orchestrator run")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--workflow")
    parser.add_argument("--story-id")
    parser.add_argument("--expected-artifact", dest="expected_artifacts", action="append", default=[])
    parser.add_argument("--details-json", default="{}")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        details = json.loads(args.details_json)
        if not isinstance(details, dict):
            raise ValueError("details-json must decode to an object")
    except Exception as exc:
        raise SystemExit(f"invalid --details-json: {exc}")

    payload = write_checkpoint(
        run_dir=Path(args.run_dir),
        stage=args.stage,
        message=args.message,
        workflow=args.workflow,
        story_id=args.story_id,
        expected_artifacts=args.expected_artifacts,
        details=details,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
