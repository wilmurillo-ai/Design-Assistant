#!/usr/bin/env python3
"""Run Claude Code for OpenClaw skill workflows.

This wrapper is intentionally narrow:
- Interactive slash workflows (`/bmad-*`, `/speckit.*`, `/opsx:*`) must go through
  the event-driven orchestrator.
- One-shot headless tasks must use `scripts/run_claude_task.sh` instead of invoking
  raw `claude -p` through background exec flows.

Legacy tmux fallback and direct headless execution were removed to prevent silent
background runs without structured status delivery.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def which(name: str) -> str | None:
    paths = os.environ.get("PATH", "").split(":")
    for p in paths:
        if not p:
            continue
        cand = Path(p) / name
        try:
            if cand.is_file() and os.access(cand, os.X_OK):
                return str(cand)
        except OSError:
            continue
    return None


def load_prompt(prompt: str | None, prompt_file: str | None) -> str | None:
    if prompt and prompt_file:
        raise ValueError("Use only one of --prompt or --prompt-file")

    if prompt_file:
        p = Path(prompt_file)
        if not p.exists():
            raise ValueError(f"prompt file not found: {prompt_file}")
        return p.read_text(encoding="utf-8")

    return prompt


def looks_like_interactive_slash_workflow(prompt: str | None) -> bool:
    if not prompt:
        return False

    for line in prompt.splitlines():
        s = line.strip()
        if not s:
            continue
        return s.startswith("/")
    return False


def infer_workflow(prompt: str | None) -> str | None:
    if not prompt:
        return None
    for line in prompt.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("/"):
            return s.split()[0][1:]
        break
    return None


def run_interactive_orchestrated(args: argparse.Namespace, prompt: str | None) -> int:
    orchestrator = SCRIPT_DIR / "claude_orchestrator.py"
    if not orchestrator.exists():
        print(f"orchestrator not found: {orchestrator}", file=sys.stderr)
        return 2

    cwd = args.cwd or os.getcwd()
    workflow = args.workflow or infer_workflow(prompt) or "interactive-workflow"
    cmd: list[str] = [
        sys.executable,
        str(orchestrator),
        "--cwd",
        cwd,
        "--workflow",
        workflow,
    ]

    if args.permission_mode:
        cmd += ["--permission-mode", args.permission_mode]
    if args.allowed_tools:
        cmd += ["--allowedTools", args.allowed_tools]
    if args.append_system_prompt:
        cmd += ["--append-system-prompt", args.append_system_prompt]
    if args.system_prompt:
        cmd += ["--system-prompt", args.system_prompt]
    if args.resume:
        cmd += ["--resume", args.resume]
    if args.install_hooks:
        cmd += ["--install-hooks"]
    if args.event_log_file:
        cmd += ["--event-log-file", args.event_log_file]
    if args.orchestrator_profile:
        cmd += ["--profile", args.orchestrator_profile]
    if args.orchestrator_profiles_file:
        cmd += ["--profiles-file", args.orchestrator_profiles_file]
    if args.story_id:
        cmd += ["--story-id", args.story_id]
    if args.story_path:
        cmd += ["--story-path", args.story_path]
    if args.stop_on_artifact_complete:
        cmd += ["--stop-on-artifact-complete"]
    if args.notify_account:
        cmd += ["--notify-account", args.notify_account]
    if args.notify_target:
        cmd += ["--notify-target", args.notify_target]
    if args.notify_channel:
        cmd += ["--notify-channel", args.notify_channel]
    if args.notify_dry_run:
        cmd += ["--notify-dry-run"]
    if args.notify_parent_session:
        cmd += ["--notify-parent-session", args.notify_parent_session]
    if args.notify_final_update:
        cmd += ["--notify-final-update"]
    if args.extra:
        cmd += ["--", *args.extra]

    if args.prompt_file:
        cmd += ["--prompt-file", args.prompt_file]
        # return subprocess.run(cmd, text=True).returncode
        import os
        os.execv(cmd[0], cmd)

    tmp_prompt = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".txt")
    try:
        tmp_prompt.write(prompt or "")
        tmp_prompt.flush()
        tmp_prompt.close()
        cmd += ["--prompt-file", tmp_prompt.name]
        # return subprocess.run(cmd, text=True).returncode
        import os
        os.execv(cmd[0], cmd)
    finally:
        try:
            os.unlink(tmp_prompt.name)
        except OSError:
            pass


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run Claude Code slash workflows via the OpenClaw event-driven orchestrator")

    ap.add_argument("-p", "--prompt", help="Prompt text")
    ap.add_argument("--prompt-file", help="Read prompt text from file")
    ap.add_argument("--cwd", help="Working directory")

    ap.add_argument("--mode", choices=["auto", "interactive", "headless"], default="auto")

    ap.add_argument("--permission-mode", default=None, help="Claude Code permission mode")
    ap.add_argument("--allowedTools", dest="allowed_tools", help="Claude Code allowed tools allowlist string")
    ap.add_argument("--append-system-prompt", dest="append_system_prompt")
    ap.add_argument("--system-prompt", dest="system_prompt")
    ap.add_argument("--resume")

    default_claude = os.environ.get("CLAUDE_CODE_BIN", which("claude") or "claude")
    ap.add_argument("--claude-bin", default=default_claude, help="Unused compatibility flag; orchestrator resolves Claude CLI")

    ap.add_argument("--install-hooks", dest="install_hooks", action="store_true", help="Install Claude lifecycle hooks before launch (default: on)")
    ap.add_argument("--no-install-hooks", dest="install_hooks", action="store_false", help="Disable hook installation")
    ap.set_defaults(install_hooks=True)
    ap.add_argument("--event-log-file", help="Custom JSONL file path for compact Claude hook events")
    ap.add_argument("--orchestrator-profile", help="Profile name from references/claude-orchestrator-profiles.yaml")
    ap.add_argument("--orchestrator-profiles-file", help="Custom orchestrator profiles YAML")
    ap.add_argument("--workflow", help="Workflow name for orchestrator state/probe rules (e.g. bmad-bmm-dev-story)")
    ap.add_argument("--story-id", help="Story id used by artifact probe (e.g. 1-4-datasource-failover)")
    ap.add_argument("--story-path", help="Explicit story file path for artifact probe")
    ap.add_argument("--stop-on-artifact-complete", action="store_true", help="Let orchestrator stop the session once artifact completion is detected")
    ap.add_argument("--notify-account", help="OpenClaw account id used for final update dispatch")
    ap.add_argument("--notify-target", help="OpenClaw message target for final update dispatch")
    ap.add_argument("--notify-channel", help="Optional channel name for final update dispatch")
    ap.add_argument("--notify-dry-run", action="store_true", help="Render final update dispatch payload without actually sending")
    ap.add_argument("--notify-parent-session", help="OpenClaw parent session key for async sessions_send callback on completion")
    ap.add_argument("--notify-final-update", dest="notify_final_update", action="store_true", help="Dispatch user-update.txt when the orchestrated run reaches a terminal state (default: on)")
    ap.add_argument("--no-notify-final-update", dest="notify_final_update", action="store_false", help="Disable final update dispatch")
    ap.set_defaults(notify_final_update=True)

    ap.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args appended after --")

    args = ap.parse_args()

    extra = args.extra or []
    if extra and extra[0] == "--":
        extra = extra[1:]
    args.extra = extra

    return args


def main() -> int:
    args = parse_args()

    try:
        prompt = load_prompt(args.prompt, args.prompt_file)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    mode = args.mode
    if mode == "auto":
        mode = "interactive" if looks_like_interactive_slash_workflow(prompt) else "headless"

    if mode == "headless":
        print(
            "Headless mode was intentionally removed from claude_code_run.py. "
            "Use scripts/run_claude_task.sh for one-shot headless Claude Code tasks.",
            file=sys.stderr,
        )
        return 2

    if not looks_like_interactive_slash_workflow(prompt):
        print(
            "claude_code_run.py is reserved for slash-command workflows. "
            "Use scripts/run_claude_task.sh for one-shot headless prompts.",
            file=sys.stderr,
        )
        return 2

    return run_interactive_orchestrated(args, prompt)


if __name__ == "__main__":
    raise SystemExit(main())
