# YouTube Shorts Engagement — Flow Cheatsheet

**Print this. Keep it next to you while running the skill.**

---

## Before Every Session

- [ ] Edit `config.yaml` with your `channel_name`
- [ ] Review comment templates
- [ ] Confirm you know the niche list by heart

---

## The Flow (One Video)

```
STEP 0 ──▶ Is the Short paused?
           │
           ├─ YES ──▶ Click Play
           │
           ▼
STEP 1 ──▶ Is this video in my niche?
           │        (title, hashtags, channel name)
           │
           ├─ NO  ──▶ Skip to next video
           │
           ▼
STEP 2 ──▶ Watch the video (30+ sec)
           │        Then: is the like button PRESSED?
           │
           ├─ YES  ──▶ Already liked — skip to next
           ├─ NO   ──▶ Proceed to Step 3
           │
           ▼
STEP 3 ──▶ NOT YET LIKED ──▶ Do full engage:
           │
           │  (a) Click Like button → confirm [pressed]
           │  (b) Open comments
           │  (c) Type comment (click textbox → snapshot → click → type)
           │  (d) Click Submit/Comment
           │  (e) Find YOUR comment ("0 seconds ago")
           │  (f) Like your own comment
           │
           ▼
           Done ──▶ Close comments ──▶ Next video
```

---

## Quick Comment Map

| Content Type | Good Comment Hook |
|---|---|
| Motivation / Mindset | "The Kobe mindset..." / "This hits different..." |
| Communication / Social | "The distinction between..." / "The reframe..." |
| Finance / Entrepreneurship | "The 'get a job' script..." / "Financial education..." |
| Books / Knowledge | "[Book title] is the original..." |
| Founders / Leadership | "The best founders I know are obsessed with..." |

**Always add 🧡** — our signature.

---

## DOM Refs — Always Fresh

> **CRITICAL:** Refs change after EVERY click. Always snapshot before each action.

```
Action order per video:
1.  snapshot → get Play button ref
2.  click Play
3.  snapshot → get Like button ref, "Next video" ref
4.  click Like
5.  snapshot → get "View comments" ref
6.  click "View comments"
7.  snapshot → get textbox ref
8.  click textbox → wait 1s
9.  snapshot → get NEW textbox ref ← MANDATORY RE-SNAPSHOT
10. click NEW textbox ref
11. type comment
12. snapshot → get "Comment" button ref
13. click "Comment"
14. snapshot → find "@YOUR_CHANNEL_NAME" → get own comment like button ref
15. click own comment like
16. close comments → next video
```

---

## Anti-Ban Rules

| Do | Don't |
|---|---|
| Watch videos first | Like and immediately skip |
| Max 10 per session | Bulk like everything |
| Mix comment styles | Same comment everywhere |
| Skip non-niche | Force engagement |
| 70% engage ratio | Engage 100% of niche videos |
| Vary timing | Post at robotic intervals |
| No follows | Follow-for-follow |

---

## Troubleshooting Quick Fixes

| Problem | Fix |
|---|---|
| "Element not found" | Snapshot again — refs changed |
| Comment text clears | Click textbox → wait 1s → snapshot → click textbox → type |
| Like doesn't show pressed | Try once more; if still fails, skip |
| Video unavailable | Skip — move on |
| JS injection fails | Use Method 1 (click + type) instead |
