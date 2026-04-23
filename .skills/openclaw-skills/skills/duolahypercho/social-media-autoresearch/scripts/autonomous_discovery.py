#!/usr/bin/env python3
"""autonomous_discovery.py — Automatically find new videos to clip.

Runs as part of the autonomous loop. Discovers new videos from:
  - RSS feeds (YouTube channels, topic feeds)
  - YouTube search (keyword-based)
  - Trending content in target niches

Outputs new video URLs to the content queue for the autonomous loop to process.

Usage:
  python3 autonomous_discovery.py              # Run discovery for all sources
  python3 autonomous_discovery.py --check      # Verify sources are accessible
  python3 autonomous_discovery.py --feeds       # RSS feeds only
  python3 autonomous_discovery.py --search      # Search only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────

QUEUE_FILE  = Path("outputs/content_queue.json")
STATE_FILE  = Path("outputs/discovery_state.json")

# Target niches — change these to match your content strategy
TARGET_NICHES = [
    "AI productivity",
    "deep work focus",
    "high performance habits",
    "founder mindset",
    "knowledge books summary",
]

# RSS feed URLs — add YouTube channel RSS feeds here
# Format: https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxx
# Or for search: https://www.youtube.com/feeds/videos.xml?query=keyword
RSS_FEEDS = [
    # Add your target channel RSS feeds here
    # Example: "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxx",
]

# Channels to monitor — these are monitored via RSS
CHANNELS = [
    # Add channel IDs to monitor
    # "UCxxxxxxx",
]

MAX_NEW_VIDEOS_PER_RUN = 5   # Max new videos to add to queue per run
DAYS_LOOKBACK          = 3   # Only find videos from the last N days


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_discovery": None, "seen_ids": [], "queue_ids": []}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_queue() -> list[dict]:
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def save_queue(queue: list[dict]) -> None:
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False))


def add_to_queue(videos: list[dict]) -> int:
    """Add new videos to the queue. Returns count of newly added."""
    queue  = get_queue()
    state  = get_state()
    seen   = set(state.get("seen_ids", []))
    existing_ids = {v["video_id"] for v in queue}

    added = 0
    for video in videos:
        vid = video.get("video_id") or extract_video_id(video.get("url", ""))
        if vid and vid not in seen and vid not in existing_ids:
            queue.append({**video, "queued_at": datetime.now(timezone.utc).isoformat()})
            seen.add(vid)
            added += 1

    save_queue(queue)
    state["seen_ids"] = list(seen)
    state["last_discovery"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    return added


def extract_video_id(url: str) -> Optional[str]:
    patterns = [
        r"watch\?v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"/shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def is_recent(published_str: str, days: int = DAYS_LOOKBACK) -> bool:
    """Check if a video was published within the lookback window."""
    if not published_str:
        return True  # No date = include it
    try:
        # Try parsing various date formats
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                pub = datetime.strptime(published_str[:19], fmt[:len(published_str[:19])])
                cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                return pub.replace(tzinfo=timezone.utc) >= cutoff
            except ValueError:
                continue
        return True
    except Exception:
        return True


def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch a URL, return body or None."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "autoresearch-discovery/1.0", "Accept": "application/xml, application/rss+xml, text/xml"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠️  Failed to fetch {url[:60]}...: {e}", file=sys.stderr)
        return None


def parse_youtube_rss(xml_body: str) -> list[dict]:
    """Parse a YouTube RSS feed and return list of videos."""
    videos = []
    # Simple regex-based XML parsing (no lxml dependency)
    entries = re.findall(r"<entry>(.*?)</entry>", xml_body, re.DOTALL)
    for entry in entries:
        video_id_m = re.search(r"<yt:videoId>(.*?)</yt:videoId>", entry)
        title_m   = re.search(r"<title>(.*?)</title>", entry)
        pub_m     = re.search(r"<published>(.*?)</published>", entry)
        link_m    = re.search(r'<link[^>]+href="(https://www\.youtube\.com/watch\?v=[^"]+)"', entry)
        if video_id_m and title_m:
            videos.append({
                "video_id":   video_id_m.group(1).strip(),
                "title":      re.sub(r"<[^>]+>", "", title_m.group(1)).strip(),
                "url":        link_m.group(1).strip() if link_m else f"https://www.youtube.com/watch?v={video_id_m.group(1)}",
                "published":  pub_m.group(1).strip() if pub_m else "",
                "source":    "rss",
            })
    return videos


def parse_generic_rss(xml_body: str) -> list[dict]:
    """Parse a generic RSS/Atom feed for video links."""
    videos = []
    # Find all item/entry blocks
    items = re.findall(r"<item>(.*?)</item>|<entry>(.*?)</entry>", xml_body, re.DOTALL)
    for item in items:
        block = item[0] or item[1]
        # Look for YouTube URLs
        urls = re.findall(r"https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}", block)
        title_m = re.search(r"<title>(.*?)</title>", block)
        pub_m   = re.search(r"<published>(.*?)</published>|<pubDate>(.*?)</pubDate>", block)
        for url in set(urls):
            vid = extract_video_id(url)
            if vid:
                videos.append({
                    "video_id":   vid,
                    "title":      re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else "",
                    "url":        url,
                    "published":  (pub_m.group(1) or pub_m.group(2) or "").strip(),
                    "source":     "rss",
                })
    return videos


# ── Discovery Sources ─────────────────────────────────────────────────────────

def discover_from_rss() -> list[dict]:
    """Discover new videos from RSS feeds."""
    all_videos = []
    for feed_url in RSS_FEEDS:
        print(f"  📡 Fetching RSS: {feed_url[:60]}...")
        body = fetch_url(feed_url)
        if not body:
            continue
        if "youtube.com" in feed_url or "yt:videoId" in body:
            videos = parse_youtube_rss(body)
        else:
            videos = parse_generic_rss(body)
        # Filter to recent only
        videos = [v for v in videos if is_recent(v.get("published", ""))]
        print(f"     Found {len(videos)} recent videos")
        all_videos.extend(videos)
        time.sleep(0.5)  # Rate limit
    return all_videos


def discover_from_search() -> list[dict]:
    """Discover new videos from YouTube search via RSS."""
    all_videos = []
    for niche in TARGET_NICHES:
        # YouTube search RSS feed
        query   = urllib.parse.quote(niche)
        rss_url = f"https://www.youtube.com/feeds/videos.xml?search_query={query}"
        print(f"  🔍 Searching: {niche}...")
        body = fetch_url(rss_url)
        if not body:
            continue
        videos = parse_youtube_rss(body)
        # Filter recent
        videos = [v for v in videos if is_recent(v.get("published", ""))]
        # Tag with niche
        for v in videos:
            v["niche"] = niche
        print(f"     Found {len(videos)} recent videos")
        all_videos.extend(videos)
        time.sleep(1.0)  # Be polite
    return all_videos


def discover_from_channels() -> list[dict]:
    """Discover new videos from monitored channel RSS feeds."""
    all_videos = []
    for channel_id in CHANNELS:
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        print(f"  📺 Channel {channel_id[:12]}...: ", end="", flush=True)
        body = fetch_url(rss_url)
        if not body:
            print("failed")
            continue
        videos = parse_youtube_rss(body)
        videos = [v for v in videos if is_recent(v.get("published", ""))]
        print(f"{len(videos)} recent videos")
        all_videos.extend(videos)
        time.sleep(0.5)
    return all_videos


def check_sources() -> None:
    """Verify all configured sources are accessible."""
    print("Checking RSS feeds...")
    for feed_url in RSS_FEEDS:
        body = fetch_url(feed_url)
        status = "✅" if body and ("<feed" in body or "<rss" in body) else "❌"
        print(f"  {status} {feed_url[:70]}")

    print("\nChecking channel feeds...")
    for channel_id in CHANNELS:
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        body = fetch_url(rss_url)
        status = "✅" if body and "yt:videoId" in body else "❌"
        print(f"  {status} {channel_id[:12]}...")

    print("\nChecking search feeds...")
    for niche in TARGET_NICHES[:3]:  # Sample first 3
        query   = urllib.parse.quote(niche)
        rss_url = f"https://www.youtube.com/feeds/videos.xml?search_query={query}"
        body = fetch_url(rss_url)
        status = "✅" if body and "yt:videoId" in body else "❌"
        print(f"  {status} search:{niche[:30]}")


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous video discovery")
    parser.add_argument("--check",  action="store_true", help="Verify sources are accessible")
    parser.add_argument("--feeds",  action="store_true", help="RSS feeds only")
    parser.add_argument("--search", action="store_true", help="Search only")
    parser.add_argument("--channels", action="store_true", help="Channel feeds only")
    args = parser.parse_args()

    if args.check:
        check_sources()
        return

    all_videos = []

    if args.feeds or (not args.search and not args.channels):
        all_videos += discover_from_rss()

    if args.search or (not args.feeds and not args.channels):
        all_videos += discover_from_search()

    if args.channels or (not args.feeds and not args.search):
        all_videos += discover_from_channels()

    # Dedupe by video_id
    seen_ids = set()
    unique   = []
    for v in all_videos:
        if v["video_id"] not in seen_ids:
            seen_ids.add(v["video_id"])
            unique.append(v)

    if not unique:
        print("No new videos found.")
        sys.exit(0)

    added = add_to_queue(unique[:MAX_NEW_VIDEOS_PER_RUN])

    queue = get_queue()
    print(f"\n✅ Discovery complete")
    print(f"   New videos found: {len(unique)}")
    print(f"   Added to queue: {added}")
    print(f"   Total in queue: {len(queue)}")
    print(f"\nQueue preview:")
    for v in queue[:5]:
        title = v.get("title", "untitled")[:50]
        niche = v.get("niche", "general")
        print(f"  [{niche[:20]}] {title}")


if __name__ == "__main__":
    main()
