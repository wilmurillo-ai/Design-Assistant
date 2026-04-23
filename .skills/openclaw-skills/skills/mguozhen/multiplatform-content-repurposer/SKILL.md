---
name: ai-content-repurposer
description: "Content repurposing agent. Transforms long-form content (blog posts, video transcripts, podcast notes) into platform-optimized formats: LinkedIn post, X/Twitter thread, email newsletter, Instagram caption, YouTube description, TikTok script. Triggers: repurpose content, content repurposing, repurpose blog post, linkedin post from blog, twitter thread from article, email from content, content distribution, content recycling, multi-platform content, content atomization"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/content-repurposer
---

# Content Repurposer

Turn one piece of long-form content into six platform-ready formats — without losing the core message or your voice.

Paste a blog post URL, drop in a transcript, or summarize your content. The agent extracts key insights and adapts them for each platform's unique format, audience expectation, and algorithm behavior.

## Commands

```
repurpose <url or paste>           # extract and analyze source content
repurpose to linkedin              # generate LinkedIn post from loaded content
repurpose to twitter thread        # generate X/Twitter thread
repurpose to email                 # generate email newsletter version
repurpose to instagram             # generate Instagram caption with hashtags
repurpose to youtube               # generate YouTube description (SEO-optimized)
repurpose to tiktok                # generate TikTok script (hook-first, 60s)
repurpose all                      # generate all 6 platform formats at once
repurpose save                     # save source content and all outputs to workspace
```

## What Data to Provide

The agent works with:
- **Blog post URL** — paste the URL and describe the content (agent cannot fetch URLs directly)
- **Pasted text** — copy-paste the full article, transcript, or notes
- **Summary brief** — "my podcast episode covered X, Y, Z main points, audience is [niche]"
- **Tone notes** — "keep it professional" / "casual and punchy" / "educational"
- **Audience notes** — "B2B SaaS founders" / "fitness enthusiasts" / "Amazon sellers"

The more context you provide, the more on-brand the output.

## Workspace

Creates `~/content-repurposer/` containing:
- `memory.md` — saved brand voice notes, tone preferences, recurring topics
- `projects/` — source content and all platform outputs per repurpose session
- `templates/` — custom platform templates if you want to override defaults

## Analysis Framework

### 1. Content Extraction and Summarization
- Identify the core thesis: what is the single most important claim or insight?
- Extract the top 3–5 supporting points or examples
- Note the strongest quote, statistic, or story moment
- Identify the call-to-action or transformation promised by the content
- Tag the content type: how-to, opinion, case study, list, story, interview

### 2. Key Insight Identification
- Rank insights by: surprising > actionable > validating > educational
- Lead with the most surprising or counterintuitive point across all platforms
- Identify which insights work best as standalone hooks vs. supporting evidence
- Note any data points, specific numbers, or named frameworks — these anchor credibility

### 3. Platform Adaptation Rules

**LinkedIn** (professional, story-led, 1,300–3,000 characters)
- Open with a single-sentence hook on its own line
- Use short paragraphs (1–3 lines max) with line breaks between each
- Build toward the key insight with a story arc: situation → problem → solution → result
- End with a question or soft CTA to drive comments
- No hashtag spam — 3–5 relevant hashtags maximum, placed at end
- Optimal length: 150–300 words for most posts; long-form (700+ words) for thought leadership

**X / Twitter Thread** (punchy, hook-first, 270 characters per tweet)
- Tweet 1: the hook — most surprising claim or bold take, standalone value
- Tweets 2–7: one insight or example per tweet, numbered (2/8, 3/8, etc.)
- Tweet N-1: synthesis or "here's what this means for you" framing
- Final tweet: CTA (follow, reply, bookmark) + link back to source
- No filler tweets — every tweet must deliver value if read standalone
- Use line breaks within tweets for scannability

**Email Newsletter** (personal, direct, subject line drives opens)
- Subject line formula: [specific number or outcome] + [who it's for] + [timeframe or qualifier]
- Preview text: first sentence of body, no emoji, under 90 characters
- Opening: address reader directly, no "I wanted to reach out" — get to the point
- Body: 3-section structure — context, key insight, actionable takeaway
- CTA: one clear action only (read, reply, click, try)
- P.S. line: restate the best insight in one sentence for skimmers

**Instagram Caption** (visual-first, emotional, hashtag-rich)
- First line: hook that works without the image context (reader sees first 125 chars)
- Use line breaks and spacing for readability in the caption
- Inject 2–3 relevant emojis naturally — not as decoration but as emphasis
- End with a question to prompt comments
- Hashtags: 10–20, mix of large (1M+), medium (100k–1M), and niche (<100k)
- Separate hashtags from caption body with a line break or dots

**YouTube Description** (SEO-optimized, first 150 chars critical)
- First 150 characters: include primary keyword + clear value statement (shows before "more")
- Timestamps: include if content has chapters (00:00 Intro, 01:30 Main point, etc.)
- Links: website, social, related videos in body
- Keyword paragraph: 2–3 sentences naturally incorporating 3–5 target search terms
- End with subscribe CTA and community links

**TikTok Script** (hook-first, 30–60 seconds, pattern interrupt)
- Second 1–3: pattern interrupt hook — say the most surprising thing first
- Second 4–15: problem or tension setup — "most people think X, but actually..."
- Second 16–45: the insight, delivered fast with examples (no padding)
- Second 46–60: payoff + CTA ("follow for more" or "comment if you agree")
- Write in spoken word cadence — short sentences, punchy, as if talking to a friend
- Flag: hook must make viewer stop scrolling; test 2–3 hook variants

### 4. Tone Calibration Per Platform
- LinkedIn: professional but human — expertise without jargon
- Twitter: direct, confident, slightly edgy — opinions welcome
- Email: warm and personal — writing to one person, not a broadcast
- Instagram: authentic, aspirational, community-feeling
- YouTube: informative, enthusiastic, searchable
- TikTok: energetic, fast, relatable — no corporate speak

## Output Format

For `repurpose all`, outputs are delivered in labeled sections:

```
## LinkedIn Post
[output]

## Twitter Thread
[Tweet 1/N]
[Tweet 2/N]
...

## Email Newsletter
Subject: [subject line]
Preview: [preview text]
[body]

## Instagram Caption
[caption]
[hashtags]

## YouTube Description
[description]

## TikTok Script
[0:00–0:03] Hook:
[0:04–0:15] Setup:
[0:16–0:45] Insight:
[0:46–0:60] Payoff + CTA:
```

## Rules

1. Never change the core facts, statistics, or claims from the source content — adapt the format, not the substance
2. Always ask for target audience and tone before generating if not provided — generic output is low value
3. Each platform format must work independently — do not reference "as mentioned above" or cross-platform
4. Flag when source content is too thin to fill all 6 formats — recommend which platforms to prioritize
5. Do not pad outputs to hit length targets — shorter and sharper beats longer and diluted on every platform
6. Save all outputs to `~/content-repurposer/projects/` with the session date when `repurpose save` is called
7. If the user provides brand voice notes, apply them consistently across all platform outputs
