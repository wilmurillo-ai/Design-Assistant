#!/usr/bin/env python3
"""selector.py — Pick the best DISCOVERED video to clip next.

Selects based on:
  1. Score (viral potential)
  2. Topic/niche match
  3. Recency (prefer newer uploads)
  4. Duration (>= 30 minutes required)

Usage:
  python3 selector.py              # Pick best and mark SELECTED
  python3 selector.py --list      # Show top candidates without selecting
  python3 selector.py --reset    # Reset all SELECTED back to DISCOVERED
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR  = Path(__file__).parent.parent.resolve()
DATA_DIR   = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
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


def _days_ago(upload_date: str) -> int | None:
    if not upload_date:
        return None
    try:
        dt = datetime.strptime(str(upload_date)[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return None


def get_best_candidates() -> list[dict]:
    """Return all DISCOVERED videos >= 30 min, scored by rank."""
    data     = load_videos()
    strategy = load_strategy()
    MIN_DUR  = 1800  # 30 min

    preferred_kw = [kw.lower() for kw in strategy.get("niches", [])]
    excluded_kw  = [kw.lower() for kw in strategy.get("skip_topics", [])]
    require_match = strategy.get("require_niche_match", False)

    candidates = []
    for v in data.get("videos", []):
        if v.get("status") != "DISCOVERED":
            continue

        # Duration filter
        dur = v.get("duration", 0)
        try:
            dur = float(dur) if dur not in (None, "", "NA", 0) else 0.0
        except Exception:
            dur = 0.0
        if dur < MIN_DUR:
            continue

        # Exclusion filter
        title = v.get("title", "").lower()
        if any(kw in title for kw in excluded_kw):
            continue

        # Score
        base_score = v.get("score") or 50
        try:
            base_score = float(base_score)
        except Exception:
            base_score = 50.0

        # Niche match bonus
        niche_bonus = 0
        for kw in preferred_kw:
            if kw and kw in title:
                niche_bonus += 5

        # Recency tiebreaker
        da = _days_ago(v.get("upload_date", ""))
        recency = -da if da is not None else 0

        # Views tiebreaker
        try:
            views = int(v.get("views", 0))
        except Exception:
            views = 0

        rank = (base_score + niche_bonus, views, recency)
        candidates.append((rank, v))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [v for _, v in candidates]


def mark_selected(video: dict, note: str = "") -> None:
    vid = video.get("video_id")
    data = load_videos()
    for v in data.get("videos", []):
        if v.get("video_id") == vid:
            v["status"] = "SELECTED"
            v["selected_date"] = datetime.now().strftime("%Y-%m-%d")
            v.setdefault("pipeline_log", []).append({
                "step": "SELECTED",
                "timestamp": now_iso(),
                "note": note or f"Selected for clipping (score: {v.get('score')})",
            })
            save_videos(data)
            return
    raise KeyError(f"Video not found: {vid}")


def reset_all_selected() -> int:
    """Reset all SELECTED videos back to DISCOVERED."""
    data = load_videos()
    count = 0
    for v in data.get("videos", []):
        if v.get("status") == "SELECTED":
            v["status"] = "DISCOVERED"
            v.setdefault("pipeline_log", []).append({
                "step": "RESET",
                "timestamp": now_iso(),
                "note": "Reset to DISCOVERED by selector.py",
            })
            count += 1
    if count:
        save_videos(data)
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Select best video to clip next")
    parser.add_argument("--list",  action="store_true", help="Show candidates without selecting")
    parser.add_argument("--reset", action="store_true", help="Reset all SELECTED to DISCOVERED")
    args = parser.parse_args()

    if args.reset:
        n = reset_all_selected()
        print(f"✅ Reset {n} video(s) to DISCOVERED")
        return

    candidates = get_best_candidates()

    if args.list:
        print(f"\n📋 Top candidates ({len(candidates)} DISCOVERED, >= 30min):")
        for i, v in enumerate(candidates[:10], 1):
            dur = v.get("duration", "?")
            try:
                dur = f"{float(dur)/60:.1f}m" if dur else "?"
            except Exception:
                pass
            print(f"\n  {i}. {v.get('title', '')[:50]}")
            print(f"     📺 {v.get('channel')} | 👁 {v.get('views')} | ⏱ {dur} | 📊 {v.get('score')}")
        return

    if not candidates:
        print("❌ No DISCOVERED videos available (need >= 30min duration)")
        print("   Run: python3 discovery.py to find new videos")
        sys.exit(1)

    best = candidates[0]
    strategy = load_strategy()
    is_match = any(
        kw.lower() in best.get("title", "").lower()
        for kw in strategy.get("niches", [])
        if kw
    )
    note = "niche=target" if is_match else "niche=fallback"
    mark_selected(best, note)

    print(f"\n🎬 Selected:")
    print(f"   Title:    {best.get('title')}")
    print(f"   Channel:  {best.get('channel')}")
    print(f"   URL:      {best.get('url')}")
    print(f"   Views:    {best.get('views')}")
    print(f"   Duration: {best.get('duration')}s")
    print(f"   Score:    {best.get('score')}")
    print(f"   Note:     {note}")
    print(f"\n✅ Marked as SELECTED — ready for clip_runner.py")


if __name__ == "__main__":
    main()
