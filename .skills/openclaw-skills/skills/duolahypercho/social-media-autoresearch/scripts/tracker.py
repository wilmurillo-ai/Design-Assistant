#!/usr/bin/env python3
"""tracker.py — Pipeline status tracker.

Usage:
  python3 tracker.py status          # Show full pipeline status
  python3 tracker.py list           # List all videos
  python3 tracker.py list DISCOVERED # List by status
  python3 tracker.py list READY      # List ready-to-post clips
  python3 tracker.py list POSTED     # List posted videos
  python3 tracker.py history <id>     # Show pipeline log for a video
  python3 tracker.py reset <id>      # Reset a video to DISCOVERED
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR   = Path(__file__).parent.parent.resolve()
DATA_DIR    = SKILL_DIR / "data"
VIDEOS_FILE = DATA_DIR / "videos.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_videos() -> dict:
    return json.loads(VIDEOS_FILE.read_text())


def save_videos(data: dict) -> None:
    data["last_updated"] = now_iso()
    VIDEOS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


PIPELINE_STATUSES = [
    "DISCOVERED", "SELECTED", "DOWNLOADING", "ANALYZING",
    "CLIPPING", "CAPTIONING", "READY", "POSTED",
]


def list_videos(status_filter: str | None = None) -> None:
    data = load_videos()
    videos = data.get("videos", [])
    if status_filter:
        videos = [v for v in videos if v.get("status") == status_filter]

    videos.sort(key=lambda x: x.get("score", 0), reverse=True)

    print(f"\n📋 Videos: {len(videos)}")
    if status_filter:
        print(f"   Filter: {status_filter}")

    for v in videos[:20]:
        title   = v.get("title", "N/A")[:40]
        status  = v.get("status", "UNKNOWN")
        score   = v.get("score", 0)
        channel = v.get("channel", "N/A")
        clips_info = ""
        if status == "READY" and v.get("clips"):
            clips_info = f" | 🎬 {len(v['clips'])} clips"
        elif status == "POSTED":
            pids = v.get("pipeline_log", [])
            clips_info = f" | ✅ posted"

        print(f"\n  [{status:12}] {title}...")
        print(f"     📺 {channel} | Score: {score}{clips_info}")


def show_status() -> None:
    data = load_videos()
    videos = data.get("videos", [])

    print(f"\n{'='*50}")
    print("PIPELINE STATUS")
    print(f"{'='*50}")

    counts = Counter(v.get("status", "UNKNOWN") for v in videos)
    print("\n📊 By Status:")
    for s in PIPELINE_STATUSES:
        n = counts.get(s, 0)
        bar = "█" * n
        print(f"   {s:12} | {bar} ({n})")

    processing = [v for v in videos if v.get("status") in [
        "SELECTED", "DOWNLOADING", "ANALYZING", "CLIPPING", "CAPTIONING"
    ]]
    if processing:
        print(f"\n🔄 Currently Processing:")
        for v in processing:
            print(f"   - {v.get('title', '')[:40]}")
            print(f"     Status: {v.get('status')}")

    ready = [v for v in videos if v.get("status") == "READY"]
    if ready:
        print(f"\n✅ Ready to Post: {len(ready)} videos")
        for v in ready[:5]:
            print(f"   🎬 {v.get('title', '')[:50]}")

    discovered = [v for v in videos if v.get("status") == "DISCOVERED"]
    print(f"\n📥 DISCOVERED (queue): {len(discovered)}")
    print(f"   Run: selector.py to pick one")


def show_history(video_id: str) -> None:
    data = load_videos()
    for v in data.get("videos", []):
        vid = v.get("video_id", "") or v.get("id", "")
        if vid != video_id:
            continue
        print(f"\n📜 Pipeline History: {v.get('title', 'N/A')}")
        print(f"   Status: {v.get('status')}")
        print(f"   Score:  {v.get('score')}")
        print(f"   Channel: {v.get('channel')}")
        print(f"\n   Log:")
        for entry in v.get("pipeline_log", []):
            ts   = entry.get("timestamp", "").replace("T", " ").replace("Z", "")[:19]
            step = entry.get("step")
            note = entry.get("note", "")
            extra = {k: v for k, v in entry.items() if k not in ("step", "timestamp", "note")}
            extra_str = " | " + ", ".join(f"{k}={v}" for k, v in extra.items()) if extra else ""
            print(f"   - {ts} | {step} {note}{extra_str}")
        return
    print(f"❌ Video not found: {video_id}")


def reset_video(video_id: str) -> None:
    data = load_videos()
    for v in data.get("videos", []):
        vid = v.get("video_id", "") or v.get("id", "")
        if vid == video_id:
            old = v.get("status")
            v["status"] = "DISCOVERED"
            v.setdefault("pipeline_log", []).append({
                "step": "RESET",
                "timestamp": now_iso(),
                "note": f"Reset from {old} to DISCOVERED",
            })
            save_videos(data)
            print(f"✅ {video_id}: {old} → DISCOVERED")
            return
    print(f"❌ Video not found: {video_id}")


def show_ready() -> None:
    data = load_videos()
    videos = [v for v in data.get("videos", []) if v.get("status") == "READY"]

    print(f"\n✅ Ready to Post ({len(videos)} videos):")
    for v in videos:
        print(f"\n  📺 {v.get('title', 'N/A')}")
        print(f"     Channel: {v.get('channel')}")
        clips = v.get("clips", [])
        print(f"     Clips: {len(clips)}")
        for clip in clips:
            print(f"       - [{clip.get('score', '?')}] "
                  f"{clip.get('title', '')[:50]} "
                  f"({clip.get('duration', '?')}s)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Track video pipeline status")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status",    help="Show pipeline status overview")
    sub.add_parser("list",       help="List all videos")
    sub.add_parser("ready",      help="List videos ready to post")

    history = sub.add_parser("history", help="Show pipeline log for a video")
    history.add_argument("video_id", help="Video ID")

    reset = sub.add_parser("reset", help="Reset a video to DISCOVERED")
    reset.add_argument("video_id", help="Video ID")

    args = parser.parse_args()

    if args.cmd == "status":
        show_status()
    elif args.cmd == "list":
        status = None
        # allow: tracker.py list DISCOVERED
        import sys as _sys
        if len(_sys.argv) > 3:
            status = _sys.argv[3]
        list_videos(status)
    elif args.cmd == "ready":
        show_ready()
    elif args.cmd == "history":
        show_history(args.video_id)
    elif args.cmd == "reset":
        reset_video(args.video_id)


if __name__ == "__main__":
    main()
