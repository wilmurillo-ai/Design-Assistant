#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pexpect
import yaml

from claude_artifact_probe import default_profiles_file, probe_completion
from claude_checkpoint import checkpoint_path as run_checkpoint_path, load_checkpoint, write_checkpoint
from claude_run_registry import RunRegistry
from claude_watchdog import reconcile as reconcile_run_state
from claude_workflow_adapter import (
    build_context as build_workflow_context,
    inject_adapter_instructions,
    read_sprint_status,
    write_context_file,
)


def load_prompt(prompt: str | None, prompt_file: str | None) -> str:
    if prompt and prompt_file:
        raise SystemExit("Use only one of --prompt or --prompt-file")
    if prompt_file:
        path = Path(prompt_file).resolve()
        if not path.exists():
            raise SystemExit(f"prompt file not found: {path}")
        return path.read_text(encoding="utf-8")
    if prompt:
        return prompt
    raise SystemExit("Missing --prompt or --prompt-file")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_profile(profiles_file: Path, profile_name: str | None) -> tuple[str, dict[str, Any]]:
    data = load_yaml(profiles_file)
    profiles = data.get("profiles") if isinstance(data, dict) else None
    if not isinstance(profiles, dict):
        return (profile_name or "default", {})
    if profile_name and profile_name in profiles and isinstance(profiles[profile_name], dict):
        return (profile_name, dict(profiles[profile_name]))
    if "default-safe" in profiles and isinstance(profiles["default-safe"], dict):
        return (profile_name or "default-safe", dict(profiles["default-safe"]))
    return (profile_name or "default", {})


def load_workflow_config(profiles_file: Path, workflow_name: str | None) -> dict[str, Any]:
    if not workflow_name:
        return {}
    data = load_yaml(profiles_file)
    workflows = data.get("workflows") if isinstance(data, dict) else None
    if not isinstance(workflows, dict):
        return {}
    workflow = workflows.get(workflow_name)
    return dict(workflow) if isinstance(workflow, dict) else {}


def build_command(args: argparse.Namespace, permission_mode: str) -> list[str]:
    cmd = [args.claude_bin, "--permission-mode", permission_mode]
    if args.allowed_tools:
        cmd += ["--allowedTools", args.allowed_tools]
    if args.append_system_prompt:
        cmd += ["--append-system-prompt", args.append_system_prompt]
    if args.system_prompt:
        cmd += ["--system-prompt", args.system_prompt]
    if args.resume:
        cmd += ["--resume", args.resume]
    if args.extra:
        cmd += args.extra
    return cmd


def build_child_env(*, run_dir: Path, workflow: str, story_id: str | None, context_file: Path | None) -> dict[str, str]:
    env = dict(os.environ)
    env["OPENCLAW_CLAUDE_RUN_DIR"] = str(run_dir)
    env["OPENCLAW_CLAUDE_WORKFLOW"] = workflow
    if story_id:
        env["OPENCLAW_CLAUDE_STORY_ID"] = story_id
    env["OPENCLAW_CLAUDE_CHECKPOINT_FILE"] = str(run_checkpoint_path(run_dir))
    if context_file:
        env["OPENCLAW_CLAUDE_WORKFLOW_CONTEXT"] = str(context_file)
    return env


def artifact_snapshot(paths: list[str]) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for raw in paths:
        path = Path(raw).resolve()
        exists = path.exists()
        stat = path.stat() if exists else None
        snapshot[str(path)] = {
            "exists": exists,
            "size": stat.st_size if stat else None,
            "mtimeNs": stat.st_mtime_ns if stat else None,
        }
    return snapshot


def artifact_snapshot_changed(old: dict[str, dict[str, Any]], new: dict[str, dict[str, Any]]) -> list[str]:
    changed: list[str] = []
    all_keys = sorted(set(old) | set(new))
    for key in all_keys:
        if old.get(key) != new.get(key):
            changed.append(key)
    return changed


def reconcile_existing_runs(registry: RunRegistry, idle_timeout_s: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for run_dir in sorted(registry.runs_dir.iterdir()) if registry.runs_dir.exists() else []:
        state_file = run_dir / "state.json"
        if not state_file.exists():
            continue
        result = reconcile_run_state(state_file, idle_timeout_s, apply_fix=True)
        if result.get("applied"):
            results.append(result)
    return results


def maybe_install_hooks(cwd: Path, event_log_file: Path | None) -> None:
    installer = Path(__file__).resolve().parent / "install_claude_hooks.py"
    cmd = [sys.executable, str(installer), "--project-root", str(cwd)]
    if event_log_file:
        cmd += ["--event-log-file", str(event_log_file)]
    subprocess.check_call(cmd)


def send_prompt(child: pexpect.spawn, prompt: str) -> None:
    # Paste the full prompt, then submit in a separate keystroke.
    # This avoids treating the final newline as part of the pasted block.
    child.send(prompt)
    time.sleep(0.15)


def submit_prompt(child: pexpect.spawn) -> None:
    # Claude Code TUI can accept the pasted text into the composer without
    # actually sending it. A separate Enter is required to submit.
    child.send("\r")
    time.sleep(0.10)


def select_menu_option(child: pexpect.spawn, option: int) -> None:
    """Select 1-based menu option using Down + Enter for TUI compatibility."""
    down_count = max(0, option - 1)
    for _ in range(down_count):
        child.send("\x1b[B")
        time.sleep(0.05)
    child.send("\r")


def compact(text: str, limit: int = 200) -> str:
    text = " ".join(text.strip().split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def strip_ansi(text: str) -> str:
    text = re.sub(r"\x1b\][^\x07]*(?:\x07|\x1b\\)", "", text)
    text = re.sub(r"\x1B\[[0-9;?]*[ -/]*[@-~]", "", text)
    return text.replace("\r", "")


def read_tail_text(path: Path, max_bytes: int = 4096) -> str:
    if not path.exists():
        return ""
    with path.open("rb") as fh:
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
        fh.seek(max(0, size - max_bytes))
        data = fh.read().decode("utf-8", errors="ignore")
    return strip_ansi(data)


def read_text_delta(path: Path, start_offset: int, max_bytes: int = 32768) -> tuple[int, str]:
    if not path.exists():
        return (start_offset, "")
    with path.open("rb") as fh:
        fh.seek(0, os.SEEK_END)
        end_offset = fh.tell()
        fh.seek(min(start_offset, end_offset))
        data = fh.read(max_bytes).decode("utf-8", errors="ignore")
    return (end_offset, strip_ansi(data))


NOISE_LINE_PATTERNS = [
    re.compile(r"^[─━]{8,}$"),
    re.compile(r"^⏵⏵"),
    re.compile(r"^❯$"),
    re.compile(r"^\d+[smh](?:\s*·.*)?$"),
    re.compile(r"^\+\d+ more tool uses"),
    re.compile(r"^ctrl\+[a-z]", flags=re.IGNORECASE),
    re.compile(r"^Wait$", flags=re.IGNORECASE),
    re.compile(r"^Running…?$", flags=re.IGNORECASE),
]
NOISE_SUBSTRINGS = [
    "fluttering…",
    "gallivanting…",
    "pondering…",
    "thought for",
    "tip: use /btw",
    "tip:use/btw",
    "current work",
    "currentwork",
    "you've used 90% of your weekly limit",
    "bypasspermissionson(shift+tabtocycle)",
    "ctrl+b to run in background",
    "ctrl+btoruninbackground",
    "ctrl+o to expand",
    "checkingforupdates",
]


def is_exit_confirmation_text(text: str) -> bool:
    lowered = strip_ansi(text).lower()
    compacted = "".join(lowered.split())
    return "pressctrl-cagaintoexit" in compacted


def normalize_progress_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in strip_ansi(text).replace("\r", "\n").splitlines():
        line = " ".join(raw.split())
        if not line:
            continue
        lowered = line.lower()
        collapsed = lowered.replace(" ", "")
        if not re.search(r"[A-Za-z\u4e00-\u9fff]", line):
            continue
        if any(pattern.match(line) for pattern in NOISE_LINE_PATTERNS):
            continue
        if is_exit_confirmation_text(line):
            continue
        if any(token in collapsed or token in lowered for token in NOISE_SUBSTRINGS):
            continue
        lines.append(line)
    return lines


def extract_progress_excerpt(text: str, limit: int = 260) -> str:
    lines = normalize_progress_lines(text)
    if not lines:
        return ""
    return compact(" | ".join(lines[-3:]), limit=limit)


def infer_stage_from_excerpt(excerpt: str) -> str | None:
    lowered = excerpt.lower()
    if "step 1" in lowered or "确定目标story" in excerpt:
        return "step-1-target-selection"
    if "step 2" in lowered or "加载并分析核心构件" in excerpt:
        return "step-2-context-loading"
    if "step 3" in lowered:
        return "step-3"
    if "step 4" in lowered:
        return "step-4"
    if "step 5" in lowered or "生成 story文件" in lowered or "template-output:" in lowered:
        return "step-5-story-generation"
    if "successfullyloadedskill" in lowered or "skill(/bmad" in lowered:
        return "workflow-skill-loaded"
    if "resume this session with:" in lowered:
        return "session-ended"
    return None


def extract_resume_id(text: str) -> str | None:
    match = re.search(r"claude\s+--resume\s+([a-f0-9-]{8,})", text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def classify_transcript_tail(text: str) -> str:
    lowered = text.lower()
    if "bypass permissions mode" in lowered and "yes, i accept" in lowered:
        return "bypass-warning"
    if "bash command" in lowered and "do you want to proceed" in lowered:
        return "bash-approval"
    if "template-output:" in lowered or "生成 story文件" in lowered:
        return "story-generation"
    if "resume this session with" in lowered:
        return "resume-offered"
    if "ctrl+g to edit in vim" in lowered or "claude code" in lowered:
        return "claude-ui"
    if text.strip():
        return "unknown-ui"
    return "no-output"


def write_summary(handle, summary: dict[str, Any]) -> None:
    handle.summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_user_update(handle, *, final_state: str, summary: dict[str, Any]) -> Path:
    probe = summary.get("artifactProbe") or {}
    evidence = probe.get("evidence") or {}

    status_cn = {
        "completed": "完成",
        "failed": "失败",
        "stuck": "卡住",
        "orphaned": "孤儿会话",
        "cancelled": "取消",
        "needs_input": "需要交互",
    }.get(final_state, final_state)

    lines = [f"状态：{status_cn}"]
    if summary.get("workflow"):
        lines.append(f"workflow：{summary.get('workflow')}")
    if summary.get("storyId"):
        lines.append(f"story：{summary.get('storyId')}")
    if evidence.get("sprintStatus"):
        lines.append(f"sprint-status：{evidence.get('sprintStatus')}")
    if evidence.get("storyStatus"):
        lines.append(f"story 状态：{evidence.get('storyStatus')}")
    if summary.get("stage"):
        lines.append(f"阶段：{summary.get('stage')}")
    if summary.get("progressExcerpt"):
        lines.append(f"进展：{summary.get('progressExcerpt')}")

    if final_state == "completed":
        lines.append("结论：产物判定通过，可进入下一工作流。")
    elif final_state == "needs_input":
        lines.append("结论：Claude 正在等待输入，请根据进展自主决策并恢复运行。")
    elif final_state in {"stuck", "failed", "orphaned"}:
        lines.append("结论：运行未成功收口，建议查看 summary.json / events.jsonl 再决定恢复或重跑。")

    if summary.get("resumeId"):
        lines.append(f"resumeId：{summary.get('resumeId')}")
    if summary.get("recoveryHint"):
        lines.append(f"恢复命令：{summary.get('recoveryHint')}")

    out_path = handle.run_dir / "user-update.txt"
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out_path


def maybe_dispatch_update(args: argparse.Namespace, run_dir: Path) -> dict[str, Any] | None:
    if not args.notify_final_update:
        return None
    if not args.notify_account or not args.notify_target:
        return {
            "dispatched": False,
            "reason": "missing-notify-target",
        }

    dispatcher = Path(__file__).resolve().parent / "claude_dispatch_update.py"
    cmd = [
        sys.executable,
        str(dispatcher),
        "--run-dir",
        str(run_dir),
        "--notify-account",
        args.notify_account,
        "--notify-target",
        args.notify_target,
    ]
    if args.notify_channel:
        cmd += ["--notify-channel", args.notify_channel]
    if args.notify_dry_run:
        cmd += ["--dry-run"]

    result = subprocess.run(cmd, text=True, capture_output=True)
    return {
        "dispatched": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
        "dryRun": bool(args.notify_dry_run),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Event-driven Claude Code orchestrator with run registry, auto-approval policy, and artifact probes")
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--story-id")
    parser.add_argument("--story-path")
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--profile")
    parser.add_argument("--profiles-file")
    parser.add_argument("--permission-mode")
    parser.add_argument("--allowedTools", dest="allowed_tools")
    parser.add_argument("--append-system-prompt")
    parser.add_argument("--system-prompt")
    parser.add_argument("--resume")
    parser.add_argument("--install-hooks", action="store_true")
    parser.add_argument("--event-log-file")
    parser.add_argument("--idle-timeout-s", type=int)
    parser.add_argument("--startup-timeout-s", type=int)
    parser.add_argument("--probe-interval-s", type=int)
    parser.add_argument("--auto-accept-bypass-warning", action="store_true")
    parser.add_argument("--auto-approve-bash", action="store_true")
    parser.add_argument("--auto-approve-bash-option", type=int, choices=[1, 2], default=None)
    parser.add_argument("--stop-on-artifact-complete", action="store_true")
    parser.add_argument("--notify-account")
    parser.add_argument("--notify-target")
    parser.add_argument("--notify-parent-session")
    parser.add_argument("--notify-channel")
    parser.add_argument("--notify-dry-run", action="store_true")
    parser.add_argument("--notify-final-update", action="store_true")
    parser.add_argument("--claude-bin", default=os.environ.get("CLAUDE_CODE_BIN", "claude"))
    parser.add_argument("extra", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    extra = args.extra or []
    if extra and extra[0] == "--":
        extra = extra[1:]
    args.extra = extra
    return args


def main() -> int:
    args = parse_args()
    cwd = Path(args.cwd).resolve()
    prompt = load_prompt(args.prompt, args.prompt_file)
    profiles_file = Path(args.profiles_file).resolve() if args.profiles_file else default_profiles_file().resolve()
    profile_name, profile = load_profile(profiles_file, args.profile)
    workflow_cfg = load_workflow_config(profiles_file, args.workflow)

    permission_mode = args.permission_mode or str(profile.get("permission_mode") or "acceptEdits")
    auto_accept_bypass = bool(args.auto_accept_bypass_warning or profile.get("auto_accept_bypass_warning"))
    auto_approve_bash = bool(args.auto_approve_bash or profile.get("auto_approve_bash"))
    auto_approve_bash_option = int(args.auto_approve_bash_option or profile.get("auto_approve_bash_option") or 2)
    idle_timeout_s = int(args.idle_timeout_s or workflow_cfg.get("idle_timeout_s") or profile.get("idle_timeout_s") or 120)
    startup_timeout_s = int(args.startup_timeout_s or workflow_cfg.get("startup_timeout_s") or profile.get("startup_timeout_s") or 30)
    probe_interval_s = int(args.probe_interval_s or workflow_cfg.get("probe_interval_s") or profile.get("probe_interval_s") or 15)
    install_hooks = bool(args.install_hooks or profile.get("install_hooks"))
    force_single_run = bool(profile.get("force_single_run", True))
    checkpoint_required = bool(workflow_cfg.get("checkpoint_required"))
    progress_strategy = str(workflow_cfg.get("progress_strategy") or "balanced").strip().lower()

    registry = RunRegistry(cwd / ".claude" / "orchestrator")
    effective_event_log = Path(args.event_log_file).resolve() if args.event_log_file else (cwd / ".claude" / "events" / "claude-events.jsonl")
    preflight_reconciled = reconcile_existing_runs(registry, idle_timeout_s)
    lock_metadata = {
        "repo": str(cwd),
        "workflow": args.workflow,
        "storyId": args.story_id,
        "profile": profile_name,
    }
    lock_path = registry.acquire_repo_lock(cwd, lock_metadata, replace_stale=True)
    handle = registry.create_run(
        repo=cwd,
        workflow=args.workflow,
        metadata={
            "profile": profile_name,
            "storyId": args.story_id,
            "storyPath": str(Path(args.story_path).resolve()) if args.story_path else None,
            "permissionMode": permission_mode,
            "profilesFile": str(profiles_file),
        },
        lock_path=lock_path,
    )

    workflow_context = build_workflow_context(
        repo=cwd,
        workflow=args.workflow,
        story_id=args.story_id,
        story_path=args.story_path,
        run_dir=handle.run_dir,
    )
    context_file = write_context_file(handle.run_dir, workflow_context)
    checkpoint_script = Path(__file__).resolve().parent / "claude_checkpoint.py"
    effective_prompt = inject_adapter_instructions(prompt, workflow_context, checkpoint_script, handle.run_dir)

    original_prompt_file = handle.run_dir / "prompt.original.txt"
    original_prompt_file.write_text(prompt, encoding="utf-8")
    prompt_file_in_run = handle.run_dir / "prompt.txt"
    prompt_file_in_run.write_text(effective_prompt, encoding="utf-8")
    registry.patch_state(
        handle,
        promptFile=str(prompt_file_in_run),
        originalPromptFile=str(original_prompt_file),
        workflowContextFile=str(context_file),
        expectedArtifacts=workflow_context.get("expectedArtifacts") or [],
        checkpointRequired=checkpoint_required,
        progressStrategy=progress_strategy,
    )
    registry.append_event(handle, "workflow_context_prepared", workflowContext=workflow_context)
    if args.workflow == "bmad-bmm-create-story":
        try:
            write_checkpoint(
                run_dir=handle.run_dir,
                workflow=args.workflow,
                story_id=args.story_id,
                stage="target-selected",
                message="已确认目标 story 并准备 create-story 上下文",
                expected_artifacts=workflow_context.get("expectedArtifacts") or [],
                details={
                    "storyPath": workflow_context.get("storyPath"),
                    "sprintStatus": workflow_context.get("sprintStatus"),
                },
            )
        except Exception as exc:
            registry.append_event(handle, "checkpoint_write_failed", stage="target-selected", error=str(exc))
    if preflight_reconciled:
        registry.append_event(handle, "preflight_reconcile", reconciled=preflight_reconciled)

    try:
        if install_hooks:
            maybe_install_hooks(cwd, effective_event_log)
            registry.append_event(handle, "hooks_installed", eventLogFile=str(effective_event_log))

        cmd = build_command(args, permission_mode)
        registry.transition(handle, "launching", command=cmd)
        if args.workflow == "bmad-bmm-create-story":
            try:
                write_checkpoint(
                    run_dir=handle.run_dir,
                    workflow=args.workflow,
                    story_id=args.story_id,
                    stage="context-loaded",
                    message="workflow adapter 上下文已加载，准备启动 Claude",
                    expected_artifacts=workflow_context.get("expectedArtifacts") or [],
                    details={"workflowContextFile": str(context_file)},
                )
            except Exception as exc:
                registry.append_event(handle, "checkpoint_write_failed", stage="context-loaded", error=str(exc))

        with handle.transcript_path.open("a", encoding="utf-8") as transcript:
            transcript.write("$ " + " ".join(shlex.quote(part) for part in cmd) + "\n")
            transcript.flush()

            child_env = build_child_env(
                run_dir=handle.run_dir,
                workflow=args.workflow,
                story_id=args.story_id,
                context_file=context_file,
            )
            child = pexpect.spawn(
                cmd[0],
                cmd[1:],
                cwd=str(cwd),
                env=child_env,
                encoding="utf-8",
                codec_errors="ignore",
                timeout=1,
                echo=False,
            )
            child.logfile = transcript
            registry.patch_state(handle, childPid=child.pid, eventLogFile=str(effective_event_log))
            registry.append_event(handle, "child_spawned", childPid=child.pid)

            start_ts = time.monotonic()
            last_progress = start_ts
            last_probe = 0.0
            last_transcript_size = handle.transcript_path.stat().st_size if handle.transcript_path.exists() else 0
            last_event_log_size = effective_event_log.stat().st_size if effective_event_log.exists() else 0
            current_checkpoint = load_checkpoint(handle.run_dir)
            last_checkpoint_ts = str(current_checkpoint.get("updatedAt") or "")
            last_emitted_stage = str(current_checkpoint.get("stage") or "")
            expected_artifacts = list(workflow_context.get("expectedArtifacts") or [])
            target_story_path = str(Path(workflow_context.get("storyPath") or "").resolve()) if workflow_context.get("storyPath") else None
            sprint_status_path = str((cwd / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml").resolve())
            last_artifact_snapshot = artifact_snapshot(expected_artifacts)
            prompt_sent = False
            prompt_submit_attempts = 0
            artifact_complete = False
            artifact_result: dict[str, Any] | None = None
            artifact_exit_requested_at: float | None = None
            artifact_exit_confirmed = False
            exit_code: int | None = None
            bypass_warning_seen = False
            bypass_confirmation_done = True
            trust_folder_seen = False
            trust_confirmation_done = True

            patterns = [
                pexpect.EOF,
                pexpect.TIMEOUT,
                "WARNING: Claude Code running in Bypass Permissions mode",
                "Yes, I trust this folder",
                "Do you want to proceed?",
                "Bash command",
                "❯",
                "TaskCompleted",
                "SessionEnd",
            ]

            while True:
                idx = child.expect(patterns, timeout=1)
                observed = ""
                if idx not in {0, 1}:
                    observed = (child.before or "") + (child.after or "")
                    last_progress = time.monotonic()
                    registry.heartbeat(handle, lastSeen=compact(observed), pid=child.pid)

                if idx == 0:  # EOF
                    exit_code = child.exitstatus if child.exitstatus is not None else child.signalstatus
                    break

                if idx == 1:  # TIMEOUT
                    now = time.monotonic()

                    transcript_size = handle.transcript_path.stat().st_size if handle.transcript_path.exists() else 0
                    if transcript_size > last_transcript_size:
                        last_transcript_size, transcript_delta = read_text_delta(handle.transcript_path, last_transcript_size)
                        progress_excerpt = extract_progress_excerpt(transcript_delta)
                        stage = infer_stage_from_excerpt(progress_excerpt) if progress_excerpt else None
                        if progress_excerpt:
                            transcript_counts_as_progress = True
                            if progress_strategy == "checkpoint-first" and not stage:
                                transcript_counts_as_progress = False
                            if transcript_counts_as_progress:
                                last_progress = now
                                heartbeat_payload: dict[str, Any] = {
                                    "source": "transcript-growth",
                                    "transcriptSize": transcript_size,
                                    "pid": child.pid,
                                    "lastSeen": progress_excerpt,
                                    "progressExcerpt": progress_excerpt,
                                }
                                if stage:
                                    heartbeat_payload["stage"] = stage
                                registry.heartbeat(handle, **heartbeat_payload)
                            else:
                                registry.append_event(
                                    handle,
                                    "transcript_signal_ignored",
                                    reason="checkpoint-first-without-stage",
                                    excerpt=progress_excerpt,
                                )

                    event_log_size = effective_event_log.stat().st_size if effective_event_log.exists() else 0
                    if event_log_size > last_event_log_size:
                        last_event_log_size, event_delta = read_text_delta(effective_event_log, last_event_log_size)
                        last_progress = now
                        registry.heartbeat(handle, source="hook-log-growth", eventLogSize=last_event_log_size, pid=child.pid)
                        if "waiting for your input" in event_delta:
                            latest_probe_for_input = probe_completion(
                                repo=cwd,
                                workflow=args.workflow,
                                story_id=args.story_id,
                                story_path=Path(args.story_path).resolve() if args.story_path else None,
                                profiles_file=profiles_file,
                            )
                            completed_enough = bool(latest_probe_for_input.get("complete"))
                            evidence = latest_probe_for_input.get("evidence") or {}
                            story_status_now = evidence.get("storyStatus")
                            sprint_status_now = evidence.get("sprintStatus")
                            if completed_enough or (args.workflow == "bmad-bmm-create-story" and (
                                story_status_now in {"ready-for-dev", "in-progress", "review", "done"} or sprint_status_now in {"ready-for-dev", "in-progress", "review", "done"}
                            )):
                                artifact_result = latest_probe_for_input
                                artifact_complete = True
                                registry.append_event(handle, "waiting_for_input_after_artifact_completion", via="hook-event", probe=latest_probe_for_input)
                                child.sendcontrol("c")
                                child.sendcontrol("c")
                                exit_code = 0
                                break
                            registry.append_event(handle, "waiting_for_input_detected", via="hook-event")
                            registry.transition(handle, "needs_input", reason="claude-waiting-for-input")
                            child.sendcontrol("c")
                            child.sendcontrol("c")
                            exit_code = 0
                            break

                    checkpoint = load_checkpoint(handle.run_dir)
                    checkpoint_ts = str(checkpoint.get("updatedAt") or "")
                    if checkpoint_ts and checkpoint_ts != last_checkpoint_ts:
                        last_checkpoint_ts = checkpoint_ts
                        current_checkpoint = checkpoint
                        if checkpoint.get("stage"):
                            last_emitted_stage = str(checkpoint.get("stage"))
                        expected_artifacts = list(dict.fromkeys([*expected_artifacts, *(checkpoint.get("expectedArtifacts") or [])]))
                        last_progress = now
                        registry.heartbeat(
                            handle,
                            source="checkpoint",
                            pid=child.pid,
                            stage=checkpoint.get("stage"),
                            progressExcerpt=compact(f"{checkpoint.get('stage')}: {checkpoint.get('message')}", limit=240),
                            checkpointTs=checkpoint_ts,
                            expectedArtifacts=expected_artifacts,
                        )

                    current_snapshot = artifact_snapshot(expected_artifacts)
                    changed_artifacts = artifact_snapshot_changed(last_artifact_snapshot, current_snapshot)
                    if changed_artifacts:
                        last_artifact_snapshot = current_snapshot
                        last_progress = now
                        registry.heartbeat(
                            handle,
                            source="artifact-change",
                            pid=child.pid,
                            changedArtifacts=changed_artifacts[:8],
                            artifactCount=len(changed_artifacts),
                            expectedArtifacts=expected_artifacts,
                        )
                        if args.workflow == "bmad-bmm-create-story":
                            try:
                                if target_story_path and target_story_path in changed_artifacts and last_emitted_stage != "story-file-written":
                                    write_checkpoint(
                                        run_dir=handle.run_dir,
                                        workflow=args.workflow,
                                        story_id=args.story_id,
                                        stage="story-file-written",
                                        message="检测到目标 story 文件已写入或更新",
                                        expected_artifacts=expected_artifacts,
                                        details={"path": target_story_path},
                                    )
                                    last_emitted_stage = "story-file-written"
                                if sprint_status_path in changed_artifacts:
                                    sprint_status = read_sprint_status(cwd, args.story_id)
                                    if sprint_status in {"ready-for-dev", "in-progress", "review", "done"} and last_emitted_stage != "sprint-status-updated":
                                        write_checkpoint(
                                            run_dir=handle.run_dir,
                                            workflow=args.workflow,
                                            story_id=args.story_id,
                                            stage="sprint-status-updated",
                                            message=f"sprint-status 已推进到 {sprint_status}",
                                            expected_artifacts=expected_artifacts,
                                            details={"sprintStatus": sprint_status},
                                        )
                                        last_emitted_stage = "sprint-status-updated"
                            except Exception as exc:
                                registry.append_event(handle, "checkpoint_write_failed", stage="artifact-driven", error=str(exc))

                    transcript_tail = read_tail_text(handle.transcript_path)
                    if artifact_complete:
                        if is_exit_confirmation_text(transcript_tail) and not artifact_exit_confirmed:
                            child.sendcontrol("c")
                            artifact_exit_confirmed = True
                            artifact_exit_requested_at = now
                            registry.append_event(handle, "artifact_complete_exit_confirmed", via="transcript-tail")
                            continue
                        if artifact_exit_requested_at and now - artifact_exit_requested_at > 5 and child.isalive():
                            registry.append_event(handle, "artifact_complete_force_terminate", graceSeconds=5)
                            child.terminate(force=True)
                            exit_code = 0
                            break

                    if (
                        auto_accept_bypass
                        and "Bypass Permissions mode" in transcript_tail
                        and "Yes, I accept" in transcript_tail
                        and not bypass_confirmation_done
                    ):
                        select_menu_option(child, 2)
                        bypass_confirmation_done = True
                        last_progress = now
                        registry.append_event(handle, "bypass_warning_accepted", option=2, via="transcript-tail")
                        registry.transition(handle, "launching", reason="bypass-warning-accepted")
                        continue

                    if (
                        auto_accept_bypass
                        and "Yes, I trust this folder" in transcript_tail
                        and "No, exit" in transcript_tail
                        and not trust_confirmation_done
                    ):
                        select_menu_option(child, 1)
                        trust_confirmation_done = True
                        last_progress = now
                        registry.append_event(handle, "workspace_trust_accepted", option=1, via="transcript-tail")
                        registry.transition(handle, "launching", reason="workspace-trust-accepted")
                        continue

                    if (
                        auto_approve_bash
                        and "Do you want to proceed?" in transcript_tail
                        and "Bash command" in transcript_tail
                    ):
                        select_menu_option(child, auto_approve_bash_option)
                        last_progress = now
                        registry.append_event(handle, "bash_approval_auto_accepted", option=auto_approve_bash_option, via="transcript-tail")
                        registry.transition(handle, "running", reason="approval-auto-accepted")
                        continue

                    if prompt_sent and prompt_submit_attempts < 3:
                        needs_resubmit = (
                            "[Pasted text" in transcript_tail
                            or "Pasted text" in transcript_tail
                        )
                        if needs_resubmit and now - last_progress > 8:
                            submit_prompt(child)
                            prompt_submit_attempts += 1
                            last_progress = now
                            registry.append_event(handle, "prompt_resubmitted", attempt=prompt_submit_attempts, via="transcript-tail")
                            continue

                    if child.isalive() is False:
                        exit_code = child.exitstatus if child.exitstatus is not None else child.signalstatus
                        registry.append_event(handle, "child_not_alive_on_timeout", exitCode=exit_code)
                        break

                    if not prompt_sent and now - start_ts > startup_timeout_s:
                        registry.transition(handle, "stuck", reason="startup-timeout")
                        child.terminate(force=True)
                        exit_code = 124
                        break

                    if prompt_sent and now - last_progress > idle_timeout_s:
                        artifact_result = probe_completion(
                            repo=cwd,
                            workflow=args.workflow,
                            story_id=args.story_id,
                            story_path=Path(args.story_path).resolve() if args.story_path else None,
                            profiles_file=profiles_file,
                        )
                        registry.append_event(handle, "artifact_probe", result=artifact_result)
                        if artifact_result.get("complete") and args.stop_on_artifact_complete:
                            artifact_complete = True
                            artifact_exit_requested_at = now
                            registry.transition(handle, "verifying", reason="artifact-complete")
                            registry.append_event(handle, "artifact_complete_stop_requested", via="artifact-probe")
                            child.sendcontrol("c")
                            last_progress = now
                            continue

                        if now - last_progress > idle_timeout_s:
                            registry.transition(handle, "stuck", reason="idle-timeout")
                            child.terminate(force=True)
                            exit_code = 124
                            break

                    if now - last_probe > probe_interval_s:
                        last_probe = now
                        artifact_result = probe_completion(
                            repo=cwd,
                            workflow=args.workflow,
                            story_id=args.story_id,
                            story_path=Path(args.story_path).resolve() if args.story_path else None,
                            profiles_file=profiles_file,
                        )
                        registry.append_event(handle, "artifact_probe", result=artifact_result)
                        if artifact_result.get("complete"):
                            artifact_complete = True
                    continue

                if idx == 2:  # bypass warning
                    bypass_warning_seen = True
                    bypass_confirmation_done = False
                    registry.transition(handle, "waiting_start_confirmation", reason="bypass-warning")
                    registry.append_event(handle, "bypass_warning_detected")
                    if auto_accept_bypass:
                        select_menu_option(child, 2)
                        bypass_confirmation_done = True
                        registry.append_event(handle, "bypass_warning_accepted", option=2)
                        registry.transition(handle, "launching", reason="bypass-warning-accepted")
                        last_progress = time.monotonic()
                    continue

                if idx == 3:  # trust folder prompt
                    trust_folder_seen = True
                    trust_confirmation_done = False
                    registry.transition(handle, "waiting_start_confirmation", reason="workspace-trust")
                    registry.append_event(handle, "workspace_trust_detected")
                    if auto_accept_bypass:
                        select_menu_option(child, 1)
                        trust_confirmation_done = True
                        registry.append_event(handle, "workspace_trust_accepted", option=1)
                        registry.transition(handle, "launching", reason="workspace-trust-accepted")
                        last_progress = time.monotonic()
                    continue

                if idx == 4:  # approval screen
                    registry.transition(handle, "needs_approval", reason="bash-approval")
                    registry.append_event(handle, "bash_approval_detected")
                    if auto_approve_bash:
                        select_menu_option(child, auto_approve_bash_option)
                        registry.append_event(handle, "bash_approval_auto_accepted", option=auto_approve_bash_option)
                        registry.transition(handle, "running", reason="approval-auto-accepted")
                        last_progress = time.monotonic()
                    continue

                if idx == 5:  # bash command header
                    registry.append_event(handle, "bash_command_seen")
                    continue

                if idx == 6:  # prompt marker
                    if not prompt_sent:
                        if bypass_warning_seen and not bypass_confirmation_done:
                            registry.transition(handle, "waiting_start_confirmation", reason="prompt-seen-before-bypass-confirm")
                            if auto_accept_bypass:
                                select_menu_option(child, 2)
                                bypass_confirmation_done = True
                                registry.append_event(handle, "bypass_warning_accepted", option=2, via="prompt-marker")
                                registry.transition(handle, "launching", reason="bypass-warning-accepted")
                                last_progress = time.monotonic()
                            continue

                        if trust_folder_seen and not trust_confirmation_done:
                            registry.transition(handle, "waiting_start_confirmation", reason="prompt-seen-before-trust-confirm")
                            if auto_accept_bypass:
                                select_menu_option(child, 1)
                                trust_confirmation_done = True
                                registry.append_event(handle, "workspace_trust_accepted", option=1, via="prompt-marker")
                                registry.transition(handle, "launching", reason="workspace-trust-accepted")
                                last_progress = time.monotonic()
                            continue

                        registry.transition(handle, "ready_for_prompt")
                        send_prompt(child, effective_prompt)
                        submit_prompt(child)
                        prompt_sent = True
                        prompt_submit_attempts = 1
                        registry.transition(handle, "prompt_submitted", promptPreview=compact(effective_prompt, limit=120), submitAttempts=prompt_submit_attempts)
                        registry.transition(handle, "running")
                        registry.append_event(handle, "prompt_submitted", submitAttempts=prompt_submit_attempts)
                        if args.workflow == "bmad-bmm-create-story" and last_emitted_stage != "drafting-started":
                            try:
                                write_checkpoint(
                                    run_dir=handle.run_dir,
                                    workflow=args.workflow,
                                    story_id=args.story_id,
                                    stage="drafting-started",
                                    message="已提交 create-story prompt，进入草稿生成阶段",
                                    expected_artifacts=expected_artifacts,
                                )
                                last_emitted_stage = "drafting-started"
                            except Exception as exc:
                                registry.append_event(handle, "checkpoint_write_failed", stage="drafting-started", error=str(exc))
                        last_progress = time.monotonic()
                    else:
                        # Prompt was already sent. If we see the prompt marker again and it's been a few seconds,
                        # Claude Code is likely waiting for human (or Operator) input.
                        # For create-story, if artifacts are already effectively complete, finalize instead of marking needs_input.
                        if time.monotonic() - last_progress > 5:
                            latest_probe_for_prompt = probe_completion(
                                repo=cwd,
                                workflow=args.workflow,
                                story_id=args.story_id,
                                story_path=Path(args.story_path).resolve() if args.story_path else None,
                                profiles_file=profiles_file,
                            )
                            completed_enough = bool(latest_probe_for_prompt.get("complete"))
                            evidence = latest_probe_for_prompt.get("evidence") or {}
                            story_status_now = evidence.get("storyStatus")
                            sprint_status_now = evidence.get("sprintStatus")
                            if completed_enough or (args.workflow == "bmad-bmm-create-story" and (
                                story_status_now in {"ready-for-dev", "in-progress", "review", "done"} or sprint_status_now in {"ready-for-dev", "in-progress", "review", "done"}
                            )):
                                artifact_result = latest_probe_for_prompt
                                artifact_complete = True
                                registry.append_event(handle, "prompt_marker_after_artifact_completion", via="prompt-marker", probe=latest_probe_for_prompt)
                                child.sendcontrol("c")
                                child.sendcontrol("c")
                                exit_code = 0
                                break
                            registry.append_event(handle, "waiting_for_input_detected", via="prompt-marker")
                            registry.transition(handle, "needs_input", reason="claude-waiting-for-prompt")
                            child.sendcontrol("c")
                            child.sendcontrol("c")
                            exit_code = 0
                            break
                    continue

                if idx in {7, 8}:
                    registry.append_event(handle, "claude_terminal_event", name=patterns[idx])
                    last_progress = time.monotonic()
                    continue

        final_probe = artifact_result or probe_completion(
            repo=cwd,
            workflow=args.workflow,
            story_id=args.story_id,
            story_path=Path(args.story_path).resolve() if args.story_path else None,
            profiles_file=profiles_file,
        )
        state = registry.load_state(handle).get("state")
        
        if state == "needs_input":
            terminal_state = "needs_input"
        elif exit_code == 0 and state not in {"stuck", "failed", "cancelled", "orphaned"}:
            terminal_state = "completed"
        else:
            terminal_state = state if state in {"stuck", "failed", "cancelled", "orphaned"} else "failed"
            
        final_state = "completed" if (final_probe.get("complete") or artifact_complete) else terminal_state
        if state == "needs_input" and not (final_probe.get("complete") or artifact_complete):
            final_state = "needs_input"

        if args.workflow == "bmad-bmm-create-story" and last_emitted_stage != "workflow-completed":
            checkpoint_complete = bool(final_probe.get("complete") or artifact_complete)
            story_status_now = (final_probe.get("evidence") or {}).get("storyStatus")
            sprint_status_now = (final_probe.get("evidence") or {}).get("sprintStatus")
            if checkpoint_complete or story_status_now in {"ready-for-dev", "in-progress", "review", "done"} or sprint_status_now in {"ready-for-dev", "in-progress", "review", "done"}:
                try:
                    write_checkpoint(
                        run_dir=handle.run_dir,
                        workflow=args.workflow,
                        story_id=args.story_id,
                        stage="workflow-completed",
                        message="create-story 工作流已完成，Story 已具备完整开发者上下文",
                        expected_artifacts=expected_artifacts,
                    )
                    last_emitted_stage = "workflow-completed"
                except Exception as exc:
                    registry.append_event(handle, "checkpoint_write_failed", stage="workflow-completed", error=str(exc))

        transcript_tail = read_tail_text(handle.transcript_path, max_bytes=6000)
        resume_id = extract_resume_id(transcript_tail)
        ui_state = classify_transcript_tail(transcript_tail)

        current_state = registry.load_state(handle)
        final_checkpoint = load_checkpoint(handle.run_dir)
        summary = {
            "runId": handle.run_id,
            "workflow": args.workflow,
            "storyId": args.story_id,
            "repo": str(cwd),
            "permissionMode": permission_mode,
            "profile": profile_name,
            "exitCode": exit_code,
            "finalState": final_state,
            "artifactComplete": bool(final_probe.get("complete")),
            "artifactProbe": final_probe,
            "promptFile": str(prompt_file_in_run),
            "originalPromptFile": str(original_prompt_file),
            "workflowContextFile": str(context_file),
            "resumeId": resume_id,
            "uiState": ui_state,
            "promptSubmitAttempts": prompt_submit_attempts,
            "stage": current_state.get("stage"),
            "progressExcerpt": current_state.get("progressExcerpt"),
            "checkpointTs": current_state.get("checkpointTs") or final_checkpoint.get("updatedAt"),
            "checkpoint": final_checkpoint,
            "expectedArtifacts": expected_artifacts,
            "checkpointRequired": checkpoint_required,
            "progressStrategy": progress_strategy,
        }
        summary["recoveryHint"] = f"python3 scripts/ops/claude_recover_run.py --run-dir {handle.run_dir} --execute"
        user_update_file = write_user_update(handle, final_state=final_state, summary=summary)
        summary["userUpdateFile"] = str(user_update_file)
        dispatch_result = maybe_dispatch_update(args, handle.run_dir)
        if dispatch_result is not None:
            summary["dispatchResult"] = dispatch_result
        write_summary(handle, summary)

        registry.finalize(handle, state=final_state, exit_code=exit_code, summary=summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if final_state == "completed" else int(exit_code or 1)

    except Exception as exc:
        registry.append_event(handle, "orchestrator_exception", error=str(exc))
        summary = {
            "runId": handle.run_id,
            "workflow": args.workflow,
            "storyId": args.story_id,
            "repo": str(cwd),
            "error": str(exc),
        }
        write_summary(handle, summary)
        registry.finalize(handle, state="failed", exit_code=1, summary=summary)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
