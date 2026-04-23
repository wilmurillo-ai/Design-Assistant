#!/usr/bin/env python3
"""postiz_poster.py — Python wrapper for Postiz CLI.

Handles the common Postiz workflows without needing to remember CLI flags.
Usage:
  python3 postiz_poster.py list                    # List integrations
  python3 postiz_poster.py upload path/to/file.mp4
  python3 postiz_poster.py post -c "text" -i <id> -s "2026-03-22T10:00:00Z"
  python3 postiz_poster.py analytics-post <post-id>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


# ── Config ───────────────────────────────────────────────────────────────────

POSTIZ_API_KEY = os.getenv("POSTIZ_API_KEY", "")
POSTIZ_API_URL = os.getenv("POSTIZ_API_URL", "")


# ── Helpers ─────────────────────────────────────────────────────────────────

def run(args: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if POSTIZ_API_KEY:
        env["POSTIZ_API_KEY"] = POSTIZ_API_KEY
    if POSTIZ_API_URL:
        env["POSTIZ_API_URL"] = POSTIZ_API_URL

    result = subprocess.run(
        ["postiz"] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0 and "not found" not in result.stderr.lower():
        print(f"ERROR: postiz {' '.join(args)} failed:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    return result


def parse_json(text: str) -> dict | list:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text.strip()}


# ── Commands ────────────────────────────────────────────────────────────────

def cmd_list() -> None:
    """List all connected integrations."""
    result = run(["integrations:list"])
    data = parse_json(result.stdout)
    print(json.dumps(data, indent=2))


def cmd_upload(file_path: str) -> None:
    """Upload a file to Postiz CDN. Returns the URL."""
    path = Path(file_path).expanduser()
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    result = run(["upload", str(path)])
    data = parse_json(result.stdout)
    print(json.dumps(data, indent=2))

    # Also print the URL directly for piping
    url = None
    if isinstance(data, dict):
        url = data.get("path", "")
    if url:
        print(f"\n📎 URL: {url}", file=sys.stdout)


def cmd_post(
    content: str,
    integration_id: str,
    schedule: str,
    media: Optional[str] = None,
    settings: Optional[str] = None,
    comment: Optional[str] = None,
    delay: int = 0,
    draft: bool = False,
) -> None:
    """Create a post via Postiz."""
    if not integration_id:
        print("ERROR: -i/--integration-id is required", file=sys.stderr)
        sys.exit(1)
    if not schedule:
        print("ERROR: -s/--schedule is required (ISO 8601 format, e.g. 2026-03-22T10:00:00Z)", file=sys.stderr)
        sys.exit(1)

    args = [
        "posts:create",
        "-c", content,
        "-s", schedule,
        "-i", integration_id,
    ]

    if media:
        args += ["-m", media]

    if settings:
        args += ["--settings", settings]

    if comment:
        args += ["-c", comment]

    if delay > 0:
        args += ["-d", str(delay)]

    if draft:
        args += ["-t", "draft"]

    result = run(args)
    data = parse_json(result.stdout)
    print(json.dumps(data, indent=2))


def cmd_analytics_post(post_id: str, days: int = 7) -> None:
    """Get analytics for a specific post."""
    result = run(["analytics:post", post_id, "-d", str(days)])
    data = parse_json(result.stdout)

    # Handle missing release ID
    if isinstance(data, dict) and data.get("missing"):
        print("⚠️  Post published but platform didn't return a post ID.", file=sys.stderr)
        print("    Run: postiz posts:missing <post-id>", file=sys.stderr)
        print("    Then: postiz posts:connect <post-id> --release-id <id>", file=sys.stderr)
        print(f"\nMissing data: {json.dumps(data, indent=2)}", file=sys.stderr)
        return

    print(json.dumps(data, indent=2))


def cmd_analytics_platform(integration_id: str, days: int = 7) -> None:
    """Get analytics for a platform."""
    result = run(["analytics:platform", integration_id, "-d", str(days)])
    data = parse_json(result.stdout)
    print(json.dumps(data, indent=2))


def cmd_missing(post_id: str) -> None:
    """List available content from a provider for a post with missing release ID."""
    result = run(["posts:missing", post_id])
    data = parse_json(result.stdout)
    print(json.dumps(data, indent=2))


def cmd_connect(post_id: str, release_id: str) -> None:
    """Connect a post to its published content on the platform."""
    result = run(["posts:connect", post_id, "--release-id", release_id])
    print("✅ Connected.")
    if result.stdout.strip():
        print(result.stdout)


def cmd_delete(post_id: str) -> None:
    """Delete a post."""
    result = run(["posts:delete", post_id])
    print("✅ Deleted." if result.returncode == 0 else result.stderr)


def cmd_list_posts(start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
    """List recent posts."""
    args = ["posts:list"]
    if start_date:
        args += ["--startDate", start_date]
    if end_date:
        args += ["--endDate", end_date]
    result = run(args)
    data = parse_json(result.stdout)
    print(json.dumps(data, indent=2))


def cmd_find_id(platform: str) -> Optional[str]:
    """Find integration ID for a platform identifier (e.g. 'youtube', 'tiktok')."""
    result = run(["integrations:list"])
    data = parse_json(result.stdout)
    if isinstance(data, list):
        for item in data:
            if item.get("identifier", "").lower() == platform.lower():
                print(item.get("id", ""))
                return item.get("id", "")
    return None


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(prog="postiz_poster.py",
                                     description="Postiz CLI wrapper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # postiz integrations:list
    sub.add_parser("list", help="List all connected integrations")

    # postiz upload
    upload = sub.add_parser("upload", help="Upload a file to Postiz CDN")
    upload.add_argument("file", help="Path to file to upload")

    # postiz posts:create
    post = sub.add_parser("post", help="Create a post")
    post.add_argument("-c", "--content", required=True, help="Post text content")
    post.add_argument("-i", "--integration-id", required=True, help="Integration ID")
    post.add_argument("-s", "--schedule", required=True,
                     help="Schedule time (ISO 8601, e.g. 2026-03-22T10:00:00Z)")
    post.add_argument("-m", "--media", help="Media URL or path (upload first!)")
    post.add_argument("--settings", help="JSON settings string")
    post.add_argument("--comment", help="Comment text (for threads)")
    post.add_argument("-d", "--delay", type=int, default=0,
                     help="Delay between comments in minutes")
    post.add_argument("--draft", action="store_true", help="Save as draft")

    # analytics
    ap = sub.add_parser("analytics-post", help="Get post analytics")
    ap.add_argument("post_id", help="Post ID")
    ap.add_argument("-d", "--days", type=int, default=7)

    aplat = sub.add_parser("analytics-platform", help="Get platform analytics")
    aplat.add_argument("integration_id", help="Integration ID")
    aplat.add_argument("-d", "--days", type=int, default=7)

    # resolve missing
    miss = sub.add_parser("missing", help="List available content for missing post")
    miss.add_argument("post_id", help="Post ID with missing release ID")

    connect = sub.add_parser("connect", help="Connect a post to its published content")
    connect.add_argument("post_id", help="Post ID")
    connect.add_argument("release_id", help="Content ID from the platform")

    # manage
    delete = sub.add_parser("delete", help="Delete a post")
    delete.add_argument("post_id", help="Post ID to delete")

    list_posts = sub.add_parser("list-posts", help="List recent posts")
    list_posts.add_argument("--start", help="Start date (ISO 8601)")
    list_posts.add_argument("--end", help="End date (ISO 8601)")

    find = sub.add_parser("find-id", help="Find integration ID by platform name")
    find.add_argument("platform", help="Platform identifier (e.g. youtube, tiktok, instagram)")

    args = parser.parse_args()

    if args.cmd == "list":
        cmd_list()
    elif args.cmd == "upload":
        cmd_upload(args.file)
    elif args.cmd == "post":
        cmd_post(
            content=args.content,
            integration_id=args.integration_id,
            schedule=args.schedule,
            media=args.media,
            settings=args.settings,
            comment=args.comment,
            delay=args.delay,
            draft=args.draft,
        )
    elif args.cmd == "analytics-post":
        cmd_analytics_post(args.post_id, args.days)
    elif args.cmd == "analytics-platform":
        cmd_analytics_platform(args.integration_id, args.days)
    elif args.cmd == "missing":
        cmd_missing(args.post_id)
    elif args.cmd == "connect":
        cmd_connect(args.post_id, args.release_id)
    elif args.cmd == "delete":
        cmd_delete(args.post_id)
    elif args.cmd == "list-posts":
        cmd_list_posts(args.start, args.end)
    elif args.cmd == "find-id":
        cmd_find_id(args.platform)


if __name__ == "__main__":
    main()
