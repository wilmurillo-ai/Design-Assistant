#!/usr/bin/env python3
"""Thin wrapper that launches the autonomous runtime and passes through its result.

The runtime handles its own lifecycle (stuck detection, max_steps, sensitive
action stops). This script provides:
  - A 10-minute hard safety cap as a last resort.
  - Screenshot materialization to a stable path.
  - A fallback result when the runtime crashes without writing its result JSON.

Output: a single JSON object to stdout matching the 5-status contract
(done, needs_input, stuck, max_steps, timeout, failed).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
RUNTIME_DIR = BASE_DIR / "runtime"
RUNTIME_MAIN = RUNTIME_DIR / "main.py"
RUNS_DIR = RUNTIME_DIR / ".runs"
SHARED_SCREENSHOT_PATH = RUNTIME_DIR / "last-screenshot.png"

DEFAULT_TIMEOUT_SECONDS = int(os.getenv("IOTA_SIDEQUEST_TIMEOUT", "600"))


def _utc_now() -> str:
    """Return the current UTC time in ISO8601 format."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_run_id() -> str:
    """Generate a compact timestamp-based run id."""

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _read_json(path: Path) -> dict[str, Any] | None:
    """Read JSON when the file exists and contains valid content."""

    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON atomically so readers never see partial contents."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temp_path, path)


def _materialize_screenshot(candidate_path: str | None) -> str:
    """Copy the latest screenshot into the skill bundle for easy sharing.

    Args:
        candidate_path: Path reported by the runtime or progress file.

    Returns:
        Stable path string, or empty string if no screenshot is available.
    """

    import shutil
    import tempfile

    candidates: list[Path] = []
    if candidate_path:
        candidates.append(Path(candidate_path))
    candidates.append(Path(tempfile.gettempdir()) / "phone-agent-last.png")
    candidates.append(SHARED_SCREENSHOT_PATH)

    for candidate in candidates:
        if not candidate.is_file():
            continue
        SHARED_SCREENSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        if candidate.resolve() != SHARED_SCREENSHOT_PATH.resolve():
            shutil.copy2(candidate, SHARED_SCREENSHOT_PATH)
        return str(SHARED_SCREENSHOT_PATH)

    return ""


def _list_connected_devices() -> list[str]:
    """Return the list of connected Android devices in `device` state."""

    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return []

    devices: list[str] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("List of devices attached"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def _resolve_device_id(requested: str | None) -> str | None:
    """Resolve the device id, auto-detecting when only one device is connected."""

    if requested:
        return requested
    devices = _list_connected_devices()
    if len(devices) == 1:
        return devices[0]
    return None


def _terminate_process(proc: subprocess.Popen[Any]) -> None:
    """Terminate the child process and its process group when possible."""

    if proc.poll() is not None:
        return
    try:
        if hasattr(os, "killpg"):
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            if hasattr(os, "killpg"):
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
            proc.wait(timeout=5)
        except Exception:
            pass


def _launch_runtime(
    command: list[str], log_path: Path
) -> tuple[subprocess.Popen[Any], Any]:
    """Launch the automation runtime and mirror output into a log file.

    Args:
        command: Full command to execute.
        log_path: Path to write stdout/stderr.

    Returns:
        Tuple of (process, log_file_handle).
    """

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("w", encoding="utf-8")
    popen_kwargs: dict[str, Any] = {
        "cwd": str(RUNTIME_DIR),
        "stdout": log_handle,
        "stderr": subprocess.STDOUT,
        "text": True,
    }
    if hasattr(os, "setsid"):
        popen_kwargs["preexec_fn"] = os.setsid
    try:
        return subprocess.Popen(command, **popen_kwargs), log_handle
    except Exception:
        log_handle.close()
        raise


def _build_timeout_result(
    *,
    task: str,
    device_id: str | None,
    timeout_seconds: int,
    progress: dict[str, Any] | None,
    screenshot_path: str,
) -> dict[str, Any]:
    """Build a synthetic timeout result when the safety cap fires.

    Args:
        task: The original task description.
        device_id: ADB device id.
        timeout_seconds: The timeout that was hit.
        progress: Last progress snapshot from the runtime, if any.
        screenshot_path: Path to the materialized screenshot.

    Returns:
        Result payload matching the 5-status contract.
    """

    steps = (progress or {}).get("steps", [])
    screen_description = str((progress or {}).get("screen_description", ""))
    step_count = int((progress or {}).get("step", 0) or 0)
    action_chain = [
        str(entry.get("action", ""))
        for entry in (steps if isinstance(steps, list) else [])
        if entry.get("action")
    ]

    return {
        "status": "timeout",
        "why": f"Safety timeout ({timeout_seconds}s) reached. The runtime did not self-terminate in time.",
        "what_i_did": " -> ".join(action_chain[-15:]) if action_chain else "",
        "where_i_am": screen_description,
        "steps": steps[-30:] if isinstance(steps, list) else [],
        "step_count": step_count,
        "screenshot_path": screenshot_path,
        "task": task,
        "device_id": device_id or "",
        "finished_at": _utc_now(),
    }


def _build_crash_result(
    *,
    task: str,
    device_id: str | None,
    return_code: int | None,
    screenshot_path: str,
) -> dict[str, Any]:
    """Build a failed result when the runtime exits without writing its result JSON.

    Args:
        task: The original task description.
        device_id: ADB device id.
        return_code: Process exit code.
        screenshot_path: Path to the materialized screenshot.

    Returns:
        Result payload matching the 5-status contract.
    """

    return {
        "status": "failed",
        "why": f"Runtime exited with code {return_code} without producing a result.",
        "what_i_did": "",
        "where_i_am": "",
        "steps": [],
        "step_count": 0,
        "screenshot_path": screenshot_path,
        "task": task,
        "device_id": device_id or "",
        "finished_at": _utc_now(),
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed namespace with task, timeout, and device_id.
    """

    parser = argparse.ArgumentParser(
        description="Launch autonomous Android automation and return the result."
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Hard safety cap in seconds (default: 600 = 10 minutes)",
    )
    parser.add_argument(
        "--device-id",
        type=str,
        default=os.getenv("PHONE_AGENT_DEVICE_ID"),
        help="Optional ADB device id override",
    )
    parser.add_argument(
        "task",
        type=str,
        help="The task description for the autonomous agent",
    )
    return parser.parse_args()


def main() -> None:
    """Launch the runtime, wait for it, and print its result JSON to stdout."""

    args = parse_args()
    run_id = _make_run_id()
    log_path = RUNS_DIR / f"{run_id}.log"
    runtime_result_path = RUNS_DIR / f"{run_id}.runtime-result.json"
    progress_path = RUNS_DIR / f"{run_id}.progress.json"
    phase_result_path = RUNS_DIR / f"{run_id}.result.json"
    resolved_device_id = _resolve_device_id(args.device_id)

    command = [
        sys.executable,
        str(RUNTIME_MAIN),
        "--skip-checks",
        "--result-json", str(runtime_result_path),
        "--progress-json", str(progress_path),
    ]
    if resolved_device_id:
        command.extend(["--device-id", resolved_device_id])
    command.append(args.task)

    # --- Launch ---
    try:
        proc, log_handle = _launch_runtime(command, log_path)
    except Exception as error:
        payload = _build_crash_result(
            task=args.task,
            device_id=resolved_device_id,
            return_code=None,
            screenshot_path=_materialize_screenshot(None),
        )
        payload["why"] = f"Could not launch runtime: {error}"
        _atomic_write_json(phase_result_path, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        sys.exit(1)

    # --- Wait with safety cap ---
    timed_out = False
    try:
        return_code = proc.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        return_code = None
        _terminate_process(proc)
    finally:
        log_handle.close()

    # --- Read runtime artifacts ---
    runtime_result = _read_json(runtime_result_path)
    progress = _read_json(progress_path)

    # Determine best screenshot source.
    raw_screenshot = (
        str((runtime_result or {}).get("screenshot_path", ""))
        or str((progress or {}).get("screenshot_path", ""))
    )
    screenshot_path = _materialize_screenshot(raw_screenshot or None)

    # --- Build final payload ---
    if timed_out:
        payload = _build_timeout_result(
            task=args.task,
            device_id=resolved_device_id,
            timeout_seconds=args.timeout,
            progress=progress,
            screenshot_path=screenshot_path,
        )
    elif runtime_result:
        # Pass through the runtime's own result, just update screenshot path.
        payload = runtime_result
        payload["screenshot_path"] = screenshot_path
    else:
        # Runtime exited but didn't write a result — treat as crash.
        payload = _build_crash_result(
            task=args.task,
            device_id=resolved_device_id,
            return_code=return_code,
            screenshot_path=screenshot_path,
        )

    _atomic_write_json(phase_result_path, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    exit_code = 0 if payload.get("status") == "done" else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
