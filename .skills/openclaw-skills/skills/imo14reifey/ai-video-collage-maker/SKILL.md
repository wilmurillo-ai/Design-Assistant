---
name: ai-video-collage-maker
version: 1.0.1
displayName: "AI Video Collage Maker — Combine Multiple Videos into Split-Screen and Grid Layouts"
description: >
  Combine multiple videos into split-screen and grid layouts with AI — create side-by-side comparisons, multi-angle views, reaction-alongside-content formats, before-and-after splits, and dynamic grid compositions that show multiple perspectives simultaneously. NemoVideo arranges videos intelligently: auto-syncing audio across clips, balancing visual weight across grid cells, animating transitions between layout configurations, and producing the multi-video formats that dominate reaction content comparison videos and social media storytelling. AI video collage maker, split screen video, video grid maker, multi video layout, side by side video, video comparison maker, reaction video layout, picture in picture video, multi angle video.
metadata: {"openclaw": {"emoji": "🔲", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Collage Maker — Multiple Videos. One Frame. Maximum Impact.

Split-screen and grid layouts are among the highest-engagement video formats on every platform. Reaction videos (creator's face alongside the content they are reacting to) are a billion-view genre on YouTube. Before-and-after comparisons (transformation shown simultaneously rather than sequentially) drive massive engagement on TikTok and Instagram. Multi-angle event coverage (three camera angles shown simultaneously) creates the broadcast-quality feel of professional production. Side-by-side product comparisons let viewers evaluate options without trusting a single narrator's opinion. The power of the collage format is simultaneous comparison. Sequential comparison (showing A, then showing B) relies on memory — the viewer must remember A while watching B. Simultaneous comparison (showing A and B side by side) eliminates memory load: differences are immediately visible, relationships are instantly apparent, and the viewer processes both inputs in real-time. This cognitive efficiency makes collage content more informative per second of watch time than any single-camera format. Creating video collages traditionally requires manual layout in editing software: positioning each video precisely within the frame, syncing audio tracks, managing the visual balance between clips of different brightness and energy levels, and ensuring the layout works at the final display size. NemoVideo automates this entire process: arranging videos in optimized layouts, syncing audio, balancing visual weight, and producing professional multi-video compositions.

## Use Cases

1. **Reaction Video — Creator Alongside Content (any length)** — The reaction format places the creator's face (showing real-time reactions) alongside the content being watched. NemoVideo: positions the reaction camera and the source content in optimized proportions (typically 30% reaction face / 70% source content, or 50/50 for commentary-heavy reactions), syncs the creator's audio reactions to the source content timeline, ensures the reaction face is large enough to read expressions at mobile viewing size, adds optional picture-in-picture mode (reaction face as a floating overlay rather than fixed split), and produces the reaction layout that drives engagement through the parasocial experience of watching content together with a creator.

2. **Before and After — Transformation Comparison (15-60s)** — Fitness transformations, home renovations, makeup tutorials, photo editing results, and any content showing change benefits from simultaneous comparison. NemoVideo: creates a clean split-screen with the "before" clip on one side and the "after" clip on the other, adds clear labels ("Before" / "After" or "Day 1" / "Day 90"), optionally adds a reveal animation (the "after" side slides in to replace the "before" or a divider line moves across the frame), syncs timing so both clips show comparable moments (same angle, same movement), and produces a transformation video that makes the change undeniable.

3. **Multi-Angle Event — Broadcast-Style Coverage (any length)** — Concerts, sports events, weddings, conferences, and presentations filmed from multiple cameras benefit from multi-angle display. NemoVideo: arranges 2-4 camera angles in a balanced grid layout, auto-selects which angle to feature (the angle with the most visual action gets the largest cell, or cycles the featured position), syncs all angles to the same timeline (ensuring simultaneous playback), manages audio (selecting the best audio source or mixing multiple sources), and produces multi-angle video with the production quality of broadcast television from consumer camera footage.

4. **Product Comparison — Side by Side Evaluation (60-300s)** — Comparing two or more products simultaneously is more persuasive than sequential comparison. NemoVideo: places products side by side with matched framing (same angle, same lighting, same scale), adds comparison labels and feature callouts per product, syncs demonstration actions (both products performing the same task at the same time), highlights differences with visual indicators, and produces a comparison video that lets viewers evaluate products with their own eyes rather than trusting a narrator's subjective assessment.

5. **Social Media Grid — Multi-Moment Storytelling (15-60s)** — A 4-panel or 6-panel grid showing multiple moments simultaneously: a day in 4 clips, a recipe in 6 steps, a trip in 4 cities. NemoVideo: arranges clips in visually balanced grid layouts (2x2, 3x2, 2x3), sequences when each cell activates (all simultaneously, or one-by-one with staggered starts for narrative effect), adds subtle borders and spacing between cells, applies consistent color treatment across all clips for visual unity, and produces grid content that tells multi-moment stories in a single frame.

## How It Works

### Step 1 — Upload Multiple Videos
Two or more video clips to combine. Specify which clip goes in which position, or let NemoVideo auto-arrange based on content analysis.

### Step 2 — Choose Layout
Split-screen (2 clips), grid (3-6 clips), picture-in-picture (overlay), or dynamic (layout changes during the video).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-collage-maker",
    "prompt": "Create a before-and-after split-screen video showing a home renovation. Left side: before footage (messy, outdated kitchen). Right side: after footage (modern, clean kitchen). Clean vertical divider line between sides. Labels: BEFORE (left, red) and AFTER (right, green). Start with full-screen BEFORE for 3 seconds, then the divider slides from left to right revealing the AFTER side. Hold split-screen for 15 seconds. Then full-screen AFTER for 3 seconds. Total duration: ~21 seconds. Sync both clips to show the same camera angle. Add subtle reveal sound effect when the divider moves. Export 9:16 for TikTok and 16:9 for YouTube.",
    "layout": "split-screen-reveal",
    "clips": {
      "left": {"label": "BEFORE", "label_color": "#FF0000"},
      "right": {"label": "AFTER", "label_color": "#00CC00"}
    },
    "reveal": {"type": "divider-slide", "direction": "left-to-right", "duration": "2s"},
    "sound_effect": "reveal-swoosh",
    "formats": ["9:16", "16:9"]
  }'
```

### Step 4 — Verify Layout Balance
Watch the collage at the target display size (especially mobile for social content). Check: is each video cell large enough to see clearly? Is the audio mix balanced between clips? Does the visual weight feel balanced across the frame? Are labels readable? Adjust layout proportions and re-render.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Collage layout requirements |
| `layout` | string | | "split-screen", "grid-2x2", "grid-3x2", "pip", "dynamic" |
| `clips` | object | | Position and label per clip |
| `reveal` | object | | {type, direction, duration} for animated reveals |
| `audio` | string | | "mix-all", "primary-clip", "mute-secondary" |
| `sync` | string | | "timeline-sync", "action-sync", "independent" |
| `borders` | object | | {width, color, style} between cells |
| `sound_effect` | string | | SFX for transitions |
| `formats` | array | | ["16:9", "9:16", "1:1"] |

## Output Example

```json
{
  "job_id": "avcol-20260329-001",
  "status": "completed",
  "layout": "split-screen-reveal",
  "clips": 2,
  "duration": "0:21",
  "outputs": {
    "tiktok": {"file": "renovation-split-9x16.mp4"},
    "youtube": {"file": "renovation-split-16x9.mp4"}
  }
}
```

## Tips

1. **Simultaneous comparison eliminates memory load** — Showing A then B requires viewers to remember A. Showing A beside B lets viewers see differences instantly. For any content involving comparison (before/after, product vs product, angle vs angle), split-screen is strictly more informative than sequential display.
2. **Reaction video proportions matter — 30/70 for content-focused, 50/50 for commentary-focused** — If the source content needs to be clearly visible (watching a music video, reviewing a film), give it 70% of the frame. If the creator's commentary and reactions are the primary value, use 50/50 or even 60/40 favoring the reaction face.
3. **Audio management determines whether collage video works** — Two video clips playing audio simultaneously creates chaos. Always designate one primary audio source. For reactions: source content audio + creator commentary. For comparisons: narration track only. For multi-angle: single best-quality audio source.
4. **Grid layouts need consistent visual treatment across cells** — Clips filmed at different times with different lighting look mismatched in a grid. Apply consistent color correction across all cells so the collage looks intentional rather than thrown together.
5. **Animated reveals (the divider slide) generate more engagement than static splits** — A before/after split that starts as one view and dramatically reveals the other creates a moment of surprise and satisfaction. The static split is informative; the animated reveal is engaging.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / Facebook |

## Related Skills

- [video-editor-ai](/skills/video-editor-ai) — Full video editing
- [video-transition-maker](/skills/video-transition-maker) — Transitions
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Labels and text
