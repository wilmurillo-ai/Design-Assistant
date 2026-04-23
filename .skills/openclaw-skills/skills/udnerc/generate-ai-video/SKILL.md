name: generate-ai-video
version: "1.0.1"
displayName: "Generate AI Video — Text to Video Generator with AI Scene and Script Builder"
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
license: MIT-0
description: >
  Generate AI Video — Text to Video Generator with AI Scene and Script Builder.
  Turn any written idea into a finished video without filming a single frame. Generate AI Video takes your script, topic, or even a rough idea and produces a complete video with AI-generated visuals, voiceover, background music, and subtitles. Tell it the length, style, and audience — it handles the rest. Works for YouTube content, marketing videos, educational explainers, and social clips. The AI writes the scene-by-scene breakdown, selects appropriate visuals, syncs audio, and renders a publish-ready MP4. Upload your own footage to blend with AI-generated segments. Adjust pacing, swap music, or rewrite any section through follow-up chat messages. No camera, no crew, no editing software. Exports in 16:9 for YouTube, 9:16 for TikTok/Reels, or 1:1 for Instagram. Credit-based system with 100 free credits for new users — enough for multiple complete videos.
apiDomain: mega-api-prod.nemovideo.ai

## 1. Role & Environment

You generate complete AI videos from text inputs, coordinating scene generation, voiceover, music, and rendering through NemoVideo's API with zero GUI interaction required from the user.

### Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| NEMO_TOKEN | No | Auto-generated (100 free credits) |
| NEMO_API_URL | No | https://mega-api-prod.nemovideo.ai |
| NEMO_CLIENT_ID | No | Auto-generated UUID |

## 2. Request Router

| User says... | Action |
|---|---|
| "export" / "download" / "render" | → §3.4 Export |
| "credits" / "balance" | → §3.3 Credits |
| "upload" / user sends file | → §3.2 Upload |
| Everything else | → §3.1 SSE |

## 3. Core Flows

$API = ${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}

### 3.1 Create session + generate
```bash
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"task_name":"project","language":"en"}'
```

### 3.2 Upload footage
```bash
curl -s -X POST "$API/api/media/upload" -H "Authorization: Bearer $TOKEN" -F "file=@video.mp4"
```

### 3.3 Credits
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN"
```

### 3.4 Render
```bash
curl -s -X POST "$API/api/tasks/{task_id}/render-video" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"quality":"high"}'
```

## 4. Error Handling

SSE timeout on long generation: poll render status every 30s, reassure user.
GUI reference: execute API equivalent silently.
