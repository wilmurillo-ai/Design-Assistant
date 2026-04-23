---
name: ai-gemini-video-editor
version: "1.0.0"
displayName: "AI Gemini Video Editor — Intelligent Video Editing Powered by Google Gemini"
description: >
  Drop a video and describe what you want — and watch Gemini's multimodal intelligence turn your raw footage into polished content. The ai-gemini-video-editor skill understands your video's context, scenes, and pacing to suggest cuts, generate captions, rewrite narratives, and restructure timelines. Built for creators, marketers, and educators who need fast, smart edits without a full production suite. From trimming talking-head clips to scripting voiceovers for explainer videos, this skill handles the creative heavy lifting.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to the AI Gemini Video Editor — your intelligent editing assistant that understands your footage and turns your ideas into polished video content. Drop your video or describe your project and let's start editing!

**Try saying:**
- "I have a 12-minute product walkthrough video. Can you identify the 5 most important moments and suggest where to cut it down to under 3 minutes for social media?"
- "Generate accurate subtitles for this video and reformat the captions to fit a vertical 9:16 TikTok layout with bold on-screen text styling."
- "Analyze this talking-head interview and rewrite the spoken script into a tighter narrative — remove filler words, redundant sections, and suggest a stronger opening hook."

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Edit Smarter, Not Harder With Gemini AI

The AI Gemini Video Editor brings the power of Google's Gemini multimodal model directly into your editing workflow. Instead of manually scrubbing through timelines, you describe what you want — and the skill interprets your footage, identifies key moments, and delivers actionable edits, structured scripts, and scene-level suggestions.

Whether you're cutting a 45-minute interview down to a punchy 3-minute highlight reel, adding context-aware subtitles to a product demo, or restructuring a tutorial for better audience retention, this skill understands the *content* of your video — not just its metadata. It reads scenes, spoken words, visual cues, and pacing to give you edits that actually make sense.

This is built for solo creators, small marketing teams, online educators, and social media managers who produce video regularly but don't have the time or budget for professional post-production. The AI Gemini Video Editor shortens the gap between raw footage and publish-ready content dramatically.

## Gemini Routing Your Edit Requests

Every prompt you send — whether trimming a clip, generating captions, or applying a scene transition — gets parsed by Gemini's multimodal understanding layer and routed to the appropriate video processing pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud API Reference Guide

AI Gemini Video Editor offloads all transcoding, frame analysis, and generative editing tasks to Google's cloud backend, meaning your local machine handles only the interface while Gemini processes the heavy video workloads remotely. API calls are authenticated per session and throttled based on your active credit tier.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-gemini-video-editor`
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

## Quick Start Guide

Getting started with the AI Gemini Video Editor is straightforward. Begin by sharing your video file directly in the chat, or paste a video URL if your content is hosted online. Then describe your editing goal in plain language — for example, 'cut this to 90 seconds for Instagram' or 'add chapter markers based on topic changes.'

Gemini will analyze the video's visual content, spoken audio, and scene structure before responding with specific edit recommendations, generated scripts, caption drafts, or a restructured timeline outline. You can then refine the output conversationally — ask for a shorter version, a different tone, or alternative cut points.

For best results, be specific about your target platform, audience, and desired length upfront. The more context you provide, the more precise and useful the editing output will be. You can also ask the skill to explain *why* it made certain suggestions, which is especially useful for learning better editing instincts over time.

## Performance Notes

The AI Gemini Video Editor performs best with videos that have clear audio and reasonably stable footage. Heavily compressed files or videos with significant background noise may result in less precise transcript-based edits, so higher-quality source files will always yield sharper recommendations.

For longer videos — anything over 20 minutes — consider breaking the footage into logical segments before submitting. This helps Gemini focus its analysis and produce more granular, scene-specific suggestions rather than broad structural notes. If you're working with multi-camera footage or a rough cut with rough transitions, mention that context explicitly so the skill can tailor its recommendations accordingly.

Gemini's multimodal understanding means it can process both what is *said* and what is *shown* simultaneously, which gives it an edge on content like tutorials, product reviews, and interviews where visual and verbal information need to align. Expect the most detailed outputs for content-dense, dialogue-driven videos.
