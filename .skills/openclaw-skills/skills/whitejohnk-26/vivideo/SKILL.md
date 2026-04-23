---
name: vivideo
version: "1.0.0"
displayName: "Vivideo — AI-Powered Video Analysis & Editing Assistant for Creators"
description: >
  Turn raw footage into polished, insight-rich video content with vivideo — the AI skill built for creators, editors, and teams who work with video every day. Vivideo analyzes, describes, and helps you work smarter with your video files across mp4, mov, avi, webm, and mkv formats. Whether you need scene breakdowns, content summaries, caption drafts, or editing direction, vivideo handles it without the usual back-and-forth. Built for real workflows, not just demos.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome to vivideo — your AI assistant for understanding and working with video content. Drop in your footage and tell me what you need: a scene breakdown, a content summary, caption ideas, or editing direction. Let's get into it — what are you working on today?

**Try saying:**
- "Summarize the key moments in this interview footage and suggest where to cut for a 90-second highlight reel"
- "Describe what's happening in each scene of this product demo video and flag any moments that seem off-brand"
- "Draft subtitles and a short social media caption based on the dialogue in this mp4 clip"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# See Your Footage in a Whole New Way

Vivideo is designed for anyone who works with video and needs more than just a playback tool. Whether you're a solo content creator reviewing raw clips, a marketing team pulling insights from product demos, or an editor trying to structure a long-form piece, vivideo gives you an intelligent layer on top of your footage.

Upload your video and ask vivideo to break down what's happening scene by scene, identify key moments, draft descriptive summaries, or suggest how to structure your edit. It reads your content the way a sharp-eyed collaborator would — noticing pacing, subject matter, dialogue cues, and visual context — then translates that into actionable language you can actually use.

Vivideo supports mp4, mov, avi, webm, and mkv files, making it flexible enough to fit into almost any production pipeline. Think of it less as a filter or effect tool, and more as the thoughtful assistant who watches your footage so you don't have to watch it five times before making a decision.

## Routing Your Edit Requests

Every prompt you send — whether you're trimming a timeline, generating captions, or asking for scene analysis — gets parsed by Vivideo's intent engine and dispatched to the appropriate NemoVideo processing endpoint automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

Vivideo runs on the NemoVideo API, which handles all heavy lifting: frame extraction, AI inference, and render queuing. Each call is stateful within your session, so context like your project settings and clip history carries through without you needing to repeat yourself.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `vivideo`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=vivideo&skill_version=1.0.0&skill_source=<platform>`

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

## Performance Notes

Vivideo works across mp4, mov, avi, webm, and mkv formats, but file size and duration can affect response depth and speed. For best results, keep individual clips under 500MB when possible, and trim footage to the relevant section before uploading if you're working with a longer raw file.

Highly compressed video files or those with very low bitrates may result in less precise visual analysis — vivideo reads what's actually in the file, so quality in generally means quality out. If you're exporting from an editing timeline specifically for vivideo analysis, a mid-range export preset (not ultra-compressed) will give you the most accurate results.

Vivideo processes one file per request, so if you have multiple clips to analyze, submit them in separate sessions. This keeps each analysis clean and ensures you get focused, file-specific output rather than blended responses across different pieces of footage.

## Best Practices

To get the most out of vivideo, be specific about what you need from your footage. Asking 'summarize this video' will get you a general overview, but asking 'identify the three strongest talking points from this interview and note the timestamps' will get you something you can act on immediately.

For longer videos, consider breaking your request into focused questions rather than asking for everything at once. Vivideo handles complex requests well, but targeted prompts tend to produce tighter, more useful output — especially when you're working toward a specific deliverable like a social cut or a transcript.

If you're working with footage that has background noise, overlapping audio, or heavy visual motion, mention that context upfront. Vivideo can adjust its analysis framing when it knows what kind of environment or production style it's dealing with. The more context you give, the sharper the output.
