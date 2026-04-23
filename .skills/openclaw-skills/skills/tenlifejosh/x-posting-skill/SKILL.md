# Skill: X (Twitter) Posting

## Purpose
Post and manage X (Twitter) content via the `bird` CLI tool. Covers posting, replying, searching, reading timelines, and monitoring mentions — with full content strategy, warm-up protocol, and best practices for 2026.

---

## Configuration (Set Once)

Check `skills/x-posting/config.json`. If not present, ask the user:

1. **Chrome profile path**: Where is your Chrome profile directory?
   - macOS default: `~/Library/Application Support/Google/Chrome/Default`
   - Linux default: `~/.config/google-chrome/Default`
   - Windows default: `%LOCALAPPDATA%\Google\Chrome\User Data\Default`
2. **X account handle**: Which account are you posting from? (e.g., `@yourhandle`)
3. **Account niche/voice**: What is this account about? (e.g., "faith and personal finance, encouraging tone")
4. **Default hashtag style**: Minimal (1-2) / Standard (2-3) / None

Save to `skills/x-posting/config.json`:

```json
{
  "chrome_profile_path": "~/Library/Application Support/Google/Chrome/Default",
  "account_handle": "@yourhandle",
  "niche": "describe account niche and voice here",
  "hashtag_style": "minimal"
}
```

**Auth requirement**: The `bird` CLI reads Chrome cookies directly. Chrome must be open and logged in to X before running any commands. If Chrome was recently cleared or the session expired, bird will fail with a cookie/auth error.

---

## Tool: bird CLI

### Install
```bash
# Install via npm
npm install -g bird-cli

# Or via Homebrew (if available)
brew install bird-cli
```

### Basic Commands

#### Post a tweet
```bash
bird --chrome-profile "/path/to/chrome/Default" tweet "your text here"
```

#### Reply to a tweet
```bash
bird --chrome-profile "/path/to/chrome/Default" reply <tweet-id> "reply text"
```

#### Post a thread
Send each tweet individually using `reply` to chain them. Start with the first tweet, note the tweet ID from the response, then reply to that ID for each subsequent tweet.

```bash
# Step 1: post the hook tweet
bird --chrome-profile "/path/to/Default" tweet "Hook tweet text here"
# Note the returned tweet ID (e.g., 1234567890)

# Step 2: reply to chain the thread
bird --chrome-profile "/path/to/Default" reply 1234567890 "Tweet 2 of thread"
bird --chrome-profile "/path/to/Default" reply 1234567890 "Tweet 3 of thread"
```

#### Search
```bash
bird --chrome-profile "/path/to/Default" search "query" --count 10
```

#### Read a specific tweet
```bash
bird --chrome-profile "/path/to/Default" read <tweet-id>
```

#### Get mentions
```bash
bird --chrome-profile "/path/to/Default" mentions
```

#### Home timeline
```bash
bird --chrome-profile "/path/to/Default" home
```

---

## Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| Error 226 | Automated behavior detected | Back off immediately. Wait 30-60 min before next post. Resume with human cadence. |
| Cookie error / auth fail | Chrome session expired or logged out | Re-open Chrome, log in to X, then retry. |
| 280 character limit | Tweet too long | bird will reject — count characters before posting. 280-char hard limit. |
| Rate limit | Too many requests | Wait 15 min minimum. Reduce posting frequency. |

---

## Content Strategy

### How the X Algorithm Works (2026)

X uses a three-stage pipeline:
1. **Candidate sourcing**: ~1,500 candidates from 500M+ daily tweets
2. **Grok AI ranking**: scores each for predicted engagement
3. **Heuristics & filtering**: content-quality filters, time decay, diversity rules

**Engagement Weights (open-sourced code):**
| Action | Weight | Implication |
|--------|--------|-------------|
| Like | 1x | Lowest signal |
| Bookmark | 10x | Create save-worthy content |
| Link click | 11x | Links with clear context perform better |
| Profile click | 12x | Write curiosity-inducing bios and content |
| Reply | 13.5x | Ask questions, start debate |
| Repost | 20x | Create shareable, quotable content |
| Reply that gets author reply | 75x | **King signal** — reply chains are everything |

**Key Insight**: Posts lose ~50% visibility every 6 hours. Post when your audience is active. The first 30-60 minutes decide everything.

### What Performs Best (Ranked)
1. **Text-only posts** — outperform video by ~30% (unique to X)
2. **Images with commentary** — infographics, charts
3. **Threads** — 3x more engagement than single tweets
4. **Polls** — high engagement signal
5. **External links** — 30-50% reach reduction; only use with X Premium

### Optimal Post Structure
- 70-100 characters for quick reads
- Use line breaks — never walls of text
- 1-2 hashtags maximum
- Threads: 4-8 tweets, each working standalone

### Thread Structure
1. **Hook tweet**: Must stand alone as compelling — this is what gets reshared
2. **Value tweets (2-6)**: Each delivers one clear insight
3. **Summary/CTA tweet**: Recap and direct to next action
4. **Self-reply**: Post a reply to your own thread boosting conversation depth signal

### Hook Formulas
- **Contrarian**: "Everyone says [belief]. Here's why that's wrong."
- **List Tease**: "I spent [time] studying [topic]. Here are [N] things nobody tells you:"
- **Data Drop**: "[Specific stat] — and here's why it matters for [audience]"
- **Story**: "In [year], I [did something]. [Unexpected result]. Here's what I learned:"
- **Question**: "Why do [X% of people] still [common mistake]?"
- **Challenge**: "I tested [thing] for [time]. Results surprised me."
- **Observation**: "I just noticed something about [topic] nobody is talking about."

### Copywriting Rules
- Lead with the most interesting word or number — never bury the hook
- Never start with "I think" — state it as fact, qualify later if needed
- Use pattern interrupts: start mid-story, unexpected formatting
- End with a reason to reply (question, challenge, controversial statement)
- Threads: each tweet works standalone AND creates curiosity for the next

---

## Posting Limits & Best Practices

- **2-3 posts/day max** during warm-up — don't blast multiple tweets in a short window
- **3-5/day** once established — consistency compounds
- **Vary timing** — morning, afternoon, and evening cadence is more human
- **No mass replies** — replying to many accounts quickly triggers automated-behavior detection
- **No delete command** — bird does NOT have a delete feature. Think before posting.
- **No automate-liking/following/unfollowing** — that's where bans happen

### Best Posting Times (EST — adjust for your timezone)
| Day | Best Windows |
|-----|-------------|
| Tuesday-Thursday | 8-10am, 6-8pm |
| Monday | 9-11am |
| Sunday | 7-9pm |
| Friday-Saturday | Avoid after 3pm |

---

## Account Warm-Up Protocol

### Week 1-2 (Foundation)
- Complete profile: real/authentic photo, keyword-rich bio, pinned tweet
- Follow 50-100 relevant accounts in your niche
- Like and reply to 20-30 posts/day — genuine, thoughtful responses
- Post 1-2x/day (text only, value-focused)
- **Zero links or promotional content**

### Week 3-4 (Building)
- Increase to 3 posts/day
- Start threading (1 thread/week)
- Continue engaging with 20+ accounts/day
- Share images and data
- Still no promotional content

### Month 2 (Establishing)
- Post 3-5x/day
- 2-3 threads/week
- Links sparingly (only effective with X Premium)
- Begin brand-related content (80/20 value:promo)
- First poll

### Month 3+ (Scaling)
- Full content strategy
- Paid amplification of top organic content
- Direct promotional posts (max 20%)
- Collaborations via quote tweets and co-threads

### X Premium
For serious accounts, X Premium is non-negotiable:
- 4x in-network visibility (vs free)
- 2x out-of-network visibility
- Links actually perform (vs near-zero reach on free)
- Long-form content (up to 4,000 chars)
- Prioritized reply visibility

---

## Content Pillars (Mix Weekly)
- **Hot Takes / Opinion**: Bold perspectives (drives replies)
- **Data & Insights**: Stats, charts, research (drives bookmarks/reposts)
- **Behind the Scenes**: Process, journey content
- **Trend Reactions**: Quick takes on relevant news (3-4x/week)
- **Engagement Posts**: Questions, polls, fill-in-the-blank
- **Product/Service Updates**: Threads/image posts with clear value (1-2x/month max)

---

## Daily Routine (10-20 min)

**Morning:**
- Check mentions and replies — respond to all
- Post primary content of the day

**Midday:**
- Engage with 5-10 accounts (genuine replies, not "great post!")
- Monitor post performance

**Evening:**
- Reply to any new comments on your posts
- Post a second piece of content or engagement question

---

## Commands / Triggers
- **"Post a tweet about [topic]"** → Generate and post a single tweet
- **"Create a thread about [topic]"** → Generate full thread and post sequentially
- **"Reply to [tweet ID] with [idea]"** → Draft and post a reply
- **"Check my mentions"** → Run bird mentions command
- **"What's on my timeline?"** → Run bird home command
- **"Search for [topic]"** → Run bird search with relevant query
- **"Schedule this week's tweets"** → Generate 5 days of content, post at configured times
- **"Draft a thread, I'll approve before posting"** → Generate thread, output for review before posting
