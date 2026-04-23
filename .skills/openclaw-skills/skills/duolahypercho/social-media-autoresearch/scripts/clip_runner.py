#!/usr/bin/env python3
"""clip_runner.py — Generate clips from the selected video.

Supports two engines:
  1. prism  — local, free (calls workspace-prism's prism_run.py)
  2. wayin  — cloud, faster (calls ai-clipping)

Usage:
  python3 clip_runner.py                              # Run on SELECTED video
  python3 clip_runner.py --url "https://youtube.com/..."  # Run on specific URL
  python3 clip_runner.py --engine wayin               # Use Wayin instead of Prism
  python3 clip_runner.py --check                      # Verify prerequisites
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR   = Path(__file__).parent.parent.resolve()
DATA_DIR    = SKILL_DIR / "data"
PRISM_RUN   = Path(os.getenv("PRISM_DIR", "~/.openclaw/workspace-prism")).expanduser() / "skills" / "prism-clips" / "prism_run.py"
PRISM_OUT  = Path(os.getenv("PRISM_OUT", "~/.openclaw/workspace-prism/clips")).expanduser()
VIDEOS_FILE = DATA_DIR / "videos.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_videos() -> dict:
    return json.loads(VIDEOS_FILE.read_text())


def save_videos(data: dict) -> None:
    data["last_updated"] = now_iso()
    VIDEOS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_strategy() -> dict:
    cfg = SKILL_DIR / "config" / "strategy.json"
    if cfg.exists():
        return json.loads(cfg.read_text())
    return {}


def get_selected_video() -> dict | None:
    data = load_videos()
    for v in data.get("videos", []):
        if v.get("status") == "SELECTED":
            return v
    return None


def mark_status(video_id: str, status: str, **extra) -> None:
    data = load_videos()
    for v in data.get("videos", []):
        if v.get("video_id") == video_id:
            v["status"] = status
            v.setdefault("pipeline_log", []).append({
                "step": status,
                "timestamp": now_iso(),
                **extra,
            })
            save_videos(data)
            return


def run_prism(url: str, strategy: dict) -> dict:
    """Run Prism on the selected video."""
    num_clips     = strategy.get("clips_per_video", 6)
    clip_duration = strategy.get("clip_duration_seconds", 35)
    skip_intro    = strategy.get("skip_intro_seconds", 180)

    cmd = [
        sys.executable, str(PRISM_RUN),
        "--url",           url,
        "--outdir",        str(PRISM_OUT),
        "--num-clips",     str(num_clips),
        "--clip-duration", str(clip_duration),
        "--skip-intro",    str(skip_intro),
        "--whisper-full-model", "base",
        "--whisper-clip-model", "tiny",
        "--pre-roll",      "2.5",
        "--selector",      "llm",
        "--portrait-mode", "letterbox",
        "--background",
    ]

    print(f"🚀 Running Prism: {url}")
    print(f"   Clips: {num_clips} × {clip_duration}s, skip intro: {skip_intro}s")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"⚠️  Prism spawn returned {result.returncode}: {result.stderr[:200]}")
        # Background mode: return what we can from stdout
        try:
            return json.loads(result.stdout.strip())
        except Exception:
            return {"folder": None, "error": result.stderr[:200]}

    try:
        return json.loads(result.stdout.strip())
    except Exception:
        return {"folder": None, "output": result.stdout[:200]}


def run_wayin(url: str, strategy: dict) -> dict:
    """Run Wayin (ai-clipping) on the selected video."""
    # Find ai-clipping scripts
    wayin_dir = SKILL_DIR / "ai-clipping"
    submit_py = wayin_dir / "scripts" / "submit_task.py"

    topics = ",".join(strategy.get("niches", ["AI", "productivity"]))
    cmd = [
        sys.executable, str(submit_py),
        "--url",   url,
        "--topics", topics,
        "--wait",
    ]

    print(f"🚀 Running Wayin: {url}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"❌ Wayin failed: {result.stderr[:200]}")
        return {"error": result.stderr[:200]}

    try:
        return json.loads(result.stdout.strip())
    except Exception:
        return {"output": result.stdout[:200]}


def wait_for_prism(folder: Path, timeout: int = 2400) -> dict:
    """Poll status.json until Prism completes."""
    print(f"\n⏳ Waiting for Prism (poll every 60s, timeout {timeout}s)...")
    elapsed = 0
    while elapsed < timeout:
        time.sleep(60)
        elapsed += 60
        status_file = folder / "status.json"
        if not status_file.exists():
            print(f"  [{elapsed}s] waiting for status.json...")
            continue
        try:
            data = json.loads(status_file.read_text())
            stage = data.get("stage", "?")
            print(f"  [{elapsed}s] {stage}")
            if stage == "completed":
                result_file = folder / "result.json"
                if result_file.exists():
                    return json.loads(result_file.read_text())
                return data
            elif stage in ("failed", "error"):
                print(f"❌ Prism failed: {data.get('error', 'unknown')}")
                return {"error": data.get("error", "unknown")}
        except json.JSONDecodeError:
            pass
    return {"error": "timeout"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate clips from selected video")
    parser.add_argument("--url",     help="Specific video URL (skip SELECTED lookup)")
    parser.add_argument("--engine",  default="prism", choices=["prism", "wayin"],
                        help="Clipping engine (default: prism)")
    parser.add_argument("--check",   action="store_true", help="Check prerequisites")
    parser.add_argument("--no-wait", dest="wait", action="store_false", default=True,
                        help="Return immediately instead of polling")
    args = parser.parse_args()

    if args.check:
        print("Checking prerequisites...")
        errors = []
        # Prism
        if not PRISM_RUN.exists():
            errors.append(f"Prism runner not found: {PRISM_RUN}")
        for bin_name in ("ffmpeg", "yt-dlp", "whisper"):
            found = subprocess.call(
                ["bash", "-lc", f"command -v {bin_name} >/dev/null 2>&1"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            ) == 0
            if not found:
                errors.append(f"{bin_name} not installed")
        # Wayin
        wayin_dir = SKILL_DIR / "ai-clipping"
        if not (wayin_dir / "scripts" / "submit_task.py").exists():
            errors.append("Wayin submit_task.py not found")
        if errors:
            for e in errors:
                print(f"  ❌ {e}")
            sys.exit(1)
        print("  ✅ All prerequisites OK")
        return

    # Get video
    video = None
    if args.url:
        video = {"url": args.url, "title": args.url, "video_id": args.url}
    else:
        video = get_selected_video()

    if not video:
        print("❌ No SELECTED video found.")
        print("   Run: selector.py to pick a video first.")
        sys.exit(1)

    url      = video.get("url")
    vid      = video.get("video_id")
    strategy = load_strategy()

    mark_status(vid, "CLIPPING", note=f"Engine: {args.engine}")

    if args.engine == "prism":
        result = run_prism(url, strategy)
    else:
        result = run_wayin(url, strategy)

    folder = result.get("folder") or result.get("output_dir")
    if folder:
        folder = Path(folder)

    if args.wait and folder and folder.exists():
        final = wait_for_prism(folder)
        # Update READY
        clips = final.get("clips", [])
        for c in clips:
            c["file_path"] = str(folder / c.get("file", ""))
        mark_status(vid, "READY",
                    clips_created=len(clips),
                    output_dir=str(folder),
                    prism_folder=str(folder),
                    prism_job_id=result.get("job_id", ""))
        print(f"\n🎉 Ready: {len(clips)} clips in {folder}")
        for c in clips:
            print(f"   [{c.get('score', '?')}] {c.get('title', '')[:50]}")
    else:
        # Background mode — trust the spawn
        mark_status(vid, "READY",
                    output_dir=str(folder) if folder else None,
                    prism_folder=str(folder) if folder else None,
                    note="Background clip generation spawned")
        print(f"\n✅ Prism spawned in background: {folder}")
        print(f"   Poll with: python3 tracker.py status")


if __name__ == "__main__":
    main()
