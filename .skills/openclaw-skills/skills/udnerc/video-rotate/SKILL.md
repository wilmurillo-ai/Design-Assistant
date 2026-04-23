---
name: video-rotate
version: "1.0.0"
displayName: "Video Rotate — Rotate and Flip Videos with AI for Any Platform Orientation"
description: >
  Rotate and flip videos using AI — fix sideways recordings, convert horizontal to vertical, convert vertical to horizontal, rotate 90 180 or 270 degrees, flip horizontally or vertically, and reframe content for any platform orientation. NemoVideo handles rotation with intelligent reframing: when rotating from 16:9 to 9:16 the AI keeps the subject centered, when flipping for mirror correction it adjusts text overlays, and when converting between orientations it adds context-aware padding or smart cropping instead of black bars. Rotate video online, flip video, turn video sideways, fix upside down video, landscape to portrait, portrait to landscape, change video orientation.
metadata: {"openclaw": {"emoji": "🔄", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Video Rotate — Fix Orientation and Convert Between Formats Intelligently

Everyone has recorded a video in the wrong orientation. The camera was tilted 90 degrees, the footage plays sideways, and the viewer has to mentally rotate the image to make sense of it. Or the footage was accidentally recorded upside down (phone held inverted). Or the front camera captured a mirror image that makes all text backward. Or the video was shot horizontally but needs to be posted vertically on TikTok — or shot vertically but needs to be horizontal for a YouTube upload. Simple rotation (90°, 180°, 270°) fixes the most common problem: sideways footage. But orientation conversion between platforms requires more than rotation — it requires intelligent reframing. When a 16:9 horizontal video needs to become 9:16 vertical, simple rotation leaves you with a tiny strip of content surrounded by black bars. NemoVideo goes beyond basic rotation: the AI detects the subject in every frame (face tracking, object detection, motion analysis) and reframes the content to keep the important elements centered and visible in the new orientation. The result is not a rotated video with black bars — it is a properly reframed video that looks like it was shot natively in the target orientation.

## Use Cases

1. **Fix Sideways Recording (90° rotation)** — A parent recorded their child's school play but held the phone at 90 degrees. The footage plays sideways. NemoVideo: detects the 90° error, rotates the footage to correct orientation, and stabilizes any shake introduced by the awkward grip. The school play memory is saved without viewers tilting their heads.
2. **Horizontal → Vertical for TikTok/Reels (16:9 → 9:16)** — A creator has a YouTube video (16:9) that needs to be posted on TikTok (9:16). Simple rotation would create a tiny horizontal strip in a vertical frame. NemoVideo: analyzes every frame for subject position, creates a 9:16 crop that follows the subject's face and movements, adds smooth panning when the subject moves across the wide frame, and outputs a vertical video that looks natively shot on a phone — no black bars, no lost content.
3. **Vertical → Horizontal for YouTube (9:16 → 16:9)** — A TikTok creator wants to repurpose their best vertical videos for YouTube. NemoVideo: places the vertical video center-frame, generates context-aware background (blurred enlarged version of the video, or gradient matching the video's color palette), adds subtle animation to the background to prevent static feel, and exports a YouTube-ready 16:9 video that looks intentional rather than repurposed.
4. **Fix Upside-Down Recording (180° rotation)** — A dashcam or mounted camera was installed inverted, producing upside-down footage. NemoVideo: rotates 180° to correct orientation, verifies text readability (license plates, signs, timestamps), and adjusts any embedded timestamp overlay to read correctly after rotation.
5. **Mirror Correction (Horizontal Flip)** — A front-camera recording shows everything mirrored — text on shirts reads backward, gestures are reversed, and the presenter appears to be using their left hand when they're right-handed. NemoVideo: applies horizontal flip to correct the mirror effect, detects and re-mirrors any on-screen text overlays so they read correctly, and adjusts the video's spatial orientation so the presenter's movements feel natural.

## How It Works

### Step 1 — Upload the Video
Upload the video that needs rotation, flipping, or orientation conversion.

### Step 2 — Specify the Transformation
Choose: specific rotation (90°, 180°, 270°), horizontal flip, vertical flip, or orientation conversion (16:9 → 9:16, 9:16 → 16:9, any → 1:1).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "video-rotate",
    "prompt": "Convert a 5-minute 16:9 YouTube video to 9:16 for TikTok. Use intelligent reframing: track the speaker face throughout, keep centered in the vertical frame, smooth pan when speaker moves across the wide frame. No black bars. Also create a 1:1 square version for Instagram feed. Maintain original audio and quality.",
    "transformation": "reframe",
    "source_orientation": "16:9",
    "target_orientations": ["9:16", "1:1"],
    "reframe_mode": "face-tracking",
    "background": "none",
    "maintain_quality": true
  }'
```

### Step 4 — Review and Export
Preview the transformed video. Check: subject framing in the new orientation, no important content cut off, smooth panning transitions. Export.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the rotation or reframing needed |
| `transformation` | string | | "rotate-90", "rotate-180", "rotate-270", "flip-h", "flip-v", "reframe" |
| `source_orientation` | string | | "16:9", "9:16", "1:1", "4:3" |
| `target_orientations` | array | | ["9:16", "1:1", "16:9"] |
| `reframe_mode` | string | | "face-tracking", "center-crop", "smart-pan", "auto" |
| `background` | string | | "none" (crop), "blur", "gradient", "color" |
| `background_color` | string | | Hex color for solid background (if background="color") |
| `maintain_quality` | boolean | | Preserve original resolution and bitrate (default: true) |
| `batch` | array | | Multiple videos for batch rotation |

## Output Example

```json
{
  "job_id": "vr-20260328-001",
  "status": "completed",
  "source": {
    "orientation": "16:9",
    "resolution": "1920x1080",
    "duration": "5:14"
  },
  "outputs": {
    "vertical_9x16": {
      "file": "reframed-9x16.mp4",
      "resolution": "1080x1920",
      "duration": "5:14",
      "reframe": "face-tracking (speaker centered 94%% of frames)",
      "panning_events": 12
    },
    "square_1x1": {
      "file": "reframed-1x1.mp4",
      "resolution": "1080x1080",
      "duration": "5:14",
      "reframe": "face-tracking (speaker centered 98%% of frames)"
    }
  }
}
```

## Tips

1. **Face tracking produces the best horizontal-to-vertical conversions** — When converting 16:9 → 9:16, the AI needs to decide which part of the wide frame to show. Face tracking ensures the speaker is always visible — the most important element in talking-head content.
2. **Blurred background beats black bars every time** — When vertical content goes horizontal, a blurred enlarged version of the video as background is universally more visually appealing than black bars. It fills the empty space without distracting from the main content.
3. **Batch rotation saves hours for multi-platform creators** — If you have 20 horizontal YouTube videos that need vertical versions for TikTok, batch-process all 20 with the same reframing settings. Consistent quality across the batch.
4. **Check text readability after flipping** — Horizontal flip (mirror correction) reverses all text in the frame. If the video has on-screen text, logos, or signs, verify they read correctly after the flip. NemoVideo automatically detects and corrects text overlays.
5. **1:1 square is the safest universal format** — When you're unsure what platform a video will be posted on, square (1:1) works acceptably everywhere: it displays well in vertical feeds, horizontal feeds, and social media cards.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 16:9 | 1920x1080 | YouTube / website |
| MP4 1:1 | 1080x1080 | Instagram / Facebook / LinkedIn |
| MP4 4:5 | 1080x1350 | Instagram feed (max space) |
| MP4 4:3 | 1440x1080 | Legacy format |

## Related Skills

- [video-enhancer-ai](/skills/video-enhancer-ai) — AI video enhancement
- [music-video-maker](/skills/music-video-maker) — Music video creation
