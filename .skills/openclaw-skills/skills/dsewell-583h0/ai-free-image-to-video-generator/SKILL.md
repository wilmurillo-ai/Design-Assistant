---
name: ai-free-image-to-video-generator
version: "1.0.0"
displayName: "AI Free Image to Video Generator — Animate Still Photos Into Dynamic Videos"
description: >
  Turn static images into captivating video clips without spending a dime using the ai-free-image-to-video-generator. Upload any still photo and watch it come alive with smooth motion, cinematic effects, and natural transitions. Ideal for content creators, small business owners, and social media marketers who need eye-catching video content fast. No subscriptions, no watermarks, no technical headaches — just results.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! Ready to turn your still photos into stunning videos? With the AI Free Image to Video Generator, you can animate any image in seconds — just upload your photo and tell me the style or motion you want to bring it to life with.

**Try saying:**
- "Animate this product photo with a slow zoom-in and soft bokeh blur for an Instagram ad"
- "Turn my landscape photograph into a cinematic video clip with a gentle parallax sky movement"
- "Convert this portrait image into a short looping video with a subtle breathing motion effect"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/ai-free-image-to-video-generator/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# From Frozen Moments to Moving Stories

Still images tell a story, but video makes people stop scrolling. The AI Free Image to Video Generator bridges that gap by transforming your photos into fluid, engaging video clips that feel professionally produced — without the production budget or software expertise.

Whether you're working with product photos, travel snapshots, portraits, or illustrations, this skill breathes life into them using intelligent motion synthesis. It analyzes the visual composition of your image and applies realistic movement — subtle camera pans, zoom effects, parallax depth, or ambient animation — tailored to the content of the photo itself.

This tool is built for creators who move fast. Social media managers can repurpose existing photo libraries into video posts. E-commerce brands can animate product shots for ads. Bloggers and journalists can turn article images into shareable reels. No prior video editing experience is required — just bring your image and describe the vibe you're going for.

## Routing Your Animation Requests

When you submit a still image for animation, your request is parsed for motion parameters, style directives, and frame duration before being dispatched to the appropriate image-to-video inference pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All image-to-video synthesis runs on a distributed cloud backend that handles frame interpolation, temporal coherence, and motion diffusion processing without consuming your local compute. Rendered video outputs are returned as streamable URLs tied to your active session token.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-free-image-to-video-generator`
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

To get the best results from the AI Free Image to Video Generator, start with high-resolution images — at least 1080px on the shortest side. Blurry or heavily compressed photos limit the quality of motion synthesis and can produce artifacts around edges.

When describing the motion you want, be specific. Instead of saying 'make it move,' try 'slow pan from left to right with a slight zoom toward the center subject.' The more directional detail you provide, the more precisely the output will match your vision.

For looping content like Instagram Reels or TikTok posts, request a 'seamless loop' in your prompt so the animation cycles smoothly without a jarring cut. Images with natural depth — foreground objects, midground subjects, and background scenery — tend to produce the most impressive parallax and 3D motion effects.

## Performance Notes

The AI Free Image to Video Generator processes most standard images within 15 to 45 seconds depending on resolution and the complexity of the requested motion. Highly detailed images with intricate textures or dense backgrounds may take slightly longer as the model maps motion vectors across more visual data.

Output videos are typically delivered in MP4 format at up to 1080p resolution, making them immediately ready for upload to major platforms including YouTube, Instagram, TikTok, and LinkedIn. For best playback performance, avoid requesting motion effects that conflict with the image's natural geometry — for example, applying a dramatic forward push-in to a flat, textureless background may produce visible distortion.

If your first result doesn't fully match your expectations, refining your motion description with additional keywords like 'gentle,' 'dramatic,' 'slow,' or 'fluid' in a follow-up prompt often produces a noticeably improved output.

## Integration Guide

The AI Free Image to Video Generator fits naturally into existing creative workflows. If you manage content for multiple platforms, batch your image uploads by campaign or theme and process them sequentially with consistent motion style prompts to maintain a cohesive visual identity across all your video outputs.

For e-commerce use cases, pair this skill with your product photography pipeline. After a photo shoot, run hero images through the generator to create animated variants for paid social ads — animated ads consistently outperform static images in click-through rates without requiring a full video production shoot.

Content teams using scheduling tools like Buffer or Later can generate videos here and download them directly for upload into their queues. For bloggers and newsletter creators, animated image clips embedded in email campaigns or blog headers dramatically increase time-on-page and engagement metrics compared to static visuals alone.
