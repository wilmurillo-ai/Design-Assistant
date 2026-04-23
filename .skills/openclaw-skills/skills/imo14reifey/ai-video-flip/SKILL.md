---
name: ai-video-flip
version: "1.0.0"
displayName: "AI Video Flip — Flip Videos Horizontally or Vertically for Any Purpose with AI"
description: >
  Flip videos horizontally or vertically with AI — correct mirrored selfie recordings, create artistic flip effects, fix upside-down footage, produce split-screen flip comparisons, and apply creative flip transitions. NemoVideo flips with intelligence: detecting text that needs correction, preserving audio sync, maintaining quality through the transformation, and optionally applying creative flip-based effects. Flip video online, horizontal flip video, vertical flip video, mirror flip video, reverse image video, flip video for TikTok, invert video.
metadata: {"openclaw": {"emoji": "🔃", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video Flip — Correct, Create, and Transform with Flip Operations

Flipping a video is one of the simplest operations and one of the most frequently needed. Horizontal flip corrects selfie-camera mirror effects — the #1 post-recording fix for front-facing camera content. Vertical flip fixes upside-down recordings from inverted camera mounts. Creative flips produce artistic effects: the world turned on its head, reflections that do not match reality, and disorienting visual tricks that drive social media engagement. The operation is simple but the applications are surprisingly diverse. A dance creator needs their tutorial flipped for students. A real estate agent needs their property tour flipped because the camera mirrored the layout. A music video director wants scenes that transition from normal to flipped for artistic effect. A content creator wants to reuse footage without it being recognizable as a repeat (horizontal flip makes footage look like a different shot). NemoVideo handles every flip scenario: one-click corrections, creative flip effects, batch flipping for entire libraries, and smart detection of what needs flipping (text, logos, directional signage).

## Use Cases

1. **Selfie Camera Fix — Text and Logo Correction (any length)** — Every front-facing phone recording mirrors the image. NemoVideo: detects mirrored text and logos in the frame, applies horizontal flip to correct readability, and preserves natural face appearance (viewers do not perceive face-flip because human faces are nearly symmetrical). The universal selfie fix.

2. **Upside-Down Fix — Inverted Recording (any length)** — A security camera, dashcam, or action camera was mounted upside-down. NemoVideo: detects the inverted orientation (people walking on ceilings, text upside-down), applies vertical flip (equivalent to 180° rotation for most cases), and exports correctly oriented. Entire recordings rescued from mounting errors.

3. **Creative Flip — Surreal Visual Effect (15-60s)** — A creator films a city street scene and wants to create a surreal effect where the world appears upside-down — buildings hanging from the sky, people walking on clouds. NemoVideo: vertically flips the footage, color grades to enhance the otherworldly feeling (slight desaturation, blue shift), and adds subtle effects (particles falling "upward"). A simple flip operation creates content that goes viral because the brain cannot reconcile the familiar scene with the inverted reality.

4. **Footage Reuse — Flip for Visual Freshness (any length)** — A creator has limited B-roll footage and needs it to appear in multiple videos without looking repetitive. NemoVideo: horizontally flips select clips, changing the visual direction (a car driving left-to-right becomes right-to-left, a person walking in one direction appears to walk in the other). The same footage looks like different shots — extending a limited B-roll library.

5. **Transition Effect — Normal to Flipped (any length)** — A creative transition where the video flips mid-scene — the world rotates and settles upside-down, or the left-right orientation reverses during a whip-pan. NemoVideo: applies animated flip transition (smooth rotation from normal to flipped over 0.5-1 second), optionally adding motion blur during the flip, and a settling effect at the destination orientation. Creative transitions that add production value.

## How It Works

### Step 1 — Upload Video
Any video that needs flipping — for correction or creative purposes.

### Step 2 — Choose Flip Operation
Horizontal flip, vertical flip, both (180° rotation equivalent), animated flip transition, or auto-detect and correct.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-flip",
    "prompt": "Horizontal flip a selfie video to correct mirrored text on the whiteboard behind me. Keep audio synced. Also create a creative version: an animated flip transition at 0:15 where the video smoothly rotates horizontally (like flipping a page) over 0.8 seconds, with motion blur during the flip. Export both versions at 9:16.",
    "operations": [
      {"type": "horizontal-flip", "purpose": "correction", "output": "corrected"},
      {"type": "animated-horizontal-flip", "at": "0:15", "duration": 0.8, "motion_blur": true, "output": "creative"}
    ],
    "format": "9:16"
  }'
```

### Step 4 — Verify
Check: text reads correctly in the corrected version, animated flip looks smooth in the creative version, audio is synced in both. Download.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Flip operation description |
| `flip_type` | string | | "horizontal", "vertical", "both", "animated", "auto-detect" |
| `animated` | object | | {at, duration, motion_blur, direction} |
| `operations` | array | | [{type, at, duration, output}] multiple flip operations |
| `format` | string | | "16:9", "9:16", "1:1" |
| `batch` | boolean | | Process multiple videos |

## Output Example

```json
{
  "job_id": "avflip-20260328-001",
  "status": "completed",
  "outputs": {
    "corrected": {"file": "tutorial-flipped-9x16.mp4", "flip": "horizontal", "text_corrected": true},
    "creative": {"file": "tutorial-creative-9x16.mp4", "animated_flip_at": "0:15", "duration": "0.8s"}
  }
}
```

## Tips

1. **Horizontal flip is the most common video fix in the world** — If you record with a front-facing camera, the output is mirrored. This affects: text readability, logo orientation, spatial accuracy, and directional consistency. Always flip selfie recordings before publishing professional content.
2. **Viewers do not notice flipped faces but instantly notice flipped text** — Human facial asymmetry is subtle enough that horizontal flip is imperceptible for faces. Text, logos, numbers, and directional signs are immediately and obviously wrong when mirrored.
3. **Flipped footage doubles your B-roll library** — A horizontally flipped version of the same clip looks like a different shot to most viewers. This extends limited footage without re-filming.
4. **Animated flip transitions add production value for zero creative cost** — A smooth page-flip transition between scenes communicates deliberate creative direction. It takes one sentence to add but gives the video a produced, intentional feel.
5. **Auto-detect saves time on mixed footage** — When some clips need flipping and others do not, auto-detection analyzes each clip for mirrored content and applies corrections only where needed. No manual review of every clip required.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram |

## Related Skills

- [ai-video-mirror](/skills/ai-video-mirror) — Mirror effects
- [ai-video-speed-changer](/skills/ai-video-speed-changer) — Speed changes
- [ai-video-zoom](/skills/ai-video-zoom) — Zoom effects

## Frequently Asked Questions

**Can I flip only part of a video?** — Yes. Specify a time range and NemoVideo flips only that segment, with smooth transitions at the boundaries. Useful for correcting a section where you switched to selfie camera mid-recording.

**Does flipping affect audio?** — No. Audio channels remain unchanged. Stereo left/right stays as recorded. Only the visual frame is flipped.

**What about text overlays added after flipping?** — Add text overlays after the flip operation. NemoVideo preserves any existing burned-in text readability by detecting and warning about text that would become mirrored.
