---
name: ffmpeg-mp4-converter
version: "1.0.0"
displayName: "FFmpeg MP4 Converter — Batch Convert Any Video Format to MP4 Instantly"
description: >
  Tired of wrestling with incompatible video formats, bloated files, or hours of manual conversion work? The ffmpeg-mp4-converter skill automates the entire process — converting MKV, AVI, MOV, WebM, FLV, and dozens of other formats into clean, compressed MP4 files. Supports batch processing, codec selection, resolution scaling, and audio normalization. Built for content creators, developers, and media teams who need reliable, repeatable conversions without touching a command line.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm your FFmpeg MP4 Converter assistant — ready to help you convert, compress, and reformat video files into MP4 with exactly the settings you need. Tell me what you're working with and I'll get it done.

**Try saying:**
- "Convert all MKV files in my downloads folder to MP4 using H.264 with a bitrate of 4000k"
- "I have a MOV file from my iPhone that's 2GB — can you convert it to MP4 and compress it under 500MB without losing too much quality?"
- "Batch convert a folder of WebM screen recordings to 1080p MP4 with AAC audio at 192kbps"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/ffmpeg-mp4-converter/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Convert Any Video to MP4 Without the Headache

Video format chaos is real. You've got footage from a drone in MKV, screen recordings in MOV, client files in AVI, and a deadline in two hours. Manually converting each file through a GUI tool is slow, inconsistent, and error-prone — especially when you need specific codecs, bitrates, or output resolutions.

The ffmpeg-mp4-converter skill solves this by giving you a conversational interface to one of the most powerful video processing engines in existence. Just describe what you need — the input format, desired quality, frame rate, audio settings — and the skill generates and executes the right FFmpeg command for your situation. No syntax memorization, no documentation diving.

Whether you're preparing videos for web delivery, archiving raw footage in a space-efficient format, or standardizing a library of mixed-format clips, this skill handles the heavy lifting. It supports single-file conversions and bulk jobs alike, with output options that match real-world publishing requirements across YouTube, Vimeo, mobile platforms, and broadcast workflows.

## Routing Your Conversion Requests

When you submit a video file or URL, the skill parses your source format, target codec preferences, and any FFmpeg flags you specify, then routes the job to the appropriate transcoding pipeline based on container type and resolution.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Transcoding Backend Reference

All conversion jobs run on a distributed FFmpeg cloud backend that handles remuxing, re-encoding, and codec normalization — including H.264/AAC output, bitrate control, and keyframe alignment — without touching your local CPU. The API accepts multipart uploads or direct stream URLs and returns a signed download link to your finished MP4 upon job completion.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ffmpeg-mp4-converter`
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

## Troubleshooting Common Conversion Issues

If your converted MP4 has no audio, the source file likely uses an audio codec — like AC3 or DTS — that needs explicit transcoding. Specify `-acodec aac` in your request and the skill will handle the remapping automatically.

Green or corrupted frames often point to a codec mismatch during stream copy. If you're seeing visual artifacts, ask the skill to force full re-encoding rather than using stream copy mode — this is slower but produces a clean output every time.

Oversized output files usually mean the bitrate wasn't constrained. Tell the skill your target file size or maximum bitrate and it will calculate the appropriate `-b:v` and `-maxrate` flags accordingly.

If a conversion stalls or fails on a specific file, it may be a corrupted container. Ask the skill to run an integrity check using FFprobe before attempting conversion — this identifies broken keyframes or missing index data that would cause FFmpeg to hang mid-process.

## Best Practices for High-Quality MP4 Output

Always specify your intended use case when making a conversion request. A video destined for YouTube has very different optimal settings than one being archived or sent via email. The skill will recommend appropriate codec profiles — like H.264 High Profile for streaming or Baseline Profile for maximum device compatibility — based on your target.

For the best balance of quality and file size, request CRF (Constant Rate Factor) encoding rather than fixed bitrate when quality consistency matters more than exact file size. A CRF value between 18 and 23 produces excellent results for most MP4 deliverables.

When batch converting, always test on a single representative file first. Confirm the output looks correct before running the full job — this avoids wasting time converting hundreds of files with a misconfigured setting.

Preserve your original files until you've verified the converted MP4 plays correctly on your target device or platform. Ask the skill to include a verification step that checks the output file's duration and stream metadata against the source before marking a job complete.

## Real-World Use Cases for FFmpeg MP4 Converter

Content creators pulling raw footage off cameras often deal with formats like AVCHD or MXF that editing platforms and social media sites reject outright. This skill converts those files to H.264 MP4 — the universal format accepted by every major platform — while preserving the original resolution and frame rate.

Developers building media pipelines use this skill to normalize uploaded video content before storage or processing. Instead of writing custom FFmpeg wrapper scripts for every new format, they describe the transformation in plain language and get consistent, production-ready output.

Archivists and educators working with legacy video collections — think old AVI or RealMedia files — use the converter to migrate their libraries to MP4 containers with modern codecs, dramatically reducing storage requirements while maintaining playback compatibility across current devices.

Streaming teams use it to generate multiple MP4 variants from a single master file: a 1080p version for desktop, a 720p version for mobile, and a low-bitrate preview for thumbnails — all in one batch job.
