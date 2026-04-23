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


def read_story_text(story_path: Path) -> str | None:
    if not story_path.exists():
        return None
    return story_path.read_text(encoding="utf-8", errors="replace")


def read_story_status(story_path: Path) -> str | None:
    text = read_story_text(story_path)
    if text is None:
        return None
    for pattern in [r"^Status:\s*(.+)$", r"^- \*\*Status:\*\*\s*(.+)$"]:
        match = re.search(pattern, text, flags=re.MULTILINE)
        if match:
            return match.group(1).strip().lower()
    return None


def read_review_verdict(story_path: Path) -> str | None:
    text = read_story_text(story_path)
    if text is None:
        return None

    lowered = text.lower()
    if "## code review" not in lowered and "### review verdict" not in lowered:
        return None

    section_match = re.search(r"^### Review Verdict\s*$([\s\S]*)", text, flags=re.MULTILINE)
    search_text = section_match.group(1) if section_match else text
    compact = " ".join(search_text.split()).lower()

    verdict_patterns = [
        (r"\*\*(approved)\*\*", "approved"),
        (r"\*\*(changes requested|changes-requested)\*\*", "changes-requested"),
        (r"review verdict[^\n]*?(approved)", "approved"),
        (r"review verdict[^\n]*?(changes requested|changes-requested)", "changes-requested"),
    ]
    for pattern, verdict in verdict_patterns:
        if re.search(pattern, search_text, flags=re.IGNORECASE):
            return verdict

    if "changes requested" in compact or "changes-requested" in compact:
        return "changes-requested"
    if "approved" in compact:
        return "approved"
    return None


def read_sprint_status(sprint_status_path: Path, story_id: str) -> str | None:
    data = load_yaml(sprint_status_path)
    dev = data.get("development_status") if isinstance(data, dict) else None
    if not isinstance(dev, dict):
        return None
    value = dev.get(story_id)
    if value is None:
        prefix = f"{story_id}-"
        for key, candidate in dev.items():
            if str(key) == story_id or str(key).startswith(prefix):
                value = candidate
                break
    return str(value).strip().lower() if value is not None else None


def default_profiles_file() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "claude-orchestrator-profiles.yaml"


def default_story_path(repo: Path, story_id: str | None) -> Path | None:
    if not story_id:
        return None
    impl_dir = repo / "_bmad-output" / "implementation-artifacts"
    candidates = sorted(impl_dir.glob(f"story-{story_id}*.md"))
    if candidates:
        return candidates[0].resolve()
    return (impl_dir / f"story-{story_id}.md").resolve()


def infer_expected_status(workflow: str, profiles_file: Path) -> str | None:
    data = load_yaml(profiles_file)
    workflows = data.get("workflows") if isinstance(data, dict) else None
    if not isinstance(workflows, dict):
        return None
    wf = workflows.get(workflow)
    if not isinstance(wf, dict):
        return None
    value = wf.get("expected_story_status")
    return str(value).strip().lower() if value else None


def probe_completion(
    *,
    repo: Path,
    workflow: str,
    story_id: str | None = None,
    story_path: Path | None = None,
    expected_story_status: str | None = None,
    profiles_file: Path | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    profiles_file = (profiles_file or default_profiles_file()).resolve()

    sprint_path = repo / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    inferred_story_path = story_path.resolve() if story_path else None
    if story_id and inferred_story_path is None:
        inferred_story_path = default_story_path(repo, story_id)

    if not expected_story_status:
        expected_story_status = infer_expected_status(workflow, profiles_file)

    story_status = read_story_status(inferred_story_path) if inferred_story_path else None
    review_verdict = read_review_verdict(inferred_story_path) if inferred_story_path else None
    sprint_status = read_sprint_status(sprint_path, story_id) if story_id else None

    evidence = {
        "repo": str(repo),
        "workflow": workflow,
        "storyId": story_id,
        "storyPath": str(inferred_story_path) if inferred_story_path else None,
        "storyFileExists": bool(inferred_story_path and inferred_story_path.exists()),
        "storyStatus": story_status,
        "reviewVerdict": review_verdict,
        "sprintStatus": sprint_status,
        "expectedStoryStatus": expected_story_status,
    }

    reasons: list[str] = []
    complete = False

    if workflow == "bmad-bmm-create-story":
        if evidence["storyFileExists"] and sprint_status in {"ready-for-dev", "in-progress", "review", "done"}:
            complete = True
        else:
            reasons.append("story file not created or sprint status not advanced")
    elif workflow == "bmad-bmm-dev-story":
        terminal = {"review", "done"}
        if sprint_status in terminal or story_status in terminal:
            complete = True
        else:
            reasons.append("story not yet advanced to review/done")
    elif workflow == "bmad-bmm-code-review":
        terminal_story = {"review", "done", "approved"}
        terminal_review = {"approved", "changes-requested"}
        if review_verdict in terminal_review:
            complete = True
        elif story_status in terminal_story:
            complete = True
        elif sprint_status in {"review", "done"}:
            complete = True
        else:
            reasons.append("review completion not yet observable from artifacts")
    elif workflow == "bmad":
        # General BMad persona runs don't have a single specific expected artifact.
        # We consider them complete to avoid failing runs that exited normally.
        complete = True
        reasons.append("bmad persona run completion accepted implicitly")
    else:
        if expected_story_status and (story_status == expected_story_status or sprint_status == expected_story_status):
            complete = True
        else:
            reasons.append("no workflow-specific completion rule matched")

    return {
        "complete": complete,
        "reasons": reasons,
        "evidence": {k: v for k, v in evidence.items() if v is not None},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe BMad artifact completion for Claude orchestrator runs")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--story-id")
    parser.add_argument("--story-path")
    parser.add_argument("--expected-story-status")
    parser.add_argument("--profiles-file")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    result = probe_completion(
        repo=Path(args.repo),
        workflow=args.workflow,
        story_id=args.story_id,
        story_path=Path(args.story_path).resolve() if args.story_path else None,
        expected_story_status=args.expected_story_status,
        profiles_file=Path(args.profiles_file).resolve() if args.profiles_file else None,
    )

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"complete={result['complete']}")
    for key, value in result["evidence"].items():
        print(f"{key}={value}")
    if result["reasons"]:
        print("reasons=" + " | ".join(result["reasons"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
