---
name: subtitle-generator-online-free
version: "1.0.0"
displayName: "Subtitle Generator Online Free — Add Captions to Video, No Signup"
description: >
  Paste your video link or drop an MP4 and this free subtitle generator online spits out accurate, time-coded captions in under 2 minutes. It's a full online caption maker that works in your browser — no install, no watermark on the SRT file you download. YouTubers, TikTok creators, and anyone subtitling a Reel will get a clean subtitle file they can burn into 1080p exports or keep as a separate.srt track.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Drop your MP4 or paste a video URL and I'll generate a free, time-coded SRT subtitle file ready to upload. No video yet? Describe your footage and the language you need.

**Try saying:**
- "generate free subtitles for my YouTube video online"
- "add captions to MP4 file free no watermark"
- "create SRT subtitle file from video online free"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Add Subtitles to Any Video File Online

Drop your MP4 (up to 2GB) into the chat, tell me the language, and you'll get a time-coded SRT file back. That file snaps straight into Premiere, CapCut, DaVinci Resolve, or YouTube Studio without extra formatting.

Say you shot a 10-minute vlog on your phone and the audio is muddy. The generator reads the speech, timestamps every line to the nearest 0.1 seconds, and returns a clean subtitle file — no manual syncing on your end.

You can also paste a YouTube URL and get captions for someone else's video in about 90 seconds. It's that direct.

## Matching Your Video To Captions

When you drop an MP4 or paste a YouTube URL, the tool checks the audio track's language tag first, then routes it to the matching speech-to-text model — English gets a different pipeline than Spanish or Japanese.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering And Transcript Sync

Your audio gets chunked into 30-second segments and processed on shared GPU nodes, so a 10-minute video typically returns an SRT file in under 90 seconds. Timestamps are pinned to word boundaries, not sentence ends, which keeps captions from lagging behind fast speech.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `subtitle-generator-online-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

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

## Performance Notes — File Size, Speed, and Format Support

The free subtitle generator online handles MP4, MOV, and WebM files up to 2GB. Processing a 5-minute clip takes around 45 seconds; a 30-minute file runs closer to 4 minutes. Don't close the chat tab mid-process or you'll restart the queue.

Output is always a plain .srt file by default. You can ask for .vtt format if you're uploading to a website or embedding subtitles in an HTML5 player — both formats come out clean with no extra characters or encoding errors.

If your video has two speakers, mention that upfront. The generator separates speaker turns into distinct subtitle blocks, which makes the final SRT a lot easier to read and edit inside tools like Aegisub or Subtitle Edit.

## Best Practices for Free Online Subtitle Generation

Keep your source audio above -12dB peak volume — the caption generator reads speech way more accurately when there's no constant background music drowning the vocals. A 1080p MP4 with clear dialogue will return a subtitle file with roughly 95% word accuracy without any editing on your part.

If you're subtitling a talking-head video under 15 minutes, just paste the YouTube link directly. It's faster than uploading the raw file and you'll still get a downloadable SRT you can edit line by line.

For vertical TikTok or Reels content, ask for captions formatted in 3-word chunks per line. That way the text fits a 1080x1920 frame without running off the edges. One small formatting request saves you 20 minutes of manual line-breaking in your editor.
