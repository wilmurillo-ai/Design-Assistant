---
name: ai-music-generator-free
version: "1.0.0"
displayName: "AI Music Generator Free — Create Original Tracks for Any Mood or Project"
description: >
  Tell me what you need and I'll compose original, royalty-free music tailored to your exact vibe, tempo, and style. This ai-music-generator-free skill lets you describe the mood, genre, or scene — and get a custom track back without spending a cent. Perfect for content creators, indie filmmakers, podcasters, and social media producers who need fresh audio without licensing headaches. Supports mp4/mov/avi/webm/mkv video uploads so you can match music directly to your footage.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to generate original, free AI music for your videos, content, or creative projects — just describe the mood, genre, or scene you have in mind and I'll compose something that fits perfectly. Ready to create your track?

**Try saying:**
- "Generate a calm, acoustic background track for a 2-minute meditation video — no drums, gentle guitar, peaceful mood"
- "Create an upbeat electronic track with a driving beat for a 30-second gym workout highlight reel"
- "I need a cinematic orchestral piece that builds tension over 90 seconds for a short film chase scene"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Your Personal Composer, No Budget Required

Creating original music used to mean hiring a composer, buying expensive software, or settling for overused stock tracks. This skill changes that entirely. Describe what you're working on — a lo-fi study montage, an upbeat product demo, a tense short film scene — and the AI generates a track built around your specific creative needs.

The ai-music-generator-free skill understands context. You're not just picking from a playlist; you're communicating intent. Want something that feels like a Sunday morning in a coastal town? Or a driving electronic beat for a gym highlight reel? Just say it. The skill interprets tone, tempo preferences, instrumentation hints, and duration to shape something that actually fits.

This is built for creators who move fast and can't afford to pause a project waiting on licensing approvals or royalty clearances. Whether you're scoring a YouTube video, adding ambiance to a podcast intro, or soundtracking a client presentation, you get usable, original audio — free, fast, and flexible.

## Routing Your Music Generation Requests

When you describe a mood, genre, tempo, or instrumentation, your prompt is parsed and dispatched to the appropriate AI composition pipeline based on track length, style complexity, and output format.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend API Reference

The NemoVideo backend processes your free AI music generation requests by converting natural-language prompts into structured audio synthesis parameters, then rendering stems and final mixed tracks through its generative model layer. Output formats include MP3 and WAV, with metadata tags for BPM, key, and genre automatically embedded.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-music-generator-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=ai-music-generator-free&skill_version=1.0.0&skill_source=<platform>`

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

## Integration Guide

Getting your generated music into your project is straightforward. Once the track is produced, download it in your preferred format and drop it directly into your editing timeline in tools like DaVinci Resolve, Adobe Premiere, CapCut, or Final Cut Pro.

If you're working with video files, you can upload your mp4, mov, avi, webm, or mkv clip directly to this skill and request music that's timed to match the clip's length. This removes the need to manually trim or loop a track afterward — the output is already sized to fit.

For podcast producers using Audacity, GarageBand, or Descript, export the generated track as a standard audio file and import it as a background layer. Adjust the volume envelope to duck under your voice track and you're done.

If you manage a content calendar with recurring formats — weekly vlogs, monthly brand videos, regular ad spots — consider generating a signature sound set once and reusing it across episodes. Consistent audio branding is one of the fastest ways to make a channel feel professional.

## Common Workflows

Most users come to this skill with one of three needs: scoring existing footage, generating background music for live or recorded content, or building a library of reusable tracks for ongoing projects.

For video scoring, the most effective approach is to upload your clip and describe the emotional arc — what happens at the start, how the energy shifts, and how it should feel at the end. The skill can generate music that mirrors that structure rather than looping a single flat tone.

For podcasters and streamers, a common workflow is generating a set of short themed pieces — an intro jingle, a transition sting, and a soft background loop — all in one session with consistent instrumentation so they feel like a cohesive package.

Content creators on tight turnaround schedules often use the skill to generate two or three variations of the same brief, then pick whichever one lands best in the edit. Since there's no cost per generation, iteration is fast and risk-free.
