#!/usr/bin/env python3
"""
XQueue Post Engine — checks the queue and posts to X.
Run via cron every 15 minutes.

Reads credentials from environment variables (X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN,
X_ACCESS_TOKEN_SECRET). Optional macOS Keychain fallback if XQUEUE_KEYCHAIN_ACCOUNT is set.
"""

import base64
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from requests_oauthlib import OAuth1

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
MAX_TWEET_LENGTH = 280
SUPPORTED_MEDIA = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_GIF_BYTES = 15 * 1024 * 1024  # 15MB


def notify_user(message: str):
    """Send a notification to the user via OpenClaw webhook."""
    try:
        # Write to a notification file that heartbeat/cron can pick up
        notif_path = Path.home() / ".openclaw" / "workspace" / "xqueue" / "notifications.log"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(notif_path, "a") as f:
            f.write(f"[{ts}] {message}\n")
        # Also try the OpenClaw gateway API for immediate delivery
        gw_token_path = Path.home() / ".openclaw" / "openclaw.json"
        if gw_token_path.exists():
            import subprocess
            subprocess.run(
                ["openclaw", "wake", "--text", f"XQueue alert: {message}"],
                capture_output=True, timeout=10
            )
    except Exception:
        pass  # Best effort — don't crash the poster


def load_config(queue_dir: Path) -> dict:
    config_path = queue_dir / "config.json"
    if not config_path.exists():
        print(f"ERROR: No config.json in {queue_dir}", file=sys.stderr)
        sys.exit(1)
    return json.loads(config_path.read_text())


def log_action(config: dict, queue_dir: Path, message: str):
    log_path = Path(config.get("logFile", "xqueue/posted.log"))
    # Security: reject absolute paths to prevent arbitrary file writes
    if log_path.is_absolute():
        log_path = Path("xqueue/posted.log")
    log_path = queue_dir.parent / log_path
    # Ensure log stays within the queue parent directory
    try:
        log_path.resolve().relative_to(queue_dir.parent.resolve())
    except ValueError:
        log_path = queue_dir.parent / "xqueue" / "posted.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a") as f:
        f.write(f"[{ts}] {message}\n")


# ---------------------------------------------------------------------------
# OAuth 1.0a (via requests-oauthlib)
# ---------------------------------------------------------------------------

def get_credential(service: str, env_var: str) -> str:
    """Get credential from env var first, fall back to macOS Keychain."""
    val = os.environ.get(env_var, "")
    if val:
        return val
    # macOS Keychain fallback — default account "meimakes", override with XQUEUE_KEYCHAIN_ACCOUNT
    account = os.environ.get("XQUEUE_KEYCHAIN_ACCOUNT", "meimakes")
    if account:
        import subprocess
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
    return ""


def get_oauth() -> OAuth1:
    """Build an OAuth1 instance from credentials."""
    return OAuth1(
        get_credential("x-consumer-key", "X_CONSUMER_KEY"),
        get_credential("x-consumer-secret", "X_CONSUMER_SECRET"),
        get_credential("x-access-token", "X_ACCESS_TOKEN"),
        get_credential("x-access-token-secret", "X_ACCESS_TOKEN_SECRET"),
    )


def oauth_request(method: str, url: str, body: dict = None, params: dict = None) -> dict:
    """Make an OAuth 1.0a signed request to the X API."""
    auth = get_oauth()
    try:
        resp = requests.request(
            method, url, auth=auth, json=body, params=params, timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        error_body = e.response.text if e.response else str(e)
        return {"error": e.response.status_code if e.response else 0, "body": error_body}
    except requests.exceptions.RequestException as e:
        return {"error": 0, "body": str(e)}


def upload_media(file_path: Path) -> str:
    """Upload media to X and return media_id string. Uses v1.1 media upload."""
    auth = get_oauth()
    media_data = file_path.read_bytes()
    media_b64 = base64.b64encode(media_data).decode()

    url = "https://upload.twitter.com/1.1/media/upload.json"
    try:
        resp = requests.post(
            url, auth=auth,
            data={"media_data": media_b64},
            timeout=60
        )
        resp.raise_for_status()
        return str(resp.json()["media_id_string"])
    except requests.exceptions.HTTPError as e:
        print(f"Media upload failed: {e.response.status_code} {e.response.text}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Media upload failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Posting logic
# ---------------------------------------------------------------------------

def split_long_text(text: str, max_len: int = MAX_TWEET_LENGTH) -> list[str]:
    """Split text that exceeds max_len into multiple tweet-sized chunks.
    Splits at paragraph breaks first, then sentence boundaries, preserving meaning."""
    if len(text) <= max_len:
        return [text]

    chunks = []

    # First try splitting on double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    current = ""
    for para in paragraphs:
        candidate = (current + "\n\n" + para).strip() if current else para
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # If single paragraph is too long, split on sentences
            if len(para) > max_len:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current = ""
                for sent in sentences:
                    candidate = (current + " " + sent).strip() if current else sent
                    if len(candidate) <= max_len:
                        current = candidate
                    else:
                        if current:
                            chunks.append(current)
                        current = sent
            else:
                current = para
    if current:
        chunks.append(current)

    return chunks if chunks else [text]


def parse_tweet_file(file_path: Path, separator: str) -> list[dict]:
    """Parse a tweet file into a list of {text, community} dicts.
    Auto-threads tweets that exceed 280 chars."""
    content = file_path.read_text().strip()
    if not content:
        return []

    # Split into individual tweets (for threads)
    parts = [p.strip() for p in content.split(separator)]
    parts = [p for p in parts if p]

    tweets = []
    for part in parts:
        community = None
        text = part

        # Check for community tag
        match = re.match(r"^Post to ([^:]+):\s*(.+)$", part, re.DOTALL)
        if match:
            community = match.group(1).strip()
            text = match.group(2).strip()

        # Auto-thread if too long
        chunks = split_long_text(text)
        for chunk in chunks:
            tweets.append({"text": chunk, "community": community})

    return tweets


def find_media(time_dir: Path) -> list[Path]:
    """Find media files in the time directory."""
    media = []
    for f in sorted(time_dir.iterdir()):
        if f.suffix.lower() in SUPPORTED_MEDIA:
            size = f.stat().st_size
            max_size = MAX_GIF_BYTES if f.suffix.lower() == ".gif" else MAX_IMAGE_BYTES
            if size <= max_size:
                media.append(f)
            else:
                print(f"WARN: {f.name} too large ({size} bytes), skipping", file=sys.stderr)
    return media[:4]  # X max 4 media per tweet


def post_tweets(tweets: list[dict], media_files: list[Path], communities: dict,
                dry_run: bool) -> list[dict]:
    """Post tweets (potentially as a thread). Returns list of results."""
    results = []
    reply_to = None

    # Upload media (attach to first tweet only for threads)
    media_ids = []
    if media_files:
        for mf in media_files:
            if dry_run:
                media_ids.append("DRY_RUN_MEDIA")
            else:
                mid = upload_media(mf)
                if mid:
                    media_ids.append(mid)

    for i, tweet in enumerate(tweets):
        text = tweet["text"]

        # Validate length
        if len(text) > MAX_TWEET_LENGTH:
            results.append({"error": f"Tweet {i+1} is {len(text)} chars (max {MAX_TWEET_LENGTH})", "text": text[:50]})
            continue

        # Build request body
        body = {"text": text}

        # Reply chain for threads
        if reply_to:
            body["reply"] = {"in_reply_to_tweet_id": reply_to}

        # Media (first tweet of thread gets the media)
        if i == 0 and media_ids and media_ids[0] != "DRY_RUN_MEDIA":
            body["media"] = {"media_ids": media_ids}

        # Community posting — X API v2 supports community_id in the tweet body
        community_name = tweet.get("community")
        if community_name and community_name in communities:
            cid = communities[community_name]
            if cid:
                body["community_id"] = cid

        if dry_run:
            results.append({"dry_run": True, "text": text[:50], "reply_to": reply_to})
            reply_to = f"DRY_RUN_{i}"
        else:
            result = oauth_request("POST", "https://api.x.com/2/tweets", body)
            if "data" in result:
                tweet_id = result["data"]["id"]
                reply_to = tweet_id
                results.append({"id": tweet_id, "text": text[:50]})
            else:
                results.append({"error": result, "text": text[:50]})
                break  # Stop thread on error

        # Small delay between thread tweets
        if len(tweets) > 1 and i < len(tweets) - 1:
            time.sleep(2)

    return results


# ---------------------------------------------------------------------------
# Main scheduler
# ---------------------------------------------------------------------------

def normalize_time(folder_name: str) -> tuple:
    """Parse time folder name like '9am', '12pm', '5pm' into (hour, minute)."""
    match = re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)", folder_name.lower())
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    ampm = match.group(3)
    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    return (hour, minute)


def should_post_now(time_folder: str, now: datetime) -> bool:
    """Check if current time is within the posting window for this time slot.
    
    Window is 30 minutes (two cron cycles) to handle cases where the
    gateway is busy/restarting during the first 15-min check.
    """
    parsed = normalize_time(time_folder)
    if parsed is None:
        return False
    hour, minute = parsed
    slot_minutes = hour * 60 + minute
    now_minutes = now.hour * 60 + now.minute
    # Post if we're 0-29 minutes past the slot time
    return 0 <= (now_minutes - slot_minutes) < 30


def run(queue_dir: Path):
    """Main run: check current day/time, post matching content."""
    config = load_config(queue_dir)
    dry_run = config.get("dryRun", False)
    delete_after = config.get("deleteAfterPost", True)
    separator = config.get("separator", "---")
    communities = config.get("communities", {})

    # Get current day/time in configured timezone
    tz_name = config.get("timezone", "UTC")
    os.environ["TZ"] = tz_name
    try:
        time.tzset()
    except AttributeError:
        pass  # Windows doesn't have tzset
    now = datetime.now()
    day_name = now.strftime("%A")  # "Monday", "Tuesday", etc.

    day_dir = queue_dir / day_name
    if not day_dir.exists():
        return  # No folder for today

    posted_count = 0
    for time_dir in sorted(day_dir.iterdir()):
        if not time_dir.is_dir():
            continue
        if not should_post_now(time_dir.name, now):
            continue

        # Find tweet files
        tweet_files = sorted([
            f for f in time_dir.iterdir()
            if f.suffix.lower() in (".md", ".txt") and f.is_file()
        ])

        # Backlog fallback: if time slot is empty, pull one from backlog/
        if not tweet_files:
            backlog_dir = queue_dir / "backlog"
            if backlog_dir.exists():
                backlog_files = sorted([
                    f for f in backlog_dir.iterdir()
                    if f.suffix.lower() in (".md", ".txt") and f.is_file()
                ])
                if backlog_files:
                    picked = backlog_files[0]
                    dest = time_dir / picked.name
                    picked.rename(dest)
                    tweet_files = [dest]
                    print(f"Backlog fallback: moved {picked.name} to {day_name}/{time_dir.name}/")

        if not tweet_files:
            continue

        media_files = find_media(time_dir)

        for tweet_file in tweet_files:
            tweets = parse_tweet_file(tweet_file, separator)
            if not tweets:
                continue

            # Pre-flight: check for @mentions (blocked by X API as of 2026-02-28)
            has_mentions = any(re.search(r'@\w+', t.get("text", "")) for t in tweets)
            if has_mentions:
                mention_msg = f"SKIPPED {tweet_file.name}: contains @mentions (blocked by X API). Post manually."
                log_action(config, queue_dir, mention_msg)
                notify_user(f"Tweet '{tweet_file.name}' has @mentions and can't post via API. Moved to manual/ folder — post it yourself!")
                print(f"  ⚠️  {mention_msg}")
                # Move to a manual/ subfolder so it doesn't retry every 15 min
                manual_dir = time_dir / "manual"
                manual_dir.mkdir(exist_ok=True)
                dest = manual_dir / tweet_file.name
                tweet_file.rename(dest)
                for mf in media_files:
                    mf_dest = manual_dir / mf.name
                    mf.rename(mf_dest)
                continue

            prefix = "[DRY RUN] " if dry_run else ""
            print(f"{prefix}Posting from {day_name}/{time_dir.name}/{tweet_file.name}")

            results = post_tweets(tweets, media_files, communities, dry_run)

            for r in results:
                if "error" in r:
                    log_action(config, queue_dir, f"ERROR {tweet_file.name}: {r['error']}")
                    notify_user(f"Tweet '{tweet_file.name}' failed to post: {r['error']}")
                    print(f"  ERROR: {r['error']}", file=sys.stderr)
                else:
                    action = "WOULD POST" if dry_run else "POSTED"
                    log_action(config, queue_dir, f"{action} {tweet_file.name}: {r.get('text', '')}")
                    print(f"  {action}: {r.get('text', '')}")

            # Clean up
            if delete_after and not dry_run and not any("error" in r for r in results):
                tweet_file.unlink()
                for mf in media_files:
                    mf.unlink()
                posted_count += 1

    if posted_count:
        print(f"Done. Posted {posted_count} item(s).")


def main():
    # Find queue dir: check argument, then workspace default
    if len(sys.argv) > 1:
        queue_dir = Path(sys.argv[1])
    else:
        # Default: look for xqueue in workspace
        workspace = Path.home() / ".openclaw" / "workspace"
        queue_dir = workspace / "xqueue"

    if not queue_dir.exists():
        print(f"Queue directory not found: {queue_dir}")
        print("Run xqueue-setup.py first.")
        sys.exit(1)

    run(queue_dir)


if __name__ == "__main__":
    main()
