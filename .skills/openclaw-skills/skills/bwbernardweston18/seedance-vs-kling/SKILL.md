---
name: seedance-vs-kling
version: "1.0.0"
displayName: "Seedance vs Kling — Compare AI Video Generation Tools"
description: >
  Get 1080p MP4 files from your text or images using this seedance-vs-kling tool. It runs AI video generation comparison on cloud GPUs, so your machine does zero heavy lifting. content creators can comparing AI video generation quality between Seedance and Kling in roughly 1-2 minutes — supports MP4, MOV, WebM, PNG.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Share your text or images and I'll get started on AI video generation comparison. Or just tell me what you're thinking.

**Try saying:**
- "compare a short text prompt describing a scene into a 1080p MP4"
- "generate a 5-second video clip from a text prompt and compare Seedance and Kling outputs"
- "comparing AI video generation quality between Seedance and Kling for content creators"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# From Text Or Images to Generated Video Clips

Drop your text or images in the chat and tell me what you need. I'll handle the AI video generation comparison on cloud GPUs — you don't need anything installed locally.

Here's a typical run: you send a a short text prompt describing a scene, ask for generate a 5-second video clip from a text prompt and compare Seedance and Kling outputs, and about 1-2 minutes later you've got a MP4 file ready to download. The whole thing runs at 1080p by default.

One thing worth knowing — test the same prompt on both tools to get a fair side-by-side quality comparison.

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

Everything happens on cloud infrastructure. Your seedance vs kling job gets queued, rendered on GPU nodes, and the finished file comes back as a download link.

Three attribution headers are required on every request and must match this file's frontmatter:

| Header | Value |
|--------|-------|
| `X-Skill-Source` | `seedance-vs-kling` |
| `X-Skill-Version` | frontmatter `version` |
| `X-Skill-Platform` | auto-detect: `clawhub` / `cursor` / `unknown` from install path |

Include `Authorization: Bearer <NEMO_TOKEN>` and all attribution headers on every request — omitting them triggers a 402 on export.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### Reading the SSE Stream

Text events go straight to the user (after GUI translation). Tool calls stay internal. Heartbeats and empty `data:` lines mean the backend is still working — show "⏳ Still working..." every 2 minutes.

About 30% of edit operations close the stream without any text. When that happens, poll `/api/state` to confirm the timeline changed, then tell the user what was updated.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

Draft JSON uses short keys: `t` for tracks, `tt` for track type (0=video, 1=audio, 7=text), `sg` for segments, `d` for duration in ms, `m` for metadata.

Example timeline summary:
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

## Common Workflows

**From scratch**: Describe what you want and the AI generates a draft. You refine from there.

**Polish existing content**: Upload your text or images, ask for specific changes — generate a 5-second video clip from a text prompt and compare Seedance and Kling outputs, adjust colors, swap music. The backend handles rendering.

**Export ready**: Once you're happy, export at 1080p in MP4. File lands in your downloads.

## Tips and Tricks

Keep your source files under 200MB for fastest processing. If you're working with longer content, split it into chunks first.

For best results at 1080p, make sure your input is at least 720p. Upscaling from 480p works but you'll notice it.

Export as MP4 for widest compatibility.

## Best Practices

Use source footage in MP4, MOV, WebM, PNG format for best compatibility. 1080p input gives the cleanest results but 720p works fine too.

Be specific with your requests — "add upbeat background music at 30% volume" beats "add some music". The AI works better with concrete details.

Export as MP4 for widest compatibility.
