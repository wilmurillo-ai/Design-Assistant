---
name: ai-video-filters
version: 1.0.1
displayName: "AI Video Filters — Apply Cinematic Color Filters and Visual Styles to Any Video"
description: >
  Apply cinematic color filters and visual styles to any video with AI — transform the mood and aesthetic of footage with one-click film looks, vintage styles, platform-optimized aesthetics, and custom color treatments. NemoVideo offers: cinematic film emulation (Kodak, Fuji, film noir), mood filters (warm sunset, cool night, golden hour, moody blue), platform aesthetics (Instagram warm, TikTok vibrant, LinkedIn clean), vintage looks (VHS, 8mm, Polaroid, 35mm grain), and custom filter creation from reference images. Video filter AI, cinematic filter, color filter video, video style transfer, aesthetic video filter, mood filter video, film look filter.
metadata: {"openclaw": {"emoji": "🎨", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Filters — One Filter Changes Everything About How Your Video Feels

A filter is a mood switch. The same footage of a person walking down a street tells a different story depending on the filter: warm golden tones and it is a romantic evening stroll, desaturated blue tones and it is a lonely walk home, high-contrast black-and-white and it is an artistic statement, vintage grain and faded colors and it is a nostalgic memory. The visual content is identical — the emotional content is entirely different. Filters are the fastest way to establish mood, genre, and visual identity. Instagram built a billion-dollar company on the insight that filters transform amateur photos into emotionally compelling images. The same principle applies to video — but video filters have been harder to access. Photo filters are one tap. Video filters in editing software require: importing footage, applying a LUT or color adjustment layer, previewing in real-time (which requires powerful hardware), adjusting per-scene (a single filter rarely works unchanged across an entire video), and rendering the export. NemoVideo applies video filters through description. "Make it look like a Wes Anderson film" or "warm Instagram aesthetic" or "VHS retro look" — and the AI applies the complete visual treatment: color temperature, contrast curve, saturation mapping, highlight/shadow tinting, grain texture, and any style-specific elements. One sentence, one filter, one mood.

## Filter Categories

### Cinematic Film Looks
- **Kodak Portra 400** — Warm skin tones, pastel highlights, gentle contrast. The portrait film look.
- **Fuji Pro 400H** — Cool clean tones, green-shifted shadows, low contrast. The editorial look.
- **Kodak Vision3 500T** — Tungsten-balanced cinema film. Warm practicals, cool shadows. The movie look.
- **Film Noir** — High contrast black-and-white, deep shadows, dramatic lighting emphasis.
- **Technicolor** — Saturated primaries, golden skin, vivid blues and reds. The classic Hollywood look.

### Mood Filters
- **Golden Hour** — Everything bathed in warm amber light. Sunset warmth without shooting at sunset.
- **Blue Hour** — Cool twilight tones. Melancholy, contemplative, cinematic.
- **Neon Night** — High contrast, saturated neon colors, deep blacks. Urban night aesthetic.
- **Misty Morning** — Lifted shadows, desaturated greens, soft contrast. Ethereal and calm.
- **Desert Heat** — Warm yellows, blown highlights, dusty texture. Arid and bold.

### Platform Aesthetics
- **Instagram Warm** — The warm, slightly faded look that dominates Instagram feeds.
- **TikTok Vibrant** — Punchy saturation, high contrast, optimized for mobile screens.
- **LinkedIn Professional** — Clean, neutral, well-exposed. Corporate-appropriate color treatment.
- **YouTube Creator** — Warm-clean with lifted shadows. The standard YouTube look.

### Vintage / Retro
- **VHS** — Scan lines, color bleed, tracking artifacts, date stamp. 80s/90s home video aesthetic.
- **Super 8** — Heavy grain, light leaks, vignette, muted colors. Home movie nostalgia.
- **Polaroid** — Faded colors, slight magenta shift, soft contrast. Instant photo aesthetic.
- **35mm Film** — Organic grain, natural color rendering, subtle halation on highlights.

## Use Cases

1. **Brand Consistency — Signature Filter Across All Content (batch)** — A lifestyle brand posts 20 videos per month. Each is shot in different conditions: studio, outdoor, phone, camera. NemoVideo applies the brand's signature filter ("warm Instagram with slightly desaturated greens and enhanced skin warmth") to every video uniformly. Twenty videos from different sources look like one cohesive visual brand. The filter becomes the brand's visual signature.

2. **Mood Setting — Same Scene, Three Moods (any length)** — A real estate agent has a property tour video. NemoVideo generates three filtered versions: Golden Hour filter (warm, inviting — for the lifestyle-focused listing), Clean Professional filter (neutral, bright — for the Zillow listing), and Cinematic filter (dramatic contrast — for the luxury social media post). Same footage, three filters, three emotional responses, three marketing applications.

3. **Vintage Content — Nostalgic Social Media (15-60s)** — A creator makes a "day in my life" video and wants the nostalgic VHS aesthetic. NemoVideo applies: scan lines, color bleed on reds, slight tracking wobble, rounded screen corners, date stamp "03.28.2026" in the corner, reduced resolution to simulate analog, and muffled audio quality. Modern phone footage becomes an authentic-feeling VHS home video. The nostalgia aesthetic that drives massive engagement on TikTok.

4. **Film Emulation — Cinema Look on Any Camera (any length)** — A filmmaker shoots on a consumer mirrorless but wants the Kodak Vision3 cinema film look. NemoVideo applies: the specific color rendering of Vision3 500T (warm tungsten whites, cyan-shifted shadows, rich mid-tone saturation), organic film grain matched to 35mm resolution, subtle halation on highlights (bright areas glow slightly), and the characteristic contrast curve (compressed mid-tones with smooth highlight roll-off). Consumer camera footage with the color signature of cinema film stock.

5. **A/B Testing — Multiple Looks for Ad Creatives (any length)** — An ad creative needs to be tested with different visual styles. NemoVideo generates: Version A with warm friendly filter (lifestyle approach), Version B with clean modern filter (tech approach), Version C with high-contrast bold filter (urgency approach). Same footage, three filters, three different emotional appeals for split testing. The winning visual style informs all future creative.

## How It Works

### Step 1 — Upload Video
Any footage from any source. NemoVideo handles all camera types and lighting conditions.

### Step 2 — Choose or Describe Filter
Select a preset (cinematic, warm, vintage, etc.) or describe the look: "like a Terrence Malick film" or "warm cozy coffee shop vibe" or "80s VHS home video."

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-filters",
    "prompt": "Apply a warm cinematic filter to a 2-minute travel vlog. Style: Kodak Portra 400 film emulation — warm skin tones, pastel highlights, gentle contrast, organic grain. Ensure consistent filter across all scenes (beach, city, food, sunset). Preserve natural skin warmth. Add subtle 35mm grain (fine, 6%% opacity). Export 16:9 for YouTube + 9:16 for Reels.",
    "filter": "kodak-portra-400",
    "grain": {"type": "35mm-fine", "opacity": 0.06},
    "consistency": "match-across-scenes",
    "skin_tones": "protected-warm",
    "formats": ["16:9", "9:16"]
  }'
```

### Step 4 — Compare and Publish
Preview filtered vs. original side-by-side. Adjust intensity: "make it more subtle" or "push the warmth further." Download and publish.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Filter description or style reference |
| `filter` | string | | Preset: "kodak-portra", "fuji-pro400h", "vhs", "golden-hour", "film-noir", etc. |
| `intensity` | float | | 0.0-1.0 (default 1.0) — how strongly the filter is applied |
| `grain` | object | | {type, opacity} |
| `consistency` | string | | "match-across-scenes", "per-scene-auto" |
| `skin_tones` | string | | "protected", "stylized", "warm" |
| `reference` | string | | Film or image to match |
| `batch` | boolean | | Apply same filter to multiple videos |
| `formats` | array | | ["16:9", "9:16", "1:1"] |
| `variations` | integer | | Generate multiple filter versions |

## Output Example

```json
{
  "job_id": "avf-20260328-001",
  "status": "completed",
  "filter_applied": "kodak-portra-400",
  "scenes_graded": 8,
  "consistency": "matched across all scenes",
  "grain": "35mm-fine at 6%%",
  "outputs": {
    "youtube": {"file": "travel-vlog-portra-16x9.mp4", "resolution": "1920x1080"},
    "reels": {"file": "travel-vlog-portra-9x16.mp4", "resolution": "1080x1920"}
  }
}
```

## Tips

1. **Filters set mood before a single word is spoken** — The viewer's emotional state is established within the first frame by the color palette. A warm filter makes the viewer feel comfortable and receptive. A cool filter makes them feel alert and analytical. Choose the filter that primes the desired emotional response.
2. **Consistency matters more than perfection** — A slightly imperfect filter applied consistently across all content is more powerful than a perfect filter applied inconsistently. Brand recognition comes from repetition, not from any single video's color grade.
3. **Film grain adds perceived quality** — Digital video is "too clean" for the human eye accustomed to film. A subtle grain overlay adds organic texture that the viewer perceives as higher production value, even though it technically adds noise. Fine grain at 4-8% opacity is the sweet spot.
4. **Vintage filters drive the highest engagement on social media** — VHS, Polaroid, and 8mm aesthetics consistently outperform clean modern looks on TikTok and Instagram. Nostalgia is a powerful engagement driver.
5. **Skin tone protection prevents amateur-looking filters** — The most common filter mistake: green or gray skin tones. Always enable skin tone protection when applying creative filters. The environment can be any color — faces must look natural.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |

## Related Skills

- [ai-video-effects](/skills/ai-video-effects) — Video effects
- [ai-video-color-grading](/skills/ai-video-color-grading) — Color grading
- [ai-video-loop](/skills/ai-video-loop) — Video loops
