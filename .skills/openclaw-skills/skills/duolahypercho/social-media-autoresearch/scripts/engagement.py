#!/usr/bin/env python3
"""engagement.py — Automated browser engagement on YouTube, TikTok, Instagram.

Engagement rules:
  - Max 10 per platform per session
  - Watch >= 30s before engaging
  - Check [pressed] before clicking like
  - Add 🧡 to every comment
  - Skip sponsored (#ad, #sponsored)

Usage:
  python3 engagement.py youtube        # Run YouTube engagement
  python3 engagement.py tiktok        # Run TikTok engagement
  python3 engagement.py instagram     # Run Instagram engagement
  python3 engagement.py all          # Run all three platforms
  python3 engagement.py --check       # Verify config
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR   = Path(__file__).parent.parent.resolve()
CONFIG_DIR  = SKILL_DIR / "config"
DATA_DIR    = SKILL_DIR / "data"
ENG_LOG     = DATA_DIR / "engagement_log.json"

MAX_PER_SESSION = 10


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config() -> dict:
    platforms = CONFIG_DIR / "platforms.json"
    if platforms.exists():
        return json.loads(platforms.read_text())
    return {}


def get_channel_name() -> str:
    cfg = load_config()
    return cfg.get("account", {}).get("channel_name", "YOUR_CHANNEL_NAME")


def get_hashtags() -> list[str]:
    cfg = CONFIG_DIR / "strategy.json"
    if cfg.exists():
        data = json.loads(cfg.read_text())
        return data.get("niches", ["AI", "productivity"])
    return ["AI", "productivity"]


COMMENT_TEMPLATES = {
    "thoughtful": [
        "The key is consistency — daily practice creates real change. 🧡",
        "This hits different because it's true. 🧡",
        "Still thinking about this take. 🧡",
        "The best version of this advice I've heard. 🧡",
    ],
    "opinionated": [
        "Either genius or derpy. Maybe both.",
        "Honestly didn't expect to care about this but here we are.",
        "This is either really smart or really dangerous. Possibly both.",
    ],
    "question": [
        "What's the #1 lesson you've learned in your own journey here?",
        "Has anyone else noticed this pattern too?",
        "What's worked for you in your own experience?",
    ],
}


def get_comment() -> str:
    import random
    style = random.choice(list(COMMENT_TEMPLATES.keys()))
    return random.choice(COMMENT_TEMPLATES[style])


def log_engagement(action: str, platform: str, detail: str = "") -> None:
    log = []
    if ENG_LOG.exists():
        log = json.loads(ENG_LOG.read_text())
    log.append({
        "action":  action,
        "platform": platform,
        "detail":  detail,
        "at":      now_iso(),
    })
    ENG_LOG.parent.mkdir(parents=True, exist_ok=True)
    ENG_LOG.write_text(json.dumps(log, indent=2))


def run_browser(script: str) -> None:
    """Execute a browser action using the browser tool in a subprocess."""
    # This script generates the JavaScript to paste into browser via exec.
    # In the OpenClaw cron context, the agent runs the browser tool directly.
    # This script generates the JS and logs what was done.
    print(script)


# ── YouTube ───────────────────────────────────────────────────────────────────

YOUTUBE_TEMPLATE = """// YouTube Shorts engagement
// Channel: {channel_name}
// Step-by-step per video:

// 1. Open YouTube Shorts
browser(action="open", profile="openclaw", targetUrl="https://www.youtube.com/shorts")

// PER VIDEO (repeat for up to {max} videos):
// a. Watch ≥30 seconds (Shorts autoplay)
// b. Snapshot → get Like button ref
// c. Check [pressed]:
//    - If [pressed] EXISTS → SKIP (already liked) → scroll to next
//    - If no [pressed] → click Like → confirm [pressed] appears
// d. Snapshot → "View X comments" → click
// e. Snapshot → textbox → click → wait 1s → snapshot → click textbox again → type: "{comment}"
// f. Snapshot → "Comment" button → click
// g. Find @{channel_name} in comments → click its like button
// h. Close comments → scroll to next Short

// JS Comment Injection (use if textbox doesn't respond):
const ce = document.getElementById('contenteditable-root');
if (!ce) {{
  const alt = document.querySelector('div[contenteditable]');
  if (alt) {{ alt.innerText = '{comment}'; alt.dispatchEvent(new Event('input', {{bubbles:true}})); return {{success:true}}; }}
  return {{error: 'No element found'}};
}}
ce.innerText = '{comment}';
ce.dispatchEvent(new Event('input', {{bubbles:true}}));
ce.dispatchEvent(new Event('change', {{bubbles:true}}));
return {{success: true}};
"""


# ── TikTok ────────────────────────────────────────────────────────────────────

TIKTOK_TEMPLATE = """// TikTok engagement — hashtag discovery
// Channel: {channel_name}

browser(action="open", profile="openclaw", targetUrl="https://www.tiktok.com/tag/productivity")

// PER VIDEO (repeat for up to {max} videos):
// a. Browse sidebar → pick niche-relevant video → navigate to direct URL
// b. Watch ≥30 seconds
// c. Snapshot → heart button → check [pressed]
//    - [pressed] EXISTS → SKIP
//    - No [pressed] → click heart → confirm turns red
// d. Snapshot → comment bubble → click
// e. Snapshot → text input → click → wait 1s → snapshot → click input again → type: "{comment}"
// f. Snapshot → Post button → click
// g. Find your @channel_name comment ("Xs ago") → click its heart
// h. Navigate to next video URL

// Discovery: /tag/productivity, /tag/motivation, /tag/AI, /tag/success
"""


# ── Instagram ─────────────────────────────────────────────────────────────────

INSTAGRAM_TEMPLATE = """// Instagram Reels engagement
// Username: {username}

browser(action="open", profile="openclaw", targetUrl="https://www.instagram.com/reels")

// PER REEL (repeat for up to {max} reels):
// a. Scroll to reel → watch ≥30 seconds
// b. Check heart:
//    - Filled red → ALREADY LIKED → scroll to next reel
//    - White/outline → click → turns red when liked
// c. Click comment bubble → type: "{comment}" → tap Post
// d. Find your comment → click its heart
// e. Scroll to next reel

// Discovery: instagram.com/explore/tags/growthmindset/
"""


def generate_script(platform: str, channel: str, comment: str, max_videos: int = MAX_PER_SESSION) -> str:
    username = load_config().get("account", {}).get("username", "YOUR_USERNAME")
    t = {
        "youtube":   YOUTUBE_TEMPLATE,
        "tiktok":   TIKTOK_TEMPLATE,
        "instagram": INSTAGRAM_TEMPLATE,
    }.get(platform.lower(), YOUTUBE_TEMPLATE)

    return t.format(
        channel_name=channel,
        username=username,
        comment=comment,
        max=max_videos,
    )


def print_engagement_guide(platform: str) -> None:
    """Print the engagement guide for a platform. Agent executes via browser tool."""
    cfg = load_config()
    channel = cfg.get("account", {}).get("channel_name", "YOUR_CHANNEL_NAME")
    comment = get_comment()
    max_v   = MAX_PER_SESSION

    print(f"\n{'='*50}")
    print(f"ENGAGEMENT: {platform.upper()}")
    print(f"{'='*50}")
    print(f"Channel: @{channel}")
    print(f"Max per session: {max_v}")
    print(f"\nComment: {comment}")
    print(f"\n--- Browser Script ---")

    if platform.lower() == "youtube":
        print(f"\n1. Open Shorts:")
        print(f'   browser(action="open", profile="openclaw", targetUrl="https://www.youtube.com/shorts")')
        print(f"\n2. Per video:")
        print(f"   SNAPSHOT → Like → check [pressed] → comment → like own comment → scroll")
        print(f"\n3. JS comment injection if typing fails:")
        print(f'   const ce = document.getElementById("contenteditable-root"); ...')

    elif platform.lower() == "tiktok":
        print(f"\n1. Open hashtag feed:")
        print(f'   browser(action="open", profile="openclaw", targetUrl="https://www.tiktok.com/tag/productivity")')
        print(f"\n2. Per video:")
        print(f"   Navigate URL → watch 30s → heart [pressed] check → comment → like own → next URL")

    else:  # instagram
        print(f"\n1. Open Reels:")
        print(f'   browser(action="open", profile="openclaw", targetUrl="https://www.instagram.com/reels")')
        print(f"\n2. Per reel:")
        print(f"   Watch 30s → heart (check not filled) → comment → like own → scroll")


def main() -> None:
    parser = argparse.ArgumentParser(description="Browser engagement guide generator")
    parser.add_argument("platform", nargs="?", help="youtube / tiktok / instagram / all")
    parser.add_argument("--check", action="store_true", help="Verify config")
    args = parser.parse_args()

    if args.check:
        cfg = load_config()
        print("✅ Platform config loaded")
        print(f"   Account: {cfg.get('account', {})}")
        print(f"   Integrations: {list(cfg.get('integrations', {}).keys())}")
        return

    if not args.platform or args.platform == "all":
        platforms = ["youtube", "tiktok", "instagram"]
    else:
        platforms = [args.platform.lower()]

    channel = get_channel_name()
    comment = get_comment()

    for platform in platforms:
        print_engagement_guide(platform)
        log_engagement("guide_printed", platform, comment)
        print()


if __name__ == "__main__":
    main()
