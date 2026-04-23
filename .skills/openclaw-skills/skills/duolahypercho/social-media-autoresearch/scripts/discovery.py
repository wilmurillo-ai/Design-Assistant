#!/usr/bin/env python3
"""discovery.py — Automatically discover new videos to clip.

Discovers from three sources:
  1. YouTube channel scanning (yt-dlp)
  2. RSS feeds (YouTube channel RSS)
  3. YouTube topic search via RSS

Stores results in data/videos.json.

Usage:
  python3 discovery.py                 # Run all sources
  python3 discovery.py --check-sources  # Verify sources are accessible
  python3 discovery.py --channels       # Channel scan only
  python3 discovery.py --rss           # RSS only
  python3 discovery.py --search        # Topic search only
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

# ── Paths ────────────────────────────────────────────────────────────────────

SKILL_DIR   = Path(__file__).parent.parent.resolve()
CONFIG_DIR  = SKILL_DIR / "config"
DATA_DIR    = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

VIDEOS_FILE = DATA_DIR / "videos.json"
STATE_FILE  = DATA_DIR / "discovery_state.json"

# ── Config ───────────────────────────────────────────────────────────────────

def load_config(name: str) -> dict:
    path = CONFIG_DIR / f"{name}.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def load_channels() -> list[dict]:
    return load_config("channels").get("channels", [])


def load_strategy() -> dict:
    return load_config("strategy")


def load_videos() -> dict:
    if VIDEOS_FILE.exists():
        return json.loads(VIDEOS_FILE.read_text())
    return {"videos": [], "last_updated": None}


def save_videos(data: dict) -> None:
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    VIDEOS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"seen_ids": [], "last_discovery": None}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── Helpers ─────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "autoresearch-discovery/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠️  Failed: {url[:60]}... — {e}", file=sys.stderr)
        return None


def parse_youtube_rss(xml_body: str) -> list[dict]:
    videos = []
    entries = re.findall(r"<entry>(.*?)</entry>", xml_body, re.DOTALL)
    for entry in entries:
        vid_m  = re.search(r"<yt:videoId>(.*?)</yt:videoId>", entry)
        title_m = re.search(r"<title>(.*?)</title>", entry)
        pub_m  = re.search(r"<published>(.*?)</published>", entry)
        link_m = re.search(r'<link[^>]+href="(https://www\.youtube\.com/watch\?v=[^"]+)"', entry)
        if vid_m and title_m:
            title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
            videos.append({
                "video_id":  vid_m.group(1).strip(),
                "title":     title,
                "url":       link_m.group(1).strip() if link_m
                            else f"https://youtube.com/watch?v={vid_m.group(1).strip()}",
                "published": pub_m.group(1).strip() if pub_m else "",
                "source":    "rss",
            })
    return videos


def is_recent(published_str: str, days: int = 30) -> bool:
    if not published_str:
        return True
    try:
        pub = published_str[:10]
        dt = datetime.strptime(pub[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days <= days
    except Exception:
        return True


# ── Source 1: Channel Scan ─────────────────────────────────────────────────────

def scan_channel(channel: dict, strategy: dict) -> list[dict]:
    """Scan a YouTube channel for recent videos using yt-dlp."""
    name = channel.get("name", "unknown")
    url  = channel.get("url", "")
    max_days = strategy.get("max_age_days", 30)
    print(f"\n🔍 Scanning channel: {name}")

    dateafter = (datetime.now() - timedelta(days=max_days)).strftime("%Y%m%d")

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dateafter", dateafter,
        "--print", "%(title)s|%(id)s|%(view_count)s|%(upload_date)s|%(duration)s|%(url)s",
        "--", url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  ⚠️  yt-dlp failed: {result.stderr[:100]}")
            return []
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return []

    videos = []
    for line in result.stdout.strip().split("\n"):
        if "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) < 6:
            continue
        title    = "|".join(parts[:-5])
        video_id = parts[-5].strip()
        views    = parts[-4].strip()
        date     = parts[-3].strip()
        duration = parts[-2].strip()
        video_url = parts[-1].strip()

        if not video_id:
            continue

        videos.append({
            "video_id":  video_id,
            "title":     title.strip(),
            "url":       video_url or f"https://youtube.com/watch?v={video_id}",
            "views":     views,
            "upload_date": date,
            "duration":   duration,
            "channel":   name,
            "source":    "channel",
            "scanned_at": now_iso(),
        })

    print(f"  ✅ Found {len(videos)} videos")
    return videos


def scan_all_channels(strategy: dict) -> list[dict]:
    channels = load_channels()
    all_videos = []
    for ch in channels:
        all_videos.extend(scan_channel(ch, strategy))
        time.sleep(1)
    return all_videos


# ── Source 2: RSS Feeds ──────────────────────────────────────────────────────

def scan_rss_feeds(strategy: dict) -> list[dict]:
    channels_cfg = load_config("channels")
    feeds = channels_cfg.get("rss_feeds", [])
    all_videos = []
    max_days = strategy.get("max_age_days", 30)

    for feed_url in feeds:
        print(f"\n📡 RSS: {feed_url[:60]}...")
        body = fetch_url(feed_url)
        if not body:
            continue
        videos = parse_youtube_rss(body)
        videos = [v for v in videos if is_recent(v.get("published", ""), max_days)]
        print(f"  ✅ {len(videos)} recent videos")
        all_videos.extend(videos)
        time.sleep(0.5)

    return all_videos


# ── Source 3: Topic Search ─────────────────────────────────────────────────────

def scan_topics(strategy: dict) -> list[dict]:
    channels_cfg = load_config("channels")
    topics = channels_cfg.get("search_topics", strategy.get("niches", ["AI productivity"]))
    all_videos = []
    max_days = strategy.get("max_age_days", 30)

    for topic in topics:
        query = urllib.parse.quote(topic)
        rss_url = f"https://www.youtube.com/feeds/videos.xml?search_query={query}"
        print(f"\n🔍 Search: {topic}")
        body = fetch_url(rss_url)
        if not body:
            continue
        videos = parse_youtube_rss(body)
        videos = [v for v in videos if is_recent(v.get("published", ""), max_days)]
        for v in videos:
            v["niche"] = topic
        print(f"  ✅ {len(videos)} recent videos")
        all_videos.extend(videos)
        time.sleep(1)

    return all_videos


# ── Scoring ───────────────────────────────────────────────────────────────────

def calculate_score(video: dict, strategy: dict) -> int:
    score = 50  # base

    # View count
    try:
        views = int(video.get("views", 0))
        if views > 10_000_000: score += 15
        elif views > 5_000_000: score += 10
        elif views > 1_000_000: score += 5
    except (ValueError, TypeError):
        pass

    # Title keywords
    title = video.get("title", "").lower()
    viral_kw = ["truth", "secret", "never", "always", "mistake", "changed",
                 "explained", "real", "actually", "shocking", "exposed", "warning",
                 "surprising", "breaks", "rules", "lies", "hidden", "simple"]
    for kw in viral_kw:
        if kw in title:
            score += 5

    # Niche match
    niches = strategy.get("niches", [])
    for niche in niches:
        if niche.lower() in title:
            score += 3

    return score


# ── Add to Tracker ─────────────────────────────────────────────────────────────

def add_to_tracker(new_videos: list[dict], strategy: dict) -> int:
    data  = load_videos()
    state = load_state()
    seen  = set(state.get("seen_ids", []))
    existing_ids = {v["video_id"] for v in data["videos"]}

    added = 0
    for video in new_videos:
        vid = video.get("video_id")
        if not vid or vid in seen or vid in existing_ids:
            continue

        video["status"]           = "DISCOVERED"
        video["discovered_date"]  = datetime.now().strftime("%Y-%m-%d")
        video["score"]            = calculate_score(video, strategy)
        video["pipeline_log"]     = [{"step": "DISCOVERED", "timestamp": now_iso()}]

        data["videos"].append(video)
        seen.add(vid)
        added += 1

    save_videos(data)
    state["seen_ids"] = seen
    state["last_discovery"] = now_iso()
    save_state(state)

    return added


# ── Check Sources ─────────────────────────────────────────────────────────────

def check_sources() -> None:
    channels = load_channels()
    cfg = load_config("channels")
    feeds = cfg.get("rss_feeds", [])
    topics = cfg.get("search_topics", [])

    print("Checking channel URLs...")
    for ch in channels:
        url = ch.get("url", "")
        if url:
            ok = fetch_url(url) is not None
            print(f"  {'✅' if ok else '❌'} {ch['name']}: {url[:60]}")

    print("\nChecking RSS feeds...")
    for feed in feeds:
        body = fetch_url(feed)
        ok = body and ("<feed" in body or "yt:videoId" in body)
        print(f"  {'✅' if ok else '❌'} {feed[:70]}")

    print("\nChecking search topics...")
    for topic in topics[:3]:
        query = urllib.parse.quote(topic)
        url = f"https://www.youtube.com/feeds/videos.xml?search_query={query}"
        body = fetch_url(url)
        ok = body and "yt:videoId" in body
        print(f"  {'✅' if ok else '❌'} search:{topic[:30]}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Discover new videos to clip")
    parser.add_argument("--check-sources", action="store_true")
    parser.add_argument("--channels", action="store_true")
    parser.add_argument("--rss",      action="store_true")
    parser.add_argument("--search",   action="store_true")
    args = parser.parse_args()

    if args.check_sources:
        check_sources()
        return

    strategy = load_strategy()
    all_videos = []

    if args.channels or (not args.rss and not args.search):
        all_videos += scan_all_channels(strategy)

    if args.rss or (not args.channels and not args.search):
        all_videos += scan_rss_feeds(strategy)

    if args.search or (not args.channels and not args.rss):
        all_videos += scan_topics(strategy)

    # Dedupe
    seen_ids = set()
    unique   = []
    for v in all_videos:
        if v["video_id"] not in seen_ids:
            seen_ids.add(v["video_id"])
            unique.append(v)

    if not unique:
        print("\nNo new videos found.")
        return

    added = add_to_tracker(unique, strategy)

    # Stats
    min_views = strategy.get("min_video_views", 1_000_000)
    try:
        min_v = int(min_views)
        viral = [v for v in unique if int(v.get("views", 0)) >= min_v]
    except (ValueError, TypeError):
        viral = []

    print(f"\n{'='*50}")
    print(f"✅ Discovery complete")
    print(f"   Total found: {len(unique)}")
    print(f"   Viral ({min_views//1_000_000}M+ views): {len(viral)}")
    print(f"   New added to tracker: {added}")

    queue = load_videos()
    print(f"   Total in tracker: {len(queue['videos'])}")


if __name__ == "__main__":
    main()
