---
name: auto-subtitle-generator-free-ab2n-0330
version: "1.0.0"
displayName: "Auto Subtitle Generator Free — Instantly Caption Any Video Without Paying a Dime"
description: >
  Drop a video and watch captions appear automatically — no subscriptions, no watermarks, no hassle. The auto-subtitle-generator-free skill transcribes spoken dialogue and burns readable subtitles directly into your footage. Upload mp4, mov, avi, webm, or mkv files and get back a fully captioned video in minutes. Perfect for content creators, educators, social media managers, and anyone who needs accessible, multilingual, or searchable video content without touching a paid tool.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to add captions to your video for free? Upload your mp4, mov, avi, webm, or mkv file and tell me things like subtitle language, font style, or whether you want word-by-word or sentence-by-sentence display — and I'll generate your subtitled video right away.

**Try saying:**
- "Add English subtitles to this mp4 interview video with white text and a dark background bar for readability"
- "Generate auto subtitles for my Spanish tutorial video and display them sentence by sentence at the bottom of the screen"
- "Transcribe and burn captions onto this webinar recording — keep the font large enough for mobile viewers"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Captions for Every Video, Completely Free

Getting subtitles onto a video used to mean paying for transcription services, wrestling with clunky desktop software, or spending hours typing captions by hand. The auto-subtitle-generator-free skill changes that entirely. Upload your video, and the skill listens to every word spoken, converts it to timed text, and overlays clean, readable subtitles directly onto your footage.

Whether you're posting a tutorial on YouTube, sharing a product demo on LinkedIn, or making a classroom lecture accessible to hearing-impaired students, subtitles make your content reach further. Studies consistently show that captioned videos hold viewer attention longer and perform better on social platforms — and now you can achieve that without spending anything.

This skill supports a wide range of video formats including mp4, mov, avi, webm, and mkv, so you don't need to convert your files before uploading. The result is a polished, subtitle-ready video you can share immediately. No technical setup, no learning curve — just upload, describe your preferences, and let the skill do the work.

## Caption Request Routing Explained

When you submit a video for auto-captioning, ClawHub parses your input — whether it's a raw video URL, an uploaded file reference, or a transcription task — and routes it directly to the NemoVideo subtitle engine based on detected media type and language parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference Notes

The NemoVideo backend handles speech-to-text transcription, subtitle timing alignment, and SRT/VTT file generation automatically — no manual timestamp editing required. Free-tier requests are processed through the same ASR pipeline as paid plans, with standard queue priority and a per-session credit allocation.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `auto-subtitle-generator-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=auto-subtitle-generator-free&skill_version=1.0.0&skill_source=<platform>`

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

## Use Cases for Auto Subtitle Generator Free

Social media creators on TikTok, Instagram Reels, and YouTube Shorts benefit enormously from auto subtitles because most mobile users watch videos on mute. Captioning a 60-second clip takes seconds with this skill, and the result immediately boosts watch time and engagement without any extra editing.

Educators and e-learning developers can use this skill to make lecture recordings, how-to videos, and course content compliant with accessibility standards like WCAG and ADA. Students who are deaf, hard of hearing, or learning in a second language get a far better experience when every word is visible on screen.

Businesses producing product demos, onboarding videos, or customer testimonials can caption their content for international audiences by requesting subtitle output in a target language. Marketing teams repurposing webinar recordings into short highlight clips will find this skill especially useful for turning raw footage into polished, shareable assets — all without a paid captioning subscription.

## Troubleshooting Common Subtitle Issues

If your generated subtitles appear out of sync with the audio, it usually means the video has a variable frame rate or a long silent intro. Try trimming any dead air from the beginning of your clip before uploading, or mention the approximate start time of the first spoken word in your prompt.

Muffled audio, heavy background music, or strong accents can sometimes cause missed words or awkward line breaks. To improve accuracy, describe the audio quality in your prompt — for example, 'the speaker has a strong Scottish accent' or 'there is background music throughout.' This helps the skill tune its transcription approach.

If subtitles are cut off at the screen edges, request a specific safe-zone margin in your prompt, such as 'keep subtitles within 10% of the screen border.' For videos with multiple speakers, ask for speaker-labeled captions so viewers can follow who is saying what without confusion.
