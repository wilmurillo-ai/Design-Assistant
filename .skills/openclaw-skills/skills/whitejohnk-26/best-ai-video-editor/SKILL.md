---
name: best-ai-video-editor
version: "1.0.0"
displayName: "Best AI Video Editor — Smart Editing Tools for Stunning Results"
description: >
  Turn raw footage into polished, professional-quality videos without spending hours in complex software. This skill helps you find and use the best-ai-video-editor tools available — comparing features, recommending workflows, and guiding edits like cuts, captions, color grading, and transitions. Whether you're a content creator, marketer, or filmmaker, get tailored advice that matches your style, platform, and timeline.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a description of your video project and I'll recommend the best AI video editor workflow, tools, and editing steps for it. No footage yet? Just describe the style or platform you're targeting.

**Try saying:**
- "I have a 10-minute raw interview recording and need to cut it down to a 90-second highlight reel for Instagram — what's the best AI video editor workflow for this?"
- "I'm making a product launch video for YouTube and want smooth transitions, captions, and a cinematic color grade — which AI editing tools should I use and in what order?"
- "I shoot travel content on my phone and want to repurpose horizontal footage into vertical Reels and TikToks automatically — what's the best AI video editor that handles this?"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Edit Smarter, Not Harder With AI Video Tools

Creating compelling video content used to require expensive software and years of practice. This skill changes that by acting as your personal guide to the best AI video editing tools and techniques available today — helping you cut through the noise and get straight to results that actually look great.

Whether you're editing a YouTube vlog, a branded social media reel, a product demo, or a short film, this skill walks you through the right approach for your specific project. You'll get concrete recommendations on which tools to use, how to structure your edit, and what features to lean on — from auto-captions and smart trimming to background removal and AI-powered color correction.

This isn't about generic advice. It's about understanding your footage, your audience, and your deadline — then helping you produce something you're genuinely proud of. Beginners get clear step-by-step guidance; experienced editors get faster workflows and sharper creative decisions.

## Smart Edit Request Routing

User prompts — whether for auto-cut, scene detection, color grading, or caption generation — are parsed by the intent engine and routed to the matching AI editing pipeline in real time.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All render jobs are offloaded to a distributed cloud backend that handles frame analysis, motion tracking, and generative fill without taxing your local machine. API calls return a job ID you can poll for progress, preview URLs, and final export links once transcoding completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `best-ai-video-editor`
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

## Quick Start Guide

Getting started with the best AI video editor for your project takes just a few steps. First, identify your output goal: Is this for YouTube, TikTok, a client presentation, or personal use? Your platform determines aspect ratio, length, and caption requirements before you touch a single clip.

Next, choose your tool based on your skill level and budget. Beginners should start with CapCut or Veed.io — both offer free tiers with strong AI auto-edit, captioning, and resizing features. Intermediate creators benefit from Descript for dialogue-driven edits or Runway for visual effects. Advanced editors should explore Adobe Premiere with AI plugins or DaVinci Resolve's neural engine for color and audio.

Once you've picked your tool, import your raw footage, run the AI scene detection or auto-cut feature first, then layer in captions, transitions, and music. Always do a final manual review pass — AI gets you 80% there fast, but your creative eye closes the gap.

## Performance Notes

AI video editors vary significantly in how they handle different types of footage. Tools like Runway ML and CapCut AI perform best with well-lit, stable clips — shaky or low-light footage may produce inconsistent results with auto-edit features. If you're working with 4K files, check that your chosen editor supports your resolution before committing to a workflow, as some browser-based AI tools compress exports by default.

For long-form content (over 20 minutes), batch processing and scene detection tools will save you the most time. Editors like Descript or Adobe Premiere with Sensei AI handle transcription-based editing well at scale. For short-form social content under 60 seconds, CapCut, OpusClip, and Veed.io tend to produce the fastest turnaround with the least manual adjustment needed.

Always export a test clip before committing to a full render — AI color grading and audio enhancement can behave differently across monitors and playback platforms.
