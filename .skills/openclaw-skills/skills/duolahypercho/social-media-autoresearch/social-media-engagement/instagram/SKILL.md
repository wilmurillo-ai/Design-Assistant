# Instagram Engagement

Engage with Instagram posts and Reels: watch, like, comment, and like your own comments.

---

## Before You Start

Edit `config.yaml` in this directory:

```yaml
account:
  username: "your_username"  # Your IG handle (without @)
```

---

## The Engagement Checklist

Every post follows this exact sequence.

### Step 0 — Start the Content
For Reels: Video autoplays. If paused, tap to play.
For Feed posts: Scroll to the post.

### Step 1 — Check Niche
Look at the caption, hashtags, and account.
- **In niche** (AI, productivity, entrepreneurship, motivation, growth) → Continue
- **Not in niche** → Scroll to next post

### Step 2 — Watch, Then Check Like Status
Watch the Reel or study the post. Then check the heart button:
- Heart is **white/outline** → **Not liked** → Proceed to Step 3
- Heart is **red/filled** → **Already liked** → Skip to next post

### Step 3 — Engage (If Not Yet Liked)

1. **Like the post** — Click the heart button. It turns red when liked.
2. **Open comments** — Click the comment (speech bubble) button.
3. **Type your comment** — Click the text field, type your comment.
4. **Submit** — Click "Post". Your comment appears.
5. **Like your own comment** — Find your comment, click its like button.

### Skip to Next Post
Close comments → Scroll to next post.

---

## How to Open

```javascript
// Instagram home feed
browser(action="open", profile="openclaw", targetUrl="https://www.instagram.com"))

// Instagram Reels
browser(action="open", profile="openclaw", targetUrl="https://www.instagram.com/reels")))

// Hashtag feed (good for niche targeting)
browser(action="open", profile="openclaw", targetUrl="https://www.instagram.com/explore/tags/growthmindset/"))
```

---

## Instagram Reels vs. Feed Posts

**Reels** (full-screen video):
- Similar to TikTok — autoplay, swipe up to navigate
- Heart fills red when liked
- Comment panel slides up from bottom
- Sound/audio is a key signal — check the track name for niche relevance

**Feed Posts** (static grid):
- Like by clicking the heart icon
- Double-tap the image to like
- Comments open inline below the post
- Carousel posts (multiple images): navigate with arrows

---

## Commenting on Instagram

### For Reels (panel slides up)

```
1. Tap comment (speech bubble) icon → panel slides up
2. Tap the text field → keyboard appears
3. Type comment using kind="type"
4. Tap "Post" button
```

### For Feed Posts (inline)

```
1. Click comment (speech bubble) icon → comments expand inline
2. Click the text field
3. Type comment
4. Click "Post"
```

**Tip:** The "Post" button is often disabled until there's text. Make sure to type something before trying to post.

---

## Comment Templates

Pick one. Mix styles. Never use the same comment twice in a session.

**Motivation / Mindset:**
- "The consistency here is real. That compounds in ways you don't see coming. 🧡"
- "This is exactly the reminder I needed today. 🧡"

**Entrepreneurship / Business:**
- "The business angle here is underrated. Saving this one."
- "Not enough people talk about this side of it. 🧡"

**Productivity:**
- "The systems approach always wins. Facts."
- "This is the version of the advice that actually works. 🧡"

**AI / Tech:**
- "The AI implications here are wild. 🧡"
- "This is exactly what the future of X looks like."

**Opinionated / Human:**
- "Either genius or derpy. Maybe both."
- "Still thinking about this."
- "Honestly didn't expect to care about this but here we are."

**Question:**
- "What's the #1 thing you've learned from this?"
- "Has anyone else tried this?"

---

## Instagram Anti-Ban Rules

These are non-negotiable:
- **No follows** — Per instruction, do not follow accounts
- **Watch before engaging** — Let Reels play 30+ seconds first
- **Max 10 per session** — Cap engagement to look human
- **Engage ~70% of niche content** — Don't engage with every post
- **Vary comment styles** — Mix thoughtful with casual
- **Skip sponsored content** — Look for "#ad" or "#sponsored" in caption
- **Don't bulk like** — Space out actions naturally
- **Avoid pods** — Don't coordinate engagement with groups
- **Don't use the same comment twice** — Instagram flags duplicate comments

---

## Troubleshooting

### "Post" button stays disabled
Type something in the text field first. The button enables once there's text.

### Comment panel doesn't open on Reels
Instagram sometimes needs a second tap. Try the comment button again.

### Heart button doesn't turn red
Try double-tapping the image/post directly. Some Like buttons require this.

### Keyboard covers the Post button
Tap outside the text field to dismiss keyboard, scroll the comment area slightly.

### Reel won't play
Tap to play manually. If it still doesn't work, skip to the next post.

### "Action Blocked" message
You've hit a rate limit. Stop immediately and wait 24-48 hours before engaging again.

---

## Files

```
instagram/
└── SKILL.md
```
