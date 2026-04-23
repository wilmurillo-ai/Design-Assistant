---
name: ai-video-brightness-adjuster
version: 1.0.1
displayName: "AI Video Brightness Adjuster — Fix Dark Video and Control Lighting Levels with AI"
description: >
  Fix dark video and control lighting levels with AI — brighten underexposed footage, dim overexposed clips, balance uneven lighting, and apply scene-by-scene brightness optimization. NemoVideo analyzes every frame and applies intelligent brightness correction: lifting shadows in dark indoor recordings, recovering detail in overexposed outdoor footage, balancing mixed-lighting environments, and ensuring consistent brightness across clips shot in different conditions. Fix dark video AI, brighten video, video brightness tool, exposure correction video, lighten dark footage, video lighting fix, adjust video brightness online, dark video enhancer.
metadata: {"openclaw": {"emoji": "☀️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Brightness Adjuster — See Everything. Even in the Dark.

Dark footage is the most common quality problem after shaky video. Indoor recordings without professional lighting, evening events, restaurant settings, conference rooms with dim overhead lights, phone recordings in clubs or concerts — all produce footage where the subject is barely visible. The camera's automatic exposure tries to compensate but introduces its own problems: noise in the shadows, uneven brightness across the frame, sudden exposure jumps when someone walks in front of a light source. The opposite problem is equally destructive: outdoor footage on a bright day where the sky is pure white, faces are washed out, and detail is lost to overexposure. Or mixed lighting: a subject standing near a window where one side of their face is properly exposed and the other side is a dark shadow. Simple brightness sliders in basic editors apply uniform adjustment across the entire frame — making bright areas brighter (overexposed) while trying to fix dark areas. This is like turning up the volume on everything when you only wanted to hear one instrument louder. NemoVideo adjusts brightness intelligently. The AI analyzes each frame's luminance distribution: lifting shadows (dark areas) without blowing out highlights (bright areas), recovering overexposed regions without darkening the overall scene, and balancing mixed lighting so every part of the frame is properly exposed. Scene-by-scene analysis means the brightness correction adapts as lighting conditions change throughout the video.

## Use Cases

1. **Dark Indoor Recording — Shadow Recovery (any length)** — A vlogger filmed in their apartment with only overhead lighting. The image is visible but dark — shadows under eyes, dark corners, skin tones appear muddy. NemoVideo: analyzes the luminance distribution, lifts shadow regions by 1-2 stops (recovering facial detail, revealing corner detail), adjusts midtones for natural skin appearance, leaves highlights untouched (windows and lamps already bright enough), and applies consistently across every frame. Dark apartment footage that now looks like it had professional key lighting.

2. **Overexposed Outdoor — Highlight Recovery (any length)** — A real estate walkthrough filmed on a sunny day. Interior rooms are properly exposed but every window is a pure white blowout, and the backyard footage has washed-out sky and bleached grass. NemoVideo: identifies overexposed regions (clipped highlights), recovers detail where data exists (modern cameras capture more highlight information than is displayed), rolls off highlights to a natural tone curve, and preserves the correctly-exposed portions of the frame. Outdoor footage that shows sky detail and color instead of pure white.

3. **Mixed Lighting Fix — Window Light vs. Indoor (any length)** — An interview filmed in an office with a large window behind the subject. The camera exposes for the subject's face: face is fine, but the window is nuclear white. Or the camera exposes for the window: window is fine, but the subject's face is a dark silhouette. NemoVideo: applies zone-based brightness correction (face zone lifted or maintained, window zone pulled down), creating an exposure that would have required a reflector or fill light during filming. The HDR-style correction that professional videographers achieve with lighting gear, applied in post from a single camera exposure.

4. **Event Footage — Variable Lighting Throughout (any length)** — A wedding or conference recording spans multiple locations and times: bright outdoor ceremony, dim reception hall, spotlight speeches, dance floor with strobes. NemoVideo: applies scene-aware brightness correction that adapts as lighting changes throughout the video, smooths sudden exposure jumps (when the camera auto-exposure lags behind a lighting change), and maintains consistent perceived brightness across the entire video. Multiple lighting environments, one consistent viewing experience.

5. **Batch Brightness Matching — Multi-Clip Consistency (multiple clips)** — A creator shot 20 clips across 3 different locations and 2 different times of day. Each clip has different brightness levels, making them look disjointed when edited together. NemoVideo: analyzes all clips, calculates a target brightness level that works for the entire set, adjusts each clip to match (some lifted, some reduced, all converged), and exports clips that cut together seamlessly. Multi-location shoots that look like they were filmed in one consistent environment.

## How It Works

### Step 1 — Upload Video
Any footage with brightness issues — dark, overexposed, mixed lighting, or variable exposure throughout.

### Step 2 — Choose Brightness Mode
Auto (AI determines optimal correction), manual (specify target brightness level), match (match the brightness of a reference clip), or zone-based (different adjustments for different frame regions).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-brightness-adjuster",
    "prompt": "Fix a dark indoor interview video. The subject face is underexposed — lift shadows to reveal facial detail, bring skin tones to natural brightness. The background has a window that is slightly overexposed — pull highlights to recover some window detail. Do not make the overall image look artificially bright — aim for natural indoor lighting feel. Also fix a section at 8:00-9:30 where someone walked in front of the light causing a sudden dark dip — smooth that exposure change. Export 16:9 at 1080p.",
    "mode": "auto-intelligent",
    "shadow_lift": "moderate",
    "highlight_recovery": "gentle",
    "target_feel": "natural-indoor",
    "smooth_exposure_changes": true,
    "format": "16:9",
    "resolution": "1080p"
  }'
```

### Step 4 — Compare Before/After
Side-by-side preview: original vs. corrected. Verify: shadows are lifted naturally, highlights are not blown, skin tones look healthy, exposure transitions are smooth. Adjust if needed.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Brightness correction requirements |
| `mode` | string | | "auto-intelligent", "manual", "match-reference", "zone-based" |
| `shadow_lift` | string | | "gentle", "moderate", "aggressive" |
| `highlight_recovery` | string | | "gentle", "moderate", "aggressive" |
| `target_brightness` | float | | 0.0-1.0 target overall brightness |
| `target_feel` | string | | "natural-indoor", "bright-clean", "cinematic-dark", "broadcast" |
| `smooth_exposure_changes` | boolean | | Smooth sudden brightness jumps |
| `zones` | array | | [{region, adjustment}] for zone-based |
| `reference_clip` | string | | URL for brightness matching |
| `format` | string | | "16:9", "9:16", "1:1" |
| `batch` | boolean | | Process multiple clips to matching brightness |

## Output Example

```json
{
  "job_id": "avbr-20260329-001",
  "status": "completed",
  "analysis": {
    "original_avg_luminance": 0.28,
    "corrected_avg_luminance": 0.52,
    "shadow_lift_applied": "+1.4 stops",
    "highlight_recovery": "-0.3 stops",
    "exposure_jumps_smoothed": 3
  },
  "outputs": {
    "corrected": {"file": "interview-bright-16x9.mp4", "resolution": "1920x1080"}
  }
}
```

## Tips

1. **Shadow lifting is far more effective than overall brightness increase** — Lifting shadows brightens dark areas without affecting already-bright areas. Overall brightness increase makes everything brighter, including areas that were already fine — creating an overexposed look while still having insufficient shadow detail.
2. **Natural-feeling correction is more important than technically perfect exposure** — A slightly dark but natural-looking image is better than a technically correct but artificial-looking one. The goal is "this looks like it was filmed with good lighting," not "every pixel is at optimal luminance."
3. **Smooth exposure transitions prevent the jarring flash effect** — When a camera auto-adjusts exposure (someone walks past a window, a light turns on), the brightness jump is distracting. Smoothing these transitions over 0.5-1 second makes them invisible to viewers.
4. **Batch brightness matching is essential for multi-location edits** — Clips from different locations with different lighting create a jarring viewing experience when cut together. Matching brightness across all clips before editing creates visual consistency that viewers feel but cannot articulate.
5. **Mixed lighting requires zone-based correction** — A single brightness adjustment cannot fix a frame where half is dark and half is bright. Zone-based correction (lifting the dark half, reducing the bright half) produces the balanced exposure that would have required professional lighting during filming.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |

## Related Skills

- [ai-video-contrast-enhancer](/skills/ai-video-contrast-enhancer) — Contrast correction
- [ai-video-color-grading](/skills/ai-video-color-grading) — Color grading
- [ai-video-filters](/skills/ai-video-filters) — Video filters
