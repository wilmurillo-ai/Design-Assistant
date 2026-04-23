---
name: google-ai
version: "1.0.0"
displayName: "Google AI Video Analyzer — Smart Insights Powered by Gemini Intelligence"
description: >
  Tired of scrubbing through hours of footage trying to extract meaning, summaries, or actionable data from your videos? The google-ai skill brings Google's Gemini-powered intelligence directly into your video workflow. Automatically generate transcripts, identify key moments, summarize content, and ask natural language questions about any video. Perfect for content creators, researchers, educators, and business teams. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🧠", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your Google AI-powered video analyst — ready to watch, understand, and break down your video content so you don't have to. Upload a video and tell me what you'd like to know — let's get started!

**Try saying:**
- "Summarize the main points discussed in this recorded team meeting"
- "Identify all the key moments and timestamps where the speaker changes topic"
- "Transcribe this video and highlight any action items or decisions mentioned"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Let Google AI Do the Heavy Lifting on Video

Video content is rich with information — but unlocking that information has always required manual effort, expensive tools, or hours of your time. The google-ai skill changes that by putting the full analytical power of Google's Gemini models to work on your video files directly inside ClawHub.

Whether you're a researcher reviewing recorded interviews, a marketer analyzing product demo videos, or a teacher breaking down lecture recordings, this skill gives you an intelligent assistant that actually watches and understands your video. Ask it to summarize what happened, identify who spoke and when, pull out key quotes, or describe the visual content scene by scene.

This isn't a generic transcription tool. Google AI understands context, tone, visual elements, and narrative structure — so the insights you get back are genuinely useful, not just raw text dumps. Upload your video, ask your question, and get a response that saves you real time.

## Gemini Intent Routing Logic

Every natural language request is parsed through Gemini's intent classification layer, which maps your query to the appropriate multimodal analysis action — whether that's scene detection, object recognition, transcript generation, or contextual summarization.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend serves as the inference bridge between ClawHub and Google's Gemini Vision models, handling video chunking, frame sampling, and prompt orchestration under the hood. API calls are stateful within a session window, meaning context from earlier queries informs subsequent Gemini responses without re-uploading your source file.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `google-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=google-ai&skill_version=1.0.0&skill_source=<platform>`

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

## Integration Guide

The google-ai skill connects your video files to Google's Gemini multimodal models, enabling deep video understanding without any manual configuration on your end. Once activated in ClawHub, the skill automatically handles video ingestion, frame analysis, and audio processing behind the scenes.

This skill works seamlessly alongside other ClawHub skills — for example, you can pair it with a summarization or export skill to turn AI-generated video insights into formatted reports or shareable documents. It supports all major video formats including mp4, mov, avi, webm, and mkv, so there's no need to convert your files before uploading.

For teams and organizations, the google-ai skill scales naturally across multiple video files in a session, making it ideal for batch analysis workflows like reviewing a series of customer interviews or processing a library of training videos.

## Quick Start Guide

Getting started with the google-ai skill takes less than a minute. Open a new ClawHub session and select the google-ai skill from your skill library. Once active, simply upload your video file — mp4, mov, avi, webm, and mkv are all supported — and type your first question or request in plain language.

Not sure what to ask? Start simple: try 'Summarize this video in three sentences' or 'What are the main topics covered?' From there, you can drill deeper — ask for timestamps, request a full transcript, or have the AI describe specific visual scenes.

Results are returned in conversational text, making them easy to copy, share, or build on with follow-up questions. There's no special syntax or formatting required — just talk to it like you would a knowledgeable colleague who just watched your video.

## Best Practices

To get the most accurate and useful results from the google-ai skill, keep a few things in mind. Clear audio significantly improves the quality of transcription and spoken content analysis — if your video has background noise, the AI will still perform well, but crisp audio yields sharper outputs.

Be specific in your prompts. Instead of asking 'What's in this video?', try 'List the three most important arguments made by the presenter' or 'Identify any product names or brands mentioned.' The more targeted your question, the more precise the Google AI response will be.

For longer videos — anything over 20 minutes — consider breaking your analysis into focused segments. Ask about the first half, then the second, or focus on specific themes per prompt. This keeps responses concise and highly relevant rather than broadly summarized. Finally, use follow-up questions to refine or expand on any initial answer — the skill maintains context throughout your session.
