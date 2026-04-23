---
name: seedance-alternative-free
version: "1.0.0"
displayName: "Seedance Alternative Free — AI Video Generation Without the Price Tag"
description: >
  Drop a video idea or raw footage and describe what you want — this skill delivers AI-powered video generation as a seedance-alternative-free solution that costs you nothing. Whether you're animating still images, generating short clips from text prompts, or transforming existing footage into stylized sequences, this tool handles it. Built for creators, marketers, and educators who want professional-grade video output without subscriptions or paywalls.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a text prompt, image, or video clip and I'll generate or transform it into polished video content for you. No media? Just describe the scene you have in mind.

**Try saying:**
- "I have a product photo of a coffee mug — animate it with steam rising and soft morning light, make it feel like a 5-second Instagram reel"
- "Generate a 10-second video clip of a sunset over a city skyline with cinematic color grading and slow camera movement, no text overlays"
- "I have a 30-second raw talking-head clip — recut it to feel more dynamic, add smooth transitions between sentences, and suggest a pacing style that works for LinkedIn"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Free AI Video Generation That Actually Delivers

Most AI video tools lock their best features behind expensive plans. This skill exists as a genuine seedance-alternative-free option — giving you access to text-to-video generation, image animation, and footage transformation without spending a cent.

You can describe a scene in plain language and watch it become a short video clip. You can upload a still image and bring it to life with motion. You can take raw footage and apply stylistic filters, pacing changes, or narrative restructuring — all through simple conversational prompts.

This is built specifically for independent creators, small business owners, social media managers, and educators who need compelling video content regularly but can't justify the cost of premium platforms. Instead of learning complex software or navigating subscription tiers, you describe what you want and get results. The workflow is intentionally simple: input your idea or media, describe your goal, and receive a video output ready for sharing or further editing.

## Routing Your Video Generation Requests

When you submit a prompt, ClawHub parses your text-to-video or image-to-video intent and routes it to the optimal free-tier inference node based on current queue depth and model availability.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing Backend Reference

The Seedance Alternative Free backend runs on distributed GPU clusters that handle diffusion-based video synthesis, automatically scaling frame interpolation and motion consistency passes without consuming your local compute. Latency varies by resolution tier — 480p jobs typically resolve faster than 720p upscaled outputs during peak generation windows.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-alternative-free`
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

## Integration Guide

Getting started with this seedance-alternative-free skill requires no account setup, no API keys, and no software installation. Simply open the skill inside ClawHub and begin by either typing a descriptive prompt or uploading your source media directly in the chat.

For text-to-video workflows, write your scene description with as much detail as you can — include mood, motion style, duration, and intended platform (vertical for TikTok/Reels, horizontal for YouTube). The more specific your prompt, the closer the output matches your vision.

For image-to-video or footage transformation tasks, attach your file and describe the transformation goal. Supported input types include static images (JPG, PNG), short video clips (MP4, MOV), and plain text descriptions. Outputs are delivered as downloadable video files ready for direct upload to any platform — no additional conversion needed.

## Use Cases

This seedance-alternative-free skill covers a wide range of practical video creation scenarios that professionals and hobbyists encounter daily.

E-commerce sellers use it to animate product photos into attention-grabbing social ads without hiring a video team. A single still image of a sneaker can become a rotating, light-catching 6-second clip ready for Instagram Stories.

Content creators on tight budgets use it to generate B-roll footage from text descriptions when their own footage falls short — filling gaps in vlogs, explainer videos, or course content without stock footage subscriptions.

Educators and trainers use it to convert slide-based lessons into short animated video segments, making dry material more engaging for remote learners. Small business owners use it to produce promotional clips for seasonal campaigns in minutes rather than days.

## Best Practices

To get the most out of this seedance-alternative-free skill, treat your prompt like a director's brief. Vague inputs produce generic outputs — specific inputs produce usable ones. Always include the target platform, desired duration, mood or tone, and any motion preferences (slow zoom, parallax, handheld feel, etc.).

When animating images, choose source photos with clear subjects and clean backgrounds. Cluttered images with many competing elements produce less predictable motion results. Portrait-oriented images work best for Reels and TikTok outputs; landscape images suit YouTube and LinkedIn.

For transformation tasks on existing footage, trim your clip to only the essential portion before submitting. Shorter inputs process more accurately and give you tighter control over the output style. If a first result isn't quite right, refine your prompt with one or two specific adjustments rather than rewriting it entirely — iterating in small steps consistently produces better final results.
