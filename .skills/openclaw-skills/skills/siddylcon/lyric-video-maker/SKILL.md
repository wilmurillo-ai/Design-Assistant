---
name: lyric-video-maker
version: "1.0.0"
displayName: "Lyric Video Maker — Sync Animated Text to Music for Stunning Visual Tracks"
description: >
  Turn your audio tracks and footage into polished lyric videos that captivate viewers from the first beat. This lyric-video-maker skill overlays synchronized, animated lyrics onto video backgrounds — with support for mp4, mov, avi, webm, and mkv files. Choose from dynamic text styles, beat-matched timing, and customizable fonts to match your song's mood. Ideal for musicians, content creators, and social media managers who want professional lyric videos without complex software.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your song into a scroll-stopping lyric video? Drop your video file, share your lyrics, and tell me the vibe you're going for — let's make your music impossible to ignore.

**Try saying:**
- "Create a lyric video for my pop track using this mp4 background — bold white text that fades in line by line on each beat"
- "Make a lyric video with a dark moody aesthetic, neon pink lyrics, and smooth slide-in transitions for each verse"
- "Generate a lyric video from my live concert footage with the chorus lyrics highlighted in a different color than the verses"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Bring Your Lyrics to Life on Screen

Every song tells a story, and this skill makes sure your audience reads every word at exactly the right moment. The Lyric Video Maker lets you take any music track paired with a video background — whether it's a live performance clip, abstract visualizer footage, or a simple color gradient — and overlay your lyrics with precise, beat-matched timing.

Unlike generic subtitle tools, this skill is built specifically for music content. You can control how each line of text enters and exits the frame, choose from bold display fonts or elegant script styles, and adjust colors to complement your album artwork or brand palette. The result feels intentional and crafted, not auto-generated.

Whether you're releasing a new single, building a YouTube presence, or creating lyric content for Instagram Reels and TikTok, this tool meets you where you are. No timeline scrubbing, no keyframe headaches — just upload your video, paste your lyrics, describe your preferred style, and let the skill handle the rest.

## Routing Your Lyric Sync Requests

When you drop in a track and paste your lyrics, the skill parses your timing cues, animation style preferences, and font choices to route each request to the correct rendering pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend API Reference

The NemoVideo backend handles frame-accurate lyric stamping, beat-sync detection, and animated text rendering — every syllable marker and transition effect you set gets processed through its video composition engine. Calls are authenticated per session, so your project state, timeline edits, and export queue persist until the session closes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `lyric-video-maker`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=lyric-video-maker&skill_version=1.0.0&skill_source=<platform>`

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

**Keep lyrics grouped by sung phrase, not by sentence.**
Breaking lyrics into the natural phrases a singer delivers — rather than full grammatical sentences — makes the on-screen text feel natural and easy to follow. Short bursts of 3–6 words per line tend to read best at video speed.

**Match your text style to your genre.**
A heavy metal track calls for aggressive, high-contrast typography, while an acoustic folk song might suit a soft, handwritten font on a muted background. Describe the emotional tone of your song and the skill can suggest a matching visual direction.

**Use high-contrast backgrounds for readability.**
Dark backgrounds with light text (or vice versa) ensure lyrics are legible across all screen sizes, including mobile. If your background footage is busy or mid-toned, ask for a subtle text shadow or semi-transparent backing bar behind the lyrics.

**Plan for platform aspect ratios.**
Mention upfront whether your lyric video is destined for YouTube (16:9 landscape), Instagram Reels (9:16 vertical), or a square format. This affects how text is positioned and sized throughout the video.

## FAQ

**What video formats does the Lyric Video Maker support?**
You can upload video backgrounds in mp4, mov, avi, webm, or mkv format. Most standard exports from phones, cameras, and editing software will work without any conversion needed.

**Do I need to time-stamp every lyric manually?**
Not necessarily. You can provide rough timestamps for each line or verse, or simply describe the song's structure (e.g., 'the chorus starts at 0:45') and the skill will handle placement. For precise sync, providing a timestamped lyric sheet gives the best results.

**Can I customize fonts, colors, and animation styles?**
Yes — describe your preferred look in plain language. For example: 'serif font, cream text, slow fade-in per line' or 'bold uppercase, glowing yellow, quick pop-on effect.' The skill interprets style descriptions and applies them consistently throughout the video.

**What's the ideal video length for best results?**
The skill handles videos from short social clips (under 60 seconds) up to full song lengths (typically 3–5 minutes). Very long files may require a moment to process.

## Quick Start Guide

**Step 1 — Prepare Your Files**
Have your video background ready in mp4, mov, avi, webm, or mkv format. This can be anything from abstract motion graphics to a performance video. Also prepare your full lyrics as plain text.

**Step 2 — Describe Your Timing**
Paste your lyrics and indicate where key sections fall in the song. Even rough markers like 'verse 1 runs from 0:00–0:45, chorus at 0:45–1:10' give the skill enough to work with. A full timestamped lyric file produces the tightest sync.

**Step 3 — Define Your Visual Style**
Tell the skill what you want the text to look like. Mention font style (bold, script, sans-serif), color, text size, and how you want lines to animate (fade, slide, pop, typewriter, etc.).

**Step 4 — Review and Refine**
Once the lyric video is generated, review the timing and style. You can request adjustments — 'make the chorus text larger' or 'slow down the fade-out on each line' — and the skill will revise accordingly until it matches your vision.
