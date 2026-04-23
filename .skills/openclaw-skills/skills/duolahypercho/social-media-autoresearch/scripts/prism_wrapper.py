#!/usr/bin/env python3
"""prism_wrapper.py — run Prism clip generation as part of the autoresearch loop.

Usage:
  python3 prism_wrapper.py --url "https://youtube.com/watch?v=..."

Requirements:
  - Prism must be installed at ~/.openclaw/workspace-prism/
    (or set PRISM_DIR env var to your Prism workspace path)
  - yt-dlp, ffmpeg, and whisper must be installed

This script:
  1. Runs prism_run.py with the given arguments
  2. Finds the output folder
  3. Prints the result.json summary (including best_clip path)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PRISM_DIR   = Path(os.getenv("PRISM_DIR", "~/.openclaw/workspace-prism")).expanduser()
PRISM_RUN   = PRISM_DIR / "skills" / "prism-clips" / "prism_run.py"
PRISM_CLIPS = PRISM_DIR / "clips"


def check_prereqs() -> bool:
    """Verify Prism and its dependencies are available."""
    errors = []

    if not PRISM_RUN.exists():
        errors.append(f"prism_run.py not found at {PRISM_RUN}")

    for bin_name in ("ffmpeg", "yt-dlp"):
        found = subprocess.call(
            ["bash", "-lc", f"command -v {bin_name} >/dev/null 2>&1"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ) == 0
        if not found:
            errors.append(f"{bin_name} not installed")

    if errors:
        for e in errors:
            print(f"❌ {e}", file=sys.stderr)
        print("\nPrism setup:", file=sys.stderr)
        print("  pip install yt-dlp", file=sys.stderr)
        print("  brew install ffmpeg", file=sys.stderr)
        print("  pip install openai-whisper", file=sys.stderr)
        return False

    print("✅ Prerequisites OK")
    print(f"   Prism workspace: {PRISM_DIR}")
    return True


def run_prism(
    url: str,
    num_clips: int = 6,
    clip_duration: int = 55,
    skip_intro: int = 180,
    whisper_model: str = "base",
    portrait_mode: str = "letterbox",
    pre_roll: float = 2.5,
    background: bool = True,
    wait: bool = False,
    poll_interval: int = 60,
) -> Path | None:
    """Run prism_run.py and return the clip folder."""

    if not PRISM_RUN.exists():
        print(f"ERROR: prism_run.py not found at {PRISM_RUN}", file=sys.stderr)
        return None

    cmd = [
        sys.executable, str(PRISM_RUN),
        "--url", url,
        "--num-clips", str(num_clips),
        "--clip-duration", str(clip_duration),
        "--skip-intro", str(skip_intro),
        "--whisper-full-model", whisper_model,
        "--portrait-mode", portrait_mode,
        "--pre-roll", str(pre_roll),
    ]
    if not background:
        cmd.append("--no-background")

    print(f"🚀 Running Prism...")
    print(f"   URL: {url}")
    print(f"   Clips: {num_clips} × {clip_duration}s, skip intro: {skip_intro}s")

    subprocess.run(cmd, cwd=str(PRISM_DIR), check=False)

    folder = find_clip_folder(url)
    if not folder:
        print("⚠️  Could not locate clip folder. Check manually:")
        print(f"   {PRISM_CLIPS}")
        return None

    print(f"\n📁 Clip folder: {folder.relative_to(PRISM_DIR)}")

    if not wait:
        print("\n✅ Prism launched. Poll for completion with:")
        print(f"   python3 prism_wrapper.py --poll {folder.name}")
        return folder

    # Poll for completion
    print(f"\n⏳ Waiting for Prism (poll every {poll_interval}s)...")
    elapsed = 0
    while True:
        time.sleep(poll_interval)
        elapsed += poll_interval

        status_file = folder / "status.json"
        if not status_file.exists():
            print(f"  [{elapsed}s] waiting...")
            continue

        try:
            data = json.loads(status_file.read_text())
            stage = data.get("stage", "?")
            print(f"  [{elapsed}s] stage: {stage}")

            if stage == "completed":
                print("\n🎉 Done!")
                print_result(folder)
                return folder
            elif stage in ("failed", "error"):
                print(f"\n❌ Failed: {data.get('error', 'unknown')}", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError:
            print(f"  [{elapsed}s] parsing status.json...")


def find_clip_folder(url: str) -> Path | None:
    """Find the clip folder for a URL."""
    if not PRISM_CLIPS.exists():
        return None

    import re
    patterns = [
        r"watch\?v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
    ]
    video_id = None
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            video_id = m.group(1)
            break

    folders = sorted(PRISM_CLIPS.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)

    if video_id:
        for f in folders:
            if video_id in f.name:
                return f

    return folders[0] if folders else None


def print_result(folder: Path) -> None:
    """Print result.json summary."""
    result_file = folder / "result.json"
    if not result_file.exists():
        return

    result = json.loads(result_file.read_text())
    clips  = result.get("clips", [])
    best   = result.get("best_clip", "")

    print(f"\n{'─'*50}")
    print(f"  Video:   {result.get('video_title', folder.name)}")
    print(f"  Clips:   {len(clips)} generated")
    print(f"  Best:    {best}")
    print(f"\n  All clips:")
    for c in clips:
        score = c.get("score", 0)
        dur   = c.get("duration_seconds", "?")
        title = c.get("title", "untitled")[:50]
        path  = c.get("final_path", "")
        print(f"    [{score:5.1f}] {dur}s | {title}")
        print(f"             → {path}")
    print(f"{'─'*50}")


def poll_folder(folder_name: str, poll_interval: int = 60) -> None:
    """Poll an existing clip folder."""
    folder = PRISM_CLIPS / folder_name
    if not folder.exists():
        matches = [f for f in PRISM_CLIPS.iterdir() if folder_name in f.name]
        if matches:
            folder = matches[0]
        else:
            print(f"ERROR: No folder found matching '{folder_name}'", file=sys.stderr)
            print(f"Available: {[f.name for f in PRISM_CLIPS.iterdir()]}")
            sys.exit(1)

    print(f"📁 Polling: {folder.relative_to(PRISM_DIR)}")
    elapsed = 0
    while True:
        time.sleep(poll_interval)
        elapsed += poll_interval

        status_file = folder / "status.json"
        if not status_file.exists():
            print(f"  [{elapsed}s] waiting for status.json...")
            continue

        try:
            data = json.loads(status_file.read_text())
            stage = data.get("stage", "?")
            print(f"  [{elapsed}s] stage: {stage}")

            if stage == "completed":
                print("\n🎉 Done!")
                print_result(folder)
                return
            elif stage in ("failed", "error"):
                print(f"\n❌ Failed: {data.get('error', 'unknown')}", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError:
            print(f"  [{elapsed}s] parsing status.json...")


def main() -> None:
    parser = argparse.ArgumentParser(prog="prism_wrapper.py",
                                     description="Generate clips with Prism")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="Verify prerequisites")

    gen = sub.add_parser("generate", help="Generate clips from YouTube URL")
    gen.add_argument("--url", required=True, help="YouTube video URL")
    gen.add_argument("--num-clips", type=int, default=6)
    gen.add_argument("--clip-duration", type=int, default=55)
    gen.add_argument("--skip-intro", type=int, default=180)
    gen.add_argument("--whisper-model", default="base",
                     choices=["tiny", "base", "small", "medium"])
    gen.add_argument("--portrait-mode", default="letterbox")
    gen.add_argument("--pre-roll", type=float, default=2.5)
    gen.add_argument("--background", action="store_true", default=True)
    gen.add_argument("--no-background", dest="background", action="store_false")
    gen.add_argument("--wait", action="store_true")
    gen.add_argument("--poll-interval", type=int, default=60)

    parser.add_argument("--check", action="store_true", help="Verify prerequisites")
    parser.add_argument("--poll", metavar="FOLDER_NAME",
                        help="Poll existing folder for completion")
    parser.add_argument("--poll-interval", type=int, default=60)

    args = parser.parse_args()

    if args.check:
        check_prereqs()
        return

    if args.poll:
        poll_folder(args.poll, args.poll_interval)
        return

    if args.cmd == "check":
        check_prereqs()
        return

    if args.cmd == "generate":
        run_prism(
            url=args.url,
            num_clips=args.num_clips,
            clip_duration=args.clip_duration,
            skip_intro=args.skip_intro,
            whisper_model=args.whisper_model,
            portrait_mode=args.portrait_mode,
            pre_roll=args.pre_roll,
            background=args.background,
            wait=args.wait,
            poll_interval=args.poll_interval,
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()
