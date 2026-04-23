---
name: add-music-to-video-for-free
version: "1.0.0"
displayName: "Add Music to Video for Free — Sync Tracks to Any Clip Instantly"
description: >
  Turn raw, silent footage into polished, emotionally engaging content by using this skill to add-music-to-video-for-free — no subscriptions, no watermarks, no hassle. Upload your video, choose a mood or track style, and get back a fully synced result with background music that fits your pacing. Perfect for content creators, small business owners, students, and anyone who wants professional-sounding videos without paying for editing software.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! This skill is built to help you add music to video for free — no paid apps, no complicated software. Tell me about your video and the mood you're going for, and let's get it sounding great right now.

**Try saying:**
- "Add free music to my video"
- "Find royalty-free track for clip"
- "Sync background music to footage"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Give Your Videos a Soundtrack Without Spending Anything

Silent videos rarely hold attention. Whether you're posting a travel montage, a product demo, a birthday reel, or a short film clip, the right music changes everything — it sets the mood, keeps viewers engaged, and makes your content feel complete. This skill exists specifically to help you add music to video for free, without needing a paid editing suite or hours of manual work.

Just describe the video you're working with, tell us the vibe you're going for — upbeat, cinematic, chill, dramatic — and this skill will guide you through finding and applying the right royalty-free track. You can also paste in a video link or describe the scene, and get tailored music suggestions that match the length and tone of your footage.

This isn't a generic media tool. It's built around the specific challenge of matching audio to video content quickly and at zero cost. Whether you're a first-time creator or someone who just wants a faster workflow, this skill makes the process straightforward from start to finish.

## Routing Your Music Sync Request

When you drop a clip and select a track, ClawHub reads your audio-video pairing intent and routes the job to the nearest available transcoding node based on file format, duration, and sync parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

ClawHub's backend leverages a distributed FFmpeg-based pipeline to merge audio tracks with raw video footage, automatically normalizing BPM alignment and volume levels in the cloud so no local rendering is required. Processed files are returned as a streamable MP4 with the selected soundtrack baked into the final output.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `add-music-to-video-for-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Use Cases — Who Benefits from Adding Free Music to Video

Social media creators are the most obvious audience — a Reel or TikTok with the right track performs significantly better than a silent one, and using royalty-free music avoids copyright strikes that can kill reach or monetization.

Small business owners creating product videos, how-to guides, or promotional clips also benefit heavily. Hiring a video editor just to add a music track isn't cost-effective, and this skill helps them do it themselves in minutes using free tools.

Students and educators producing presentation videos, documentaries, or classroom content often need background music to make their work feel more polished without any budget. Likewise, event photographers and videographers who want to deliver a quick highlight reel to a client can use free music to add that final professional touch without licensing fees.

## Common Workflows for Adding Free Music to Video

The most common workflow starts with identifying your video's length and emotional tone. Once you know whether your clip is 15 seconds or 3 minutes, and whether it needs something energetic or ambient, you can narrow down royalty-free music libraries like YouTube Audio Library, Pixabay Music, or Free Music Archive to find tracks that fit.

After selecting a track, the next step is trimming or looping it to match your video's exact duration. Many free tools — including CapCut, Clipchamp, and DaVinci Resolve's free tier — let you drag and drop audio onto a timeline and adjust the fade-in and fade-out so the music doesn't cut off abruptly.

For creators working on phones, apps like InShot or VN Video Editor allow you to import a downloaded track and sync it to your footage in under two minutes. This skill can walk you through any of these paths depending on the device and format you're working with.
