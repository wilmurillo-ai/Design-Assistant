---
name: generate-video-ai
version: "1.0.0"
displayName: "Generate Video AI — AI Video Creator for Marketing Education and Social Media"
description: >
  Create videos with AI for marketing, education, and social media — generate professional videos from descriptions, outlines, and briefs without filming or editing. NemoVideo is the AI video creator that produces: marketing campaign videos, social media ads, educational content, training material, product showcases, brand stories, testimonial compilations, event promos, and tutorial series — all from text input. Describe the video you need and receive a ready-to-publish result with visuals, narration, music, captions, and platform-optimized formatting.
metadata: {"openclaw": {"emoji": "🤖", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Generate Video AI — The AI Video Creator for Every Business Need

Video is the dominant content format across every digital platform. LinkedIn posts with video get 5x more engagement. Email campaigns with video increase click-through by 300%. Landing pages with video convert 80% better. Training modules with video improve knowledge retention by 65%. Every business knows video works — but most businesses don't make enough of it. The bottleneck is production. A single professional marketing video requires: creative brief, scriptwriting, storyboarding, filming or animation, editing, voiceover recording, music licensing, caption generation, and multi-format export. Cost: $2,000-$15,000. Timeline: 2-6 weeks. For a marketing team that needs 20 pieces of video content per month, traditional production is impossible at scale. NemoVideo makes video production scale with demand. Describe the video in a brief — "a 45-second ad for our summer sale targeting 25-34 women, vibrant colors, upbeat music, showing our top 5 products, ending with free shipping CTA" — and receive a finished video ready for Facebook, Instagram, TikTok, and YouTube. The same AI that generates one video can generate twenty in a batch. The production bottleneck disappears.

## Use Cases

1. **Marketing — Campaign Video Series (15-60s each)** — A fashion brand launches a summer collection with 8 product categories. NemoVideo batch-generates: 8 videos (one per category), each 30 seconds with product showcase visuals, benefit text overlays, seasonal music, and unified branding. Plus one 60-second hero video combining highlights from all categories. Each video exports in 4 formats (16:9, 9:16, 1:1, 4:5). 36 unique video assets from one campaign brief — enough to run different creative across every platform for the entire campaign.
2. **Education — Course Module Series (3-10 min each)** — An online course on digital marketing needs 12 video modules. NemoVideo generates each module from the lesson outline: animated concept explanations, diagram visualizations for frameworks (marketing funnel, customer journey, attribution models), screen mockups for tool demonstrations (Google Analytics, ad dashboards), practice exercise prompts, and quiz transitions. Consistent visual style across all 12 modules. Professional narration with pedagogical pacing (130 wpm). A complete course produced from lesson outlines.
3. **Social Media — Daily Content Machine (15-60s)** — A fitness brand needs daily social content across Instagram, TikTok, and YouTube Shorts. NemoVideo generates 30 days of content: workout tip videos (animated exercise demonstrations), motivational quotes (cinematic visuals with text overlay), product features (lifestyle footage with product callouts), and community spotlights (text-based testimonial cards). Each piece in 9:16 format with captions and trending-style music. A month of social media video from a content calendar spreadsheet.
4. **Training — Employee Onboarding (5-15 min each)** — An HR team needs onboarding videos for 6 departments. NemoVideo produces: company overview (mission, values, culture with animated infographics), department-specific modules (role expectations, tools, workflows with screen mockup demonstrations), compliance training (policy highlights with scenario animations), and benefits overview (plan comparison with animated charts). Consistent branded template across all modules. Narration: professional, welcoming, clear. An entire onboarding video library from policy documents.
5. **E-commerce — Product Videos at Scale (15-30s each)** — An online store with 200 products needs a video for each product page. NemoVideo batch-generates: product showcase from images and descriptions (zoom, rotate, lifestyle context), feature callouts as animated text, customer review quotes, and "Add to Cart" CTA end frame. 200 product videos from a product catalog CSV. Each video unique to the product, all sharing consistent brand aesthetics.

## How It Works

### Step 1 — Provide a Brief
Describe: what the video should communicate, who the audience is, where it will be published, and the desired tone. A one-sentence brief works. A detailed creative brief with scene descriptions works better.

### Step 2 — Set Production Defaults
Choose: visual style, voiceover character, music mood, branding elements, and output formats.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "generate-video-ai",
    "prompt": "Create a 45-second summer sale ad for a fashion brand. Target: women 25-34. Show top 5 products: floral dress, denim jacket, white sneakers, straw hat, leather bag. Each product gets 6 seconds with lifestyle visual and price tag animation. Opening: vibrant summer beach scene with SUMMER SALE text. Closing: FREE SHIPPING on all orders + shop now CTA. Music: upbeat tropical pop at -14dB. Brand colors: coral #FF6B6B and white. Export all 4 formats.",
    "type": "marketing-ad",
    "audience": "women 25-34",
    "visual_style": "vibrant-lifestyle",
    "music": "upbeat-tropical",
    "music_volume": "-14dB",
    "brand": {"primary": "#FF6B6B", "secondary": "#FFFFFF", "logo": true},
    "captions": {"style": "minimal-bold"},
    "duration": "45 sec",
    "formats": ["16:9", "9:16", "1:1", "4:5"]
  }'
```

### Step 4 — Review and Deploy
Preview all format versions. Check: brand color accuracy, product representation, CTA visibility. Deploy to ad platforms or social media scheduler.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Video brief and requirements |
| `type` | string | | "marketing-ad", "educational", "social-content", "training", "product-demo" |
| `audience` | string | | Target viewer demographic |
| `visual_style` | string | | "vibrant-lifestyle", "corporate-clean", "cinematic", "animated", "minimal" |
| `voice` | string | | "warm-female", "authoritative-male", "energetic", "none" |
| `music` | string | | "upbeat-tropical", "corporate", "cinematic", "lo-fi", "trending" |
| `music_volume` | string | | "-12dB" to "-22dB" |
| `brand` | object | | {primary, secondary, logo, fonts} |
| `captions` | object | | {style, text, highlight, bg} |
| `duration` | string | | "15 sec", "30 sec", "45 sec", "60 sec", "3 min" |
| `formats` | array | | ["16:9","9:16","1:1","4:5"] |
| `batch` | array | | Multiple briefs for batch production |

## Output Example

```json
{
  "job_id": "gva-20260328-001",
  "status": "completed",
  "type": "marketing-ad",
  "duration_seconds": 46,
  "outputs": {
    "landscape": {"file": "summer-sale-16x9.mp4", "resolution": "1920x1080"},
    "vertical": {"file": "summer-sale-9x16.mp4", "resolution": "1080x1920"},
    "square": {"file": "summer-sale-1x1.mp4", "resolution": "1080x1080"},
    "portrait": {"file": "summer-sale-4x5.mp4", "resolution": "1080x1350"}
  },
  "production": {
    "scenes": 7,
    "products_featured": 5,
    "brand_colors": "coral #FF6B6B + white",
    "music": "upbeat-tropical at -14dB",
    "cta": "FREE SHIPPING — Shop Now"
  }
}
```

## Tips

1. **Batch production is the ROI multiplier** — One video at a time is expensive in creative energy. 20 videos in one batch uses the same creative energy once and multiplies the output. Always think in batches for campaigns and content calendars.
2. **Platform-native formats outperform cross-posted content** — A video natively formatted for TikTok (9:16, fast cuts, captions, trending music) outperforms the same content cross-posted from YouTube (16:9, longer pacing). Generate platform-specific versions from the start.
3. **Brand object is a one-time setup with permanent returns** — Set your brand colors, logo, and font preferences once. Every future video automatically maintains brand consistency. The upfront 5 minutes saves hours of manual brand checking.
4. **Education videos need 130 wpm, ads need 170 wpm** — Pacing is content-type-specific. Educational content needs time for concepts to sink in. Ads need urgency and density. Specify the content type for optimal pacing.
5. **Product videos from catalog data scale infinitely** — If you have a product CSV (name, description, price, image URL), NemoVideo can batch-generate hundreds of unique product videos. E-commerce video at catalog scale.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website / presentation |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts / Stories |
| MP4 1:1 | 1080x1080 | Instagram / Facebook / LinkedIn |
| MP4 4:5 | 1080x1350 | Facebook / Instagram feed (max space) |
| GIF | 720p | Email / web preview |
| SRT | — | Closed captions |

## Related Skills

- [generate-ai-video](/skills/generate-ai-video) — AI video from text prompts
- [video-from-script](/skills/video-from-script) — Script to video
- [video-idea-generator](/skills/video-idea-generator) — Video ideas
