---
name: online-video-editor-free
version: "1.0.0"
displayName: "Online Video Editor Free — Edit, Trim & Export Videos Without Software"
description: >
  Turn raw clips into polished, share-ready videos without downloading a single app. This online-video-editor-free skill helps creators, marketers, and educators cut footage, add text overlays, apply transitions, and export in multiple formats — all from a browser. Whether you're building social reels, tutorial videos, or product demos, you get fast, guided editing assistance with zero cost barriers.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to your free online video editing assistant — I'll help you cut, enhance, and export your videos without any software downloads. Tell me about your footage or the type of video you want to create, and let's get started!

**Try saying:**
- "Trim my video to 60 seconds"
- "Add captions to this clip"
- "Export video for Instagram Reels"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Edit Any Video Free, Right From Your Browser

Not everyone has access to expensive desktop software like Premiere Pro or Final Cut — and they shouldn't need it. This skill is built around the idea that great video editing should be accessible to anyone with a browser and a story to tell. Whether you're a small business owner putting together a product walkthrough, a student editing a class project, or a content creator prepping short-form clips for TikTok or YouTube, this tool meets you where you are.

Using this online video editor free skill, you can get step-by-step guidance on trimming footage, layering text and captions, applying color corrections, adding background music, and structuring your timeline for maximum impact. You don't need to learn a complicated interface from scratch — just describe what you want your video to do, and you'll get clear, actionable instructions or direct editing support.

The focus here is practical output: videos that look intentional, not accidental. From aspect ratio adjustments for different platforms to export settings that won't bloat your file size, this skill covers the full editing workflow without the paywall.

## Routing Edits to the Right Tool

When you describe a video task — trimming a clip, merging footage, adding captions, or exporting to MP4 — ClawHub parses your intent and routes it directly to the matching free online editor function without requiring any software download.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All video processing runs on a browser-based cloud rendering backend, meaning your trim points, cut sequences, and export settings are handled server-side — no local encoder needed. Supported formats include MP4, MOV, WebM, and GIF, with resolution options up to 1080p depending on your session tier.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `online-video-editor-free`
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

This online-video-editor-free skill is designed to support a wide range of real-world editing scenarios without requiring a budget or technical background.

**Content Creators & Influencers:** Quickly cut raw footage into platform-optimized clips for YouTube Shorts, TikTok, or Instagram Reels. Add text hooks, transitions, and royalty-free music without paying for a subscription tool.

**Small Business Owners:** Create product demos, promotional videos, or customer testimonial edits using free browser tools. Export in the right resolution and aspect ratio for your website or social media ads.

**Educators & Trainers:** Trim lecture recordings, add on-screen annotations, and export compressed video files suitable for LMS platforms or email delivery — all from a free online editor.

**Freelancers & Agencies on a Budget:** Prototype video concepts for clients or deliver quick-turnaround edits without licensing professional software. This skill helps you identify the right free tool for each specific editing task and use it efficiently.

## Integration Guide

Getting started with a free online video editor through this skill requires no technical setup — but a few practical steps will make your workflow much smoother.

**Step 1 — Choose Your Platform:** Based on your editing needs (trimming, subtitles, multi-track audio, etc.), this skill will recommend the best free browser-based editor such as CapCut Online, Clipchamp, or DaVinci Resolve Free. Each has different strengths, and the recommendation will match your specific task.

**Step 2 — Upload Your Footage:** Most free online editors accept MP4, MOV, and AVI files. Keep your source file under 2GB for smooth browser performance. This skill can advise on compressing large files before upload if needed.

**Step 3 — Follow the Editing Workflow:** Describe your desired output — length, format, captions, music, transitions — and receive a step-by-step editing plan tailored to whichever free tool you're using.

**Step 4 — Export & Distribute:** Get guidance on export settings (resolution, bitrate, file format) optimized for your target platform, whether that's YouTube, a website embed, or a direct file share.
