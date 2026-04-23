---
name: free-ai-text-to-video-generator
version: "1.0.0"
displayName: "Free AI Text to Video Generator — Turn Words Into Stunning Videos Instantly"
description: >
  Type a scene, a story, or a script — and watch it become a video in seconds. This free-ai-text-to-video-generator takes your written ideas and transforms them into engaging visual content without any design skills, software downloads, or budget. Perfect for marketers, educators, content creators, and small business owners who need professional-looking videos fast. Write your concept, pick a style, and get a shareable video ready to post.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome! You're one text prompt away from a finished video — just describe your scene, topic, or story and this free AI text to video generator will bring it to life. Ready to create your first video? Type your idea below and let's get started.

**Try saying:**
- "Generate a 30-second promotional video for a handmade candle brand using warm, cozy visuals and soft background music"
- "Create an animated explainer video showing how a water filtration system works, written for a general audience"
- "Turn this blog post intro into a short social media video with bold text overlays and upbeat pacing: 'Five habits that changed my mornings forever...'"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# From Plain Text to Polished Video — No Camera Needed

Most people have ideas worth sharing but lack the time, budget, or technical skills to produce video content. That's exactly the gap this skill was built to close. By simply describing what you want — a product showcase, an explainer clip, a social media reel, or an animated story — you get a fully rendered video without touching a single editing tool.

The free AI text to video generator interprets your written prompt and assembles visuals, motion, and pacing that match your intent. Whether you're describing a futuristic cityscape, a step-by-step tutorial, or a heartfelt brand message, the output reflects your words with surprising accuracy and creative flair.

This is especially useful for teams running lean operations, solo creators building a content library, or educators who need visual aids without a production budget. You write, the AI builds — it's that straightforward. No storyboard, no stock footage hunting, no rendering queues to manage manually.

## Prompt Routing and Video Dispatch

When you submit a text prompt, ClawHub parses your generation request and routes it to the optimal AI video synthesis engine based on prompt complexity, style tags, and current model availability.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

The free AI text to video generator runs on a distributed cloud rendering backend that queues your prompt, tokenizes scene descriptions, and streams back rendered frames via asynchronous API calls. Diffusion model inference and frame interpolation happen server-side, so no local GPU is required.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-ai-text-to-video-generator`
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

## Performance Notes

Video quality and accuracy improve significantly when your text prompt includes specific details. Vague prompts like 'make a video about nature' produce generic results, while prompts like 'a slow-motion aerial shot of a pine forest at golden hour with ambient wind sounds' give the generator clear creative direction.

For best results, specify the intended platform (YouTube, Instagram, LinkedIn), the desired length, the visual tone (cinematic, minimalist, bold), and any text overlays or voiceover style you want included. The more context you provide, the closer the output matches your vision.

Processing time varies based on video length and complexity. Short clips under 30 seconds typically generate faster than multi-scene productions. If you're generating multiple videos in a session, spacing out requests helps maintain consistent output quality across all of them.

## Common Workflows

The most popular use case is social media content creation — users paste a caption or short script and request a vertical video formatted for Instagram Reels or TikTok. The generator handles aspect ratio, pacing, and visual style based on the tone of the text.

Another frequent workflow is educational content. Teachers and course creators describe a concept — like 'explain photosynthesis for 10-year-olds with colorful animations' — and receive a structured explainer video ready to embed in a lesson.

Small business owners often use it for product launches. Instead of hiring a videographer, they write a product description with key selling points and request a 60-second showcase video. The result can be posted directly to e-commerce pages or ad platforms.

For longer-form needs, users break their content into scenes — describing each one separately — then request them stitched into a single narrative video. This scene-by-scene approach gives more creative control over the final output.
