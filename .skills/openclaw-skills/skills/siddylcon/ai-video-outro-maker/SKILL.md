---
name: ai-video-outro-maker
version: "1.0.0"
displayName: "AI Video Outro Maker — Create End Screens Subscribe Cards and Closing Sequences"
description: >
  Create end screens, subscribe cards, and closing sequences with AI — generate professional video outros with animated subscribe buttons, next video suggestions, social media links, end cards, credit rolls, and branded closing animations. NemoVideo builds complete outro sequences that maximize post-video actions: subscribe clicks, next video watches, social follows, and website visits. Turn the last 15-20 seconds of every video into an engagement machine. Video outro maker AI, end screen creator, YouTube end card maker, subscribe animation, closing sequence generator, video ending maker, outro template creator.
metadata: {"openclaw": {"emoji": "🔚", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video Outro Maker — Turn Every Ending into the Next Beginning

The last 20 seconds of a video are the most underutilized real estate in content creation. The viewer just finished watching — they are maximally engaged with the creator and primed for action. Yet most videos simply end: a cut to black, an awkward goodbye, or an abrupt stop. No subscribe prompt. No next video suggestion. No social link. No call to action. Every video that ends without an outro is a missed conversion opportunity. YouTube's end screen feature allows interactive elements in the final 5-20 seconds, but only if the video has visual space designed for those elements. A properly designed outro provides: a visual framework for YouTube's end screen elements (video suggestions, subscribe button, channel link), animated call-to-action prompts that guide the viewer's eye, social media handles and links for cross-platform growth, branded closing animation for professional consistency, and a smooth emotional landing after the content's climax. NemoVideo generates complete outros tailored to each creator's brand and platform strategy. Describe your channel and goals — the AI produces an outro with animated elements, background music, call-to-action text, social handles, and designated spaces for platform-native interactive elements.

## Use Cases

1. **YouTube End Screen Outro — Maximize Subscribe and Watch Next (15-20s)** — A YouTube creator needs an outro that works with YouTube's end screen feature. NemoVideo generates: a branded background with animated elements (subtle motion keeps attention during the outro), two designated rectangular zones for YouTube's end screen video suggestions (positioned for optimal click-through), a subscribe button animation zone (YouTube's circular subscribe element fits here), animated text ("If you enjoyed this, you'll love..." / "Subscribe for weekly videos"), background music that provides a satisfying emotional closure, and the channel logo for final brand impression. The outro that turns viewers into subscribers.

2. **Social CTA Outro — Drive Cross-Platform Follows (10-15s)** — A creator active on multiple platforms needs viewers to follow everywhere. NemoVideo creates: animated social media icons (Instagram, TikTok, Twitter, Discord) that appear sequentially with corresponding handles, a QR code for the creator's link-in-bio page (scannable from screen), a "Follow me everywhere" or "Join the community" call to action, and a subtle animated background. The outro that grows all platforms simultaneously.

3. **Podcast Outro — Professional Show Closing (15-25s)** — A video podcast needs a consistent closing sequence for every episode. NemoVideo generates: host name and title animation, show logo animation, "Available on Apple Podcasts, Spotify, YouTube" with platform icons, next episode teaser text ("Next week: [Guest Name] on [Topic]"), and a musical outro that fades professionally. A broadcast-quality show closing from a text prompt.

4. **Course/Tutorial Outro — Guide to Next Lesson (10-15s)** — An educational creator needs outros that guide students through a learning path. NemoVideo creates: "Up Next: [Lesson Title]" with visual preview, progress indicator ("Lesson 3 of 12 complete"), animated checkmark for lesson completion, CTA to playlist or course page, and encouraging text ("You're making great progress!"). The pedagogical outro that keeps students moving through the curriculum.

5. **Short-Form CTA — TikTok/Reels Follow Prompt (3-5s)** — Short-form content needs a fast, punchy outro — not a 20-second end screen. NemoVideo creates: a 3-second animated overlay ("Follow for Part 2" / "More tips on my page"), bold text with the creator's handle, a subtle visual cue (arrow pointing to the follow button's screen position), and an audio cue (notification sound). The micro-outro that converts short-form viewers into followers.

## How It Works

### Step 1 — Describe Your Channel and Goals
Channel name, brand colors, primary platform, content category, and desired viewer actions (subscribe, watch next, follow social, visit website).

### Step 2 — Choose Outro Style
End screen (YouTube-optimized), social CTA, podcast closing, course navigation, or short-form CTA.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-outro-maker",
    "prompt": "Create a 20-second YouTube outro for a cooking channel called TastyMinutes. Brand colors: warm orange (#FF6B35) and cream (#FFF8F0). Style: warm, inviting, kitchen-cozy. Elements: (1) Two rectangles for YouTube end screen video suggestions positioned in the right two-thirds. (2) Subscribe button zone in the bottom-left. (3) Animated text: Thanks for cooking with me! in handwritten-style font. (4) Social handles: @TastyMinutes on Instagram and TikTok, animated sequentially. (5) Gentle acoustic guitar background music. (6) Channel logo fade-in at the end. Export 16:9 at 1080p.",
    "brand": {
      "name": "TastyMinutes",
      "colors": ["#FF6B35", "#FFF8F0"],
      "category": "cooking"
    },
    "outro_type": "youtube-end-screen",
    "duration": 20,
    "elements": ["video-suggestions", "subscribe-zone", "social-handles", "logo-close"],
    "social": {"instagram": "@TastyMinutes", "tiktok": "@TastyMinutes"},
    "music": "acoustic-guitar-warm",
    "format": "16:9"
  }'
```

### Step 4 — Add YouTube End Screen Elements
Upload the outro to YouTube, then add end screen elements (video suggestions, subscribe) in the designated zones. The outro's visual design guides element placement.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Outro description and brand context |
| `brand` | object | | {name, colors, logo_url, category} |
| `outro_type` | string | | "youtube-end-screen", "social-cta", "podcast-close", "course-nav", "short-form-cta" |
| `duration` | float | | Outro length in seconds |
| `elements` | array | | ["video-suggestions", "subscribe-zone", "social-handles", "logo-close", "qr-code"] |
| `social` | object | | {instagram, tiktok, twitter, discord, website} |
| `music` | string | | Background music style |
| `cta_text` | string | | Custom call-to-action text |
| `next_episode` | object | | {title, guest} for series |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "avoutro-20260328-001",
  "status": "completed",
  "outro_duration": "20.0s",
  "brand": "TastyMinutes",
  "elements": {
    "video_suggestion_zones": 2,
    "subscribe_zone": true,
    "social_handles": ["instagram", "tiktok"],
    "logo_animation": true
  },
  "outputs": {
    "outro": {"file": "tastyminutes-outro-16x9.mp4", "resolution": "1920x1080"},
    "audio": {"file": "tastyminutes-outro-music.wav"}
  }
}
```

## Tips

1. **YouTube end screen elements need designated visual space** — YouTube's interactive elements (video suggestions, subscribe button) are overlay graphics placed in the final 5-20 seconds. The outro must have clean zones where these elements will appear without covering important visuals or text.
2. **The subscribe prompt works because the viewer just consumed value** — Post-video is the highest-intent moment for subscription. The viewer just received value and is deciding whether to commit. A clear, well-timed subscribe prompt at this moment converts significantly better than mid-video interruptions.
3. **Two video suggestions outperform one** — YouTube allows up to two end screen video elements. Using both gives the viewer a choice (latest video + best video, or two related topics), doubling the chance that one resonates enough to click.
4. **Short-form outros must be under 5 seconds** — TikTok and Reels viewers will scroll the moment content feels over. A 3-second "Follow for more" overlay is effective. A 15-second end screen is a guaranteed swipe-away on short-form platforms.
5. **Consistent outros compound into brand recognition** — Like intros, the same outro visual and audio signature across all videos creates a Pavlovian association: this closing sequence means "good content just ended, subscribe for more." Consistency builds the association; variation breaks it.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube |
| MP4 9:16 | 1080x1920 | TikTok / Reels |
| MP4 1:1 | 1080x1080 | Instagram |
| MOV (alpha) | 1080p | Overlay compositing |

## Related Skills

- [ai-video-intro-maker](/skills/ai-video-intro-maker) — Video intros
- [ai-video-thumbnail-maker](/skills/ai-video-thumbnail-maker) — Thumbnails
- [ai-video-highlight-maker](/skills/ai-video-highlight-maker) — Highlight reels
