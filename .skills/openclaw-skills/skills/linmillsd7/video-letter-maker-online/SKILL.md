---
name: video-letter-maker-online
version: "1.0.0"
displayName: "Video Letter Maker Online — Create and Send Video Letters"
description: >
  Get personalized video letters ready to post, without touching a single slider. Upload your photos, text, audio (JPG, PNG, MP4, MP3, up to 200MB), say something like "turn my written message and photos into a video letter I can send to my friend", and download 1080p MP4 when it's done. Built for everyday users, gift senders, long-distance couples who move fast and want to send a meaningful video message without video editing skills.
metadata: {"openclaw": {"emoji": "💌", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your photos, text, audio and I'll handle the AI video letter creation. Or just describe what you're after.

**Try saying:**
- "create a personal photo and a typed heartfelt message into a 1080p MP4"
- "turn my written message and photos into a video letter I can send to my friend"
- "creating heartfelt video messages to send to friends and family for everyday users, gift senders, long-distance couples"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Video Letter Maker Online — Create and Send Video Letters

This tool takes your photos, text, audio and runs AI video letter creation through a cloud rendering pipeline. You upload, describe what you want, and download the result.

Say you have a personal photo and a typed heartfelt message and want to turn my written message and photos into a video letter I can send to my friend — the backend processes it in about 30-60 seconds and hands you a 1080p MP4.

Tip: adding a voiceover or background music makes the video letter feel more personal.

## Matching Input to Actions

User prompts referencing video letter maker online, aspect ratio, text overlays, or audio tracks get routed to the corresponding action via keyword and intent classification.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render Pipeline Details

Each export job queues on a cloud GPU node that composites video layers, applies platform-spec compression (H.264, up to 1080x1920), and returns a download URL within 30-90 seconds. The session token carries render job IDs, so closing the tab before completion orphans the job.

Headers are derived from this file's YAML frontmatter. `X-Skill-Source` is `video-letter-maker-online`, `X-Skill-Version` comes from the `version` field, and `X-Skill-Platform` is detected from the install path (`~/.clawhub/` = `clawhub`, `~/.cursor/skills/` = `cursor`, otherwise `unknown`).

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

### Translating GUI Instructions

The backend responds as if there's a visual interface. Map its instructions to API calls:

- "click" or "点击" → execute the action via the relevant endpoint
- "open" or "打开" → query session state to get the data
- "drag/drop" or "拖拽" → send the edit command through SSE
- "preview in timeline" → show a text summary of current tracks
- "Export" or "导出" → run the export workflow

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

## Common Workflows

**Quick edit**: Upload → "turn my written message and photos into a video letter I can send to my friend" → Download MP4. Takes 30-60 seconds for a 30-second clip.

**Batch style**: Upload multiple files in one session. Process them one by one with different instructions. Each gets its own render.

**Iterative**: Start with a rough cut, preview the result, then refine. The session keeps your timeline state so you can keep tweaking.

## Tips and Tricks

The backend processes faster when you're specific. Instead of "make it look better", try "turn my written message and photos into a video letter I can send to my friend" — concrete instructions get better results.

Max file size is 200MB. Stick to JPG, PNG, MP4, MP3 for the smoothest experience.

Export as MP4 for widest compatibility across devices and messaging apps.
