---
name: motion-graphics-video
version: "1.0.0"
displayName: "Motion Graphics Video Creator — Animate Ideas Into Stunning Visual Stories"
description: >
  Transform static concepts into captivating motion-graphics-video content that grabs attention and holds it. This skill helps creators, marketers, and video producers craft animated titles, kinetic typography, logo reveals, lower thirds, and dynamic visual overlays — all guided by AI. Whether you're producing social media reels, explainer videos, or brand content, get polished motion graphics output without a steep learning curve.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your video concept, script, or rough idea and I'll map out a full motion graphics video plan for you. No footage yet? Just describe the vibe, audience, and message you want to hit.

**Try saying:**
- "Create a kinetic typography intro for my YouTube channel that shows my brand name animating in with a neon glow effect over a dark background"
- "I need a 15-second motion graphics video for Instagram that announces a product launch — include animated stats, a logo reveal, and a call-to-action at the end"
- "Design a storyboard and animation guide for an explainer video showing how our SaaS onboarding process works in 60 seconds"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Bring Your Videos to Life With Motion

Static visuals don't cut through the noise anymore. Motion graphics video combines animation, typography, and design to create content that feels alive — whether that's a product launch reel, an animated infographic, or a branded intro sequence that plays before every YouTube upload.

This skill is built specifically for people who want professional-grade motion graphics without spending weeks in After Effects or hiring a dedicated motion designer. Describe what you need — a kinetic text animation, a smooth logo sting, a data visualization that animates on screen — and get actionable creative direction, script-ready storyboards, and layer-by-layer guidance to produce it.

From social media creators who need eye-catching Instagram stories to corporate teams building presentation videos, this tool adapts to your project's tone, pacing, and brand identity. Think of it as a motion design collaborator that speaks your language and helps you ship faster.

## Routing Your Animation Requests

Each request you submit — whether it's a kinetic typography sequence, an animated infographic, or a full explainer video — gets parsed for style, duration, and motion parameters before being dispatched to the appropriate rendering pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render API Reference

Motion graphics processing runs through a distributed cloud backend that handles keyframe interpolation, asset compositing, and export encoding in parallel — keeping render times fast even for complex multi-layer timelines. All vector assets, easing curves, and color grading instructions are processed server-side, so your local machine stays free.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `motion-graphics-video`
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

## Use Cases for Motion Graphics Video

**Social Media Content Creators:** Produce scroll-stopping Reels, TikToks, and YouTube Shorts with animated text overlays, transition effects, and branded lower thirds that make your content look professionally produced.

**Marketing & Advertising Teams:** Build motion graphics video assets for product launches, campaign announcements, and paid ads. Animated visuals consistently outperform static images in click-through rates — this skill helps you produce them faster.

**Educators & Course Creators:** Turn complex topics into animated explainer videos with on-screen text, illustrated transitions, and visual metaphors that make learning stick. Great for online courses, webinars, and tutorial content.

**Startup Founders & Brand Builders:** Create a polished brand identity through animated logos, intro sequences, and pitch deck videos that communicate professionalism without a full production budget. Motion graphics video is one of the highest-ROI investments in early brand building.

## Frequently Asked Questions

**Do I need video editing software to use this skill?**
Not to get started. This skill generates creative direction, animation scripts, layer breakdowns, and storyboards you can take into tools like After Effects, CapCut, Canva, or DaVinci Resolve. It bridges the gap between idea and execution.

**What types of motion graphics video can I create?**
You can work on logo animations, lower thirds, title sequences, animated social media posts, explainer videos, data visualizations, kinetic typography, and full branded video intros or outros.

**Can this help me if I'm not a designer?**
Absolutely. The skill is designed for marketers, content creators, and entrepreneurs who want motion graphics results without a design background. It explains every step in plain language and adapts to your skill level.

**What if I already have footage and just need graphics overlaid?**
Share your footage description or timeline and this skill will recommend exactly which motion graphic elements to add, where to place them, and how to style them to match your existing content.
