# YouTube Shorts Engagement

Engage with YouTube Shorts: watch videos, like, comment, and like your own comments.

---

## Before You Start

Copy and edit `config.yaml` with your account details:

```yaml
account:
  channel_name: "YourChannelName"  # Used to find your own comments
```

---

## The Engagement Checklist

Every video follows this exact sequence. No exceptions.

### ⚠️ THE GOLDEN RULE: Never Engage With an Already-Liked Video

**Before clicking the like button — ALWAYS check the `[pressed]` attribute.**

- If the like button has `[pressed]` → **ALREADY LIKED → SKIP. Do not engage.**
- If the like button has NO `[pressed]` → Proceed with the checklist below.

This is the most important rule. Skipping it is how accounts get flagged.

---

### Step 0 — Start the Short
If paused, click **Play**.

### Step 1 — Check Niche
Look at the video title, channel name, and hashtags.
- **In niche** (AI, productivity, entrepreneurship, motivation, growth) → Continue
- **Not in niche** → Skip to next video

### Step 2 — Watch, Then Check Like Status
Watch the Short (or at least 30 seconds). Then check the like button:
- Button says **"Like"** (no `[pressed]`) → **Not yet liked** → Proceed to Step 3
- Button says **"Like" with `[pressed]`** → **Already liked** → **SKIP immediately. Do nothing else.**

### Step 3 — Engage (If Not Yet Liked)

1. **Like the video** — Click like button. Confirm `[pressed]` appears.
2. **Open comments** — Click "View X comments".
3. **Type your comment** — Click the textbox, type your comment.
4. **Submit** — Click "Comment". Your comment appears with "0 seconds ago".
5. **Like your own comment** — Find your comment by channel name, click its like button.

### Skip to Next Video
Close comments → Click "Next video" (or press ArrowDown).

---

## How to Open

```javascript
browser(action="open", profile="openclaw", targetUrl="https://www.youtube.com/shorts")
```

---

## Commenting: The Key Technique

YouTube Shorts uses a JS comment box that blocks normal keyboard input.

### Method 1: Click + Type (Most Reliable)

Refs change after EVERY click. Always snapshot fresh before each action.

```
1. snapshot → get Play button ref
2. click Play
3. snapshot → get Like button ref
4. click Like
5. snapshot → get "View comments" ref
6. click "View comments"
7. snapshot → get textbox ref
8. click textbox → wait 1s
9. snapshot → get NEW textbox ref (MUST re-snapshot!)
10. click NEW textbox ref
11. type comment
12. snapshot → get "Comment" button ref
13. click "Comment"
14. snapshot → find own comment → get its like button ref
15. click own comment like
16. close → next video
```

### Method 2: JS Injection (Fallback)

If Method 1 fails, use `scripts/comment-inject.js`:

```javascript
browser(action="act", targetId="<tabId>", kind="evaluate", fn="<INJECT_SCRIPT>")
```

---

## Comment Templates

Pick one. Add 🧡. Never use the same comment twice in a session.

**Motivation / Mindset:**
- "The Kobe mindset clip hits different every time. That relentlessness doesn't leave you — it becomes how you operate. 🧡"
- "This hits different because it's true. 🧡"

**Communication / Social Skills:**
- "The distinction between impressing and making people feel special is everything. Chris always cuts through the noise. 🧡"
- "The 'how does this affect my value' reframe is exactly the right way to think about advocating for yourself. 🧡"

**Financial Mindset / Entrepreneurship:**
- "This hits different because it's true. The 'get a job' script is still being handed out in schools everywhere. Financial education is the real gap. 🧡"
- "The best founders I know are obsessed with leaving something behind — not just building a company. 🧡"

**Books / Knowledge:**
- "The 48 Laws of Power is the original 'dangerous' book list. Games People Play with it though — that one actually changed how I see relationships. 🧡"

**Opinionated / Human:**
- "This is either genius or derpy. Maybe both."
- "Still thinking about this take."

---

## Troubleshooting

### "Element not found" when commenting
Refs change after every interaction. Take a fresh snapshot before EVERY action.

### Comment text clears or doesn't appear
Click textbox → wait 1s → fresh snapshot → click textbox again from new snapshot → type.

### Like button doesn't show `[pressed]`
YouTube sometimes needs a second click. Try once more; if it still doesn't register, skip.

### Video unavailable / crashes
Skip to next video. Move on.

---

## Anti-Ban Rules

- **⚠️ ALWAYS check [pressed] before liking** — If already liked, SKIP. Never double-like.
- Watch videos before engaging (don't like-and-skip)
- Max 10 engagements per session
- Don't engage every video — leave some alone to look human
- Vary comment length and style
- Skip non-niche rather than force engagement
- No follow-for-follow
- Don't bulk like

---

## Files

```
youtube/
├── SKILL.md
├── config.yaml         ← Your settings
├── scripts/
│   ├── comment-inject.js
│   └── README.md
└── references/
    └── flow-cheatsheet.md
```
