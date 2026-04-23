---
name: ai-video-background
version: "1.0.0"
displayName: "AI Video Background — Change Replace and Customize Video Backgrounds with AI"
description: >
  Change, replace, and customize video backgrounds with AI — swap backgrounds in real-time, add virtual environments, blur distracting backgrounds, replace green screens without a green screen, and create professional studio looks from any recording location. NemoVideo separates foreground subjects from backgrounds using AI segmentation: replace a messy home office with a clean professional backdrop, add cinematic environments behind a talking-head, blur a distracting background for focus, or insert custom branded backgrounds for consistent content. Video background changer, replace video background, virtual background video, AI background removal video, green screen without green screen, background blur video, custom video backdrop.
metadata: {"openclaw": {"emoji": "🖼️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video Background — Record Anywhere. Look Like You Are Anywhere.

The background of a video communicates as much as the speaker. A messy bedroom behind a business presenter undermines credibility. A plain white wall behind a creative professional feels sterile. A busy café behind a course instructor distracts from the lesson. The background sets the context, establishes professionalism, and either supports or sabotages the content. Traditional solutions — dedicated studios, green screen setups, careful location selection — add cost, time, and logistical constraints to every recording. A basic green screen setup costs $100-500 and requires proper lighting to avoid spill. A dedicated studio space costs $500-5,000/month. Even virtual backgrounds in Zoom require strong hardware and often produce visible artifacts around hair and edges. NemoVideo changes backgrounds after recording. Film anywhere — bedroom, kitchen, hotel room, car, café — and replace the background in post. The AI segments the foreground subject (people, objects) from the background with edge precision that handles hair, translucent elements, and moving subjects. Replace with: a professional office, a custom branded backdrop, a cinematic environment, a blurred version of the original (focus on the speaker), or any image or video background.

## Use Cases

1. **Remote Worker — Professional Backdrop for Video Calls (any length)** — A consultant records client-facing videos from their apartment. The background shows a bed, laundry, and a cat. NemoVideo: segments the consultant from the background with precise edge detection (including hair strands), replaces with a clean modern office background (bookshelf, plant, soft lighting), color-matches the subject to the new environment (lighting consistency), and maintains natural-looking edges throughout the video. The consultant looks like they have a professional studio. The cat remains out of frame.

2. **Content Creator — Themed Backgrounds for Series (multiple)** — A creator produces different content series that each need a distinct visual identity: tech reviews (dark studio with RGB lighting), cooking tips (kitchen environment), motivation (sunrise mountain backdrop). NemoVideo: takes all recordings from the same desk setup and applies different backgrounds per series, maintaining consistent lighting integration for each environment. One recording space, multiple visual identities.

3. **Corporate Training — Branded Backdrop (batch)** — A company produces 20 training videos with 8 different presenters. Each presenter records in their own location (home offices, meeting rooms, hotel rooms). NemoVideo: applies the company's branded background to all 20 videos (consistent backdrop with company logo, brand colors, subtle animated elements), color-matches each presenter to the branded environment, and produces a visually consistent training library. Eight different locations become one professional brand.

4. **Background Blur — Focus on the Speaker (any length)** — A presenter records in a busy office. Colleagues walking behind, screens with sensitive information visible, visual clutter competing with the speaker. NemoVideo: detects the speaker as the foreground subject, applies cinematic background blur (adjustable bokeh intensity), keeps the speaker in sharp focus, and maintains natural depth-of-field appearance. The background becomes a soft, non-distracting wash of color while the speaker commands full attention.

5. **Green Screen Replacement — Without the Green Screen (any length)** — A creator wants to place themselves in front of a fantasy landscape for a storytelling video but does not own a green screen. NemoVideo: segments the creator from their actual background using AI (no green screen needed), replaces with the fantasy landscape image or video, handles edge blending around hair and clothing, adds subtle environmental effects (matching the landscape's lighting on the subject's skin), and exports. The green screen effect without the green screen — from any recording environment.

## How It Works

### Step 1 — Upload Video
Any video with a subject you want to separate from the background. Works with: single person, multiple people, objects, or any defined foreground element.

### Step 2 — Choose Background Treatment
Replace (new image/video background), blur (adjustable intensity), remove (transparent for compositing), or brand (company backdrop).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-background",
    "prompt": "Replace the background of a 5-minute talking-head video. Current background: messy home office. New background: clean modern office with bookshelf, plant, and soft window light from the left. Match the new background lighting to the subject (light source from upper-left). Maintain precise hair edge detection. Also generate a blurred-background version (cinematic bokeh, moderate intensity) as an alternative. Export both at 16:9 1080p.",
    "background_action": "replace",
    "new_background": "modern-office-bookshelf-window-light",
    "lighting_match": "upper-left",
    "edge_quality": "hair-precise",
    "alternatives": [
      {"action": "blur", "intensity": "moderate-cinematic-bokeh"}
    ],
    "format": "16:9",
    "resolution": "1080p"
  }'
```

### Step 4 — Review Edge Quality
Watch for: hair edge artifacts, shadow consistency, lighting match. Adjust if needed. Download preferred version.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Background change description |
| `background_action` | string | | "replace", "blur", "remove", "brand" |
| `new_background` | string | | Background description, image URL, or preset |
| `blur_intensity` | string | | "light", "moderate", "heavy", "cinematic-bokeh" |
| `lighting_match` | string | | Match light direction to new background |
| `edge_quality` | string | | "standard", "hair-precise", "maximum" |
| `brand_background` | object | | {logo, colors, elements} for corporate backdrop |
| `alternatives` | array | | Generate multiple background versions |
| `format` | string | | "16:9", "9:16", "1:1" |
| `resolution` | string | | "720p", "1080p", "4K" |
| `batch` | array | | Multiple videos with same background |

## Output Example

```json
{
  "job_id": "avbg-20260328-001",
  "status": "completed",
  "source_duration": "5:08",
  "segmentation": {
    "subject": "single person",
    "edge_quality": "hair-precise",
    "frames_processed": 9144
  },
  "outputs": {
    "replaced": {
      "file": "video-office-bg.mp4",
      "background": "modern office (bookshelf + window light)",
      "lighting_matched": true
    },
    "blurred": {
      "file": "video-blur-bg.mp4",
      "blur": "moderate cinematic bokeh"
    }
  }
}
```

## Tips

1. **Lighting direction must match between subject and new background** — If the subject is lit from the left but the new background has a window on the right, the scene looks wrong even if the viewer cannot articulate why. Always match light direction.
2. **Hair edge quality is the test of professional vs. amateur background replacement** — Blocky edges around hair instantly reveal the replacement. Hair-precise edge detection handles individual strands and creates the natural blending that makes the background change invisible.
3. **Background blur is the safest professional option** — If the goal is simply "look professional," blurring the existing background is often better than replacing it. It looks natural (because it IS the real environment, just defocused), requires no lighting matching, and signals "intentional focus on the speaker" rather than "virtual background."
4. **Branded backgrounds create instant corporate consistency** — When every presenter in a 20-person team uses the same branded background, the video library looks cohesive regardless of where each person recorded. Brand consistency from distributed recording locations.
5. **Test with fast movement** — The edge segmentation is most visible when the subject moves quickly (gesturing, turning). Always preview a section with movement to verify edge quality before processing the full video.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website / presentation |
| MP4 9:16 | 1080x1920 | TikTok / Reels |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |
| MOV (alpha) | 1080p | Compositing (transparent BG) |

## Related Skills

- [ai-video-resize](/skills/ai-video-resize) — Video resizing
- [ai-video-effects](/skills/ai-video-effects) — Video effects
- [ai-video-filters](/skills/ai-video-filters) — Video filters
