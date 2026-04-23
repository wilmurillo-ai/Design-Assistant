---
name: video-editing-with-ai
version: "1.0.1"
displayName: "AI Video Editing Assistant — Smart Cuts, Captions & Creative Direction in Seconds"
description: >
  Tell me what you need and I'll help you shape raw footage into polished, publish-ready video content using video-editing-with-ai techniques. Whether you're trimming a long-form interview, scripting a reel, writing cut-by-cut edit instructions, or brainstorming transitions and pacing — this skill handles the creative and structural heavy lifting. Built for content creators, marketers, YouTubers, and social media editors who want faster turnaround without sacrificing quality.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Share your footage description, transcript, or edit goals and I'll give you a full editing plan, cut list, or caption draft — no footage on hand? Just describe the video you're making.

**Try saying:**
- "I have a 12-minute interview recording and need to cut it down to a 3-minute highlight reel for LinkedIn. Here's the transcript — which sections should I keep and in what order?"
- "Write an edit script for a 60-second Instagram Reel promoting a skincare product launch, including suggested shot types, text overlays, and music mood."
- "I'm editing a travel vlog shot in Portugal. Suggest a pacing structure, b-roll placement strategy, and transition style that fits a cinematic YouTube format."

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Your AI Co-Editor for Every Kind of Video

Video editing is more than cutting clips — it's about pacing, storytelling, and knowing exactly where to hold a shot and where to let it breathe. This skill acts as your intelligent editing partner, helping you plan, script, and structure video projects from a single rough idea all the way to a frame-by-frame edit list.

Whether you're working on a YouTube documentary, a 15-second product ad, a wedding highlight reel, or a corporate explainer, the approach adapts to your format and platform. You can describe your footage, paste a transcript, or share a rough outline — and get back structured edit notes, caption drafts, b-roll suggestions, music cue recommendations, and scene-by-scene pacing guidance.

This isn't a one-size-fits-all tool. It understands the difference between editing for TikTok versus editing for a film festival submission. The goal is to give you creative direction that actually fits your project — so you spend less time staring at a timeline and more time publishing work you're proud of.

## Routing Cuts, Captions & Prompts

Every request — whether you're trimming a timeline, generating auto-captions, or prompting a creative direction change — gets parsed and routed to the appropriate AI processing pipeline based on intent, media context, and edit complexity.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All video analysis, frame segmentation, and caption generation run through a distributed cloud backend that processes your media asynchronously — so heavy multi-track renders and AI-driven cut suggestions don't bottleneck your local machine. API calls are stateful within an active session, meaning the model retains timeline context across sequential edits.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-editing-with-ai`
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

## Performance Notes

This skill works best when you give it context about your footage — even a rough description of what's in each clip goes a long way. If you have a transcript, paste it in full; the more raw material available, the more precise the edit recommendations will be.

For longer projects (30+ minutes of footage), break your input into segments and work through the edit in stages rather than trying to process everything at once. This keeps the output focused and actionable rather than overwhelming.

Platform matters significantly for video-editing-with-ai output quality. Specifying whether you're cutting for YouTube Shorts, Instagram Reels, TikTok, LinkedIn, or long-form YouTube changes the pacing logic, caption style, and structural recommendations considerably. Always mention your target platform upfront for the most relevant edit plan.

## Tips and Tricks

One of the most underused features of this skill is transcript-based editing. If you paste a raw spoken transcript, it can identify the strongest soundbites, flag filler-heavy sections to cut, and reorder content for better narrative flow — saving hours of manual scrubbing through footage.

For social-first content, ask for a 'hook-first' edit structure. This prompts the skill to identify the most attention-grabbing moment in your footage and restructure the edit so that moment appears in the first three seconds — a proven technique for reducing scroll-past rates.

Don't overlook music and pacing prompts. Describing the emotional tone you want (e.g. 'urgent and energetic' vs. 'warm and nostalgic') helps generate cut rhythm suggestions that align your editing beats with the right music tempo range. You can also ask for chapter markers, end screen placement ideas, and thumbnail moment callouts as part of any edit plan.
