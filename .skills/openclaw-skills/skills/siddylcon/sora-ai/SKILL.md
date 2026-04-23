---
name: sora-ai
version: "1.0.0"
displayName: "Sora AI Video Generator — Create Stunning AI-Powered Videos from Text & Footage"
description: >
  Turn your ideas and raw footage into cinematic, AI-generated video content using sora-ai on ClawHub. This skill taps into Sora's generative video capabilities to help creators, marketers, and filmmakers produce polished scenes, extend clips, and reimagine visuals with natural language prompts. Whether you're building social content, concept reels, or product demos, sora-ai handles the heavy lifting. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your Sora AI video assistant — ready to help you generate, extend, or reimagine video content using the power of sora-ai. Drop in a text prompt or upload your footage and let's start creating something extraordinary.

**Try saying:**
- "Generate a 10-second cinematic clip of a futuristic city at sunset with slow drone movement"
- "Extend this uploaded mp4 clip by 5 seconds, keeping the same visual style and camera motion"
- "Create a product showcase video for a sleek black smartwatch with soft studio lighting and close-up detail shots"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Generate Cinematic Videos With Just a Prompt

Sora AI represents a leap forward in how video content gets made. Instead of spending hours in editing timelines or sourcing stock footage, you describe what you want — and sora-ai brings it to life. Whether you're a solo creator with a big idea or a brand team looking to prototype a campaign, this skill gives you a direct line to generative video production without any technical barriers.

With sora-ai on ClawHub, you can upload existing footage and ask the model to extend it, restyle it, or generate complementary scenes that match your original material. You can also start from scratch with a text description and receive a fully rendered video clip ready for use in your project. The model understands cinematic language — lighting, pacing, camera motion, mood — so your prompts can be as creative or as precise as you need.

This skill is built for content creators, video marketers, indie filmmakers, and anyone who wants to move from concept to finished video faster than ever before. No film crew required.

## Routing Your Sora Prompts

Each request is parsed for intent — text-to-video generation, video extension, or footage remixing — then dispatched to the appropriate Sora pipeline endpoint automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

Sora AI Video Generator runs on the NemoVideo backend, which handles prompt queuing, diffusion model orchestration, and clip rendering before returning your finalized video asset. All generation parameters — aspect ratio, duration, motion style — are passed directly through NemoVideo's API layer.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `sora-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=sora-ai&skill_version=1.0.0&skill_source=<platform>`

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

## Best Practices

Before submitting a generation request, define your intended output use: social media clips, presentation b-roll, and narrative film sequences each benefit from different aspect ratios, pacing, and visual density. State your intended format in the prompt when possible.

Keep generated clips between 5 and 15 seconds for the sharpest quality and most coherent motion. Longer generations can be chained together in post-production for seamless sequences. If you're extending uploaded footage, ensure your source file is at least 720p resolution — higher input quality leads to more detailed and consistent sora-ai outputs.

Always review generated content for any unintended visual artifacts before publishing, particularly in scenes with human faces or text. Sora AI excels at environments, abstract motion, and product visuals. For dialogue-heavy or text-overlay content, plan to layer those elements in post. Save your best-performing prompts as templates to reuse across future projects.

## Integration Guide

ClawHub's sora-ai skill fits naturally into existing creative and production workflows. If you're working in a video editing suite like DaVinci Resolve or Premiere Pro, use this skill to generate b-roll or transitional clips, then import the downloaded mp4 or mov files directly into your timeline as supplementary assets.

For marketing teams using content management platforms, the sora-ai skill can serve as a rapid prototyping layer — generate concept videos for stakeholder review before committing to a full production shoot. This cuts ideation cycles significantly and gives stakeholders something tangible to react to early in the process.

Content creators publishing to YouTube, TikTok, or Instagram can use sora-ai to produce intro sequences, background loops, or stylized cutaways that elevate production value without additional equipment. Generated clips in webm and mkv formats are also well-suited for web embeds and interactive media environments. Simply download your output from ClawHub and slot it into whichever platform or tool is next in your pipeline.

## Tips and Tricks

Getting the most out of sora-ai starts with how you write your prompts. Be specific about camera movement — words like 'slow pan left,' 'handheld shake,' or 'static wide shot' give the model strong directional cues. Lighting descriptors such as 'golden hour,' 'neon-lit,' or 'overcast diffused light' dramatically shape the mood of your output.

When uploading existing footage for extension or restyling, trim your clip to the most visually stable section before uploading. Sora AI performs best when the input has clear visual context — a shaky or cut-heavy segment may produce less consistent results.

For brand or commercial work, include color palette references in your prompt (e.g., 'warm terracotta tones with muted shadows') to keep outputs aligned with your visual identity. You can also iterate quickly by slightly adjusting a single variable in your prompt — like swapping 'urban street' for 'coastal boardwalk' — to explore different creative directions without starting over.
