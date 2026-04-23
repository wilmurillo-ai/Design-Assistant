---
name: ai-image-to-video-generator-free
version: "1.0.0"
displayName: "AI Image to Video Generator Free — Animate Your Photos Into Stunning Videos"
description: >
  Tell me what you need and I'll transform your still images into dynamic, eye-catching videos — no cost, no complicated setup. This ai-image-to-video-generator-free skill breathes life into photos by adding motion, transitions, and cinematic effects. Upload a single image or a batch, choose your animation style, and export in mp4, mov, avi, webm, or mkv. Perfect for content creators, marketers, and social media managers who want scroll-stopping visuals without a production budget.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you turn your photos into stunning videos using this free AI image-to-video generator. Drop in your images and tell me the style, mood, or platform you're creating for — let's make something worth watching!

**Try saying:**
- "Animate my 10 product photos into a 30-second promotional video with a smooth zoom effect and export as mp4"
- "Convert this single landscape photo into a 15-second cinematic video with a slow Ken Burns pan for my YouTube intro"
- "Take these 5 event snapshots and create a slideshow video with fade transitions and upbeat pacing, saved as webm"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Static Photos Into Captivating Video Content Instantly

Most people have folders full of great photos that never get seen because static images struggle to compete in a video-first world. This skill closes that gap by converting your images into polished video clips complete with motion effects, smooth transitions, and optional background music sync — all without spending a dime.

Whether you're working with product photography, travel snapshots, event photos, or digital artwork, the AI analyzes each image and applies intelligent animation that feels natural rather than gimmicky. You control the pacing, the mood, and the output format, so the final video matches your brand or personal style.

Content creators, small business owners, educators, and social media teams use this skill to produce Reels, TikToks, YouTube intros, and presentation slideshows in a fraction of the time traditional video editing would require. No timeline scrubbing, no keyframe headaches — just upload, customize, and export.

## Routing Your Animation Requests

Each image-to-video request is parsed for motion style, frame duration, and source image URL before being dispatched to the appropriate NemoVideo rendering pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles diffusion-based frame interpolation and temporal coherence to transform static images into fluid, AI-animated video clips. All render jobs are queued through the NemoVideo inference engine, which manages keyframe generation, motion vector estimation, and final video encoding.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-image-to-video-generator-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=ai-image-to-video-generator-free&skill_version=1.0.0&skill_source=<platform>`

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
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Use Cases

E-commerce sellers use this skill to turn flat product photos into looping video ads that outperform static images on platforms like Instagram and Facebook — without hiring a videographer or paying for stock footage.

Real estate agents upload property photos and generate virtual walkthrough-style videos that can be shared in listings or via email, giving buyers a stronger sense of the space before scheduling a showing.

Teachers and trainers convert diagram images, infographics, and slide screenshots into short explainer videos that are easier to share and more engaging than PDFs. The exported files drop directly into any LMS or presentation tool.

Personal users — especially those preserving family memories — use the free ai-image-to-video-generator-free skill to build tribute videos, birthday reels, and anniversary slideshows from old photo albums, exporting in high-quality mp4 or mov for easy sharing with family members on any device.

## Common Workflows

The most popular workflow starts with a batch upload — drop in anywhere from 1 to 50 images, then specify the desired video length, transition style (fade, zoom, slide, or Ken Burns), and output format. The skill sequences the images intelligently based on visual similarity or the order you provide.

For single-image animation, users typically describe the type of motion they want: a slow outward zoom for dramatic effect, a subtle parallax shift for depth, or a gentle pan across a wide landscape. These single-image videos are especially popular for social media cover videos and website hero backgrounds.

Another common workflow involves themed storytelling — users upload a series of images from an event or trip and ask for a narrative-style video with title cards between sections. The skill handles the sequencing, pacing, and export in mp4, mov, avi, webm, or mkv depending on where the video will be published.
