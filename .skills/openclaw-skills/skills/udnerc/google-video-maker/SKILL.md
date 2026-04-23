---
name: google-video-maker
version: "2.0.1"
displayName: "AI Video Maker - Create Professional Videos with AI Assistant"
description: >
  Create professional videos with AI — generate marketing videos, product demos, social media clips, training content, and promotional videos from text or images without video editing experience. NemoVideo handles the complete production pipeline: automated scene composition, voiceover generation, background music, animated text overlays, transitions, and export in every platform format. Build videos for YouTube, TikTok, Instagram Reels, LinkedIn, website landing pages, and internal communications in minutes. AI video maker, create video with AI, professional video generator, automated video creation, AI marketing video, text to video AI, video maker online, social media video creator, product demo video AI, promotional video maker.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video Maker — Professional Videos from Text, Images, or a Simple Prompt

Create professional videos for any purpose — marketing, product demos, social media, training, or internal communications — without a camera, editing software, or production team. Describe what you need and NemoVideo builds the complete video.

## What You Can Create

1. **Marketing and Promotional Videos** — Product launches, brand stories, service explainers, and campaign content for every platform.

2. **Social Media Clips** — Short-form content optimized for TikTok, Instagram Reels, YouTube Shorts, and LinkedIn — correct aspect ratio, pacing, and format for each platform.

3. **Product Demo Videos** — Feature walkthroughs, how-it-works animations, and comparison videos that convert visitors into customers.

4. **Training and Onboarding Videos** — Employee onboarding, process walkthroughs, compliance training, and knowledge transfer content.

5. **Internal Communications** — Company updates, announcements, team recognition, and event recaps.

## How It Works

### Step 1 — Describe Your Video
Write a prompt describing what you want: topic, audience, tone, length, and any specific requirements.

### Step 2 — Configure Output
Set format (16:9, 9:16, 1:1), duration, style, branding elements, and voice preferences.

### Step 3 — Generate and Review
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "google-video-maker",
    "prompt": "Create a 60-second product marketing video for a project management app. Target audience: small business owners. Tone: professional but approachable. Highlight: saves 5 hours per week, easy team collaboration, mobile-friendly. CTA: Start free trial. Format: 16:9 for YouTube and 9:16 for Instagram Stories.",
    "duration": 60,
    "formats": ["16:9", "9:16"],
    "style": "modern-professional",
    "voiceover": true,
    "music": "upbeat-corporate"
  }'
```

### Step 4 — Export and Publish
Download in your required format and resolution, ready for direct upload to any platform.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Video description and requirements |
| `duration` | number | | Target length in seconds |
| `formats` | array | | ["16:9", "9:16", "1:1"] |
| `style` | string | | "modern-professional", "minimal", "bold", "cinematic" |
| `voiceover` | boolean | | Include AI narration |
| `music` | string | | Background music style |
| `branding` | object | | {logo, colors, fonts} |
| `cta` | string | | Call-to-action text |

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / Website / Presentations |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Stories |
| MP4 1:1 | 1080x1080 | LinkedIn / Facebook / Email |

## Related Skills

- [add-subtitles-to-video](/skills/add-subtitles-to-video) — Auto-generate captions
- [ai-video-voiceover](/skills/ai-video-voiceover) — Custom narration
- [ai-video-music-sync](/skills/ai-video-music-sync) — Sync music to video beats
