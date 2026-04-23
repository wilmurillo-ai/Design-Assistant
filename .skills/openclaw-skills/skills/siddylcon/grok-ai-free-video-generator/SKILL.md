---
name: grok-ai-free-video-generator
version: "1.0.0"
displayName: "Grok AI Free Video Generator — Create Stunning Videos with Zero Cost"
description: >
  Turn your ideas into polished videos without spending a dime using the grok-ai-free-video-generator skill on ClawHub. This skill taps into Grok AI's generative capabilities to help you script, storyboard, and produce video content from plain text prompts. Whether you're a content creator, marketer, or educator, you get fast, coherent video concepts with scene descriptions, voiceover text, and visual direction — all free.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! You're using the Grok AI Free Video Generator — let's turn your ideas into compelling video content right now. Tell me your topic, target audience, or video goal and I'll build a complete video structure for you instantly.

**Try saying:**
- "Generate a 60-second promotional video script for a new coffee brand targeting young professionals"
- "Create a 3-scene educational video breakdown explaining how solar panels work for middle school students"
- "Write a YouTube intro video concept with scene descriptions and voiceover text for a travel vlog channel"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/grok-ai-free-video-generator/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Generate Real Videos From Ideas — Instantly and Free

Most video creation tools either cost a fortune or demand hours of editing experience. The Grok AI Free Video Generator skill changes that equation entirely. By combining the natural language intelligence of Grok AI with ClawHub's skill framework, this tool lets you describe what you want and receive structured, production-ready video content in seconds.

Whether you're producing a short social media clip, a product explainer, a YouTube intro, or an educational walkthrough, this skill helps you move from a blank page to a complete video blueprint without touching a timeline or paying for a subscription. You describe the tone, subject, and style — the skill handles the creative heavy lifting.

This is especially powerful for solo creators, small business owners, and teachers who need professional-quality video output on a tight budget. The skill generates scene-by-scene breakdowns, suggested visuals, narration scripts, and transition cues so you or any video tool can bring the vision to life immediately.

## Routing Your Video Prompts

When you submit a video generation request, ClawHub parses your natural language prompt and routes it directly to Grok's Aurora video synthesis engine, matching your intent to the appropriate resolution, duration, and style parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Aurora API Backend Reference

Grok's free video generation runs through xAI's Aurora diffusion model hosted on distributed cloud infrastructure, handling frame interpolation, temporal coherence, and prompt-to-video rendering server-side so your local device stays unburdened. Each API call packages your prompt tokens, aspect ratio preferences, and seed values before dispatching to the Aurora endpoint for asynchronous processing.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `grok-ai-free-video-generator`
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

## Use Cases for Grok AI Free Video Generator

The grok-ai-free-video-generator skill shines across a wide range of real-world video creation scenarios. Social media managers can use it to rapidly generate short-form video scripts for TikTok, Instagram Reels, or YouTube Shorts — complete with hooks, scene pacing, and call-to-action endings.

Small business owners who can't afford a production agency can describe their product or service and receive a full explainer video structure they can hand off to a freelancer or feed into a text-to-video tool. Educators and trainers benefit from the skill's ability to convert complex topics into digestible, scene-by-scene lesson videos with clear narration cues.

Content creators launching new channels can use it to batch-generate video ideas, outlines, and full scripts in one session — dramatically cutting pre-production time. Even podcast hosts can convert episode summaries into audiogram-style video scripts ready for publishing.

## Performance Notes

The grok-ai-free-video-generator skill performs best when you provide specific context in your prompt — including the intended platform (YouTube, TikTok, LinkedIn), video length, tone (professional, casual, humorous), and target audience. Vague prompts like 'make a video' will produce usable but generic output, while detailed prompts unlock highly tailored scene structures and scripts.

For longer videos (5+ minutes), consider breaking your request into segments — ask for the intro, middle sections, and outro separately to maintain coherence and detail across the full piece. The skill handles narrative flow well but benefits from clear topic boundaries on extended content.

Output from this skill is designed to be immediately usable in tools like Runway, Pictory, Synthesia, or even manual editing workflows. Scene descriptions follow a visual-first format so you can match them directly to stock footage libraries or AI image generators without additional reformatting.
