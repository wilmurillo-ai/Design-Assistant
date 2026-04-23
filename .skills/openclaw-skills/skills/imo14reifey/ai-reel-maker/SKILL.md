---
name: ai-reel-maker
version: 1.0.1
displayName: "AI Reel Maker — Create Instagram Reels and Short Videos with AI Automatically"
description: >
  Create Instagram Reels and short-form videos using AI — turn raw footage, photos, or text into scroll-stopping vertical content with trending captions, beat-synced transitions, background music, speed ramps, and hook-first editing. NemoVideo applies the Reels editing playbook automatically: bold opening hook, tight pacing with zero dead air, word-by-word animated captions for sound-off viewers, energy-matched music, and 9:16 export optimized for Instagram's algorithm and engagement patterns.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Reel Maker — Create Instagram Reels with AI

Instagram Reels is the platform's fastest-growing content format and the primary driver of organic reach in 2026. Accounts that post Reels consistently get 2-3x more impressions than those posting only photos and carousels. But Reels demand a specific editing style that most creators struggle to produce: a hook in the first 1.2 seconds that stops the scroll, fast pacing without dead air, captions styled for sound-off viewing (70% of Reels play on mute), music that matches the content's energy, and a duration that's long enough to satisfy but short enough to retain. Producing a polished 30-second Reel in Premiere or CapCut takes 30-60 minutes of manual editing: cropping to 9:16, timing captions word-by-word, syncing cuts to music beats, testing hook variations, and exporting with Instagram's preferred codec settings. NemoVideo produces Reels-optimized content in one command. Upload raw footage (any orientation, any length), describe the edit, and receive a vertical video with AI-generated hook, silence removal, word-by-word animated captions, beat-synced transitions, and 9:16 1080x1920 export — every Instagram editing best practice applied automatically.

## Use Cases

1. **Talking-Head → Reel (15-60s)** — A creator has a 4-minute horizontal recording of a hot take. NemoVideo: finds the most provocative 35-second segment via transcript analysis, crops to 9:16 with face-tracking, adds a text hook in the first 1.2 seconds ("Nobody wants to hear this but..."), removes all silences over 0.4 seconds, adds word-by-word highlight captions (white text, pink active word on a translucent dark pill), and overlays trending music at -14dB synced to zoom-cut transitions. Four minutes of raw footage becomes a scroll-stopping Reel.
2. **Product Photos → Carousel Reel (15-30s)** — An e-commerce brand has 6 product photos. NemoVideo: applies Ken Burns motion to each photo (slow zoom on details, pan across textures), transitions between photos on musical beats, overlays product name and price as animated text, adds an upbeat track, and exports 9:16 with "Shop now" CTA at the end. Static product images become a dynamic shopping Reel.
3. **Recipe → Quick Tutorial Reel (30-60s)** — A food creator has 6 minutes of cooking footage. NemoVideo: extracts action moments only (chopping, sizzling, plating — 2-4 seconds each), removes all waiting and prep, adds step labels ("Step 1: Sear the salmon"), syncs cuts to upbeat music, slow-mo on the final plated shot, and adds "Save this recipe 📌" text overlay. Six minutes become 40 seconds of mouth-watering content.
4. **Before/After → Transformation Reel (10-20s)** — A home renovation, makeup transformation, or fitness progress. NemoVideo: shows "before" for 3 seconds with desaturated color and muted audio, hits a bass-drop transition (flash + zoom + color pop), reveals "after" with vibrant color grade and energetic music, loops the final 2 seconds for replay satisfaction. The format with the highest save rate on Instagram.
5. **Text → Reel — No Footage Needed (15-45s)** — A motivational quote, a business tip, or a fun fact. NemoVideo generates: atmospheric background visuals, bold animated text displaying the quote word-by-word, dramatic voiceover narration, cinematic music, and 9:16 export. Content creation from text alone — no camera, no footage, no filming.

## How It Works

### Step 1 — Upload Material
Provide: video clips (any orientation), photos, or just text. NemoVideo handles 9:16 conversion with intelligent subject tracking.

### Step 2 — Choose Reel Style
Pick: talking-head, product showcase, recipe tutorial, transformation, text-to-reel, or montage. Each applies format-specific optimizations.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-reel-maker",
    "prompt": "Create an Instagram Reel from a 4-minute horizontal talking-head video. Find the most engaging 35-second segment. Hook: text overlay with the most controversial sentence in the first 1.2 seconds. Crop 9:16 with face tracking. Captions: word-by-word highlight, white text, pink (#FF69B4) active word, dark pill background. Remove silences over 0.4 sec. Zoom-cuts every 6 seconds. Music: trending pop-lo-fi at -14dB, beat-synced to zoom cuts.",
    "reel_style": "talking-head",
    "target_duration": "35 sec",
    "hook": "auto-controversial",
    "captions": {"style": "word-highlight", "text": "#FFFFFF", "highlight": "#FF69B4", "bg": "pill-dark"},
    "silence_threshold": 0.4,
    "zoom_cuts_interval": 6,
    "music": "trending-pop-lo-fi",
    "music_volume": "-14dB",
    "beat_sync": true,
    "format": "9:16"
  }'
```

### Step 4 — Preview and Post
Preview. Adjust hook, captions, or music. Export and post to Instagram.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe footage and desired Reel |
| `reel_style` | string | | "talking-head", "product", "recipe", "transformation", "text-to-reel", "montage" |
| `target_duration` | string | | "15 sec", "30 sec", "45 sec", "60 sec", "90 sec" |
| `hook` | string | | "auto-controversial", "auto-question", "custom-text", "visual-surprise" |
| `captions` | object | | {style, text, highlight, bg} configuration |
| `silence_threshold` | float | | Seconds (default: 0.4) |
| `zoom_cuts_interval` | integer | | Seconds between cuts (default: 6) |
| `music` | string | | "trending-pop-lo-fi", "energetic", "dramatic", "acoustic", "custom" |
| `music_volume` | string | | "-12dB" to "-18dB" (default: "-14dB") |
| `beat_sync` | boolean | | Sync cuts to beats (default: true) |
| `speed_ramp` | boolean | | Speed variations for energy (default: false) |
| `format` | string | | "9:16" (Instagram standard) |

## Output Example

```json
{
  "job_id": "arm-20260328-001",
  "status": "completed",
  "source_duration": "4:12",
  "reel_duration": "0:34",
  "format": "mp4",
  "resolution": "1080x1920",
  "file_size_mb": 9.8,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/arm-20260328-001.mp4",
  "reel_edit": {
    "hook": "Nobody wants to hear this but your morning routine is wasting your life (0:00-0:01.2)",
    "segment": "2:08-2:48 (highest energy)",
    "silences_removed": "0:06 (12 cuts)",
    "zoom_cuts": 5,
    "captions": "word-highlight white/#FF69B4 (32 words)",
    "music": "trending-pop-lo-fi at -14dB, beat-synced",
    "face_tracking": "centered, 97% coverage"
  }
}
```

## Tips

1. **The hook decides your reach** — Instagram shows the first 1.2 seconds to decide whether to push the Reel. A text overlay with a provocative claim or a visual surprise outperforms a slow "Hey guys" intro by 10x.
2. **0.4-second silence threshold for Reels** — Instagram viewers scroll faster than YouTube viewers. Any pause over half a second kills momentum. Aggressive silence removal is non-negotiable.
3. **Word-by-word captions are the #1 engagement driver** — 70% of Reels play on mute. Animated captions keep sound-off viewers watching by creating a reading rhythm that anchors attention.
4. **Beat-synced cuts feel native to the platform** — Instagram's culture rewards musical editing. Cuts landing on beats make content feel like it belongs on the platform rather than being repurposed from elsewhere.
5. **Save-worthy content gets algorithmic boost** — Reels that viewers save (recipes, tutorials, lists) get pushed harder by Instagram's algorithm. End with "Save this for later 📌" to drive saves.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | Instagram Reels (primary) |
| MP4 9:16 | 1080x1920 | TikTok cross-post |
| MP4 4:5 | 1080x1350 | Instagram feed video |
| MP4 1:1 | 1080x1080 | Instagram carousel |

## Related Skills

- [ai-shorts-creator](/skills/ai-shorts-creator) — YouTube Shorts creation
- [ai-video-script-generator](/skills/ai-video-script-generator) — Video script writing
- [ai-thumbnail-maker](/skills/ai-thumbnail-maker) — Thumbnail generation
