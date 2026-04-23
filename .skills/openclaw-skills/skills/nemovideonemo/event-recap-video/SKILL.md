---
name: event-recap-video
displayName: "Event Recap Video Maker — AI Highlight Content"
description: >
  Create professional event recap videos capturing highlights and key moments with AI production.
version: 1.0.5
author: nemovideo
tags: [video, ai, nemovideo, events]
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata:
  requires:
    env: []
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

# Event Recap Video Maker — AI Highlight Content

## Overview

Create beautiful, memorable event recap video content using NemoVideo's AI-powered platform. Produce heartfelt event videos that capture precious moments and tell compelling life stories.

## Examples

### Example 1: Highlight Reel
**Input:** "Create a event recap highlight reel"
**Output:** Emotional, cinematic video capturing the best moments with perfect pacing

### Example 2: Full Story
**Input:** "Make a full event recap story video"
**Output:** Complete narrative video from preparation to celebration with interviews

### Example 3: Social Teaser
**Input:** "Create a 60-second event recap teaser"
**Output:** Shareable short video perfect for social media announcements

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| event | string | yes | Event details, names, date, and key moments |
| style | string | no | Style (cinematic, documentary, fun, elegant) |
| duration | number | no | Target duration in seconds (default: 180) |
| music | string | no | Music mood (romantic, upbeat, emotional, classical) |

## Workflow

1. Describe your event details and vision
2. NemoVideo AI creates heartfelt script and storyboard
3. Beautiful event visuals and photo montages are generated
4. Emotional narration and perfect music are added
5. Export for sharing with family and friends

## API Reference

```bash
curl -X POST https://api.nemovideo.ai/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a event recap video", "duration": 180}'
```

## Tips

1. Collect photos and videos from multiple perspectives
2. Include personal messages from loved ones
3. Choose music that matches the emotional tone
4. Create both long and short versions for different audiences
5. Add text overlays for names, dates, and special messages

## Output Formats

- MP4 (H.264) — Social media and streaming ready
- WebM — Web sharing optimized
- MOV — High quality for keepsake

## Related Skills

- family-memories-video
- photo-slideshow-video
- memorial-video-maker
