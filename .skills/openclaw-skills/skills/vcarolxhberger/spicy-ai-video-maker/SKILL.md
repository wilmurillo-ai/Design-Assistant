---
name: spicy-ai-video-maker
version: "1.0.0"
displayName: "Spicy AI Video Maker — Create Bold, Attention-Grabbing Videos with AI"
description: >
  Turn your ideas, scripts, or raw clips into scroll-stopping videos using spicy-ai-video-maker — the AI skill built for creators who want edge, energy, and style in every frame. Generate punchy video concepts, write scene-by-scene scripts, craft viral hooks, and get dynamic editing directions tailored to your brand voice. Whether you're a content creator, marketer, or social media manager, spicy-ai-video-maker helps you produce bold video content faster without the creative block.
metadata: {"openclaw": {"emoji": "🌶️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to Spicy AI Video Maker — your creative partner for building bold, high-energy video content that cuts through the noise. Tell me what you're making today and let's build something worth watching.

**Try saying:**
- "Write a viral video hook now"
- "Script a 30-second product launch video"
- "Generate bold video concept ideas"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Make Videos That Actually Stop the Scroll

Most video content blends into the background. Spicy AI Video Maker exists to fix that. Whether you're building short-form content for TikTok and Reels, producing YouTube videos with real narrative punch, or crafting brand campaigns that demand attention — this skill helps you think, write, and structure video content with genuine creative heat.

From generating bold video concepts and scene-by-scene scripts to writing hooks that grab viewers in the first two seconds, Spicy AI Video Maker acts as your creative co-director. Describe your audience, your message, or even just a vibe — and get back a full video blueprint ready to shoot or animate.

This isn't a generic script generator. It's built around the specific craft of making videos feel alive: pacing, tone, visual direction, call-to-action placement, and storytelling structure that holds attention from open to close. Use it to break through creative blocks, iterate on ideas fast, and produce content that actually performs.

## How Your Prompts Get Processed

Every video generation request you fire off gets parsed for style directives, motion cues, and tone intensity before being routed to the appropriate rendering pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Backend API Reference Guide

Spicy AI Video Maker runs on a distributed cloud rendering backend that handles text-to-video synthesis, dynamic caption overlays, and hook-optimized scene sequencing in parallel. Your generation jobs are queued, processed, and returned as ready-to-export clips without any local compute required.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `spicy-ai-video-maker`
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

## Common Workflows

The most effective way to use Spicy AI Video Maker is to start with context: tell it your platform (TikTok, YouTube, Instagram Reels, LinkedIn), your audience, and the core message you want to land. From there, the skill can generate a full script, a concept outline, or just a killer hook — depending on where you are in your process.

A popular workflow for solo creators: use the skill to generate three different hook variations for the same video topic, test them in your head or with a small audience, then come back to flesh out the winning one into a full script with scene directions.

For brand teams, a common use case is briefing the skill with product features and brand tone-of-voice guidelines, then generating multiple short-form video angles — educational, entertaining, testimonial-style — to give the creative team real options to choose from rather than starting from a blank page.

## Integration Guide

Spicy AI Video Maker fits into your existing content production stack without friction. Use it at the ideation stage to rapidly prototype video concepts before you commit to production, or bring it in mid-project when your script needs a stronger opening or a tighter structure.

If you're working with a video editor, export the scene breakdowns and shot directions directly as a production brief. For social media managers scheduling content calendars, use the skill to batch-generate multiple video scripts for the week in a single session — just provide your content pillars and target platforms.

For teams using tools like Notion, ClickUp, or Airtable for content workflows, paste the generated scripts and concepts directly into your templates. Spicy AI Video Maker outputs clean, structured text that slots into any brief or storyboard format without reformatting headaches.

## Tips and Tricks

The more specific your input, the spicier the output. Instead of saying 'make a video about coffee,' try 'make a 45-second Reels script for specialty coffee drinkers who hate corporate coffee chains — use a rebellious tone and end with a discount offer.' Specificity unlocks dramatically better results.

Use the skill to stress-test your existing scripts. Paste in a draft and ask it to identify where viewers are most likely to drop off, or request a punchier version of your opening 10 seconds. It works as a creative editor, not just a generator.

Don't overlook the visual direction features — when you ask for scene breakdowns, request on-screen text suggestions, b-roll ideas, and music mood descriptors at the same time. This turns a script into a near-complete production brief in one pass, saving hours of back-and-forth with your editor or animator.
