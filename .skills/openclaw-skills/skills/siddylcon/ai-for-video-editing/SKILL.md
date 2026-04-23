---
name: ai-for-video-editing
version: "1.0.0"
displayName: "AI for Video Editing — Smarter Cuts, Captions, and Creative Direction"
description: >
  Turn raw footage into polished, publish-ready video with the power of ai-for-video-editing built into your workflow. This skill helps video creators plan edit sequences, write scene descriptions, generate b-roll suggestions, craft compelling captions, and brainstorm pacing strategies — all through conversation. Whether you're a solo content creator, a social media manager, or a post-production professional, this skill accelerates every stage of your editing process without touching a timeline.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm here to help you take your video editing to the next level using AI — from planning your cut sequence to writing captions and generating b-roll ideas. Tell me about your project and let's start building something great together.

**Try saying:**
- "I have a 10-minute interview video. Suggest an edit structure that keeps viewers engaged and where I should cut for pacing."
- "Write 5 caption options for a 30-second product demo video aimed at Instagram Reels — upbeat, punchy tone."
- "I'm editing a travel vlog set in Tokyo. What b-roll shots should I look for in my footage to make transitions feel cinematic?"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Edit Smarter: Your AI Co-Editor Is Ready

Most video editors don't have a shortage of footage — they have a shortage of time and creative clarity. This skill is built specifically to help you move faster from raw clips to a finished cut by acting as a knowledgeable creative partner at every decision point.

With ai-for-video-editing, you can describe your footage and get back a suggested edit structure, ask for caption ideas that match your video's tone, or request b-roll concepts that would strengthen a particular scene. You can even paste a rough script and get pacing notes, transition suggestions, or a breakdown of where to cut for maximum impact.

This skill is especially useful during the planning phase — before you even open your editing software — and during the review phase, when you need a second perspective on whether a sequence is landing the way you intended. Think of it as having an experienced editor in the room who's always available, never tired, and full of ideas.

## Routing Cuts and Caption Requests

When you submit a prompt — whether it's a rough cut instruction, an auto-caption request, or a creative direction note — ClawHub parses the intent and routes it to the appropriate AI processing pipeline for timeline editing, transcription, or style generation.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

Video processing calls are handled by a distributed cloud backend that runs frame analysis, speech-to-text transcription, and generative cut suggestions asynchronously — so heavy renders don't block your session. Large files are chunked and processed in parallel before the edited timeline or caption track is returned to your workspace.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-for-video-editing`
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

To get the most out of ai-for-video-editing, treat the skill like a creative collaborator rather than a search engine. Instead of asking broad questions like 'how do I edit better,' describe a specific problem: 'My talking-head interview feels slow around the 2-minute mark — what editing techniques can tighten it up?'

Use the skill iteratively. Start with a high-level edit plan, then zoom into individual scenes. Ask for three different pacing approaches and compare them before committing. If you're writing captions, request multiple tone variations — one formal, one casual, one punchy — so you have real options to choose from.

Another powerful use: paste in your video script or a rough transcript and ask the skill to flag natural cut points, suggest where graphics or text overlays would add clarity, or identify moments where a cutaway would improve the flow. This works especially well for educational content, explainer videos, and documentary-style edits where structure is everything.

## Quick Start Guide

Getting started with this skill is straightforward — just describe your video project in plain language. You don't need to upload files or share technical specs. Start by telling the skill what type of video you're editing (tutorial, vlog, ad, documentary, short film), who your audience is, and what platform it's destined for.

From there, you can ask for a suggested edit order if you have a list of clips, request caption or subtitle copy, brainstorm a hook for your opening sequence, or get feedback on a rough cut description you paste in. The more context you give — tone, length, goal, audience — the more tailored and useful the output will be.

A good first prompt might be: 'I'm editing a 60-second brand video for a coffee shop. The footage includes barista close-ups, latte art, and customer reactions. What edit structure would work best?' From that starting point, you can drill down into transitions, music mood, caption style, and more.
