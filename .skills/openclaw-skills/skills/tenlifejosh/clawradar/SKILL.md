# ClawRadar — Real-Time Trend Monitor
**Skill for OpenClaw | Version 1.0.0**

---

## What ClawRadar Is

ClawRadar is J's real-time trend intelligence layer. It watches X (Twitter) and Reddit continuously, scoring every post for engagement velocity, freshness, and niche relevance. When something is going viral in the AI/indie hacking/entrepreneurship space, J gets an instant Telegram alert — with context and a ready-made opportunity note.

**The strategic insight:** The window to ride a trend is 30–90 minutes. After that, the wave has passed and you're just noise. ClawRadar gives you that window, reliably, without manual monitoring.

---

## What It Monitors

### X (Twitter)
Searches run on every scan:
- `"AI agent"` — catching new tool releases, viral takes
- `"indie hacker"` — maker community momentum
- `"AI automation"` — workflow/productivity trends
- `"MCP server"` — protocol-level AI infrastructure
- `"openclaw"` — brand monitoring
- `"SaaS launch"` — product launches gaining traction
- `"AI tool launch"` — new tools going viral

### Reddit Communities
- **r/artificial** — general AI discourse, breaking news
- **r/MachineLearning** — technical AI trends with research implications
- **r/SideProject** — indie projects gaining traction (launch opportunities)
- **r/entrepreneur** — business/founder mindset content
- **r/ChatGPT** — mainstream AI discourse and viral use cases
- **r/singularity** — forward-looking AI discussion

### Why These Sources
X is where trends start. Reddit is where they get validated and discussed in depth. Together they cover the full lifecycle: early signal (X) → community validation (Reddit) → mainstream (everywhere else). ClawRadar catches it at stage 1 or 2.

---

## How Scores Work

### Composite Score (0–100+)

```
Score = (engagement_velocity × 0.40) + (freshness × 0.30) + (keyword_relevance × 0.30)
```

**Engagement Velocity (40%):**
> (likes + 2×retweets + comments) / hours_since_posted
> 
> A post with 500 likes in 30 minutes scores higher than one with 500 likes over 3 days. RTs count double because they indicate content spread, not just approval.

**Freshness (30%):**
> Linear decay from 100 (just posted) to 0 (2 hours old). Content older than 2 hours gets a freshness score of 0 and is excluded entirely.

**Keyword Relevance (30%):**
> Each niche keyword hit = 10 points, capped at 100. Keywords include: AI, agent, automation, indie, saas, launch, GPT, LLM, Claude, OpenAI, Anthropic, MCP, tool, startup, revenue, and ~20 more.

### Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 80–100 | 🔥🔥🔥🔥🔥 Critical trend | Act immediately — post a reply/thread NOW |
| 65–79 | 🔥🔥🔥🔥 Hot signal | Strong opportunity — draft a response within 30 min |
| 55–64 | 🔥🔥🔥 Worth watching | Good signal — engage if you have something genuine to add |
| <55 | Below threshold | Not alerted |

---

## Interpreting Alerts

### Alert Anatomy

```
🚨 TREND RADAR — 2:30 PM MDT        ← when ClawRadar caught it
━━━━━━━━━━━━━━━━━━━━━
📈 VIRAL: "[Post title/tweet]"       ← the content (first 200 chars)

Platform: X | By: @username         ← source and author
Engagement: 4.2K likes, 1.1K RTs    ← raw engagement numbers
in 45min                            ← how long since posted
Relevance: AI tools, indie hacking  ← which niches it hits
Score: 🔥🔥🔥🔥 (82/100)              ← composite score + fire rating
URL: [link]                         ← direct link to engage

💡 Opportunity: [action suggestion]  ← what to do right now
━━━━━━━━━━━━━━━━━━━━━
```

### Reading the Opportunity Note

The opportunity note is auto-generated based on niche tags:
- **AI tools/automation** → Thread on @HutchCOO comparing to your builds
- **Indie hacking/SaaS** → Build-in-public update or reply with your angle
- **Reddit** → Jump into comments for targeted exposure
- **Faith+tech** → Engage now and cross-post Prayful context
- **Entrepreneurship** → Your story (restaurants → agency → AI) is uniquely relevant

These are starting points — use your judgment. The best engagement is always authentic and specific.

---

## Responding to a Trend

### Decision Framework

**Act now (score 70+, age <45 min):**
1. Open the URL immediately
2. Read the content + top replies
3. Choose your angle (see templates below)
4. Post within 15 minutes of receiving the alert

**Act soon (score 55–70, age <90 min):**
1. Read the content when you can
2. Post a reply or thread within 60 minutes
3. Still valuable, just less urgent

**Skip if:**
- You don't have a genuine perspective on it
- You'd just be saying "great point!" with no substance
- The thread is already 200+ replies deep with no top spots left
- It conflicts with your brand voice

---

## Content Templates

### X Reply Template
```
[Specific observation about their point]

[Your contrasting or complementary experience]

[One specific thing you're building/doing that's relevant]

[Optional: Question that adds to the conversation]
```

**Example:**
> The hardest part about AI agents isn't the intelligence — it's the persistence. Getting them to remember context, resume tasks, and not forget everything between sessions.
>
> Building this exact problem away with @openclaw. Still hard, but getting there.
>
> What's your biggest agent reliability issue?

### X Thread Template (for major trends)
```
Tweet 1: [Hook — the trend or contrarian take]
Tweet 2: [Why this matters / what most people miss]
Tweet 3: [What you're actually doing about it]
Tweet 4: [The result / what you learned]
Tweet 5: [Call to action or question]
```

### Reddit Comment Template
```
[Acknowledge what OP said specifically]

[Your real experience or data point]

[Relevant project/context without being salesy]

[Question or invitation to discuss]
```

---

## Adjusting ClawRadar

All config lives in `clawradar/radar.py` under `CONFIG`.

### Adjust Sensitivity

```python
# More alerts (lower bar):
"score_threshold": 40,

# Fewer, higher-quality alerts:
"score_threshold": 70,

# Catch older but still relevant content:
"max_age_hours": 4,
```

### Add Keywords

```python
"keywords": [
    # Existing...
    "prayful",   # Your app name
    "MFJ",       # MyFirstJob
    "GND",       # Good Neighbor Design
],
```

### Add Niche Keywords (triggers niche filter)

```python
"niche_keywords": [
    # Existing...
    "local business",    # GND niche
    "web design",        # GND niche
    "bible app",         # Prayful niche
],
```

### Add X Searches

```python
"x_searches": [
    # Existing...
    ("local business website", 15),
    ("web design agency", 10),
    ("bible app launch", 10),
],
```

### Add Subreddits

```python
"subreddits": [
    # Existing...
    ("webdev", "hot", 20),
    ("smallbusiness", "hot", 20),
    ("Christianity", "hot", 15),
],
```

---

## Cron Status

ClawRadar runs every 30 minutes, 7am–11pm Mountain.

```bash
# Check cron status:
openclaw cron list

# Run now:
openclaw cron run --name "ClawRadar — Trend Monitor"

# View run history:
openclaw cron runs --name "ClawRadar — Trend Monitor"
```

---

## Troubleshooting

### No Alerts (expected behavior check)

ClawRadar is designed to stay silent when there's nothing notable. Silence = no viral trends in your niche right now. That's correct behavior.

To verify it's running and scoring:
```bash
python3 clawradar/radar.py --dry-run --debug --threshold 20
```
This will show everything it found, scored, and filtered — even content that didn't make the threshold.

### Getting Too Many Alerts

```python
# Raise threshold:
"score_threshold": 70,
# Or add more restrictive niche keywords
```

### Getting Too Few Alerts

```python
# Lower threshold:
"score_threshold": 40,
# Add more search queries
# Add more subreddits
# Expand keywords list
```

### X Searches Failing

Verify bird CLI is working:
```bash
bird --chrome-profile "Profile 1" search "AI" --count 5 --json
```

If it fails, the Chrome session may need refreshing. Open Chrome with "Profile 1" and visit X.com to re-authenticate.

### Reddit Rate Limiting

Reddit's public JSON API allows ~60 requests/minute. ClawRadar includes 500ms delays between subreddit calls. If you see HTTP 429 errors, increase the delay in `fetch_reddit_posts()`.

---

## Architecture Notes

**No external dependencies** beyond Python 3.9+ stdlib + bird CLI + openclaw. No API keys, no PRAW, no OAuth flows. Reddit uses the public JSON API (`reddit.com/r/subreddit.json`). X uses bird CLI (which handles Chrome cookie extraction).

**Idempotent** — runs safely every 30 minutes. The seen.json tracker ensures you never alert on the same content twice within 48 hours.

**Graceful degradation** — if X is down, Reddit still runs. If a subreddit errors, the rest continue. No single point of failure.

---

## Logs

```bash
# Live tail:
tail -f clawradar/logs/radar.log

# Last 50 lines:
tail -50 clawradar/logs/radar.log

# Count alerts sent today:
grep "Alert sent" clawradar/logs/radar.log | grep $(date +%Y-%m-%d) | wc -l
```

---

*ClawRadar v1.0.0 | Part of the Ten Life Creatives operating system | openclaw.ai*
