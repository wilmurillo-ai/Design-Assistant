---
name: gemini-video-editor
version: "1.0.0"
displayName: "Gemini Video Editor — AI-Powered Editing, Captions & Smart Scene Analysis"
description: >
  Turn raw footage into polished, publish-ready videos using the gemini-video-editor skill. Powered by Google Gemini's multimodal intelligence, this skill analyzes video content, generates scene descriptions, writes captions, suggests cuts, and crafts scripts aligned with your footage. Ideal for content creators, marketers, and filmmakers who want faster edits without sacrificing quality.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a video link or describe your footage and I'll generate scene breakdowns, captions, cut suggestions, or a full script. No video yet? Just describe what you're editing and what you need.

**Try saying:**
- "Analyze this YouTube video and suggest where I should cut it down to a 60-second highlight reel for Instagram."
- "Generate accurate subtitles and a chapter breakdown for this 20-minute tutorial video."
- "Write a voiceover script that matches the pacing and tone of this product demo footage."

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Edit Smarter: Let Gemini Read Your Footage

Most video editing tools make you do all the thinking — scrubbing timelines, writing captions from scratch, and guessing where to cut. The gemini-video-editor skill flips that model. By leveraging Google Gemini's ability to actually understand what's happening inside a video, it gives you intelligent suggestions based on real content, not just metadata.

Upload a clip or share a video URL and the skill gets to work: identifying key moments, describing scenes, generating subtitle text, proposing a narrative structure, or even drafting a voiceover script that matches the pacing of your footage. Whether you're repurposing a long-form interview into social snippets or building a product demo from raw screen recordings, this skill compresses hours of manual work into minutes.

This is especially useful for solo creators and small teams who wear many hats. You don't need a dedicated editor or a copywriter — Gemini handles the analysis, and you stay in creative control of the final decisions.

## Routing Edits Through Gemini

Every request — whether you're triggering auto-captions, running smart scene detection, or applying AI-driven cuts — gets parsed by Gemini's intent engine and dispatched to the appropriate processing pipeline based on your prompt context and timeline state.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

Gemini Video Editor offloads all heavy lifting — frame analysis, multimodal scene tagging, caption generation, and render jobs — to Google's Gemini cloud backend, meaning your local machine stays responsive even on long-form footage. API calls are authenticated per session and tied to your project token, so each timeline operation stays scoped and stateless.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `gemini-video-editor`
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

## Integration Guide

To get the most out of the gemini-video-editor skill, start by sharing your video in one of two ways: paste a publicly accessible video URL (YouTube, Vimeo, direct MP4 links) or describe your video content in detail if you can't share the file directly. The skill uses Google Gemini's multimodal capabilities to process visual and audio context from the footage.

For best results, specify your output goal upfront. Tell the skill whether you need captions, a script, scene timestamps, a social media cut list, or a full narrative breakdown. The more context you give — target platform, audience, desired tone, video length — the more precise and usable the output will be.

If you're working inside a content pipeline, you can chain outputs: first request a scene analysis, then use those scene labels to ask for a structured script, then request platform-specific caption variations. The gemini-video-editor skill is designed to work iteratively, so don't hesitate to refine and build on each response.

## Best Practices

When using the gemini-video-editor skill, specificity is your biggest advantage. Instead of asking for 'a summary,' ask for 'a 3-sentence summary written for a LinkedIn audience with a professional but approachable tone.' Gemini performs significantly better when it knows the context, format, and purpose of your output.

For subtitle and caption generation, always specify whether you want verbatim transcription or cleaned-up, edited captions. Raw interview footage often contains filler words and false starts that need to be trimmed in the final caption pass — telling the skill which style you need saves you editing time downstream.

If you're working on a series of videos with consistent branding, paste in a brief style guide or example script at the start of your session. This anchors the skill's tone and vocabulary to your brand voice, making outputs across multiple videos feel cohesive without extra prompting each time.
