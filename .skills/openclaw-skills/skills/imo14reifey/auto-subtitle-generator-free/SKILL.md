---
name: auto-subtitle-generator-free
version: "1.0.0"
displayName: "Auto Subtitle Generator Free — Instantly Caption Any Video Without Spending a Dime"
description: >
  Tired of manually transcribing every word just to add subtitles to your videos? The auto-subtitle-generator-free skill automatically detects speech and generates accurate, time-synced captions for any video — no expensive software required. Whether you're a content creator, educator, or marketer, this tool delivers SRT files, burned-in text, or editable caption tracks in minutes. Supports multiple languages, custom styling, and batch processing for high-volume needs.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! Ready to add accurate, time-synced subtitles to your video for free? Drop your video file or paste a link and let's generate captions automatically — tell me your preferred language or style to get started!

**Try saying:**
- "Generate subtitles for my 10-minute YouTube tutorial video and export them as an SRT file"
- "Add burned-in captions to this Instagram Reel with bold white text and a dark background"
- "Transcribe and subtitle this Spanish-language interview video with English captions"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/auto-subtitle-generator-free/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Caption Every Video Automatically — Zero Cost, Full Control

Adding subtitles used to mean hours of rewinding, typing, and syncing timestamps by hand. The auto-subtitle-generator-free skill changes that entirely. It listens to the audio in your video, converts speech to text, and locks each caption to the exact moment it's spoken — all without you lifting more than a finger to start the process.

This skill is built for anyone who needs reliable captions fast. YouTubers who want to boost watch time, teachers uploading lecture recordings, small business owners creating product demos, or social media managers posting reels and shorts — all can generate professional-looking subtitles without touching a paid plan or a complicated editing timeline.

The output is flexible too. You can export a standalone SRT or VTT file to upload to any platform, choose to burn subtitles directly into the video, or get an editable text transcript you can clean up before finalizing. It handles background noise, accents, and fast speech better than most manual workflows — making it a genuinely useful free alternative to premium captioning services.

## Routing Caption Requests Intelligently

When you submit a video for free auto subtitling, your request is parsed for language, frame rate, and audio track quality before being dispatched to the nearest available transcription node.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Transcription API Reference

The backend leverages a speech-to-text pipeline with automatic language detection, splitting your audio into phoneme-level segments to generate timestamped SRT or VTT caption files in near real time. Subtitle burn-in and raw caption export both run through the same cloud processing layer, keeping latency low even on longer video files.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `auto-subtitle-generator-free`
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

## Tips and Tricks

For the most accurate results, use video files with clean audio. If your recording has heavy background music or overlapping voices, try running a noise reduction pass before submitting — even basic cleanup noticeably improves caption accuracy.

When captioning videos with technical jargon, industry terms, or brand names, include a short glossary or correction list in your prompt. This helps the skill prioritize correct spelling for specialized vocabulary that generic speech models might mishear.

If you're captioning vertical videos for mobile platforms like TikTok or Reels, specify the text position explicitly (e.g., center-lower third) to avoid captions overlapping with UI elements like like buttons or profile names.

Finally, always preview the SRT file before burning captions in permanently. Catching a single timestamp misalignment or misspelled word at the text stage is far easier than re-rendering the entire video after the fact.

## Use Cases

The auto-subtitle-generator-free skill fits naturally into a wide range of real-world scenarios. Content creators on YouTube, TikTok, and Instagram use it to improve accessibility and keep viewers watching longer — videos with captions consistently outperform those without on most platforms.

Educators and course creators rely on it to make lecture videos and tutorials compliant with accessibility standards, reaching students who are deaf or hard of hearing without the cost of professional transcription services.

Corporate teams use it to caption internal training videos, webinar recordings, and client-facing demos. Journalists and podcasters convert audio-heavy content into searchable, shareable text. Even filmmakers working on indie projects use it to produce rough-cut subtitle tracks before final color grading. Wherever there's spoken audio in a video, this skill has a practical role to play.

## Common Workflows

A typical workflow starts with uploading your video file or providing a direct URL to hosted content. The skill processes the audio track, detects speech segments, and returns a caption file synced to the video's timeline — usually within a few minutes depending on video length.

For social media content, many users follow a two-step process: generate the raw SRT file first, make quick edits to fix any proper nouns or brand names, then re-submit for burned-in rendering with their preferred font and color settings.

For multilingual content, a common workflow is to generate captions in the source language first, review for accuracy, then request a translated version for a second subtitle track. This is especially useful for creators targeting international audiences without hiring separate translators for every video.

Batch workflows are also supported — users managing a backlog of unsubbed videos can queue multiple files and receive caption outputs sequentially without restarting the process each time.
