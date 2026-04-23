---
name: ai-reel-creator
version: "1.0.0"
displayName: "AI Reel Creator — Generate Instagram Reels TikToks and Shorts from Any Input"
description: >
  Generate Instagram Reels, TikToks, and YouTube Shorts from any input with AI — text prompts, blog posts, product photos, raw clips, audio files, or just an idea. NemoVideo produces complete vertical short-form videos: AI visuals, voiceover narration, trending captions, beat-synced music, hook text, transitions, and multi-platform export. Create Reels without filming, without editing software, and without design skills. One prompt produces ready-to-post content for all three short-form platforms simultaneously. AI Reel creator, Reel maker AI, TikTok generator, Shorts creator, vertical video AI, short form video generator, auto Reel maker.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Reel Creator — One Prompt. Three Platforms. Ready to Post.

The short-form video opportunity is staggering: Instagram Reels reaches 2 billion accounts monthly, TikTok has 1.5 billion active users, YouTube Shorts exceeds 70 billion daily views. Combined, short-form vertical video reaches more people daily than any other content format in human history. The barrier to capturing this opportunity is production throughput. Algorithms reward frequency — daily posting outperforms weekly by 5-7x in follower growth. Daily posting across three platforms means 21 videos per week. Even a 20-minute-per-video workflow requires 7 hours per week of production. For most creators and businesses, this is unsustainable alongside their actual work. NemoVideo makes 21 videos per week achievable in under 2 hours. Provide 7 topics (one per day) as text prompts. The AI generates each as a complete vertical video with visuals, narration, captions, and music — then exports three platform-optimized versions (Reels, TikTok, Shorts) from each. Seven prompts become 21 platform-ready videos. Daily multi-platform presence becomes a scheduling task rather than a production burden.

## Use Cases

1. **Text to Reel — Idea to Posted Content (15-60s)** — A business coach has 30 tip ideas in a notes app. NemoVideo: takes each tip as a one-line prompt ("Why most networking advice is wrong"), generates a complete Reel per tip (hook text in first frame, AI visuals illustrating the concept, voiceover delivering the tip with authority, word-by-word captions, upbeat background music, CTA ending), and exports all 30 for three platforms. A month of daily multi-platform content from a notes app.

2. **Photos to Reel — Product Showcase Without Video (15-30s)** — A jewelry brand has beautiful product photography but no video content. NemoVideo: takes 5-8 product photos per piece, applies cinematic motion (slow zoom, gentle pan, parallax depth effect), transitions between photos synced to elegant music, adds text overlays ("Handcrafted" / "14K Gold" / "Free Shipping"), includes a price card and shop CTA, and exports as a shoppable Reel. Static photography becomes dynamic video content that Instagram's algorithm prioritizes over image posts.

3. **Blog to Reel — Written Content Repurposed (30-60s)** — A SaaS company publishes weekly blog posts that get 3,000 reads. The same insights as Reels would reach 30,000-100,000. NemoVideo: takes the blog post URL, extracts the 3-5 key insights, condenses into a 45-second visual narrative, generates illustrative visuals per insight, produces voiceover summarizing the post, adds captions and music, and exports for all platforms. Written content reaches the video-first audience without rewriting or re-researching.

4. **Audio to Reel — Podcast Highlights Visualized (30-55s)** — A podcast guest said something brilliant in 40 seconds. NemoVideo: takes the audio clip, generates relevant visuals that illustrate the speaker's points (conceptual imagery, data visualizations, reaction visuals), adds the speaker's photo with name/title overlay, applies word-by-word captions synced to the audio, adds subtle background music under the speech, and exports as a visual Reel. Audio-only content gains the visual dimension that social platforms require.

5. **Batch Reels — Content Series Production (multiple)** — A fitness creator plans a "5 Exercises You're Doing Wrong" series — 5 Reels, one per exercise. NemoVideo: takes all 5 exercise descriptions, generates each Reel with consistent series branding (same intro template: "Exercise 3/5 You're Doing Wrong"), AI-generated exercise demonstration visuals, voiceover coaching correct form, numbered progress indicator, and series finale CTA ("Follow for parts 4 and 5"). A complete 5-part series from 5 sentences, with visual consistency that builds series recognition.

## How It Works

### Step 1 — Provide Any Input
Text prompt, script, blog URL, photos, video clips, audio file, or just a topic. NemoVideo builds the Reel from whatever you give it.

### Step 2 — Set Style and Platform
Tone (energetic, calm, professional, funny), caption style, music preference, and platform targets.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-reel-creator",
    "prompt": "Create a 35-second Reel about why most people fail at morning routines. Hook: first frame text — The morning routine lie nobody talks about (bold white on dark, 1.5s). Content: the real reason is not discipline, it is that people copy routines that do not fit their life. Show: person struggling with 5am alarm → frustrated → discovering their own rhythm → thriving at their natural wake time. Voice: warm relatable female. Music: chill motivational at -20dB. Captions: word-by-word (white, #A78BFA purple highlight, pill-dark). CTA: last 2s — What time do YOU actually wake up? Comment 👇",
    "input_type": "text",
    "hook": {"text": "The morning routine lie nobody talks about", "duration": 1.5},
    "voice": "warm-relatable-female",
    "music": {"style": "chill-motivational", "volume": "-20dB"},
    "captions": {"style": "word-highlight", "text": "#FFFFFF", "highlight": "#A78BFA", "bg": "pill-dark"},
    "cta": {"text": "What time do YOU actually wake up? Comment 👇", "duration": 2},
    "duration": 35,
    "platforms": ["reels", "tiktok", "shorts"]
  }'
```

### Step 4 — Post to All Platforms
Preview all three versions. Each is subtly optimized for its platform (different safe zones, slightly different caption positioning). Download and post simultaneously.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Reel concept from any input type |
| `input_type` | string | | "text", "photos", "blog-url", "audio", "clips", "script" |
| `hook` | object | | {text, duration} — scroll-stopping first frame |
| `voice` | string | | "energetic-male", "warm-female", "authoritative", "casual" |
| `music` | object | | {style, volume, ducking} |
| `captions` | object | | {style, text, highlight, bg} |
| `cta` | object | | {text, duration} — ending call to action |
| `duration` | integer | | 15, 30, 35, 45, or 60 seconds |
| `platforms` | array | | ["reels", "tiktok", "shorts"] |
| `color_grade` | string | | "warm", "cool", "vibrant", "moody", "clean" |
| `series` | object | | {name, episode, total} |
| `batch` | array | | Multiple Reels in one request |

## Output Example

```json
{
  "job_id": "arc-20260328-001",
  "status": "completed",
  "duration": "0:35",
  "production": {
    "hook": "The morning routine lie nobody talks about (1.5s)",
    "voice": "warm-relatable-female",
    "captions": "word-highlight (white + #A78BFA purple)",
    "music": "chill-motivational at -20dB",
    "cta": "What time do YOU actually wake up? (2s)"
  },
  "outputs": {
    "reels": {"file": "morning-routine-reels.mp4", "resolution": "1080x1920"},
    "tiktok": {"file": "morning-routine-tiktok.mp4", "resolution": "1080x1920"},
    "shorts": {"file": "morning-routine-shorts.mp4", "resolution": "1080x1920"}
  }
}
```

## Tips

1. **The hook decides 95% of the Reel's performance** — On all three platforms, the algorithm tests your Reel on a small audience first. If they stop scrolling and watch, it gets distributed wider. The hook is the only thing that determines this initial test. Invest maximum creative energy in the first 1.5 seconds.
2. **Question-based CTAs drive comments — comments drive distribution** — "What do YOU think?" and "Comment your answer" drive 3-5x more comments than "Follow for more." Comments are weighted heavily by all three platform algorithms. A Reel with 200 comments outperforms one with 2,000 likes.
3. **Batch 7 Reels in one session for consistent quality** — Creating Reels individually means variable quality and inconsistent style. Batch-creating a week's worth in one session produces consistent branding and saves 5+ hours per week.
4. **Platform-specific subtle differences matter** — Reels and TikTok have different safe zones (where UI elements overlay). Shorts has different text positioning. NemoVideo adjusts caption and CTA placement per platform so nothing gets hidden behind buttons.
5. **Series content is the fastest path to follower growth** — "Part 1 of 5" creates a reason to follow. Viewers who see Part 2 and missed Part 1 go to your profile. Series mechanics drive profile visits, which drive follows. Always frame recurring topics as numbered series.

## Output Formats

| Format | Resolution | Platform |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | Instagram Reels |
| MP4 9:16 | 1080x1920 | TikTok |
| MP4 9:16 | 1080x1920 | YouTube Shorts |
| MP4 1:1 | 1080x1080 | Instagram Feed (alt) |

## Related Skills

- [ai-clip-maker](/skills/ai-clip-maker) — Clip extraction
- [ai-video-creator](/skills/ai-video-creator) — Video creation
- [video-maker-ai](/skills/video-maker-ai) — AI video maker
