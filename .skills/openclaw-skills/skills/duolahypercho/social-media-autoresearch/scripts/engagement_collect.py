#!/usr/bin/env python3
"""engagement_collect.py — collect engagement metrics from Postiz or paste them manually.

Usage:
  python3 engagement_collect.py --source postiz --days 3   # From Postiz
  python3 engagement_collect.py --source manual             # Paste them yourself

Output: outputs/engagement/<date>.json  (one file per run, merged by post_id)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

POSTIZ_API_URL = os.getenv("POSTIZ_API_URL", "https://api.postiz.com")
POSTIZ_TOKEN   = os.getenv("POSTIZ_TOKEN", "")

# ── Paths ─────────────────────────────────────────────────────────────────────

def output_dir() -> Path:
    d = Path("outputs/engagement")
    d.mkdir(parents=True, exist_ok=True)
    return d


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ── Postiz ────────────────────────────────────────────────────────────────────

def collect_postiz(days: int = 3) -> list[dict]:
    """Fetch recent posts + metrics from Postiz API.

    Postiz aggregates metrics across all platforms (X, YouTube, TikTok, LinkedIn, etc.)
    so you only need this one source.
    """
    if not POSTIZ_TOKEN:
        print("ERROR: POSTIZ_TOKEN not set.", file=sys.stderr)
        print("  Set it with:  export POSTIZ_TOKEN=your_token", file=sys.stderr)
        print("  Or run with:  --source manual", file=sys.stderr)
        sys.exit(1)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_iso = cutoff.isoformat()

    headers = {
        "Authorization": f"Bearer {POSTIZ_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "autoresearch-engagement/1.0",
    }

    url = f"{POSTIZ_API_URL}/v1/posts"
    params = {"after": cutoff_iso, "limit": 100, "include_metrics": "true"}

    try:
        import urllib.request
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"ERROR: Postiz API request failed: {e}", file=sys.stderr)
        sys.exit(1)

    posts = data.get("posts", data) if isinstance(data, dict) else data
    results = []

    for post in posts:
        if not isinstance(post, dict):
            continue
        m = post.get("metrics", {})
        results.append({
            "post_id":         post.get("id", post.get("_id", "")),
            "platform":        post.get("channel", post.get("platform", "unknown")),
            "posted_at":       post.get("publishedAt", post.get("created_at", "")),
            "content":         post.get("content", post.get("text", ""))[:200],
            "views":           m.get("views", 0),
            "likes":           m.get("likes", 0),
            "retweets":        m.get("retweets", 0) or m.get("shares", 0),
            "replies":         m.get("replies", 0),
            "bookmarks":       m.get("bookmarks", 0) or m.get("saves", 0),
            "impressions":     m.get("impressions", 0),
            "completion_rate": m.get("completionRate") or m.get("completion_rate"),
            "collected_at":    datetime.now(timezone.utc).isoformat(),
        })

    return results


# ── Manual Fallback ───────────────────────────────────────────────────────────

def collect_manual() -> list[dict]:
    """Interactive: paste metrics one post at a time. Works with any platform."""
    print("\n📋 Manual entry mode — paste metrics for each post.")
    print("   Press Ctrl+C to finish.\n")

    results = []
    while True:
        try:
            pid    = input("Post ID (or Enter to finish): ").strip()
            if not pid:
                break
            views  = int(input("  Views:      ") or 0)
            likes  = int(input("  Likes:      ") or 0)
            rts    = int(input("  Retweets:   ") or 0)
            replies= int(input("  Replies:    ") or 0)
            saves  = int(input("  Bookmarks:  ") or 0)
            imps   = int(input("  Impressions:") or 0)
            results.append({
                "post_id":         pid,
                "platform":        "manual",
                "posted_at":       "",
                "content":         "",
                "views":           views,
                "likes":           likes,
                "retweets":        rts,
                "replies":         replies,
                "bookmarks":       saves,
                "impressions":     imps,
                "completion_rate": None,
                "collected_at":    datetime.now(timezone.utc).isoformat(),
            })
            print()
        except (EOFError, KeyboardInterrupt):
            print()
            break

    return results


# ── Merge + Save ─────────────────────────────────────────────────────────────

def merge_and_save(new_records: list[dict]) -> None:
    """Append to daily file, deduplicating by post_id (newer wins)."""
    out_dir   = output_dir()
    out_file  = out_dir / f"{today()}.json"

    existing = json.loads(out_file.read_text()) if out_file.exists() else []

    by_id = {r["post_id"]: r for r in existing}
    for rec in new_records:
        by_id[rec["post_id"]] = rec

    merged = sorted(by_id.values(), key=lambda r: r.get("collected_at", ""), reverse=True)
    out_file.write_text(json.dumps(merged, indent=2, ensure_ascii=False))

    print(f"Saved {len(merged)} total records to {out_file}")
    print(f"  New this run: {len(new_records)}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect engagement metrics from Postiz or paste them manually.")
    parser.add_argument(
        "--source", choices=["postiz", "manual"], default="postiz",
        help="'postiz' = pull from Postiz API (needs POSTIZ_TOKEN env var). "
             "'manual' = paste metrics interactively (no API needed).")
    parser.add_argument(
        "--days", type=int, default=3,
        help="Days of history to fetch from Postiz (default: 3)")
    args = parser.parse_args()

    records = collect_postiz(args.days) if args.source == "postiz" else collect_manual()

    if not records:
        print("No records collected.")
        sys.exit(0)

    merge_and_save(records)

    print("\n─── Summary ───────────────────────────────")
    for r in records:
        print(f"  {r['platform']}/{r['post_id'][:12]} | "
              f"views={r['views']:,} | likes={r['likes']} | "
              f"RT={r['retweets']} | replies={r['replies']}")


if __name__ == "__main__":
    main()
