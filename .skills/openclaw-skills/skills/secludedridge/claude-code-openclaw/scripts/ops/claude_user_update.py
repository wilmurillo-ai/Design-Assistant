#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from ops.claude_run_report import build_report


def build_text(report: dict) -> str:
    run_id = report.get("runId")
    workflow = report.get("workflow") or "unknown-workflow"
    story_id = report.get("storyId") or "-"
    state = report.get("state") or "unknown"
    recommended = report.get("recommended") or {}
    artifact_complete = report.get("artifactComplete")
    reason = recommended.get("reason")
    idle_age = recommended.get("idleAgeSeconds")
    checkpoint_age = recommended.get("checkpointAgeSeconds")
    checkpoint_required = recommended.get("checkpointRequired")
    stage = report.get("stage")
    progress_excerpt = report.get("progressExcerpt")
    checkpoint_ts = report.get("checkpointTs")
    progress_source = report.get("lastProgressSource")
    ui_state = (report.get("summary") or {}).get("uiState")
    resume_id = (report.get("summary") or {}).get("resumeId")
    recovery_hint = (report.get("summary") or {}).get("recoveryHint")

    status_map = {
        "completed": "已完成",
        "running": "运行中",
        "stuck": "已判定卡住",
        "orphaned": "已判定孤儿 run",
        "failed": "执行失败",
        "cancelled": "已取消",
        "needs_approval": "等待审批",
    }
    human_state = status_map.get(state, state)

    lines = [
        f"运行状态：{human_state}",
        f"workflow：{workflow}",
        f"story：{story_id}",
        f"runId：{run_id}",
    ]

    if artifact_complete is not None:
        lines.append(f"产物完成判定：{'是' if artifact_complete else '否'}")
    if reason:
        lines.append(f"原因：{reason}")
    if idle_age is not None:
        lines.append(f"最近静默时长：{idle_age}s")
    if checkpoint_required is not None:
        lines.append(f"checkpoint 协议：{'必需' if checkpoint_required else '可选'}")
    if checkpoint_age is not None:
        lines.append(f"最近 checkpoint 时长：{checkpoint_age}s")
    if stage:
        lines.append(f"阶段：{stage}")
    if progress_excerpt:
        lines.append(f"进展摘要：{progress_excerpt}")
    if checkpoint_ts:
        lines.append(f"checkpointTs：{checkpoint_ts}")
    if progress_source:
        lines.append(f"进展来源：{progress_source}")
    if ui_state:
        lines.append(f"UI 状态：{ui_state}")
    if resume_id:
        lines.append(f"resumeId：{resume_id}")
    if recovery_hint:
        lines.append(f"恢复命令：{recovery_hint}")

    summary = report.get("summary") or {}
    artifact_probe = summary.get("artifactProbe") or {}
    evidence = artifact_probe.get("evidence") or {}
    sprint_status = evidence.get("sprintStatus")
    story_status = evidence.get("storyStatus")
    if sprint_status:
        lines.append(f"sprint-status：{sprint_status}")
    if story_status:
        lines.append(f"story 状态：{story_status}")

    last_events = report.get("lastEvents") or []
    if last_events:
        lines.append("最近事件：")
        for item in last_events[-3:]:
            event = item.get("event")
            extra = item.get("extra") or item.get("reason") or item.get("source") or item.get("name")
            if extra:
                lines.append(f"- {event}: {extra}")
            else:
                lines.append(f"- {event}")

    tail = (report.get("transcriptTail") or "").strip()
    if tail:
        tail = "\n".join(tail.splitlines()[-8:])
        lines.append("终端尾部：")
        lines.append(tail)

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a user-facing Chinese update from a Claude orchestrator run")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--idle-timeout-s", type=int, default=180)
    args = parser.parse_args()

    report = build_report(Path(args.run_dir).resolve(), args.idle_timeout_s)
    print(build_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
