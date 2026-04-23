---
name: ai-video-script-generator
version: "1.0.0"
displayName: "AI Video Script Generator — Write Video Scripts for YouTube TikTok and Reels with AI"
description: >
  Generate video scripts using AI — write retention-optimized scripts for YouTube, TikTok, Reels, ads, explainers, and any video format. NemoVideo produces complete scripts with hook-first structure, timestamp breakdowns, visual direction notes, B-roll suggestions, chapter markers, and platform-specific pacing — turning a topic or rough idea into a shoot-ready script that keeps viewers watching until the end.
metadata: {"openclaw": {"emoji": "📝", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video Script Generator — Write Scripts That Keep Viewers Watching

The script is where every good video starts and where most bad videos fail. A perfectly filmed, beautifully edited video with a weak script still loses viewers at the 30-second mark. A phone-recorded video with a brilliant script holds attention for 15 minutes. The script determines the hook (will they keep watching?), the pacing (will they stay engaged?), the structure (will they understand the point?), and the CTA (will they subscribe, buy, or share?). But scriptwriting is the hardest part of video production for most creators. Writing for spoken delivery is fundamentally different from writing for reading: sentences must be shorter, transitions must be explicit, key points need repetition, and the emotional arc must be deliberate. A blog post that works perfectly as text fails completely when read aloud because written prose and spoken script follow different rules. NemoVideo generates scripts that are written specifically for video: hook-first openings that stop the scroll, pacing calibrated to the platform (faster for TikTok, deliberate for YouTube), visual direction notes that tell you or the AI what to show during each section, B-roll suggestions matched to the content, and chapter markers for longer formats. The output is a shoot-ready script or a direct input to NemoVideo's video generation pipeline.

## Use Cases

1. **YouTube Long-Form — Retention-Optimized (8-20 min)** — Topic: "Why Most People Fail at Investing." NemoVideo generates: a controversial hook that challenges common wisdom ("Everything your bank told you about investing is designed to keep you poor"), an open loop that promises payoff ("By the end of this video, you'll know the one strategy that actually works"), 5 content sections with smooth transitions, each section opening with a curiosity-driven sub-hook, visual direction for each section (charts, examples, B-roll suggestions), a recap that reinforces the key takeaway, and a CTA tied to the content ("Download my free portfolio template — link in the description"). Estimated runtime, word count, and chapter timestamps included.
2. **TikTok/Reels — Hook-First Short (15-60s)** — Topic: "One productivity hack that changed my life." NemoVideo generates: a 1.2-second hook line ("Stop making to-do lists. Here's what actually works."), 3-4 rapid-fire points with no filler words, visual beat markers (where to cut, zoom, or add text overlay), and a closing hook that drives engagement ("Comment 'SYSTEM' and I'll send you the full method"). Script timed to exactly 42 seconds at speaking pace.
3. **Product Ad — Conversion Script (15-30s)** — Product: wireless earbuds. NemoVideo generates: problem-agitation-solution structure ("Tired of earbuds that die mid-workout? These last 30 hours. Sweat-proof. One-tap pairing. $49 — link in bio."), visual direction for each beat (frustrated runner → product hero shot → sweat close-up → pricing frame → CTA), and music/pacing suggestions. Script timed to 22 seconds.
4. **Explainer Video — Educational (3-8 min)** — Topic: "How does a blockchain actually work?" NemoVideo generates: an analogy-first hook ("Imagine a notebook that everyone in the world can read but nobody can erase"), progressive explanation building from simple to complex, analogies for every technical concept, visual direction (animated diagrams, real-world examples), check-in questions ("Still with me? Good, because this next part is where it gets interesting"), and a summary section. Script designed for 6 minutes at 150 wpm.
5. **Batch Scripts — Content Calendar (5-10 scripts)** — A creator needs scripts for 5 videos this week. NemoVideo batch-generates: 5 scripts on related topics with varied hooks (question, controversy, story, statistic, direct challenge), each with unique structure to prevent repetitiveness across the channel, cross-references between videos ("I covered the basics in Tuesday's video — today we go deeper"), and consistent brand voice throughout. A week of scripted content in one batch.

## How It Works

### Step 1 — Provide Topic or Idea
Give as much or as little as you have: a specific topic, a rough idea, bullet points, or just a content niche. NemoVideo researches and develops the concept.

### Step 2 — Set Script Parameters
Choose: platform (YouTube, TikTok, Reels, ad), duration, tone (professional, casual, dramatic, humorous), and audience level (beginner, intermediate, expert).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-script-generator",
    "prompt": "Write a YouTube script about why most people fail at meal prep. Target: 10 minutes. Hook: controversial (challenge the meal prep culture). Structure: hook + 5 failure reasons + the better alternative + CTA. Tone: conversational and relatable, like talking to a friend. Include visual direction notes and B-roll suggestions for each section. Chapter timestamps. Target audience: busy professionals who tried meal prep and quit.",
    "platform": "youtube",
    "duration": "10 min",
    "tone": "conversational-relatable",
    "hook_style": "controversial",
    "include": ["visual-direction", "b-roll-suggestions", "chapters", "timestamps"],
    "audience": "busy-professionals"
  }'
```

### Step 4 — Review and Produce
Review the script. Edit lines, adjust pacing, or refine the hook. Use directly as a teleprompter script or feed into NemoVideo's video generation pipeline.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Topic and script requirements |
| `platform` | string | | "youtube", "tiktok", "reels", "ad", "explainer", "podcast" |
| `duration` | string | | "15 sec", "60 sec", "3 min", "10 min", "natural" |
| `tone` | string | | "conversational", "professional", "dramatic", "humorous", "authoritative" |
| `hook_style` | string | | "controversial", "question", "statistic", "story", "direct-challenge" |
| `include` | array | | ["visual-direction", "b-roll-suggestions", "chapters", "timestamps", "cta"] |
| `audience` | string | | "beginner", "intermediate", "expert", or custom description |
| `word_count` | integer | | Target word count (150 words ≈ 1 minute) |
| `batch_topics` | array | | Multiple topics for batch script generation |

## Output Example

```json
{
  "job_id": "avsg-20260328-001",
  "status": "completed",
  "script": {
    "title": "Stop Meal Prepping (Do This Instead)",
    "word_count": 1520,
    "estimated_duration": "10:08",
    "sections": [
      {"title": "Hook", "timestamp": "0:00", "words": 85, "visual": "Rotting meal prep containers in fridge"},
      {"title": "Failure #1: Sunday Burnout", "timestamp": "0:34", "words": 210, "visual": "Exhausted person in kitchen, time-lapse of 4-hour prep"},
      {"title": "Failure #2: Flavor Fatigue", "timestamp": "2:10", "words": 195, "visual": "Same chicken and rice 5 days straight"},
      {"title": "Failure #3: Portion Waste", "timestamp": "3:28", "words": 220, "visual": "Trash can with uneaten meals"},
      {"title": "Failure #4: Schedule Rigidity", "timestamp": "4:58", "words": 180, "visual": "Calendar with every meal blocked"},
      {"title": "Failure #5: It's Not Cooking", "timestamp": "6:10", "words": 200, "visual": "Assembly line vs joyful cooking comparison"},
      {"title": "The Better Alternative", "timestamp": "7:32", "words": 280, "visual": "Relaxed weeknight cooking, ingredient prep only"},
      {"title": "Recap + CTA", "timestamp": "9:24", "words": 150, "visual": "Before/after comparison, subscribe animation"}
    ],
    "hook_line": "Meal prep is a scam — and your fridge full of rotting chicken proves it."
  }
}
```

## Tips

1. **The hook determines 70% of the video's performance** — Viewers decide to stay or leave in the first 5-8 seconds. A controversial claim, a surprising statistic, or a direct challenge keeps them watching. "Hey guys, welcome back to my channel" loses them instantly.
2. **Write for the ear, not the eye** — Read every line out loud. If you stumble, the viewer will stumble. Short sentences. Clear transitions. No nested clauses. No words you wouldn't say in conversation.
3. **Visual direction notes save hours of editing** — Knowing what B-roll to show during each section before filming/sourcing eliminates the "what do I put here?" decision during editing.
4. **Open loops create binge-watching** — "I'll explain why in a moment, but first..." forces the viewer to keep watching to close the loop. Strategic open loops at 2-minute intervals prevent mid-video drop-off.
5. **Platform pacing varies dramatically** — TikTok: 200+ words/minute, zero dead space. YouTube: 140-160 wpm with deliberate pauses for emphasis. An explainer: 130 wpm with repetition of key concepts. The same topic requires a fundamentally different script for each platform.

## Output Formats

| Format | Content | Use Case |
|--------|---------|----------|
| TXT | Plain script | Teleprompter / recording |
| MD | Formatted with sections | Review and editing |
| JSON | Structured with metadata | API pipeline input |
| DOCX | Professional document | Team collaboration |

## Related Skills

- [ai-video-summarizer](/skills/ai-video-summarizer) — Summarize videos
- [video-hook-maker](/skills/video-hook-maker) — Generate video hooks
- [talking-avatar-video](/skills/talking-avatar-video) — Avatar video production
