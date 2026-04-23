# Thrift Haul Video Maker — Turn Goodwill Finds into Viral Before-After Content

Describe your thrift store haul and NemoVideo builds the video. Share vintage denim from the rack, Goodwill price tags, before-after outfit shots — and get a #ThriftHaul-ready short for TikTok, Reels, or Shorts. Built for Z-gen creators riding the sustainable fashion wave.

## When to Use This Skill

Use this skill when you want to create thrift haul content:
- Turn rack photos into before-after outfit transformation videos
- Showcase Goodwill or Buffalo Exchange finds with price callouts
- Build a weekly #ThriftHaul series with consistent styling
- Highlight vintage denim, retro pieces, and second-hand gems
- Create sustainable fashion content that resonates with eco-conscious audiences

## How to Describe Your Haul

Tell NemoVideo what you found and how you styled it. Be specific about:
- Where you shopped (Goodwill, Depop, Buffalo Exchange, local thrift store)
- Key pieces (vintage denim jacket, 90s windbreaker, Y2K cargo pants)
- Price points (the $8 find, the $3 graphic tee)
- Styling angle (casual street, elevated thrift, before-after transformation)

**Examples of good prompts:**
- "Goodwill haul: vintage Levi's 501s $8, oversized denim jacket $12, 90s windbreaker $5 — before-after outfit transformation video, upbeat indie music"
- "Buffalo Exchange thrift haul — 5 pieces under $40 total, show rack to street styled looks, #ThriftHaul TikTok style"
- "Second-hand sustainable fashion mini-doc, 60 seconds, show the thrift store rack, try-on, and final styled outfit with price tags"

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `haul_items` | List of thrifted pieces with prices | `"vintage denim jacket $12, Levi's $8"` |
| `store_name` | Where you shopped | `"Goodwill"`, `"Buffalo Exchange"` |
| `video_style` | Format preference | `"before_after"`, `"haul_walkthrough"`, `"outfit_showcase"` |
| `music_style` | Vibe | `"upbeat_indie"`, `"y2k_throwback"`, `"acoustic_chill"` |
| `duration` | Length in seconds | `15`, `30`, `45`, `60` |
| `platform` | Target platform | `"tiktok"`, `"reels"`, `"shorts"` |

## Workflow

1. Describe your haul items, store, and styling angle
2. NemoVideo builds the scene sequence (rack → try-on → styled look)
3. Price callout overlays and hashtags added automatically
4. Export vertical MP4 (9:16) optimized for your platform

## API Usage

### Basic Thrift Haul Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "thrift-haul-video",
    "input": {
      "prompt": "Goodwill haul: vintage denim jacket $12, high-waisted Levi 501s $8, 90s windbreaker $5 — before-after transformation, total haul $25",
      "store_name": "Goodwill",
      "video_style": "before_after",
      "music_style": "upbeat_indie",
      "duration": 30,
      "platform": "tiktok",
      "show_prices": true,
      "hashtags": ["ThriftHaul", "SustainableFashion", "VintageFinds", "ThriftFlip"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "thrift_abc123",
  "status": "processing",
  "estimated_seconds": 90,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/thrift_abc123"
}
```

### Sustainable Fashion Series Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "thrift-haul-video",
    "input": {
      "prompt": "Weekly thrift haul at Buffalo Exchange — vintage denim rack finds, Y2K graphic tees, before-after street style transformation, Z-gen sustainable fashion angle",
      "store_name": "Buffalo Exchange",
      "video_style": "haul_walkthrough",
      "music_style": "y2k_throwback",
      "duration": 45,
      "platform": "reels",
      "voiceover": true,
      "show_prices": true
    }
  }'
```

## Tips for Best Results

- **Include price tags**: "$8 Levi's" beats "cheap jeans" — specificity drives engagement
- **Name the store**: "Goodwill haul" performs better than generic "thrift store"
- **Rack-to-outfit arc**: Describe both the raw find and the styled look
- **Sustainable angle**: Mention eco-conscious messaging for #SustainableFashion audience
- **Hook in first 3 seconds**: Lead with the most surprising find or price

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| TikTok | 1080×1920 | 15–60s |
| Instagram Reels | 1080×1920 | 15–90s |
| YouTube Shorts | 1080×1920 | up to 60s |

## Related Skills

- `outfit-video-maker` — Styled outfit showcase without the haul journey
- `fashion-lookbook-video` — Multi-look editorial content
- `tiktok-content-maker` — General TikTok short video creation
- `product-photography-enhance` — Improve thrift item photos before video

## Common Questions

**Can I upload my own thrift photos?**
Yes — pass image URLs in the `images` array parameter. NemoVideo will incorporate your actual photos into the video sequence.

**Does it auto-add hashtags?**
Yes. `#ThriftHaul` is always included. Pass a `hashtags` array to customize the full set.

**What music is available?**
Royalty-free library with indie, Y2K throwback, acoustic, and chill genres — all cleared for commercial use on TikTok and Reels.

**How long does generation take?**
30-second videos process in 60–120 seconds. Poll the job URL for status.
