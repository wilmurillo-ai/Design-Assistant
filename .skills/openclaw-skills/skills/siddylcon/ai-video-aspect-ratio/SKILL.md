---
name: ai-video-aspect-ratio
version: 1.0.1
displayName: "AI Video Aspect Ratio — Change Video Aspect Ratio for Any Platform with AI"
description: >
  Change video aspect ratio for any platform with AI — convert between 16:9 landscape, 9:16 vertical, 1:1 square, 4:5 tall, 4:3 classic, and any custom ratio with intelligent subject tracking. NemoVideo reframes your video for every platform: YouTube (16:9), TikTok and Instagram Reels (9:16), Instagram Feed (1:1 or 4:5), LinkedIn (16:9 or 1:1), Facebook (16:9, 1:1, 4:5), Pinterest (2:3), and Twitter (16:9). One video becomes platform-native for every destination with AI subject tracking that keeps faces and key elements perfectly framed at every ratio. Change aspect ratio video, video ratio converter, landscape to portrait video, 16:9 to 9:16, square video maker, video reframe AI, multi-platform video, aspect ratio changer online.
metadata: {"openclaw": {"emoji": "📐", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Aspect Ratio — One Video. Every Platform. Every Shape.

Every social platform demands a different shape. YouTube wants 16:9 landscape. TikTok and Instagram Reels want 9:16 vertical. Instagram Feed performs best at 1:1 square or 4:5 tall. LinkedIn accepts 16:9 or 1:1. Facebook supports 16:9, 1:1, and 4:5 depending on placement. Pinterest prefers 2:3 or 9:16. Twitter uses 16:9 or 1:1. Publishing one video across all major platforms requires 4-6 different aspect ratio versions. The traditional workflow: duplicate your project in editing software, manually reframe for each aspect ratio, reposition text overlays and graphics for each version, re-render each export. For a single video: 30-60 minutes of purely mechanical reformatting. For a team publishing 10+ videos per week across platforms: 5-10 hours weekly of work that adds zero creative value. Center-cropping is not the answer. Cropping a 16:9 video to 9:16 by centering the crop removes 75% of the frame. If the speaker is positioned using rule-of-thirds composition (off-center, as most professional video is framed), they are partially or completely cropped out. If text overlays or graphics are near frame edges, they disappear. If the action moves laterally, it exits the visible area. Intelligent reframing is required: tracking the most important element in every frame and repositioning the crop window to keep it visible regardless of how the aspect ratio changes. NemoVideo reframes with AI subject tracking. The AI identifies faces, follows subjects, tracks movement, repositions overlays, and ensures every element that matters remains visible and properly framed at every aspect ratio.

## Use Cases

1. **YouTube to TikTok — 16:9 to 9:16 with Face Tracking (any length)** — A creator's 16:9 YouTube video needs a 9:16 TikTok version. The speaker is positioned left-of-center (rule-of-thirds). Center-cropping would cut their face in half. NemoVideo: tracks the speaker's face throughout the video, positions the vertical crop window to keep their face centered at every moment, follows any lateral movement (when they gesture, walk, or lean), repositions lower-third text overlays from bottom-left to bottom-center (visible in vertical), and moves captions to the vertical safe zone (above TikTok's UI overlay at the bottom 15%). A YouTube video that was composed for horizontal becomes a TikTok that feels native to vertical.

2. **Multi-Platform Export — One Source, Six Formats (any length)** — A brand's product launch video needs to be posted on YouTube (16:9), TikTok (9:16), Instagram Reels (9:16), Instagram Feed (1:1), LinkedIn (16:9 + 1:1), and Facebook (4:5). NemoVideo: generates all 6 versions from one source with intelligent reframing per aspect ratio, subject tracking adjusted per format, text overlays repositioned per version, platform-specific safe zone compliance (TikTok bottom 15%, Instagram top 10%), and caption positions adapted. Six platform-native versions from one upload.

3. **Presentation to Social — 16:9 Slides to Vertical (any length)** — A conference presentation was recorded in 16:9 widescreen: speaker on the left, slides on the right. NemoVideo: creates intelligent versions per ratio — for 9:16 vertical, alternates between speaker-focused framing (when they are speaking without referencing slides) and slide-focused framing (when slide content is the focus), detecting these transitions from speech content and visual cues. For 1:1 square, frames the speaker with a portion of the slide visible. Widescreen presentations become mobile-readable social content without losing either the speaker or the slides.

4. **E-Commerce — Product Content for Every Ad Format (batch)** — An online store has 16:9 product lifestyle videos that need to become ads across every platform. NemoVideo: reframes for each ad format (9:16 for TikTok Ads, 1:1 for Facebook Feed, 4:5 for Instagram Feed, 16:9 for YouTube Pre-roll, 2:3 for Pinterest), ensures the product remains centered and prominent at every ratio, repositions CTA overlays to each format's optimal placement, and processes the entire product catalog. One product video, every ad format, every platform.

5. **Archive Reformatting — 4:3 to Modern Formats (batch)** — A media company has a library of 4:3 (standard definition era) content that needs distribution on modern platforms. NemoVideo: reframes 4:3 to 16:9 (AI-extends or blurs the sides for widescreen), reframes to 9:16 for vertical platforms (subject tracking within the narrower window), reframes to 1:1 for social feeds, and batch-processes the entire library. Legacy content accessible on every modern platform without the pillarboxing or letterboxing that signals outdated content.

## How It Works

### Step 1 — Upload Source Video
Any aspect ratio input. NemoVideo accepts 16:9, 9:16, 4:3, 1:1, ultrawide, or any custom ratio.

### Step 2 — Select Target Ratios and Platforms
Choose one or multiple target aspect ratios. NemoVideo applies intelligent reframing and platform-specific adjustments for each.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-aspect-ratio",
    "prompt": "Convert a 16:9 talking-head YouTube video to all major platform formats. Speaker is positioned left-of-center using rule-of-thirds. Lower-third text at bottom-left. Captions at bottom-center. Generate: 9:16 (TikTok/Reels — face tracking, captions repositioned above TikTok UI zone), 1:1 (Instagram Feed/LinkedIn — speaker centered with slight background visible), 4:5 (Instagram Feed — speaker centered with more headroom), 2:3 (Pinterest — speaker centered). Keep all text readable. Reposition overlays per format. Export all at 1080p.",
    "source_ratio": "16:9",
    "targets": [
      {"ratio": "9:16", "platforms": ["tiktok", "reels"], "tracking": "face", "safe_zone": "tiktok"},
      {"ratio": "1:1", "platforms": ["instagram-feed", "linkedin"], "tracking": "face"},
      {"ratio": "4:5", "platforms": ["instagram-feed"], "tracking": "face"},
      {"ratio": "2:3", "platforms": ["pinterest"], "tracking": "face"}
    ],
    "reposition_overlays": true,
    "resolution": "1080p"
  }'
```

### Step 4 — Verify Each Version
Preview each aspect ratio version. Check: subject is never cut off, text is always readable, no important visuals are outside the frame. Download all versions.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Aspect ratio change requirements |
| `source_ratio` | string | | "16:9", "9:16", "4:3", "1:1", "custom" |
| `targets` | array | | [{ratio, platforms, tracking, safe_zone}] |
| `tracking` | string | | "face", "subject", "action", "center" |
| `reposition_overlays` | boolean | | Move text/captions for new ratios |
| `background_fill` | string | | "blur", "black", "ai-extend", "mirror" |
| `resolution` | string | | "720p", "1080p", "4K" |
| `batch` | array | | Multiple videos |

## Output Example

```json
{
  "job_id": "avar-20260329-001",
  "status": "completed",
  "source": "16:9 (1920x1080)",
  "outputs": {
    "tiktok_reels_9x16": {"file": "video-9x16.mp4", "resolution": "1080x1920", "tracking": "face"},
    "instagram_1x1": {"file": "video-1x1.mp4", "resolution": "1080x1080", "tracking": "face"},
    "instagram_4x5": {"file": "video-4x5.mp4", "resolution": "1080x1350", "tracking": "face"},
    "pinterest_2x3": {"file": "video-2x3.mp4", "resolution": "1000x1500", "tracking": "face"}
  },
  "overlays_repositioned": 6,
  "frames_tracked": "all"
}
```

## Tips

1. **Face tracking is essential when converting from landscape to vertical** — A speaker off-center in 16:9 will be cropped out in 9:16 without tracking. Always enable face tracking for any aspect ratio change involving videos with people.
2. **Platform safe zones differ and must be respected** — TikTok covers the bottom 15% with UI. Instagram Reels has different overlay positions. YouTube has progress bar controls at the bottom. Caption and overlay positioning must account for these per-platform UI elements.
3. **1:1 square is the most universal single format** — If forced to choose one aspect ratio that works acceptably everywhere, 1:1 square displays well on Instagram, Facebook, LinkedIn, and Twitter without severe cropping on any platform. It is the safest single-format choice.
4. **Multi-format from one source saves 5-10 hours per week** — Manual reformatting for each platform is the most tedious production task for any multi-platform creator. Automating it with AI reframing eliminates hours of mechanical work with zero quality loss.
5. **Overlay repositioning prevents invisible CTAs and lost captions** — A subscribe button designed for the bottom-left of 16:9 will be completely outside a 9:16 crop. Captions positioned for YouTube's bottom-center are hidden behind TikTok's UI. Always enable overlay repositioning when changing aspect ratios.

## Output Formats

| Ratio | Resolution | Platform |
|-------|-----------|----------|
| 16:9 | 1920x1080 / 3840x2160 | YouTube / LinkedIn / website |
| 9:16 | 1080x1920 | TikTok / Reels / Shorts / Stories |
| 1:1 | 1080x1080 | Instagram Feed / Facebook / LinkedIn |
| 4:5 | 1080x1350 | Instagram Feed |
| 2:3 | 1000x1500 | Pinterest |
| 4:3 | 1440x1080 | Legacy / presentation |

## Related Skills

- [ai-video-resize](/skills/ai-video-resize) — Video resizing
- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Auto captions
- [ai-video-intro-maker](/skills/ai-video-intro-maker) — Video intros
