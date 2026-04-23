---
name: voiceover-app
version: "1.0.0"
displayName: "Voiceover App — Record, Sync & Polish Professional Narration for Any Video"
description: >
  Turn silent footage into compelling, broadcast-ready content with the voiceover-app skill. Built for content creators, educators, and video producers, this skill helps you script, time, and refine voiceover narration that syncs naturally with your visuals. Whether you're producing YouTube tutorials, corporate explainers, or documentary-style content, voiceover-app streamlines the entire narration workflow from first draft to final take.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm here to help you craft, refine, and time voiceover scripts that bring your videos to life. Tell me about your video — what it covers, who it's for, and the tone you're going for — and let's build your narration together.

**Try saying:**
- "Write a 90-second voiceover script for a product demo video showcasing a new project management app, aimed at small business owners."
- "Break this 3-minute explainer script into timestamped cue points so I can record it in sync with my video timeline."
- "Rewrite my existing voiceover draft to sound warmer and more conversational — it currently feels too stiff and corporate."

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/voiceover-app/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Give Your Videos a Voice That Captivates

Great video content isn't just about what viewers see — it's about what they hear. A well-crafted voiceover can transform a rough cut into a polished, professional piece that holds attention and communicates clearly. The voiceover-app skill is designed to help you craft narration that feels natural, purposeful, and perfectly timed to your footage.

Whether you're a solo creator working on a YouTube channel, an instructional designer building e-learning modules, or a marketing team producing product demos, this skill meets you where you are. You can generate full voiceover scripts from a brief description of your video, refine existing narration for tone and pacing, or break down a long script into timestamped cue points that match your timeline.

The goal is simple: remove the friction from voiceover production. Instead of staring at a blank page or wrestling with awkward phrasing, you get a working draft in seconds — one you can record immediately or hand off to a voice actor with confidence. Every output is written for the ear, not the eye, so your narration always sounds like it belongs.

## Routing Takes to the Right Track

When you submit a narration request — whether it's punching in a retake, syncing a new audio layer, or scrubbing noise from a recorded take — ClawHub parses the intent and routes it to the matching voiceover workflow automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Engine API Reference

All audio processing runs through a cloud-based rendering backend that handles waveform alignment, ADR sync, and noise reduction in real time without taxing your local machine. Session state, take metadata, and mix settings are persisted server-side so your project stays intact across devices.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `voiceover-app`
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

## Frequently Asked Questions

**Can this skill write voiceover scripts for any type of video?** Yes. Whether you're producing a YouTube tutorial, a corporate training video, a real estate walkthrough, or a short film narration, the voiceover-app skill adapts to your format, audience, and tone. Just describe your video and what you want viewers to feel or understand.

**How do I get a script that matches my video's length?** Provide the target duration (e.g., 60 seconds, 3 minutes) and the skill will pace the script accordingly. A general rule is roughly 130–150 words per minute for natural spoken delivery, and the output respects that rhythm.

**Can I use this to edit a voiceover script I've already written?** Absolutely. Paste in your existing draft and describe what isn't working — too formal, too long, awkward transitions — and the skill will revise it while preserving your original intent.

**Does this skill help with multi-voice or interview-style formats?** Yes. You can request scripts formatted for two speakers, a host-and-guest structure, or even documentary-style narration with alternating voices and natural pause cues built in.

## Integration Guide

**Fitting voiceover-app into your video production workflow** is straightforward once you know where it slots in best. Most creators use it at two key stages: pre-production (scripting before recording) and post-production (refining narration after a rough cut is assembled).

**Pre-production use:** Before you record a single word, use the skill to generate a full voiceover script from your video outline or storyboard. Export the script as plain text and load it into your teleprompter app, or share it directly with your voice actor alongside the video brief.

**Post-production use:** Once your edit is locked, paste in your timeline notes or scene descriptions and request a timestamped script. This gives you precise cue points — for example, 'at 0:42, transition to product close-up' — so your narration lands exactly where it should in the final cut.

**Tool compatibility:** The plain-text outputs from voiceover-app work cleanly with tools like Adobe Premiere Pro's captions panel, DaVinci Resolve's subtitle track, CapCut, and any teleprompter or recording app that accepts text input. No special formatting or conversion is needed.
