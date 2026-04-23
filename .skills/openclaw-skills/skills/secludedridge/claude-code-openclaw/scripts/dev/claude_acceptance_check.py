#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_FILES = [
    "scripts/claude_code_run.py",
    "scripts/claude_orchestrator.py",
    "scripts/claude_run_registry.py",
    "scripts/claude_checkpoint.py",
    "scripts/claude_workflow_adapter.py",
    "scripts/claude_artifact_probe.py",
    "scripts/claude_watchdog.py",
    "scripts/ops/claude_run_report.py",
    "scripts/ops/claude_latest_run_report.py",
    "scripts/ops/claude_reconcile_runs.py",
    "scripts/ops/claude_user_update.py",
    "scripts/ops/claude_recover_run.py",
    "scripts/claude_dispatch_update.py",
    "scripts/install_claude_hooks.py",
    "scripts/claude_hook_event_logger.py",
    "scripts/dev/claude_v2_smoke.py",
    "scripts/dev/claude_event_summary.py",
]


def run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "cmd": cmd,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Acceptance check for claude-code-openclaw orchestration control plane")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--registry-dir")
    parser.add_argument("--workflow")
    parser.add_argument("--story-id")
    parser.add_argument("--run-dir")
    parser.add_argument("--notify-account")
    parser.add_argument("--notify-target")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    results: dict[str, Any] = {}

    py_compile_cmd = [sys.executable, "-m", "py_compile", *[str(repo / rel) for rel in SCRIPT_FILES]]
    results["py_compile"] = run(py_compile_cmd, repo)

    results["v2_smoke"] = run([
        sys.executable,
        str(repo / "scripts/dev/claude_v2_smoke.py"),
    ], repo)

    results["git_status"] = run(["git", "status", "--short", "--branch"], repo)

    if args.registry_dir:
        latest_cmd = [
            sys.executable,
            str(repo / "scripts/ops/claude_latest_run_report.py"),
            "--registry-dir",
            args.registry_dir,
            "--format",
            "text",
        ]
        if args.workflow:
            latest_cmd += ["--workflow", args.workflow]
        if args.story_id:
            latest_cmd += ["--story-id", args.story_id]
        results["latest_run_report"] = run(latest_cmd, repo)

        reconcile_cmd = [
            sys.executable,
            str(repo / "scripts/ops/claude_reconcile_runs.py"),
            "--registry-dir",
            args.registry_dir,
            "--idle-timeout-s",
            "180",
            "--format",
            "text",
        ]
        results["reconcile_runs"] = run(reconcile_cmd, repo)

    if args.run_dir:
        results["run_report"] = run([
            sys.executable,
            str(repo / "scripts/ops/claude_run_report.py"),
            "--run-dir",
            args.run_dir,
            "--idle-timeout-s",
            "180",
            "--format",
            "text",
        ], repo)
        results["user_update"] = run([
            sys.executable,
            str(repo / "scripts/ops/claude_user_update.py"),
            "--run-dir",
            args.run_dir,
            "--idle-timeout-s",
            "180",
        ], repo)
        results["recover_command"] = run([
            sys.executable,
            str(repo / "scripts/ops/claude_recover_run.py"),
            "--run-dir",
            args.run_dir,
        ], repo)

        if args.notify_account and args.notify_target:
            results["dispatch_dry_run"] = run([
                sys.executable,
                str(repo / "scripts/claude_dispatch_update.py"),
                "--run-dir",
                args.run_dir,
                "--notify-account",
                args.notify_account,
                "--notify-target",
                args.notify_target,
                "--dry-run",
            ], repo)

    ok = all(item.get("ok", False) for item in results.values())
    payload = {
        "ok": ok,
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
