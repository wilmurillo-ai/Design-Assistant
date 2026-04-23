---
name: ai-video-rotate
version: "1.0.0"
displayName: "AI Video Rotate — Rotate Flip and Fix Video Orientation with AI"
description: >
  Rotate, flip, and fix video orientation with AI — correct sideways recordings, flip for mirror effect, rotate to any angle, and fix orientation metadata issues. NemoVideo handles: 90-degree rotation for sideways phone recordings, 180-degree rotation for upside-down footage, horizontal flip for mirror-image correction, vertical flip, custom angle rotation with AI background fill, and automatic orientation detection and correction. Rotate video online, fix sideways video, flip video, video orientation fix, turn video, rotate video 90 degrees, mirror video, video rotation tool.
metadata: {"openclaw": {"emoji": "🔄", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video Rotate — Fix the Orientation. Save the Footage.

It happens to everyone. You record an important moment — a child's first steps, a crucial meeting, a once-in-a-lifetime event — and when you play it back, it is sideways. The phone was held in the wrong orientation. The camera's auto-rotation failed. The screen recording captured in portrait when it should have been landscape. The footage is perfect except for one thing: it is rotated 90 degrees and unwatchable without tilting your head. This is one of the most common video problems in the world. Smartphones record billions of videos per day, and orientation errors affect an estimated 5-10% of all recordings. That is hundreds of millions of sideways, upside-down, or mirror-flipped videos created every day. Simple rotation — turning the video 90 degrees — is available in most tools. But simple rotation creates problems: a 1920x1080 landscape video rotated 90 degrees becomes 1080x1920 with black bars if the player expects landscape, or the resolution changes unexpectedly, or text overlays that were horizontal are now vertical. NemoVideo handles rotation intelligently: rotating the video, adjusting the canvas, maintaining resolution quality, correcting any text overlays, and optionally filling black bar areas with AI-generated content or blurred extensions.

## Use Cases

1. **Sideways Phone Recording — 90° Fix (any length)** — A parent recorded their child's school play but held the phone sideways. The entire 30-minute recording is rotated 90 degrees clockwise. NemoVideo: rotates 90° counter-clockwise, adjusts the canvas to match the new orientation, maintains original resolution quality (no quality loss from re-encoding), and exports as a properly oriented video. Thirty minutes of precious footage saved from being unwatchable.

2. **Upside-Down Footage — 180° Correction (any length)** — An action camera was mounted upside-down (common with GoPro chest mounts and helmet mounts). NemoVideo: detects the 180° orientation issue, flips both vertically and horizontally simultaneously (equivalent to 180° rotation), preserves all metadata and audio sync, and exports correctly oriented. Entire adventure footage recovered.

3. **Mirror Fix — Horizontal Flip for Selfie Video (any length)** — A creator recorded a tutorial using the front-facing camera. The text on their whiteboard appears mirror-reversed. NemoVideo: applies horizontal flip (mirror), correcting all text readability while flipping the speaker's appearance (viewers do not notice the speaker is mirrored; they absolutely notice mirrored text). Tutorial footage becomes usable.

4. **Creative Rotation — Artistic Angle (any length)** — A music video director wants a scene where the world gradually tilts: starting normal and rotating 45 degrees over 10 seconds. NemoVideo: applies smooth animated rotation from 0° to 45° over the specified duration, fills the exposed corners with AI-extended background (no black triangles), maintains subject focus during the rotation, and creates a disorienting artistic effect. Creative rotation for visual storytelling.

5. **Batch Orientation Fix — Multiple Clips (multiple files)** — A photographer shot an event on their phone, alternating between portrait and landscape throughout the day. Some clips are correct, some are sideways, some are upside-down. NemoVideo: auto-detects the intended orientation of each clip using content analysis (not just metadata, which is often wrong), applies the correct rotation per clip, and exports all clips in consistent orientation. A mixed-orientation event becomes a consistently oriented collection ready for editing.

## How It Works

### Step 1 — Upload Video
Any video with orientation issues. NemoVideo auto-detects the problem in most cases.

### Step 2 — Specify Rotation
Auto-detect (AI determines correct orientation), manual (90°, 180°, 270°, custom), flip (horizontal/vertical), or animated rotation.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-rotate",
    "prompt": "Fix a sideways phone recording — the video is rotated 90 degrees clockwise and needs to be corrected to normal landscape orientation. Maintain original quality. Also create a vertical (9:16) version with face tracking for TikTok. And fix the orientation metadata so it plays correctly on all devices.",
    "rotation": "auto-detect",
    "fix_metadata": true,
    "additional_outputs": [
      {"format": "9:16", "tracking": "face", "platform": "tiktok"}
    ]
  }'
```

### Step 4 — Verify and Download
Play the corrected video. Confirm: orientation is correct, quality is maintained, audio is synced. Download.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Rotation description |
| `rotation` | string | | "auto-detect", "90-cw", "90-ccw", "180", "horizontal-flip", "vertical-flip", "custom" |
| `angle` | float | | Custom rotation angle in degrees |
| `animated` | object | | {from_angle, to_angle, duration} for animated rotation |
| `corner_fill` | string | | "ai-extend", "blur", "black", "mirror" for non-90° rotations |
| `fix_metadata` | boolean | | Correct orientation metadata |
| `additional_outputs` | array | | [{format, tracking, platform}] |
| `batch` | boolean | | Process multiple files |

## Output Example

```json
{
  "job_id": "avrot-20260328-001",
  "status": "completed",
  "detected_issue": "90° clockwise rotation",
  "correction_applied": "90° counter-clockwise",
  "quality": "lossless re-encode",
  "metadata_fixed": true,
  "outputs": {
    "corrected": {"file": "video-fixed.mp4", "resolution": "1920x1080", "orientation": "landscape"},
    "tiktok": {"file": "video-tiktok.mp4", "resolution": "1080x1920", "tracking": "face"}
  }
}
```

## Tips

1. **Auto-detect catches orientation issues that metadata misses** — Phone metadata often says "landscape" when the video is clearly portrait (or vice versa). NemoVideo's AI analyzes the actual content — faces, text, horizon lines — to determine the correct orientation regardless of metadata.
2. **Always fix metadata alongside visual rotation** — A visually rotated video with incorrect metadata will display wrong on some players and devices. Fixing both ensures universal compatibility.
3. **Horizontal flip fixes selfie text but consider the speaker** — Mirrored text is always worth fixing. But be aware that the speaker's parting, moles, and other asymmetric features will also flip. Most viewers never notice — text readability is more important.
4. **Batch orientation fix saves event footage** — When multiple clips from one event have mixed orientations, fixing them one by one is tedious. Batch auto-detect processes the entire collection in one operation.
5. **Creative rotation needs corner fill** — Rotating a video by any non-90° angle exposes empty corners. AI background extension fills these corners naturally, maintaining the visual flow without distracting black triangles.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |
| MOV | Original | Professional workflow |

## Related Skills

- [ai-video-resize](/skills/ai-video-resize) — Video resizing
- [ai-video-effects](/skills/ai-video-effects) — Video effects
- [ai-video-loop](/skills/ai-video-loop) — Video loops
