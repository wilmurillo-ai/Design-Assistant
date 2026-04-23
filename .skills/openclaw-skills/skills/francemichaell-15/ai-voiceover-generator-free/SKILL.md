---
name: ai-voiceover-generator-free
version: "1.0.0"
displayName: "AI Voiceover Generator Free — Generate Voiceovers for Videos"
description: >
  generate text or script into voiced video files with this skill. Works with MP4, MOV, TXT, DOCX files up to 200MB. content creators, marketers, students use it for adding AI narration to videos without recording — processing takes 20-40 seconds on cloud GPUs and you get 1080p MP4 files.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Share your text or script and I'll get started on AI voiceover generation. Or just tell me what you're thinking.

**Try saying:**
- "generate my text or script"
- "export 1080p MP4"
- "generate a natural voiceover for my"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# AI Voiceover Generator Free — Generate Voiceovers for Videos

Send me your text or script and describe the result you want. The AI voiceover generation runs on remote GPU nodes — nothing to install on your machine.

A quick example: upload a 200-word product description script, type "generate a natural voiceover for my script in a female American English voice", and you'll get a 1080p MP4 back in roughly 20-40 seconds. All rendering happens server-side.

Worth noting: shorter scripts under 150 words produce the most natural-sounding results.

## Matching Input to Actions

User prompts referencing ai voiceover generator free, aspect ratio, text overlays, or audio tracks get routed to the corresponding action via keyword and intent classification.

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
- `X-Skill-Source`: `ai-voiceover-generator-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

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

**Quick edit**: Upload → "generate a natural voiceover for my script in a female American English voice" → Download MP4. Takes 20-40 seconds for a 30-second clip.

**Batch style**: Upload multiple files in one session. Process them one by one with different instructions. Each gets its own render.

**Iterative**: Start with a rough cut, preview the result, then refine. The session keeps your timeline state so you can keep tweaking.

## Tips and Tricks

The backend processes faster when you're specific. Instead of "make it look better", try "generate a natural voiceover for my script in a female American English voice" — concrete instructions get better results.

Max file size is 200MB. Stick to MP4, MOV, TXT, DOCX for the smoothest experience.

Export as MP4 for widest compatibility across platforms and devices.
