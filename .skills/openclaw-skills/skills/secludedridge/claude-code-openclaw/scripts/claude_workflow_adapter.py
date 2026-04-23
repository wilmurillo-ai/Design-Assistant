#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_sprint_status(repo: Path, story_id: str | None) -> str | None:
    if not story_id:
        return None
    sprint_path = repo / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    data = load_yaml(sprint_path)
    development_status = data.get("development_status") if isinstance(data, dict) else None
    if not isinstance(development_status, dict):
        return None
    value = development_status.get(story_id)
    if value is None:
        prefix = f"{story_id}-"
        for key, candidate in development_status.items():
            if str(key) == story_id or str(key).startswith(prefix):
                value = candidate
                break
    return str(value).strip().lower() if value is not None else None


def infer_previous_story_path(repo: Path, story_id: str | None) -> str | None:
    if not story_id:
        return None
    match = re.match(r"^(\d+)-(\d+)-", story_id)
    if not match:
        return None
    epic_num = int(match.group(1))
    story_num = int(match.group(2))
    if story_num <= 1:
        return None
    impl_dir = repo / "_bmad-output" / "implementation-artifacts"
    prefix = f"story-{epic_num}-{story_num - 1}-"
    candidates = sorted(impl_dir.glob(f"{prefix}*.md"))
    return str(candidates[0]) if candidates else None


def default_story_path(repo: Path, story_id: str | None) -> str | None:
    if not story_id:
        return None
    impl_dir = repo / "_bmad-output" / "implementation-artifacts"
    candidates = sorted(impl_dir.glob(f"story-{story_id}*.md"))
    if candidates:
        return str(candidates[0])
    return str(impl_dir / f"story-{story_id}.md")


def create_story_stage_plan() -> list[dict[str, str]]:
    return [
        {"stage": "target-selected", "description": "已确认本轮要生成的目标 story"},
        {"stage": "context-loaded", "description": "已加载 sprint / architecture / epics / 上游 story 等核心上下文"},
        {"stage": "drafting-started", "description": "已开始按模板起草 story 内容"},
        {"stage": "story-file-written", "description": "目标 story 文件已写入或更新"},
        {"stage": "sprint-status-updated", "description": "sprint-status.yaml 已推进到 ready-for-dev 或更后状态"},
        {"stage": "workflow-completed", "description": "create-story 工作流已完成"},
    ]


def build_create_story_context(repo: Path, story_id: str | None, story_path: str | None, run_dir: Path) -> dict[str, Any]:
    repo = repo.resolve()
    target_story_path = str(Path(story_path).resolve()) if story_path else default_story_path(repo, story_id)
    sprint_status_path = str(repo / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml")
    architecture_path = str(repo / "_bmad-output" / "planning-artifacts" / "architecture.md")
    epics_path = str(repo / "_bmad-output" / "planning-artifacts" / "epics-and-stories.md")
    previous_story_path = infer_previous_story_path(repo, story_id)

    input_files = [sprint_status_path, architecture_path, epics_path]
    if previous_story_path:
        input_files.append(previous_story_path)

    expected_artifacts = [p for p in [target_story_path, sprint_status_path] if p]

    return {
        "adapterVersion": "v2",
        "workflow": "bmad-bmm-create-story",
        "storyId": story_id,
        "storyPath": target_story_path,
        "repo": str(repo),
        "runDir": str(run_dir),
        "sprintStatus": read_sprint_status(repo, story_id),
        "previousStoryPath": previous_story_path,
        "inputFiles": input_files,
        "expectedArtifacts": expected_artifacts,
        "stagePlan": create_story_stage_plan(),
    }


def build_context(repo: Path, workflow: str, story_id: str | None, story_path: str | None, run_dir: Path) -> dict[str, Any]:
    if workflow == "bmad-bmm-create-story":
        return build_create_story_context(repo, story_id, story_path, run_dir)

    target_story_path = str(Path(story_path).resolve()) if story_path else default_story_path(repo, story_id)
    payload = {
        "adapterVersion": "v2",
        "workflow": workflow,
        "storyId": story_id,
        "storyPath": target_story_path,
        "repo": str(repo.resolve()),
        "runDir": str(run_dir),
        "expectedArtifacts": [p for p in [target_story_path] if p] if target_story_path else [],
        "stagePlan": [],
    }
    return payload


def build_checkpoint_instruction_block(context: dict[str, Any], checkpoint_script: Path, run_dir: Path) -> str:
    stage_lines = []
    for item in context.get("stagePlan") or []:
        stage_lines.append(f"  - {item.get('stage')}: {item.get('description')}")

    expected_args = " ".join(
        f"--expected-artifact {json.dumps(path, ensure_ascii=False)}" for path in (context.get("expectedArtifacts") or [])
    )
    example = (
        f"python3 {checkpoint_script} --run-dir {run_dir} --workflow {context.get('workflow')} "
        f"--story-id {context.get('storyId') or ''} --stage <stage> --message \"<中文说明>\" {expected_args}"
    ).strip()

    lines = [
        "[OpenClaw Orchestrator V2]",
        f"- 先读：{run_dir / 'workflow-context.json'}",
        "- 不要先在仓库里盲搜；先用 context 文件中的目标路径。",
        "- 仅在关键阶段写 checkpoint，避免无效频繁汇报。",
        f"- checkpoint 示例：{example}",
    ]
    if stage_lines:
        lines.append("- 预期阶段：")
        lines.extend(stage_lines)
    return "\n".join(lines)


def inject_adapter_instructions(prompt: str, context: dict[str, Any], checkpoint_script: Path, run_dir: Path) -> str:
    instruction_block = build_checkpoint_instruction_block(context, checkpoint_script, run_dir)
    lines = prompt.splitlines()
    if not lines:
        return instruction_block

    first_nonempty = None
    for idx, line in enumerate(lines):
        if line.strip():
            first_nonempty = idx
            break
    if first_nonempty is None:
        return instruction_block

    head = lines[: first_nonempty + 1]
    tail = lines[first_nonempty + 1 :]
    injected = head + ["", instruction_block, ""] + tail
    return "\n".join(injected)


def write_context_file(run_dir: Path, context: dict[str, Any]) -> Path:
    path = run_dir / "workflow-context.json"
    write_json(path, context)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare workflow adapter context for Claude Orchestrator V2")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--story-id")
    parser.add_argument("--story-path")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = build_context(
        repo=Path(args.repo),
        workflow=args.workflow,
        story_id=args.story_id,
        story_path=args.story_path,
        run_dir=Path(args.run_dir),
    )
    write_context_file(Path(args.run_dir), context)
    if args.format == "json":
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        print(f"workflow={context.get('workflow')}")
        print(f"storyId={context.get('storyId')}")
        print(f"storyPath={context.get('storyPath')}")
        print(f"expectedArtifacts={','.join(context.get('expectedArtifacts') or [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
