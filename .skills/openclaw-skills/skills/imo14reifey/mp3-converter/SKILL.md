---
name: mp3-converter
version: "1.0.0"
displayName: "MP3 Converter — Convert Any Audio or Video File to MP3 Instantly"
description: >
  Extract clean, high-quality MP3 audio from videos, podcasts, voice memos, and more — without juggling clunky desktop software. This mp3-converter skill handles format conversion on demand, letting you set bitrate, trim silence, and rename output files through simple chat commands. Perfect for content creators, musicians, students, and anyone who needs audio in a portable format fast.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm your MP3 Converter assistant — ready to help you extract, convert, and fine-tune audio into MP3 format from virtually any source file. Drop a file or describe what you need converted and let's get started!

**Try saying:**
- "Convert this MP4 video to MP3 at 192kbps and keep the original filename"
- "Extract just the first 3 minutes of this WAV file and save it as an MP3"
- "Convert all the FLAC files in this folder to MP3 at 320kbps with metadata preserved"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/mp3-converter/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Convert Anything to MP3 Without the Hassle

Whether you're pulling a soundtrack from a YouTube-style video file, extracting interview audio from an MP4 recording, or converting a FLAC album for your phone, the MP3 Converter skill gets it done through a straightforward conversation — no software installs, no confusing menus.

Just tell the skill what you have and what you need. You can specify output quality (from 64kbps voice recordings all the way up to 320kbps studio-grade audio), choose whether to preserve metadata like artist and track title, and even trim the file to a specific time range before converting. It handles common source formats including MP4, WAV, OGG, AAC, FLAC, WMA, and MOV.

This skill is built for real workflows — not just one-off conversions. Batch processing, consistent naming conventions, and quality presets mean you can set a standard once and reuse it every time. Whether you're a podcaster archiving episodes, a teacher clipping lecture audio, or a musician bouncing demos, this tool fits naturally into how you already work.

## Routing Your Conversion Requests

When you submit an audio or video file, the skill parses the source format, bitrate preferences, and output parameters before dispatching the job to the appropriate conversion pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing Backend Reference

The MP3 Converter skill connects to a cloud-based transcoding engine that handles format demuxing, audio stream extraction, and re-encoding to MP3 at your specified bitrate — all without local processing. Jobs are queued, processed, and returned as a downloadable MP3 link typically within seconds, depending on file size and server load.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `mp3-converter`
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

## Troubleshooting

**Output file sounds distorted or has artifacts:** This usually happens when converting from a low-quality source at a high bitrate setting. The converter can't add quality that wasn't there — try matching your output bitrate closer to the source's original quality, or use 128kbps for voice content and 192–320kbps for music.

**Conversion fails or stalls on large files:** Very large video files (over 2GB) may time out depending on your environment. Try trimming the file to the relevant segment first, then converting — this also speeds up the process significantly for long recordings.

**Metadata (artist, title) not showing up in the MP3:** Some source formats store metadata differently. If tags aren't carrying over automatically, you can explicitly tell the skill which tags to write — for example: 'Set artist to John Smith and title to Episode 12 on the output file.'

**Wrong audio track extracted from a multi-track video:** Broadcast recordings and some MP4 files contain multiple audio streams. Specify which track you want — for example, 'Use audio track 2' — and the skill will target that stream during conversion.

## Common Workflows

**Podcast episode archiving:** Many podcasters record in WAV or AIFF for editing, then need compressed MP3s for distribution. A typical workflow: convert the final edited WAV to MP3 at 128kbps mono (ideal for voice), embed the episode title and number as metadata, and output with a date-stamped filename like `2024-06-01_episode-42.mp3`.

**Stripping audio from screen recordings or tutorials:** If you've recorded a software walkthrough or lecture as an MP4 and only need the audio for a transcript or audio-only version, ask the skill to extract the audio track and convert it to MP3 — this dramatically reduces file size and makes it easy to upload to transcription tools.

**Music library format standardization:** If you have a mixed library of FLAC, OGG, and AAC files and want everything in MP3 for device compatibility, describe your naming convention and quality preference once. The skill can apply the same settings consistently across a batch, saving significant manual effort.

**Ringtone or clip creation:** Specify a start time and end time (e.g., '0:45 to 1:10') along with your conversion request, and the skill will trim and convert in a single step — no separate editing needed.
