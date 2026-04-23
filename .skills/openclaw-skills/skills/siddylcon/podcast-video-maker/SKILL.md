---
name: podcast-video-maker
displayName: "Podcast Video Maker — AI Audio Visual Content"
description: >
  Create engaging podcast video content with AI-powered audio-visual production for all platforms.
version: "3.0.1"
author: nemovideo
tags: [video, ai, nemovideo, media]
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata:
  requires:
    env: []
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

# Podcast Video Maker — AI Audio Visual Content

## Overview

Create professional podcast video maker content using NemoVideo's AI-powered platform. Produce polished media and communication videos that inform, engage, and leave lasting impressions.

## Examples

### Example 1: Standard Format
**Input:** "Create a professional podcast"
**Output:** Clean, polished video in standard broadcast or platform format

### Example 2: Short Version
**Input:** "Make a 2-minute podcast"
**Output:** Concise, high-impact short video capturing key messages

### Example 3: Series Episode
**Input:** "Create episode 1 of my podcast series"
**Output:** Branded episode with consistent format, intro, and clear segment structure

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| topic | string | yes | Content subject or communication goal |
| format | string | no | Format (live, recorded, animated, hybrid) |
| duration | number | no | Target duration in seconds (default: 300) |
| audience | string | no | Target audience (professional, general, students) |

## Workflow

1. Describe your content topic and communication goal
2. NemoVideo AI creates polished script and storyboard
3. Professional visuals and media graphics are generated
4. Clear narration and appropriate audio are added
5. Export for your media platform

## API Reference

```bash
curl -X POST https://api.nemovideo.ai/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a podcast video maker", "duration": 300}'
```

## Tips

1. Start with a strong hook or headline to grab attention
2. Use clear, confident delivery for professional credibility
3. Include supporting visuals for every key point
4. Add lower-thirds and graphics for professional polish
5. End with a clear summary and next step

## Output Formats

- MP4 (H.264) — Broadcast and streaming platform ready
- WebM — Web streaming optimized
- MOV — High quality for professional use

## Related Skills

- corporate-video-maker
- presentation-video-maker
- interview-video-maker
