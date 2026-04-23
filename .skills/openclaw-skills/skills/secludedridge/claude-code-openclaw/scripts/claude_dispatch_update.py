#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch a Claude orchestrator user update via openclaw message send")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--notify-account", required=True)
    parser.add_argument("--notify-target", required=True)
    parser.add_argument("--notify-channel")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    update_file = run_dir / "user-update.txt"
    summary_file = run_dir / "summary.json"
    message = load_text(update_file)
    if not message:
        raise SystemExit(f"user update file missing or empty: {update_file}")

    payload = {
        "runDir": str(run_dir),
        "summaryFile": str(summary_file),
        "notifyAccount": args.notify_account,
        "notifyTarget": args.notify_target,
        "notifyChannel": args.notify_channel,
        "message": message,
    }

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    openclaw_bin = shutil.which("openclaw")
    if not openclaw_bin:
        raise SystemExit("openclaw binary not found in PATH")

    cmd = [
        openclaw_bin,
        "message",
        "send",
        "--account",
        args.notify_account,
        "--target",
        args.notify_target,
        "--message",
        message,
    ]
    if args.notify_channel:
        cmd += ["--channel", args.notify_channel]

    result = subprocess.run(cmd, text=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
