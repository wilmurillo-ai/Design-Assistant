#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def build_recovery_command(run_dir: Path) -> list[str]:
    summary = load_json(run_dir / "summary.json")
    state = load_json(run_dir / "state.json")
    repo = state.get("repo")
    workflow = state.get("workflow")
    story_id = state.get("storyId")
    profile = state.get("profile") or summary.get("profile")
    resume_id = summary.get("resumeId")
    prompt_file = summary.get("promptFile") or state.get("promptFile")

    if not repo or not workflow:
        raise SystemExit("run is missing repo/workflow metadata")

    script = Path(__file__).resolve().parent.parent / "claude_code_run.py"
    cmd = [
        sys.executable,
        str(script),
        "--mode",
        "interactive",
        "--cwd",
        str(repo),
        "--workflow",
        str(workflow),
    ]
    if story_id:
        cmd += ["--story-id", str(story_id)]
    if profile:
        cmd += ["--orchestrator-profile", str(profile)]
    cmd += ["--install-hooks"]

    if resume_id:
        cmd += ["--resume", str(resume_id)]
    elif prompt_file:
        cmd += ["--prompt-file", str(prompt_file)]
    else:
        raise SystemExit("run is missing both resumeId and promptFile; cannot recover")

    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or execute recovery command for a prior Claude orchestrator run")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    cmd = build_recovery_command(Path(args.run_dir).resolve())
    if not args.execute:
        print(" ".join(shlex.quote(part) for part in cmd))
        return 0

    return subprocess.run(cmd, text=True).returncode


if __name__ == "__main__":
    raise SystemExit(main())
