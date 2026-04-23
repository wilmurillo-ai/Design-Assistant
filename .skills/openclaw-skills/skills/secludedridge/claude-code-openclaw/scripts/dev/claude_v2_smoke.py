#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from claude_checkpoint import checkpoint_path, load_checkpoint, write_checkpoint
from claude_orchestrator import extract_progress_excerpt
from claude_artifact_probe import probe_completion
from ops.claude_run_report import build_report
from ops.claude_recover_run import build_recovery_command
from claude_workflow_adapter import build_context, write_context_file


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def run_smoke() -> dict:
    with tempfile.TemporaryDirectory(prefix="claude-v2-smoke-") as td:
        root = Path(td)
        repo = root / "repo"
        run_dir = repo / ".claude" / "orchestrator" / "runs" / "20260313T000000Z-bmad-bmm-create-story"
        run_dir.mkdir(parents=True, exist_ok=True)

        story_id = "2-9-smoke"
        story_path = repo / "_bmad-output" / "implementation-artifacts" / f"story-{story_id}.md"
        sprint_path = repo / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
        architecture_path = repo / "_bmad-output" / "planning-artifacts" / "architecture.md"
        epics_path = repo / "_bmad-output" / "planning-artifacts" / "epics-and-stories.md"

        architecture_path.parent.mkdir(parents=True, exist_ok=True)
        epics_path.parent.mkdir(parents=True, exist_ok=True)
        architecture_path.write_text("# arch\n", encoding="utf-8")
        epics_path.write_text("# epics\n", encoding="utf-8")
        write_yaml(
            sprint_path,
            {
                "development_status": {
                    story_id: "backlog",
                }
            },
        )

        prompt_file = run_dir / "prompt.txt"
        prompt_file.write_text("/bmad-agent-bmm-sm\nCS\n", encoding="utf-8")
        state_payload = {
            "runId": run_dir.name,
            "repo": str(repo.resolve()),
            "workflow": "bmad-bmm-create-story",
            "storyId": story_id,
            "state": "running",
            "pid": 1,
            "lastProgressAt": None,
            "promptFile": str(prompt_file),
            "profile": "default-safe",
        }
        (run_dir / "state.json").write_text(json.dumps(state_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (run_dir / "transcript.log").write_text("", encoding="utf-8")
        (run_dir / "events.jsonl").write_text("", encoding="utf-8")

        context = build_context(
            repo=repo,
            workflow="bmad-bmm-create-story",
            story_id=story_id,
            story_path=str(story_path),
            run_dir=run_dir,
        )
        context_file = write_context_file(run_dir, context)

        write_checkpoint(
            run_dir=run_dir,
            workflow="bmad-bmm-create-story",
            story_id=story_id,
            stage="target-selected",
            message="smoke target selected",
            expected_artifacts=context.get("expectedArtifacts") or [],
        )

        story_path.parent.mkdir(parents=True, exist_ok=True)
        story_path.write_text("# Story\n\nStatus: ready-for-dev\n", encoding="utf-8")
        write_yaml(
            sprint_path,
            {
                "development_status": {
                    story_id: "ready-for-dev",
                }
            },
        )

        write_checkpoint(
            run_dir=run_dir,
            workflow="bmad-bmm-create-story",
            story_id=story_id,
            stage="workflow-completed",
            message="smoke completed",
            expected_artifacts=context.get("expectedArtifacts") or [],
            details={"mode": "smoke"},
        )

        checkpoint = load_checkpoint(run_dir)
        report = build_report(run_dir, idle_timeout_s=180)
        recovery_cmd = build_recovery_command(run_dir)
        exit_excerpt = extract_progress_excerpt("\u0003Press Ctrl-C again to exit")
        review_story_id = "4-1-review-smoke"
        review_story_path = repo / "_bmad-output" / "implementation-artifacts" / f"story-{review_story_id}.md"
        review_story_path.write_text(
            "# Story 4.1 Review Smoke\n\nStatus: approved\n\n## Code Review\n\n### Review Verdict\n\n**APPROVED**\n",
            encoding="utf-8",
        )
        review_probe = probe_completion(
            repo=repo,
            workflow="bmad-bmm-code-review",
            story_id=review_story_id,
            story_path=review_story_path,
        )

        create_story_probe = probe_completion(
            repo=repo,
            workflow="bmad-bmm-create-story",
            story_id=story_id,
            story_path=story_path,
        )

        checks = {
            "contextFileExists": context_file.exists(),
            "checkpointFileExists": checkpoint_path(run_dir).exists(),
            "checkpointHasStage": bool(checkpoint.get("stage")),
            "checkpointHasExpectedArtifacts": bool(checkpoint.get("expectedArtifacts")),
            "reportHasStage": bool(report.get("stage")),
            "reportHasProgressExcerpt": bool(report.get("progressExcerpt")),
            "reportHasCheckpointTs": bool(report.get("checkpointTs")),
            "reportHasWorkflowContext": bool(report.get("workflowContextFile")),
            "recoveryCommandIsCompatible": "--orchestrate" not in recovery_cmd and any(str(part).endswith("claude_code_run.py") for part in recovery_cmd),
            "exitPromptIgnoredAsProgress": exit_excerpt == "",
            "codeReviewApprovedProbeComplete": bool(review_probe.get("complete")),
            "reportArtifactCompleteUsesEvaluation": bool(report.get("artifactComplete")),
            "createStoryProbeResolvesSluggedPath": bool(create_story_probe.get("complete")),
        }
        ok = all(checks.values())

        return {
            "ok": ok,
            "checks": checks,
            "contextFile": str(context_file),
            "checkpoint": checkpoint,
            "report": {
                "stage": report.get("stage"),
                "progressExcerpt": report.get("progressExcerpt"),
                "checkpointTs": report.get("checkpointTs"),
                "workflowContextFile": report.get("workflowContextFile"),
                "artifactComplete": report.get("artifactComplete"),
            },
            "reviewProbe": review_probe,
            "recoveryCommand": recovery_cmd,
            "exitPromptExcerpt": exit_excerpt,
        }


def main() -> int:
    result = run_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
