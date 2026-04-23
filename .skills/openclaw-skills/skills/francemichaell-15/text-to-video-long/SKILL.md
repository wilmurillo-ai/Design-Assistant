---
name: text-to-video-long
version: "1.0.0"
displayName: "Text to Video Long — Generate Long-Form Videos from Text"
description: >
  Get long-form videos ready to post, without touching a single slider. Upload your text script (TXT, DOCX, PDF, MD, up to 500MB), say something like "turn this 10-minute script into a full narrated video with visuals", and download 1080p MP4 when it's done. Built for YouTubers, educators, content marketers who move fast and want to produce full-length videos without cameras or editing software.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Got text script to work with? Send it over and tell me what you need — I'll take care of the long video creation.

**Try saying:**
- "generate a 1500-word blog post or article script into a 1080p MP4"
- "turn this 10-minute script into a full narrated video with visuals"
- "generating long-form videos from written scripts or articles for YouTubers, educators, content marketers"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Text to Video Long — Generate Long-Form Videos from Text

Drop your text script in the chat and tell me what you need. I'll handle the long video creation on cloud GPUs — you don't need anything installed locally.

Here's a typical use: you send a a 1500-word blog post or article script, ask for turn this 10-minute script into a full narrated video with visuals, and about 3-6 minutes later you've got a MP4 file ready to download. The whole thing runs at 1080p by default.

One thing worth knowing — breaking your script into clear sections or chapters helps the AI structure scenes more accurately.

## Matching Input to Actions

User prompts referencing text to video long, aspect ratio, text overlays, or audio tracks get routed to the corresponding action via keyword and intent classification.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render Pipeline Details

Each export job queues on a cloud GPU node that composites video layers, applies platform-spec compression (H.264, up to 1080x1920), and returns a download URL within 30-90 seconds. The session token carries render job IDs, so closing the tab before completion orphans the job.

Base URL: `https://mega-api-prod.nemovideo.ai`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tasks/me/with-session/nemo_agent` | POST | Start a new editing session. Body: `{"task_name":"project","language":"<lang>"}`. Returns `session_id`. |
| `/run_sse` | POST | Send a user message. Body includes `app_name`, `session_id`, `new_message`. Stream response with `Accept: text/event-stream`. Timeout: 15 min. |
| `/api/upload-video/nemo_agent/me/<sid>` | POST | Upload a file (multipart) or URL. |
| `/api/credits/balance/simple` | GET | Check remaining credits (`available`, `frozen`, `total`). |
| `/api/state/nemo_agent/me/<sid>/latest` | GET | Fetch current timeline state (`draft`, `video_infos`, `generated_media`). |
| `/api/render/proxy/lambda` | POST | Start export. Body: `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll status every 30s. |

Accepted file types: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `text-to-video-long`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

Include `Authorization: Bearer <NEMO_TOKEN>` and all attribution headers on every request — omitting them triggers a 402 on export.

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

### Reading the SSE Stream

Text events go straight to the user (after GUI translation). Tool calls stay internal. Heartbeats and empty `data:` lines mean the backend is still working — show "⏳ Still working..." every 2 minutes.

About 30% of edit operations close the stream without any text. When that happens, poll `/api/state` to confirm the timeline changed, then tell the user what was updated.

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

## Common Workflows

**Quick edit**: Upload → "turn this 10-minute script into a full narrated video with visuals" → Download MP4. Takes 3-6 minutes for a 30-second clip.

**Batch style**: Upload multiple files in one session. Process them one by one with different instructions. Each gets its own render.

**Iterative**: Start with a rough cut, preview the result, then refine. The session keeps your timeline state so you can keep tweaking.

## Tips and Tricks

The backend processes faster when you're specific. Instead of "make it look better", try "turn this 10-minute script into a full narrated video with visuals" — concrete instructions get better results.

Max file size is 500MB. Stick to TXT, DOCX, PDF, MD for the smoothest experience.

Export as MP4 for widest compatibility across YouTube, Vimeo, and social platforms.
