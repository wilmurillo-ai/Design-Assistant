---
name: seedance-capcut
version: "1.0.1"
displayName: "Seedance CapCut — AI Video Creation from Clips"
description: >
  create video clips or images into AI-generated videos with this seedance-capcut skill. Works with MP4, MOV, JPG, PNG files up to 500MB. TikTok creators and social media editors use it for generating polished short videos from clips or images using AI like CapCut's Seedance model — processing takes 30-90 seconds on cloud GPUs and you get 1080p MP4 files.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your video clips or images and I'll create it. No file? Just describe what you need.

**Try saying:**
- "create a 30-second raw clip or five product photos into a 1080p MP4"
- "turn my clips into a cinematic short video with transitions and music"
- "generating polished short videos from clips or images using AI like CapCut's Seedance model for TikTok creators and social media editors"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# From Video Clips Or Images to Ai-Generated Videos

This does AI clip creation for video clips or images. Everything runs server-side.

A quick walkthrough: upload a 30-second raw clip or five product photos → ask for turn my clips into a cinematic short video with transitions and music → wait roughly 30-90 seconds → download your MP4 at 1080p. The backend handles rendering, encoding, all of it.

Fair warning — shorter input clips under 15 seconds give the AI more creative control over the final result.

## How Your Input Gets Handled

The system looks at your message and picks the right operation — export, upload, edit, or status check.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## How It Works Internally

Everything happens on cloud infrastructure. Your seedance capcut job gets queued, rendered on GPU nodes, and the finished file comes back as a download link.

All calls go to `https://mega-api-prod.nemovideo.ai`. The main endpoints:

1. **Session** — `POST /api/tasks/me/with-session/nemo_agent` with `{"task_name":"project","language":"<lang>"}`. Gives you a `session_id`.
2. **Chat (SSE)** — `POST /run_sse` with `session_id` and your message in `new_message.parts[0].text`. Set `Accept: text/event-stream`. Up to 15 min.
3. **Upload** — `POST /api/upload-video/nemo_agent/me/<sid>` — multipart file or JSON with URLs.
4. **Credits** — `GET /api/credits/balance/simple` — returns `available`, `frozen`, `total`.
5. **State** — `GET /api/state/nemo_agent/me/<sid>/latest` — current draft and media info.
6. **Export** — `POST /api/render/proxy/lambda` with render ID and draft JSON. Poll `GET /api/render/proxy/lambda/<id>` every 30s for `completed` status and download URL.

Formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Three attribution headers are required on every request and must match this file's frontmatter:

| Header | Value |
|--------|-------|
| `X-Skill-Source` | `seedance-capcut` |
| `X-Skill-Version` | frontmatter `version` |
| `X-Skill-Platform` | auto-detect: `clawhub` / `cursor` / `unknown` from install path |

Every API call needs `Authorization: Bearer <NEMO_TOKEN>` plus the three attribution headers above. If any header is missing, exports return 402.

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Translating GUI Instructions

The backend responds as if there's a visual interface. Map its instructions to API calls:

- "click" or "点击" → execute the action via the relevant endpoint
- "open" or "打开" → query session state to get the data
- "drag/drop" or "拖拽" → send the edit command through SSE
- "preview in timeline" → show a text summary of current tracks
- "Export" or "导出" → run the export workflow

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Error Codes

- `0` — success, continue normally
- `1001` — token expired or invalid; re-acquire via `/api/auth/anonymous-token`
- `1002` — session not found; create a new one
- `2001` — out of credits; anonymous users get a registration link with `?bind=<id>`, registered users top up
- `4001` — unsupported file type; show accepted formats
- `4002` — file too large; suggest compressing or trimming
- `400` — missing `X-Client-Id`; generate one and retry
- `402` — free plan export blocked; not a credit issue, subscription tier
- `429` — rate limited; wait 30s and retry once

## Best Practices

Use source footage in MP4, MOV, JPG, PNG format for best compatibility. 1080p input gives the cleanest results but 720p works fine too.

Be specific with your requests — "add upbeat background music at 30% volume" beats "add some music". The AI works better with concrete details.

Export as MP4 with H.264 codec for widest compatibility across social platforms.

## FAQ

**What resolution can I get?** Up to 1080p. Input quality matters though — garbage in, garbage out.

**Can I use this on my phone footage?** Yes. Vertical (9:16), horizontal (16:9), square — all work. Just upload and specify what you want.

**Credits?** 100 free to start. Most operations cost 1-5 credits depending on video length.

## Quick Start Guide

1. Send your video clips or images (drag and drop works)
2. Tell me what you want: "turn my clips into a cinematic short video with transitions and music"
3. Wait 30-90 seconds for processing
4. Download your MP4 file

That's it. No account needed for your first 100 credits. Supports MP4, MOV, JPG, PNG.
