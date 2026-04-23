---
name: text-to-image-ai
version: "1.0.0"
displayName: "Text-to-Image AI — Generate Stunning Visuals From Any Description"
description: >
  Tell me what you need and I'll turn your words into vivid, detailed images instantly. This text-to-image-ai skill transforms plain-language descriptions into custom visuals — from photorealistic scenes to stylized illustrations, concept art, and product mockups. Designed for creators, marketers, designers, and storytellers who need original imagery fast. Supports mp4/mov/avi/webm/mkv for video-based generation workflows.
metadata: {"openclaw": {"emoji": "🎨", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to turn your descriptions into beautiful, custom-generated images using text-to-image-ai. Tell me what you'd like to visualize — be as detailed or as open-ended as you like — and let's create something together.

**Try saying:**
- "Generate a photorealistic image of a cozy coffee shop interior on a rainy afternoon with warm lighting and wooden furniture"
- "Create an illustration in a vintage travel poster style showing the coastline of Amalfi, Italy at sunset"
- "Make a futuristic product mockup of a sleek smartwatch with a dark matte finish on a clean white background"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# From Words on a Page to Images That Speak

Describing what you want to see has never been enough — until now. The text-to-image-ai skill on ClawHub takes your written prompts and transforms them into fully realized visuals, no design software or artistic background required. Whether you're building a brand campaign, drafting a storyboard, or just trying to visualize an idea that's been living in your head, this skill bridges the gap between imagination and output.

You can go broad or incredibly specific. Describe a misty mountain village at dawn, a futuristic city skyline in neon tones, or a minimalist logo concept — and receive a generated image that reflects your intent. The skill is built to interpret natural language, so you don't need to learn prompt engineering jargon to get great results.

This is a practical tool for content creators producing social media visuals, product teams exploring design directions, writers building visual references for their stories, and anyone who needs original imagery without the cost and time of a traditional creative process.

## Prompt Routing and Model Dispatch

Every natural-language prompt you submit is parsed for style tokens, aspect ratio hints, and subject descriptors before being dispatched to the optimal diffusion pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles inference through a queued diffusion engine that processes your prompt, negative prompt, and sampling parameters — including steps, CFG scale, and seed — to return a high-resolution image URL. Latency varies based on model load and resolution tier selected.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `text-to-image-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=text-to-image-ai&skill_version=1.0.0&skill_source=<platform>`

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

The text-to-image-ai skill fits naturally into creative and production workflows on ClawHub. You can chain it with other skills — for example, generating a base image and then passing it into a video animation skill to create motion content, or feeding the output into an upscaling skill for print-ready resolution.

For teams working on content calendars, the skill supports batch-style use: prepare a set of descriptive prompts in advance and run them sequentially to generate a full library of visuals in one session. This is particularly useful for social media managers who need consistent themed imagery across multiple posts.

If you're using this skill as part of a storyboarding or pre-production process, consider pairing your prompts with scene descriptions from a script. The skill can generate reference frames for each scene, giving directors and clients a visual language to react to before production begins. Output images can be saved and organized directly within your ClawHub workspace for easy access across projects.

## Best Practices

The quality of your output is directly tied to the quality of your prompt. Start with the subject, then layer in environment, lighting, style, and mood. A strong prompt structure might look like: '[Subject] in [setting], [time of day or lighting], [artistic style], [color palette], [camera angle].' This framework keeps your description organized and gives the model clear signals to work with.

For brand-consistent imagery, establish a style anchor in every prompt — such as 'flat design illustration' or 'cinematic photography' — so that a series of generated images shares a visual identity. This is especially valuable for marketing teams producing multiple assets for a single campaign.

Avoid overloading a single prompt with conflicting styles or too many competing subjects. If you want a complex scene, break it into layers: generate the background first, then generate foreground elements separately if needed. Keeping prompts focused on one primary visual idea tends to produce sharper, more intentional results than trying to describe everything at once.

## Troubleshooting

If your generated image doesn't match what you envisioned, the most common cause is an underspecified prompt. Vague descriptions like 'a nice landscape' give the model wide latitude, which can lead to generic results. Try adding details about lighting, mood, color palette, perspective, and style — for example, 'a foggy forest at dawn with soft golden light filtering through pine trees, painterly style.'

If the image contains unwanted elements, use negative phrasing in your prompt to signal what to exclude, such as 'no people, no text, no cars.' For outputs that feel off in composition or proportion, try specifying the framing directly — 'wide shot,' 'close-up portrait,' or 'bird's eye view' can dramatically change results.

Occasionally, certain abstract or highly conceptual prompts may produce inconsistent outputs across generations. In these cases, running the prompt two or three times and selecting the best result is a reliable workaround. If a prompt repeatedly fails to generate, simplify it to its core subject and build complexity back in gradually.
