# TikTok Engagement

Engage with TikTok videos: watch, like, comment, and like your own comments.

---

## Before You Start

Edit `config.yaml` in this directory:

```yaml
account:
  channel_name: "hypercho"  # Your TikTok handle (without @)
```

---

## The Engagement Checklist

Every video follows this exact sequence. No exceptions.

### ⚠️ THE GOLDEN RULE: Never Engage With an Already-Liked Video

**Before clicking the like button — ALWAYS check the `[pressed]` attribute.**

- If the heart button has `[pressed]` → **ALREADY LIKED → SKIP. Do not engage.**
- If the heart button has NO `[pressed]` → Proceed with the checklist below.

This is the most important rule. Skipping it is how accounts get flagged.

---

### Step 0 — Start the Video
Video autoplays by default. If paused, tap the screen or Play button.

### Step 1 — Check Niche
Look at the video caption, hashtags, and sounds.
- **In niche** (AI, productivity, entrepreneurship, motivation, growth) → Continue
- **Not in niche** → Navigate to next video → skip

### Step 2 — Watch, Then Check Like Status
Watch for at least 30 seconds. Then check the heart button:
- Heart is **white/outline** (no `[pressed]`) → **Not liked** → Proceed to Step 3
- Heart is **red/filled** with `[pressed]` → **Already liked** → **SKIP immediately. Do nothing else.**

### Step 3 — Engage (If Not Yet Liked)

1. **Like the video** — Click the heart button. Confirm `[pressed]` appears.
2. **Open comments** — Click the comment (speech bubble) button.
3. **Type your comment** — Click the text field, type your comment.
4. **Submit** — Click Post/Send. Your comment appears with "Xs ago" next to your @handle.
5. **Like your own comment** — Find your comment (shows your @channel_name), click its heart button.

### Skip to Next Video
Close comments → Navigate to the next video's direct URL.

---

## How to Open

```javascript
// For You feed
browser(action="open", profile="openclaw", targetUrl="https://www.tiktok.com/foryou"))

// Hashtag feed (best for niche targeting — use this!)
browser(action="open", profile="openclaw", targetUrl="https://www.tiktok.com/tag/motivation"))
browser(action="open", profile="openclaw", targetUrl="https://www.tiktok.com/tag/productivity"))
browser(action="open", profile="openclaw", targetUrl="https://www.tiktok.com/tag/success"))

// Direct video URL (most reliable — navigate here after each engagement)
browser(action="navigate", targetId="<tabId>", url="https://www.tiktok.com/@channelname/video/123456")
```

**Tip:** Opening the For You feed shows a sidebar of videos. Clicking sidebar thumbnails rarely works reliably in the browser. Use direct video URLs instead — they're fast and deterministic.

---

## Finding Niche Content on TikTok Web

TikTok's algorithm on web doesn't always serve niche content in For You. Best approach:

1. Open a hashtag page in your niche (e.g. `/tag/motivation`, `/tag/productivity`)
2. Browse the video thumbnails in the sidebar
3. Pick a niche-relevant video and navigate to its direct URL
4. Engage there

This consistently surfaces relevant content. The sidebar thumbnails on hashtag pages are clickable.

---

## Commenting on TikTok

TikTok uses a **standard text input** — simpler than YouTube. No JS injection needed.

### The Comment Workflow (Step by Step)

1. **Click comment (speech bubble) button** → comment panel slides up
2. **Click the text input field** → it activates, Post button still disabled
3. **Wait ~1 second** → take a fresh snapshot to get the current textbox ref
4. **Click the textbox ref from the fresh snapshot**
5. **Type your comment** using `kind="type"`
6. **Snapshot again** — Post button should now be enabled
7. **Click Post**

### Why the Extra Snapshots?

TikTok's DOM ref numbers shift constantly. Always snapshot fresh before every action after the first click.

### How to Confirm Your Comment Was Posted

Look for your `@channel_name` in the comment list — it appears with a timestamp like "1s ago" or "0s ago" directly below your handle. That's how you know it's live.

### Liking Your Own Comment

After posting, scroll the comment list to find your @channel_name. Its heart button starts empty — click it to like. Confirm `[pressed]` appears.

---

## Comment Templates

Pick one. Mix styles. Never use the same comment twice in a session.

**Motivation / Mindset:**
- "The consistency here is real. That compounds in ways you don't see coming. 🧡"
- "This is exactly the reminder I needed today. 🧡"
- "Stay hard. 🧡"

**David Goggins / Discipline:**
- "Fail. Rise. Succeed. That's the Goggins way. Stay hard. 🧡"
- "Lock In. That's the move. Stay hard. 🧡"
- "Life is short — Goggins said it best. 🧡"

**Entrepreneurship / Business:**
- "The business angle here is underrated. Saving this one."
- "Not enough people talk about this side of it. 🧡"

**Productivity:**
- "The systems approach always wins. Facts."
- "This is the version of the advice that actually works. 🧡"

**Opinionated / Human:**
- "Either genius or derpy. Maybe both."
- "Still thinking about this."
- "Honestly didn't expect to care about this but here we are."

**Question:**
- "What's the #1 thing you've learned from this?"
- "Has anyone else tried this?"

---

## TikTok Anti-Ban Rules

These are non-negotiable:
- **No follows** — Per instruction, do not follow creators
- **Watch before engaging** — Let videos play 30+ seconds first
- **Max 10 per session** — Cap engagement to look human
- **Engage ~70% of niche videos** — Don't engage with every single one
- **Vary comment styles** — Mix thoughtful with casual
- **Skip sponsored content** — Look for "#ad" or "#sponsored" in captions
- **Don't bulk like** — Space out your actions naturally
- **Avoid engagement pods** — Don't coordinate with others to inflate engagement
- **No duplicate comments** — TikTok flags repeated identical comments

---

## Troubleshooting

### Comment panel won't open
TikTok sometimes needs a second tap. Try clicking the comment button again.

### Post button stays disabled
You must type something in the text field first. The Post button enables once there's text.

### Keyboard covers the Post button
Tap outside the text field to dismiss the keyboard, then the Post button should be accessible.

### Heart button doesn't turn red / doesn't show `[pressed]`
TikTok sometimes needs a second tap. Try once more; if it still doesn't register, skip the video.

### Video won't play or "Video unavailable"
Skip to the next video. Some videos go offline mid-session.

### Sidebar thumbnails don't respond to clicks
This is a known TikTok web quirk. Navigate directly to the video URL instead — much more reliable.

### "Something went wrong" error
Skip to the next video. Technical glitch on TikTok's end.

### Comment posted but can't find it to like it
Scroll the comment list — new comments appear at the top with your @channel_name. It's usually the first or second comment visible.

---

## TikTok Web DOM Quirks (For Agents)

These are the practical findings from running this skill:

- **Standard text input, not contenteditable** — TikTok's comment box is a plain `<input>` or `<textarea>`. Normal `kind="type"` works perfectly. No JS injection needed.
- **Refs change constantly** — Always snapshot before every action after the first click. Old refs become stale.
- **Comment posted confirmation** — Your comment shows your `@channel_name` with a "Xs ago" timestamp directly below the handle. That's how you know it's live.
- **Direct URLs work best** — Sidebar navigation on TikTok web is unreliable. After each engagement, navigate to the next video's direct URL.
- **Hashtag pages are the discovery shortcut** — `/tag/motivation`, `/tag/success`, etc. show relevant thumbnails you can browse to find good targets.
- **Heart [pressed] = liked** — `[pressed]` attribute on the heart button means it's already liked.
- **Comments count updates** — After posting, the comment count increments (e.g. "433 comments" → "434 comments"). Good signal it went through.

---

## Files

```
tiktok/
└── SKILL.md
```
