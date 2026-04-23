---
name: video-ai-generator-free
version: "1.0.0"
displayName: "Video AI Generator Free — Create Stunning AI-Powered Videos Without Spending a Dime"
description: >
  Turn raw ideas, scripts, or images into polished videos using video-ai-generator-free — no budget, no camera, no editing experience needed. This skill helps creators, marketers, and educators produce engaging video content by generating scenes, voiceovers, captions, and transitions from simple text prompts. Whether you're building social media reels, explainer clips, or product showcases, get professional-quality results fast.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Share your video idea, topic, or script and I'll turn it into a fully structured AI-generated video plan. No idea yet? Just describe your audience and goal.

**Try saying:**
- "Create a 60-second product explainer video script for a reusable water bottle targeting eco-conscious millennials, with scene descriptions and suggested visuals"
- "Generate a free AI video outline for a YouTube tutorial on how to start a vegetable garden, including intro hook, 5 main steps, and a call-to-action ending"
- "Make a short social media video concept for Instagram Reels promoting a local coffee shop, with text overlays, mood suggestions, and background music style recommendations"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Create Real Videos From Ideas — Completely Free

Most people assume making quality video content requires expensive software, a production team, or hours of editing. Video AI Generator Free flips that assumption entirely. You bring an idea — a concept, a script, a topic — and this skill helps you shape it into a complete, watchable video with structure, visuals, and narrative flow.

Whether you're a solo content creator trying to grow a YouTube channel, a small business owner who needs product demo videos, or a teacher building lesson content, this tool meets you where you are. No prior video editing knowledge is required. Just describe what you want, and the skill guides you through building it piece by piece.

The real power here is speed and accessibility. You can go from a blank page to a fully scripted, scene-by-scene video outline — complete with suggested visuals, on-screen text, and audio cues — in minutes. It's not about replacing creativity; it's about removing the barriers that stop most people from creating at all.

## Routing Your Video Generation Requests

When you submit a prompt, the skill parses your text-to-video parameters — resolution, duration, style, and motion cues — then routes the job to the optimal free-tier AI model endpoint based on current queue load and feature support.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All rendering happens on distributed GPU clusters via the backend API, which handles diffusion model inference, frame interpolation, and audio sync without touching your local hardware. Free-tier requests are queued through shared compute nodes, so generation latency varies depending on server load and clip length.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-ai-generator-free`
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

## FAQ

**Is this actually free to use?** Yes — video-ai-generator-free is designed to help you generate video content, scripts, and production plans without any paid tools or subscriptions required on your end.

**What kinds of videos can I create?** You can generate content for explainer videos, social media reels, YouTube tutorials, product demos, educational lessons, event promos, and more. If it can be scripted and structured, this skill can help build it.

**Do I need to know how to edit video?** Not at all. The skill produces ready-to-use scripts, scene outlines, voiceover text, and visual direction notes. You can use these with free tools like CapCut, Canva Video, or DaVinci Resolve — or hand them off to someone else.

**Can I generate videos in different languages?** Yes. Specify your target language in the prompt and the skill will produce scripts and on-screen text accordingly, making it useful for multilingual content strategies.

## Tips and Tricks

Getting the most out of video-ai-generator-free starts with being specific in your prompts. Instead of saying 'make a marketing video,' try 'make a 45-second Instagram video for a skincare brand targeting women aged 25-35 with a calm, natural aesthetic.' The more context you give, the more tailored and usable your output will be.

Use the scene-by-scene breakdown feature to plan your video before committing to any production. Each scene description acts like a shot list — you can hand it directly to a video editor or use it as a guide if you're recording yourself.

For free AI video generation, pairing text prompts with reference examples works especially well. Describe a video style you admire ('like a Wired explainer' or 'in the style of a calm meditation channel') and the skill will adapt tone, pacing, and structure accordingly.

Finally, don't overlook the power of repurposing. One long-form video script can be broken into three short clips, a blog post, and a carousel — ask the skill to help you do exactly that.

## Quick Start Guide

**Step 1 — Define your video goal.** Start by telling the skill what the video is for: a product launch, a tutorial, a brand story, or a social clip. Include your target platform (YouTube, TikTok, Instagram) and approximate length.

**Step 2 — Describe your audience.** The more the skill knows about who's watching, the better it can tailor tone, vocabulary, and pacing. Example: 'first-time homebuyers aged 30-45 who are nervous about the mortgage process.'

**Step 3 — Choose your output format.** Ask for a full script, a scene-by-scene breakdown, a voiceover draft, or an on-screen text plan. You can request all of these together or one at a time.

**Step 4 — Refine and iterate.** Once you have a draft, ask for revisions. Shorten a section, change the tone from formal to casual, or add a stronger call-to-action at the end. Video AI Generator Free works best as a back-and-forth conversation, not a one-shot request.
