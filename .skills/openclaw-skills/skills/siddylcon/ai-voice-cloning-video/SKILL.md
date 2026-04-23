---
name: ai-voice-cloning-video
version: "1.0.0"
displayName: "AI Voice Cloning for Video — Clone Any Voice and Sync It to Your Footage"
description: >
  Tired of re-recording voiceovers every time your script changes, or losing a project because your original speaker is unavailable? ai-voice-cloning-video lets you clone a voice from a short audio sample and apply it directly to your video content — synced, natural-sounding, and ready to publish. Ideal for content creators, educators, marketers, and video producers who need consistent narration without repeated recording sessions.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a voice sample and your video script, and I'll clone that voice and sync it to your footage. No sample yet? Just describe the voice style and content you want.

**Try saying:**
- "I have a 10-second audio clip of my narrator — clone that voice and apply it to this 2-minute product demo script"
- "My original voiceover artist is unavailable. Use this old recording of theirs to re-narrate my updated training video script"
- "Clone my own voice from this sample and generate a Spanish-language version of my YouTube intro using the same tone"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Clone Any Voice, Drop It Into Your Video

Recording voiceovers is one of the most time-consuming parts of video production. A single script change means booking studio time, coordinating with talent, or settling for inconsistent audio quality across your project. AI Voice Cloning for Video breaks that cycle entirely.

This skill lets you take a voice sample — even just a few seconds of clean audio — and generate a cloned version that can narrate any script you provide. The result gets mapped to your video timeline, so your footage and voice stay in sync without manual editing gymnastics.

Whether you're producing YouTube tutorials, corporate training videos, social media ads, or multilingual content, this tool gives you a consistent, repeatable voice that you control. Update your script, regenerate the audio, and your video stays current — without ever touching a microphone again.

## Routing Clone and Sync Requests

When you submit a voice cloning or lip-sync request, the skill parses your intent and routes it to the appropriate pipeline — whether that's voice sample ingestion, neural voice model training, or frame-accurate audio-to-video synchronization.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud API Reference Guide

All voice cloning and sync operations run through a distributed cloud backend that handles speaker embedding extraction, mel-spectrogram synthesis, and phoneme-to-viseme alignment at scale. Trained voice models are stored as lightweight speaker embeddings, allowing rapid inference without re-uploading your reference audio on each session.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-voice-cloning-video`
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

## Use Cases

AI Voice Cloning for Video fits naturally into several real production workflows. Content creators who publish regularly can clone their own voice once and use it to narrate videos during periods when they're sick, traveling, or simply short on time — maintaining a consistent channel identity without gaps in output.

Corporate and e-learning teams benefit from being able to update training videos without rehiring voice talent every quarter. Clone the original narrator once, then regenerate only the sections that changed — keeping the full video feeling cohesive.

Multilingual video producers use voice cloning to preserve a speaker's unique vocal identity across language versions. Rather than hiring a different actor for each language, the cloned voice can deliver translated scripts while retaining the original speaker's tone and cadence.

Advertising and marketing teams can also use this skill to rapidly prototype video ads with a consistent brand voice before committing to a full professional recording session — saving both time and budget in the early creative stages.

## Performance Notes

Voice clone quality depends heavily on the input sample you provide. For best results, use a clean audio clip of at least 5–15 seconds with minimal background noise, reverb, or music bleed. Samples recorded in a quiet room or with a decent microphone will produce noticeably more natural output than phone recordings or clips pulled from noisy environments.

Longer source samples (30 seconds or more) allow the cloning model to capture more tonal nuance, breath patterns, and speaking rhythm — which matters especially for longer video narrations. Short, punchy scripts tolerate shorter samples better than documentary-style content with varied pacing.

Script formatting also affects sync accuracy. Providing clean, punctuated text — broken into natural spoken phrases rather than walls of text — helps the system time pauses and emphasis correctly against your video timeline. If your video has existing music or sound effects underneath the narration, factor that into your script pacing before submission.
