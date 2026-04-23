---
name: image-to-video-free-ai
version: "1.0.0"
displayName: "Image to Video Free AI — Animate Still Photos Into Stunning Videos Instantly"
description: >
  Drop a still photo and watch it come alive — image-to-video-free-ai transforms static images into smooth, dynamic video clips without any cost or complex setup. Whether you're a content creator, marketer, or hobbyist, this skill breathes motion into portraits, landscapes, product shots, and more. Powered by cutting-edge generative AI, it produces lifelike animations with natural movement, cinematic panning, and scene-aware transitions — all from a single image.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome! I can turn your still photos into dynamic, animated video clips using free AI — no cost, no complicated tools. Share your image and tell me what kind of motion or mood you're going for, and let's bring it to life!

**Try saying:**
- "Here's a photo of a mountain lake at sunset — can you animate it with gentle water ripples and slow drifting clouds?"
- "I have a product photo of my skincare bottle. Make it into a short video with a slow zoom-in and soft light shimmer effect."
- "Animate this portrait of my dog so it looks like he's subtly turning his head and blinking."

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Turn Any Photo Into a Moving Masterpiece

Still images tell a story, but video makes people feel it. This skill takes your photos — whether they're portraits, travel snapshots, product images, or digital artwork — and generates fluid, eye-catching video clips that look like they were filmed, not fabricated.

Using free AI-powered animation technology, the skill analyzes the content of your image and applies intelligent motion: a gentle breeze through hair, clouds drifting across a skyline, water rippling on a lake surface, or a subtle zoom that gives your product photo a professional commercial feel. You describe the motion you want, and the AI handles the rest.

This is ideal for social media creators who want to stand out on Instagram Reels or TikTok, small business owners who need affordable promotional content, and anyone who wants to repurpose their photo library into engaging video content — no video editing experience required.

## Routing Your Animation Requests

When you submit a still photo, your request is parsed for motion parameters — frame interpolation style, duration, and animation intensity — then dispatched to the appropriate image-to-video pipeline based on your selected output resolution and generation mode.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All image-to-video synthesis runs on a distributed cloud backend that handles diffusion-based frame generation, temporal consistency smoothing, and MP4 encoding without any local compute required on your end. API calls are stateless and authenticated per session, so each animation job is queued, processed, and returned as a signed video URL within the response payload.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `image-to-video-free-ai`
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

## Best Practices

For the best animation results, start with a high-resolution image — blurry or heavily compressed photos tend to produce less convincing motion. Images with clear foreground and background separation (like a subject against an open sky or landscape) animate most naturally because the AI can apply parallax-style depth movement.

Be specific in your motion description. Instead of saying 'make it move,' try 'add a slow leftward pan with a subtle zoom-in on the subject's face.' The more directional detail you provide, the more precisely the output matches your vision.

Avoid images with dense, overlapping text or complex geometric patterns — these can distort when motion is applied. Portraits work best when the subject is centered and well-lit. Finally, if you're planning to use the clip on social media, mention your target platform so the output can be framed and paced appropriately for that format.

## Use Cases

Image-to-video-free-ai serves a surprisingly wide range of real-world needs. Social media managers use it to transform static brand assets into scroll-stopping Reels and TikToks without a video production budget. Wedding photographers offer animated highlight previews to clients by turning a few key photos into short cinematic clips.

E-commerce businesses animate product photos to simulate a 360-degree-style view or spotlight key features with motion — dramatically increasing engagement compared to static listings. Educators and presenters use animated images to make slideshows and explainer content feel more dynamic without filming new footage.

Memorial and tribute creators use the skill to gently animate old family photos, giving cherished memories a new dimension. Digital artists animate their illustrations to share on platforms that favor video content over static posts.

## Common Workflows

Most users start by uploading a single image and describing the type of motion they want — this is the fastest path to a finished video clip. For portraits, common requests include subtle head tilts, eye blinks, or hair movement. For landscapes, users typically ask for parallax depth effects, moving clouds, or flowing water.

Another popular workflow is batch animation: uploading multiple product or travel photos and generating a series of short clips that can be stitched together into a slideshow-style video. This is especially useful for e-commerce sellers and travel bloggers.

For social media creators, a third workflow involves starting with AI-generated motion and then layering on captions or music using a separate editing tool — using this skill purely for the animation step before final production polish.
