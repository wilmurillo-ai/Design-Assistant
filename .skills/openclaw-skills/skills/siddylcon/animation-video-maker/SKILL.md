---
name: animation-video-maker
version: "1.0.0"
displayName: "Animation Video Maker — Turn Ideas Into Stunning Animated Videos Instantly"
description: >
  Tired of spending hours in complex animation software just to produce a short clip? The animation-video-maker skill lets you create polished animated videos through simple conversational prompts — no timeline scrubbing, no keyframe headaches. Describe your scene, characters, or motion sequence and watch it come to life. Supports mp4, mov, avi, webm, and mkv formats. Perfect for marketers, educators, content creators, and indie developers who need professional-quality animation without the steep learning curve.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! 🎬 I'm your animation video maker — ready to turn your concepts into eye-catching animated videos. Tell me what scene, story, or sequence you have in mind and let's start creating together!

**Try saying:**
- "Create a 15-second animated explainer video showing how a mobile app works, with smooth transitions and bold text callouts"
- "Make an animated logo reveal for my brand with a particle burst effect and a dark background, export as mp4"
- "Generate a short animated social media clip of a cartoon character announcing a product sale, upbeat style, 9:16 vertical format"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Bring Your Stories to Life With Animated Video

Creating animated video used to mean mastering expensive tools, hiring specialists, or settling for clunky templates that looked like everyone else's content. The animation-video-maker skill changes that equation entirely. You describe what you want — a character walking through a cityscape, a product reveal with motion graphics, or an explainer sequence with animated text — and the skill handles the creative heavy lifting.

Whether you're building a social media campaign, an educational module, or a promotional reel, this skill adapts to your vision rather than forcing your vision into a rigid workflow. You can iterate quickly: refine the motion style, swap color palettes, adjust pacing, or add voiceover-ready timing — all through natural conversation.

The result is a production-ready animated video file you can drop straight into your project. No render farms, no plugin subscriptions, no five-hour YouTube tutorials required. Just your idea, clearly described, transformed into motion.

## Directing Your Animation Requests

Every prompt you send — whether it's a scene description, character brief, style preference, or storyboard concept — gets parsed and routed to the appropriate NemoVideo rendering pipeline based on animation type, duration, and visual complexity.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Engine Reference

The NemoVideo backend handles keyframe generation, motion interpolation, and style rendering in real time, converting your text prompts into fully animated video sequences. Each API call manages scene composition, frame rate settings, and export formatting automatically so you stay focused on creative direction.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `animation-video-maker`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=animation-video-maker&skill_version=1.0.0&skill_source=<platform>`

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

## Quick Start Guide

Getting your first animated video out the door is straightforward. Start by describing your core idea in one or two sentences — include the mood, length, and intended platform (Instagram Reel, YouTube intro, presentation slide, etc.). The more context you give upfront, the closer the first output will be to what you're imagining.

Next, specify your format preference. The animation-video-maker skill supports mp4, mov, avi, webm, and mkv, so just name the one your editing tool or platform expects. If you're not sure, mp4 is a safe universal default.

Once you receive your animated video, review the motion timing and visual style. You can ask for adjustments in plain language — 'make the text appear slower,' 'use a warmer color palette,' or 'loop the ending seamlessly.' Iteration is fast, so don't hesitate to refine until it feels exactly right. There's no penalty for asking for changes.

## Integration Guide

The animation-video-maker skill fits naturally into most content production pipelines. If you're working inside ClawHub, you can chain this skill with audio tools to add background music or voiceover to your animated output, creating a fully composed video asset in a single session.

For teams using external platforms — video editors like DaVinci Resolve, Premiere Pro, or CapCut — simply export your animation in the format that matches your project sequence settings (mov for lossless workflows, mp4 for web delivery, webm for browser-based players). Drop the exported file directly onto your timeline as you would any footage.

If you're embedding animated videos into a website or app, webm format offers excellent compression for fast load times. For presentation tools like PowerPoint or Keynote, mp4 with H.264 encoding ensures the broadest compatibility. You can request specific codec preferences or resolution targets directly in your prompt to make handoff seamless.
