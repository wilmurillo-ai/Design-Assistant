#!/usr/bin/env python3
"""collector.py — Collect engagement metrics from Postiz.

Usage:
  python3 collector.py --source postiz --days 3   # From Postiz
  python3 collector.py --source manual             # Paste manually
  python3 collector.py --source postiz --days 1   # Quick daily check
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILL_DIR   = Path(__file__).parent.parent.resolve()
DATA_DIR    = SKILL_DIR / "data" / "engagement"
DATA_DIR.mkdir(parents=True, exist_ok=True)
POSTIZ_TOKEN = os.getenv("POSTIZ_TOKEN", "")


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def output_file() -> Path:
    return DATA_DIR / f"{today()}.json"


def load_existing() -> list[dict]:
    f = output_file()
    if f.exists():
        return json.loads(f.read_text())
    return []


def save_records(records: list[dict]) -> None:
    output_file().write_text(json.dumps(records, indent=2, ensure_ascii=False))


def collect_postiz(days: int = 3) -> list[dict]:
    """Fetch recent posts + metrics from Postiz."""
    if not POSTIZ_TOKEN:
        print("ERROR: POSTIZ_TOKEN not set.", file=sys.stderr)
        print("  export POSTIZ_TOKEN=your_token", file=sys.stderr)
        print("  Or use: --source manual", file=sys.stderr)
        sys.exit(1)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    headers = {
        "Authorization": f"Bearer {POSTIZ_TOKEN}",
        "Content-Type": "application/json",
    }

    import urllib.request
    url = "https://api.postiz.com/v1/posts"
    params = f"?after={cutoff.isoformat()}&limit=100&include_metrics=true"

    try:
        req = urllib.request.Request(url + params, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"ERROR: Postiz API failed: {e}", file=sys.stderr)
        sys.exit(1)

    posts = data.get("posts", data) if isinstance(data, dict) else data
    results = []
    for post in posts:
        if not isinstance(post, dict):
            continue
        m = post.get("metrics", {})
        results.append({
            "post_id":         post.get("id", ""),
            "platform":        post.get("channel", post.get("platform", "unknown")),
            "posted_at":       post.get("publishedAt", ""),
            "content":         post.get("content", "")[:200],
            "views":           m.get("views", 0),
            "likes":           m.get("likes", 0),
            "retweets":        m.get("retweets", 0) or m.get("shares", 0),
            "replies":         m.get("replies", 0),
            "bookmarks":       m.get("bookmarks", 0) or m.get("saves", 0),
            "impressions":     m.get("impressions", 0),
            "completion_rate": m.get("completionRate"),
            "collected_at":    datetime.now(timezone.utc).isoformat(),
        })
    return results


def collect_manual() -> list[dict]:
    """Interactive manual entry."""
    print("\n📋 Manual entry — paste metrics. Ctrl+C to finish.\n")
    results = []
    while True:
        try:
            pid    = input("Post ID (Enter to finish): ").strip()
            if not pid:
                break
            results.append({
                "post_id":         pid,
                "platform":        "manual",
                "posted_at":       "",
                "content":         "",
                "views":           int(input("  Views:      ") or 0),
                "likes":           int(input("  Likes:      ") or 0),
                "retweets":        int(input("  Retweets:   ") or 0),
                "replies":         int(input("  Replies:    ") or 0),
                "bookmarks":       int(input("  Bookmarks:  ") or 0),
                "impressions":     int(input("  Impressions:") or 0),
                "completion_rate": None,
                "collected_at":    datetime.now(timezone.utc).isoformat(),
            })
        except (EOFError, KeyboardInterrupt):
            print()
            break
    return results


def merge_and_save(new_records: list[dict]) -> None:
    existing = load_existing()
    by_id = {r["post_id"]: r for r in existing}
    for rec in new_records:
        by_id[rec["post_id"]] = rec
    merged = sorted(by_id.values(), key=lambda r: r.get("collected_at", ""), reverse=True)
    save_records(merged)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect engagement metrics")
    parser.add_argument("--source", choices=["postiz", "manual"], default="postiz")
    parser.add_argument("--days",   type=int, default=3)
    args = parser.parse_args()

    records = collect_postiz(args.days) if args.source == "postiz" else collect_manual()

    if not records:
        print("No records collected.")
        sys.exit(0)

    merge_and_save(records)
    print(f"\n✅ Saved {len(records)} new records to {output_file()}")
    print(f"   Total in file: {len(load_existing())}")

    print("\n─── Summary ──────────────────────────────")
    for r in records:
        print(f"  {r['platform']}/{r['post_id'][:10]} | "
              f"views={r['views']:,} | likes={r['likes']} | "
              f"RT={r['retweets']}")


if __name__ == "__main__":
    main()
