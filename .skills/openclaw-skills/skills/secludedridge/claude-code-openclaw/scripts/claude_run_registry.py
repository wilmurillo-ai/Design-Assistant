#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TERMINAL_STATES = {"completed", "failed", "cancelled", "stuck", "orphaned", "needs_input"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return cleaned.strip("-._") or "run"


def pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


@dataclass
class RunHandle:
    run_id: str
    run_dir: Path
    lock_path: Path
    state_path: Path
    events_path: Path
    transcript_path: Path
    summary_path: Path


class RunRegistry:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.runs_dir = self.base_dir / "runs"
        self.locks_dir = self.base_dir / "locks"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.locks_dir.mkdir(parents=True, exist_ok=True)

    def load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default

    def _repo_lock_path(self, repo: str | Path) -> Path:
        repo_key = _sanitize(str(Path(repo).resolve()))
        return self.locks_dir / f"{repo_key}.lock.json"

    def repo_lock_path(self, repo: str | Path) -> Path:
        return self._repo_lock_path(repo)

    def acquire_repo_lock(self, repo: str | Path, metadata: dict[str, Any], *, replace_stale: bool = True) -> Path:
        path = self._repo_lock_path(repo)
        if path.exists():
            current = self.load_json(path, {})
            if pid_alive(int(current.get("pid") or 0)):
                raise RuntimeError(f"active run lock exists: {path}")
            if replace_stale:
                path.unlink(missing_ok=True)
        lock_record = {
            "ts": utc_now(),
            "pid": os.getpid(),
            **metadata,
        }
        path.write_text(json.dumps(lock_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def release_lock(self, lock_path: Path) -> None:
        lock_path.unlink(missing_ok=True)

    def open_run(self, run_dir: str | Path, lock_path: Path | None = None) -> RunHandle:
        run_dir = Path(run_dir).resolve()
        return RunHandle(
            run_id=run_dir.name,
            run_dir=run_dir,
            lock_path=lock_path or Path(),
            state_path=run_dir / "state.json",
            events_path=run_dir / "events.jsonl",
            transcript_path=run_dir / "transcript.log",
            summary_path=run_dir / "summary.json",
        )

    def create_run(self, *, repo: str | Path, workflow: str, metadata: dict[str, Any], lock_path: Path) -> RunHandle:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_id = f"{ts}-{_sanitize(workflow)}"
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        handle = RunHandle(
            run_id=run_id,
            run_dir=run_dir,
            lock_path=lock_path,
            state_path=run_dir / "state.json",
            events_path=run_dir / "events.jsonl",
            transcript_path=run_dir / "transcript.log",
            summary_path=run_dir / "summary.json",
        )

        state = {
            "runId": run_id,
            "repo": str(Path(repo).resolve()),
            "workflow": workflow,
            "createdAt": utc_now(),
            "updatedAt": utc_now(),
            "state": "created",
            "pid": os.getpid(),
            "lastProgressAt": None,
            **metadata,
        }
        self.write_state(handle, state)
        self.append_event(handle, "run_registered", state="created", metadata=metadata)
        return handle

    def write_state(self, handle: RunHandle, state: dict[str, Any]) -> None:
        state["updatedAt"] = utc_now()
        handle.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def load_state(self, handle: RunHandle) -> dict[str, Any]:
        return self.load_json(handle.state_path, {})

    def patch_state(self, handle: RunHandle, **changes: Any) -> dict[str, Any]:
        state = self.load_state(handle)
        state.update(changes)
        self.write_state(handle, state)
        return state

    def transition(self, handle: RunHandle, new_state: str, **extra: Any) -> dict[str, Any]:
        state = self.patch_state(handle, state=new_state, **extra)
        self.append_event(handle, "state_changed", state=new_state, extra=extra)
        return state

    def append_event(self, handle: RunHandle, event: str, **payload: Any) -> None:
        record = {
            "ts": utc_now(),
            "event": event,
            **payload,
        }
        with handle.events_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def heartbeat(self, handle: RunHandle, **payload: Any) -> dict[str, Any]:
        now = utc_now()
        source = payload.get("source")
        changes = {"lastProgressAt": now, **payload}
        if source:
            changes["lastProgressSource"] = source
        state = self.patch_state(handle, **changes)
        self.append_event(handle, "heartbeat", **payload)
        return state

    def finalize(self, handle: RunHandle, *, state: str, exit_code: int | None = None, summary: dict[str, Any] | None = None) -> None:
        self.transition(handle, state, exitCode=exit_code, finishedAt=utc_now())
        if summary is not None:
            handle.summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.release_lock(handle.lock_path)


__all__ = [
    "RunHandle",
    "RunRegistry",
    "TERMINAL_STATES",
    "pid_alive",
    "utc_now",
]
