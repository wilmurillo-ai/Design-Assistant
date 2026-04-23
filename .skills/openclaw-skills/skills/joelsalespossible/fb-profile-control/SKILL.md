---
name: fb-group-scanner
description: >
  CREDENTIALS REQUIRED: FB_COOKIE_FILE (Facebook session cookies JSON — treat as password),
  FB_STATE_FILE (Playwright state path, writable). Optional: FB_DRY_RUN (default true — no
  live comments until explicitly set false), FB_USER_AGENT, NOTIFY_WEBHOOK.
  INSTALL: pip install patchright && python -m patchright install chromium (PyPI + Playwright
  Chromium distribution). Scans Facebook groups for keyword-matching posts using Patchright
  (stealth Chromium), GraphQL response interception, and human-like mouse/scroll behavior.
  Auto-comments on matches. Use when building a bot that monitors FB groups for targeted
  hiring posts, comments on them, and notifies via webhook. Security: runs in dry-run mode
  by default; requires explicit opt-in for live commenting; no hardcoded endpoints or keys.
metadata:
  {
    "openclaw":
      {
        "primaryEnv":
          [
            {
              "name": "FB_COOKIE_FILE",
              "required": true,
              "secret": true,
              "description": "Path to exported Facebook session cookies JSON (Selenium/Puppeteer format). Grants full account access — treat as a password.",
            },
            {
              "name": "FB_STATE_FILE",
              "required": true,
              "secret": false,
              "description": "Writable path for Playwright storage state JSON. Defaults to /tmp/fb_state.json.",
            },
            {
              "name": "FB_DRY_RUN",
              "required": false,
              "secret": false,
              "description": "Set to 'false' to enable live commenting. Defaults to 'true' (scan-only mode).",
            },
            {
              "name": "FB_USER_AGENT",
              "required": false,
              "secret": false,
              "description": "Override browser user agent string.",
            },
            {
              "name": "NOTIFY_WEBHOOK",
              "required": false,
              "secret": true,
              "description": "Webhook URL for match notifications. Skill skips notifications if unset.",
            },
          ],
        "requires":
          {
            "bins": ["python3"],
            "env":
              [
                "FB_COOKIE_FILE",
                "FB_STATE_FILE",
              ],
          },
        "install":
          [
            {
              "id": "patchright",
              "kind": "shell",
              "command": "pip install -r scripts/requirements.txt",
              "label": "Install patchright (PyPI)",
            },
            {
              "id": "chromium",
              "kind": "shell",
              "command": "python -m patchright install chromium",
              "label": "Install Chromium binary (patchright/Playwright distribution)",
            },
          ],
      },
  }
---

# FB Group Scanner Skill

Scan Facebook groups for targeted posts and auto-comment using undetected browser automation.

## ⚠️ Before You Start

- **Cookies = credentials.** `FB_COOKIE_FILE` grants full Facebook account access. Store with `chmod 600`, never commit to git.
- **Use a dedicated/throwaway FB account** — never your personal account.
- **Dry-run is ON by default** (`FB_DRY_RUN=true`). The skill will scan and log matches but post zero comments until you explicitly set `FB_DRY_RUN=false`.
- **Run in a container or VM** — not directly on your host machine.
- **May violate Facebook TOS.** You are responsible for compliance.

## Environment Variables

| Variable | Required | Secret | Description |
|----------|----------|--------|-------------|
| `FB_COOKIE_FILE` | ✅ | ✅ | Path to Facebook cookies JSON (Selenium format). Full account access — treat as password. |
| `FB_STATE_FILE` | ✅ | — | Writable path for Playwright storage state (default: `/tmp/fb_state.json`) |
| `FB_DRY_RUN` | — | — | `true` (default) = scan only. `false` = live commenting. |
| `FB_USER_AGENT` | — | — | Override browser user agent |
| `NOTIFY_WEBHOOK` | — | ✅ | Webhook URL for match alerts. Skipped if unset. |

## Install

```bash
pip install -r scripts/requirements.txt   # patchright from PyPI
python -m patchright install chromium      # Chromium from Playwright distribution
```

## How to Get Cookies

1. Log in to Facebook in real Chrome (manually, once, dedicated account)
2. Export all `facebook.com` cookies as JSON via EditThisCookie or DevTools
3. Save to the path in `FB_COOKIE_FILE` with `chmod 600`

Cookies last ~30–90 days. Re-export manually when expired — no automated re-login included.

## Architecture

```
Patchright browser (stealth Chromium — patches navigator.webdriver + CDP detection)
  └─ Cookie auth (no login form)
       └─ Navigate group feed → intercept GraphQL responses passively
            └─ Filter posts: trigger phrase + topic keyword − exclusions
                 └─ FB_DRY_RUN=true → log match only
                    FB_DRY_RUN=false → human_type() comment + screenshot + webhook
```

## 1. Session (scripts/fb_session.py)

Reads `FB_COOKIE_FILE` and `FB_STATE_FILE` from environment. Returns `(playwright, browser, context, page)`.

```python
from fb_session import create_session
pw, browser, ctx, page = await create_session()
# Raises RuntimeError if cookies are stale
```

## 2. GraphQL Interception

Passively intercept FB's internal API responses — no synthetic clicks, no DOM scraping:

```python
responses = []
async def capture(r):
    if "graphql" in r.url and r.status == 200:
        try: responses.append(await r.json())
        except: pass
page.on("response", capture)
await page.goto(group_url)
await asyncio.sleep(5)
```

See `references/graphql-patterns.md` for walking the response tree.

## 3. Human-Like Behavior (scripts/human_mouse.py)

- `human_scroll(page)` — variable-speed wheel ticks with micro-pauses
- `human_click(page, x, y)` — bezier curve mouse path + hover + hold
- `human_type(page, text)` — variable WPM, occasional typos + backspace
- `idle_mouse_drift(page)` — aimless drift while "reading"
- `reading_pause(min_s, max_s)` — random pre-action sleep

Timing: 3–8s after page load, 50–120s between groups, never back-to-back.

## 4. User Controls

```python
import os, re

DRY_RUN = os.environ.get("FB_DRY_RUN", "true").lower() == "true"

def redact_pii(text):
    """Strip emails and phone numbers before any external send."""
    text = re.sub(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', '[EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE]', text)
    return text

NOTIFY_WEBHOOK = os.environ.get("NOTIFY_WEBHOOK", "")
if not NOTIFY_WEBHOOK:
    # Skill skips all external notifications when unset
    pass
```

## 5. Post Filtering

See `references/filter-logic.md` — four-stage pipeline:
1. **Trigger phrase** — hiring signal ("hiring", "looking for", "seeking", etc.)
2. **Topic keyword** — target role ("csm", "client success manager", "retention", etc.)
3. **Job title exclusions** — reject different roles in headline (first 200 chars)
4. **Seeking-work exclusions** — reject service-offer posts

## 6. Scheduling

```python
import schedule, time, asyncio
schedule.every().hour.at(":00").do(lambda: asyncio.run(scan_bucket("A")))
schedule.every().hour.at(":30").do(lambda: asyncio.run(scan_bucket("B")))
while True:
    schedule.run_pending()
    time.sleep(30)
```

8am–11pm only. Track seen posts in SQLite to prevent duplicate comments.

## Files

| File | Purpose |
|------|---------|
| `scripts/fb_session.py` | Cookie session factory (env vars only, no hardcoded paths) |
| `scripts/human_mouse.py` | Stealth mouse/scroll/type helpers (bezier curves, variable timing) |
| `scripts/requirements.txt` | Python dependencies (`patchright>=1.0.0`) |
| `references/graphql-patterns.md` | FB GraphQL response tree parsing guide |
| `references/filter-logic.md` | Keyword filter architecture + tuning guide |
