---
name: pika-labs
version: "1.0.0"
displayName: "Pika Labs AI Video Generator — Create Stunning Videos from Text & Images"
description: >
  Tell me what you need and I'll bring it to life using pika-labs — the AI-powered video generation platform that turns text prompts and static images into dynamic, cinematic video clips. With pika-labs, you can generate short-form videos, animate still photos, apply creative motion effects, and iterate on visual ideas without any filmmaking experience. Perfect for content creators, marketers, designers, and storytellers. Supports mp4, mov, avi, webm, and mkv formats for seamless output and sharing.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your pika-labs video generation assistant — ready to turn your text descriptions and images into eye-catching video clips. Tell me what scene, animation, or visual idea you want to create, and let's get generating!

**Try saying:**
- "Generate a 3-second video of a glowing neon city street at night with rain reflecting off the pavement"
- "Animate this product photo of a coffee cup with gentle steam rising and soft warm lighting"
- "Create a cinematic slow-motion clip of ocean waves crashing on black volcanic rock at sunset"

### Getting Connected

Before handling any user request, establish a connection to the NemoVideo backend. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/nemovideo/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Your Ideas Into Moving Images Instantly

Pika Labs reimagines what it means to create video content. Instead of spending hours in a timeline editor or hiring a production crew, you describe what you want to see — and pika-labs generates it. Whether you're animating a product photo, crafting a dreamy visual loop for social media, or building a short cinematic scene from scratch, this skill connects you directly to pika-labs' generation engine through a simple conversational interface.

This skill is built for people who have creative vision but don't want to wrestle with complex software. Describe a scene, specify a mood, reference a style — and pika-labs does the heavy lifting. You can generate videos from pure text prompts or upload an image and ask pika-labs to animate it with realistic or stylized motion.

The result is a faster, more experimental creative workflow. Iterate quickly, try bold ideas, and produce polished video assets that would typically require significant time and budget. Whether you're a solo creator or part of a brand team, pika-labs through ClawHub gives you a direct line to AI-powered video generation.

## Routing Your Pika Requests

Every prompt you send — whether it's a text-to-video generation, image-to-video animation, or a Pikaffects motion request — gets parsed and routed to the appropriate Pika Labs endpoint based on your input type and parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

ClawHub connects to Pika Labs through the NemoVideo backend, which handles session authentication, queues your generation jobs, and streams back the rendered video output. NemoVideo acts as the middleware layer managing your Pika credits, model version selection (Pika 1.0, 1.5, 2.0), and motion intensity settings.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `pika-labs`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=pika-labs&skill_version=1.0.0&skill_source=<platform>`

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

## Use Cases

Pika-labs through ClawHub serves a wide range of creative and professional video needs. Social media creators use it to generate scroll-stopping short clips, animated backgrounds, and looping visuals for Reels, TikTok, and YouTube Shorts — without a production budget.

E-commerce brands animate product photography to create more engaging listings and ad creatives. Instead of a static image, shoppers see a product with life and motion, which dramatically improves engagement rates.

Filmmakers and concept artists use pika-labs to prototype scene ideas before committing to a full shoot. A rough text prompt can validate whether a visual direction is worth pursuing, saving significant pre-production time.

Educators and presenters use animated visuals to make complex topics more accessible, generating custom illustrative clips that match their specific content rather than relying on generic stock footage. Pika-labs fills the gap between imagination and production.

## Integration Guide

ClawHub connects directly to pika-labs so you can generate AI videos right inside your existing workflow. Once the pika-labs skill is active in your ClawHub workspace, you simply describe your video concept in natural language — no external app switching required.

You can pass text prompts, reference visual styles, or upload source images directly through the chat interface. The skill handles the generation request on your behalf and returns the finished video clip, ready to download in your preferred format including mp4, mov, webm, avi, or mkv.

For teams, this means faster asset production pipelines. A designer can request a looping background video, a marketer can generate a product animation, and a social media manager can prototype a visual concept — all from the same ClawHub environment without needing separate pika-labs accounts or manual file transfers.

## Quick Start Guide

Getting started with the pika-labs skill is straightforward. Begin by typing a clear, descriptive prompt about the video you want to create. The more specific you are about subject, motion, lighting, mood, and style, the closer the output will match your vision.

For image-to-video generation, upload your source image and then describe how you want it to move — for example, 'make the clouds drift slowly across the sky' or 'add subtle fabric movement to this portrait photo.'

If your first result isn't quite right, refine your prompt by adjusting the motion description, camera angle, or visual style. Pika-labs responds well to cinematic references like 'drone shot,' 'rack focus,' or 'timelapse effect.' Experiment freely — generation is fast, so iteration is part of the creative process. Output files can be saved in mp4 or other supported formats for immediate use across platforms.
