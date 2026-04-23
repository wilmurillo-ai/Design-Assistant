#!/usr/bin/env python3
"""posting.py — Post clips to platforms via Postiz.

Usage:
  python3 posting.py --clip path/to/clip.mp4 --platform youtube --caption "..."
  python3 posting.py --clip path/to/clip.mp4 --platforms youtube,tiktok,instagram --caption "..."
  python3 posting.py --clip path/to/clip.mp4 --platforms youtube,tiktok,instagram \
      --title "My Clip Title" --caption "The key..." --hashtags "AI #Productivity"
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
from typing import Optional

SKILL_DIR   = Path(__file__).parent.parent.resolve()
CONFIG_DIR  = SKILL_DIR / "config"
DATA_DIR    = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
VIDEOS_FILE = DATA_DIR / "videos.json"

POSTIZ_API_KEY = os.getenv("POSTIZ_API_KEY", "")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_videos() -> dict:
    return json.loads(VIDEOS_FILE.read_text())


def save_videos(data: dict) -> None:
    data["last_updated"] = now_iso()
    VIDEOS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_platforms() -> dict:
    path = CONFIG_DIR / "platforms.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def get_integration_id(platform: str) -> str | None:
    platforms = load_platforms()
    return platforms.get("integrations", {}).get(platform)


def run_postiz(args: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if POSTIZ_API_KEY:
        env["POSTIZ_API_KEY"] = POSTIZ_API_KEY
    result = subprocess.run(
        ["postiz"] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def upload_media(file_path: str) -> str:
    """Upload file to Postiz CDN. Returns CDN URL."""
    path = Path(file_path).expanduser()
    if not path.exists():
        print(f"❌ File not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"📤 Uploading: {path.name}")
    result = run_postiz(["upload", str(path)])
    if result.returncode != 0:
        print(f"❌ Upload failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
        url = data.get("path", "")
        if url:
            print(f"  ✅ Uploaded: {url}")
            return url
        print(f"❌ No URL in upload response: {result.stdout[:200]}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Could not parse upload response: {result.stdout[:200]}", file=sys.stderr)
        sys.exit(1)


def create_post(
    content: str,
    platform: str,
    media_url: str,
    schedule: str | None = None,
) -> dict:
    """Create a post via Postiz CLI. Returns parsed JSON response."""
    integration_id = get_integration_id(platform)
    if not integration_id:
        print(f"❌ No integration ID for platform: {platform}", file=sys.stderr)
        print(f"   Add it to config/platforms.json", file=sys.stderr)
        sys.exit(1)

    cmd = ["posts:create", "-c", content, "-i", integration_id]
    if media_url:
        cmd += ["-m", media_url]
    if schedule:
        cmd += ["-s", schedule]
    else:
        cmd += ["-s", now_iso()]  # Post immediately

    print(f"📤 Creating post on {platform}...")
    result = run_postiz(cmd)
    if result.returncode != 0:
        print(f"⚠️  Post failed (may be rate limit or bad settings): {result.stderr[:200]}")
        return {}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def format_caption(caption: str, hashtags: list[str]) -> str:
    """Build caption from base text + hashtags."""
    if not hashtags:
        return caption
    tags = " ".join(h if h.startswith("#") else f"#{h}" for h in hashtags)
    return f"{caption}\n\n{tags}"


def format_title(title: str, hashtags: list[str]) -> str:
    """Build platform title. Truncates to 100 chars, max 5 hashtags."""
    tags = " ".join(h if h.startswith("#") else f"#{h}" for h in hashtags[:5])
    if tags:
        # Leave room for tags
        remaining = 100 - len(tags) - 1
        title = title[:remaining]
        return f"{title} {tags}"
    return title[:100]


def post_clip(
    clip_path: str,
    platform: str,
    caption: str,
    hashtags: list[str],
    title: str,
) -> dict:
    """Full upload + post workflow for one platform."""
    # Upload first
    cdn_url = upload_media(clip_path)

    # Format
    full_caption = format_caption(caption, hashtags)
    platform_title = format_title(title or caption, hashtags)

    # Settings per platform
    settings = {}
    if platform == "tiktok":
        settings = '{"privacy":"PUBLIC_TO_EVERYONE","duet":true,"stitch":true}'
    elif platform == "instagram":
        settings = '{"post_type":"reel"}'
    elif platform == "youtube":
        settings = '{"type":"public"}'

    # Create post
    cmd = ["posts:create",
           "-c", full_caption,
           "-i", get_integration_id(platform),
           "-m", cdn_url,
           "-s", now_iso()]
    if settings:
        cmd += ["--settings", settings]

    result = run_postiz(cmd)
    post_data = {}
    if result.returncode == 0:
        try:
            post_data = json.loads(result.stdout)
        except Exception:
            pass

    return {
        "cdn_url":    cdn_url,
        "post_id":    (post_data.get("id") or post_data.get("post_id") or ""),
        "platform":   platform,
        "posted_at":  now_iso(),
        "post_data":  post_data,
    }


def update_video_posted(video_id: str, posts: list[dict]) -> None:
    """Record post IDs in videos.json."""
    data = load_videos()
    for v in data.get("videos", []):
        if v.get("video_id") == video_id:
            v["status"] = "POSTED"
            v.setdefault("pipeline_log", []).append({
                "step": "POSTED",
                "timestamp": now_iso(),
                "postiz_post_ids": [p.get("post_id", "") for p in posts if p.get("post_id")],
            })
            save_videos(data)
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a clip to platforms via Postiz")
    parser.add_argument("--clip",       required=True, help="Path to clip video file")
    parser.add_argument("--platform",   help="Single platform (youtube/tiktok/instagram)")
    parser.add_argument("--platforms",  help="Comma-separated: youtube,tiktok,instagram")
    parser.add_argument("--caption",    required=True, help="Post caption/text")
    parser.add_argument("--title",      help="Title (defaults to caption)")
    parser.add_argument("--hashtags",   help="Comma-separated hashtags")
    parser.add_argument("--schedule",   help="ISO8601 schedule time")
    parser.add_argument("--video-id",   help="Video ID in videos.json to update")
    args = parser.parse_args()

    platforms = []
    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(",")]
    elif args.platform:
        platforms = [args.platform]

    if not platforms:
        print("❌ Specify --platform or --platforms", file=sys.stderr)
        sys.exit(1)

    hashtags = []
    if args.hashtags:
        hashtags = [h.strip() for h in args.hashtags.split(",")]

    results = []
    for platform in platforms:
        result = post_clip(
            clip_path = args.clip,
            platform  = platform,
            caption   = args.caption,
            hashtags  = hashtags,
            title     = args.title or args.caption,
        )
        results.append(result)
        print(f"  ✅ {platform}: post_id={result.get('post_id', 'n/a')}")
        time.sleep(2)  # Rate limit between platforms

    # Update videos.json
    if args.video_id:
        update_video_posted(args.video_id, results)

    print(f"\n✅ Posted to {len(platforms)} platform(s)")


if __name__ == "__main__":
    main()
