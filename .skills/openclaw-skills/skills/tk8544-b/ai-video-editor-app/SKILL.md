---
name: ai-video-editor-app
version: "1.0.0"
displayName: "AI Video Editor App — Smart Editing Tools That Cut, Enhance & Export Fast"
description: >
  Turn raw footage into polished, share-ready videos without touching a timeline. This ai-video-editor-app skill handles the heavy lifting — trimming clips, generating captions, suggesting cuts, writing scripts, and crafting edit briefs based on your footage description. Built for content creators, marketers, and social media managers who need professional results without a steep learning curve or expensive software.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to your AI video editing assistant — describe your footage or project and I'll generate a complete edit plan, captions, and platform-ready recommendations. Ready to start? Tell me what video you're working on!

**Try saying:**
- "I have a 12-minute interview with a CEO. Help me cut it down to a 90-second LinkedIn highlight reel with captions and a strong opening hook."
- "I'm making a product demo video for a skincare brand. Suggest a scene-by-scene edit structure, on-screen text, and background music style for Instagram Reels."
- "I recorded a 45-minute webinar. Help me identify the 5 best short clips to repurpose for YouTube Shorts, and write captions for each one."

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit Smarter, Not Harder With AI

Most video editing tools demand hours of manual work — scrubbing timelines, syncing audio, adjusting color, and writing captions frame by frame. This skill changes that equation entirely. Describe your footage, your goal, and your audience, and get back a structured edit plan, caption drafts, scene suggestions, and export recommendations tailored to your platform.

Whether you're cutting a 10-minute interview down to a punchy 60-second reel, building a product demo for your landing page, or repurposing a podcast episode into short-form clips for TikTok and Instagram, this skill maps out every step. You'll get shot-by-shot guidance, on-screen text ideas, hook scripts, and b-roll suggestions — all without opening a single editing app until you're ready.

This is the AI co-editor that understands storytelling, pacing, and platform-specific formats. No more staring at a blank timeline wondering where to start.

## Routing Edits to the Right Pipeline

When you submit a cut, enhancement, or export request, ClawHub parses your intent and routes it to the matching AI editing pipeline — whether that's scene detection, color grading, auto-captioning, or render optimization.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing Backend Reference

All video processing runs on distributed cloud inference nodes that handle frame analysis, AI upscaling, and codec-level export encoding in parallel. Requests are queued by job type — trim and cut operations resolve fastest, while full-timeline AI enhancements may batch across multiple GPU instances depending on clip length and resolution.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-editor-app`
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

## Use Cases

**Content Creators & YouTubers:** Use this skill to plan your edit before you even open your software. Get a timestamped cut list, hook ideas for the first 5 seconds, and chapter suggestions based on your video topic.

**Social Media Managers:** Repurpose long-form videos into platform-specific formats. Get tailored aspect ratio recommendations, caption styles, and clip lengths for TikTok, Instagram Reels, YouTube Shorts, and LinkedIn — all from one source video.

**Marketing Teams:** Build polished product demos, testimonial edits, and brand story videos with AI-generated scripts, scene structures, and call-to-action placement suggestions. No video production background required.

**Podcasters Going Visual:** Describe your episode and get a clip extraction plan that identifies the most quotable, shareable moments — complete with suggested on-screen text and thumbnail copy.

## FAQ

**Do I need to upload my actual video files?** No — this skill works from your descriptions. Tell me what's in your footage, how long it is, and what you want to achieve, and I'll generate a complete edit plan you can execute in any editing app.

**Which editing software does this work with?** The edit plans and suggestions are software-agnostic. Whether you use Premiere Pro, Final Cut, CapCut, DaVinci Resolve, or a mobile app, the output translates to any tool.

**Can it write captions and subtitles?** Yes. Describe the spoken content or paste a transcript and I'll format captions optimized for readability, timing, and platform style — including burned-in subtitle suggestions and accessibility-friendly formatting.

**What if I don't know what kind of video I want?** Just describe your goal and audience. I'll recommend a video format, structure, and editing approach that fits your use case — from scratch.
