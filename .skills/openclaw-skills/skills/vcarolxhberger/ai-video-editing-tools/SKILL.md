---
name: ai-video-editing-tools
version: "1.0.0"
displayName: "AI Video Editing Tools — Smart Cuts, Captions, and Creative Edits in Seconds"
description: >
  Drop a video and describe what you want — trim dead air, add captions, reframe for Reels, or punch up the pacing. This skill brings together ai-video-editing-tools capabilities into one conversational workspace. Tell it to cut silences, suggest B-roll placements, write on-screen text, or restructure a talking-head clip into a highlight reel. Built for creators, marketers, and social teams who want faster edits without learning complex software.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to your AI video editing workspace — whether you're trimming a raw interview, building a highlight reel, or repurposing long content into social clips, I've got you covered. Drop your footage details or describe your project and let's start editing.

**Try saying:**
- "I have a 45-minute webinar recording. Help me identify the 5 best clips under 60 seconds each for LinkedIn and write captions for each one."
- "Here's a transcript from my talking-head YouTube video — rewrite the first 10 seconds to be a stronger hook and suggest where I should cut to keep viewers watching past 30 seconds."
- "I need to repurpose a horizontal brand video into a vertical format for Instagram Reels. Tell me what to reframe, where to add text overlays, and how to restructure the pacing."

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Edit Smarter: Let AI Handle the Heavy Cuts

Most video editing eats hours you don't have — scrubbing timelines, hunting for the right frame, rewriting captions three times. This skill changes that by letting you describe what you want in plain language and getting back actionable edits, structured timecodes, caption drafts, and scene-by-scene suggestions you can actually use.

Whether you're cleaning up a podcast recording, repurposing a webinar into short-form clips, or building a product demo from raw footage, the skill adapts to your format and goal. Describe your audience, your platform, and your vision — and it maps out an editing plan that fits.

It's not just about cutting — it's about shaping a story. You can ask for pacing feedback, hook rewrites for the first five seconds, lower-third text ideas, or a full edit brief your video editor can execute immediately. Think of it as a creative collaborator that knows the language of video.

## Routing Edits to the Right Engine

Each request — whether you're triggering auto-captions, smart cuts, or style transfers — is parsed by intent and routed to the matching processing pipeline based on task type, media length, and output format.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud API Reference Guide

All render jobs run on a distributed cloud backend that handles frame extraction, model inference, and re-encoding in parallel — so heavy tasks like scene detection or generative B-roll don't block your timeline. Transcription, caption styling, and cut-point analysis each hit dedicated microservices tuned for low-latency media workflows.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-editing-tools`
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

## Best Practices

**Be specific about your platform first.** A TikTok edit and a LinkedIn edit from the same footage need completely different pacing, hook styles, and text placement. Mention your target platform upfront so every suggestion is calibrated correctly.

**Share context, not just footage.** The more you describe — who's speaking, what the video is promoting, who the audience is — the sharper the edit recommendations. Vague inputs get generic outputs; specific inputs get a real editing roadmap.

**Use transcripts whenever possible.** If you can paste a transcript or even rough notes, the skill can work with exact language to find the strongest moments, rewrite weak hooks, and build captions that match your tone — rather than guessing from a description alone.

**Iterate in rounds.** Start with structure (what to cut and keep), then refine captions, then polish on-screen text. Trying to solve everything in one prompt often produces unfocused results. Treat it like a real edit session — pass by pass.

## Common Workflows

**Podcast-to-Clips Pipeline:** Paste your episode transcript and ask for the top 3-5 quotable moments with suggested cut points, hook rewrites, and caption text. You'll get a ready-to-execute brief without scrubbing the timeline manually.

**Talking-Head Cleanup:** Describe your raw footage — length, topic, any filler or dead air — and the skill will suggest a tighter structure, flag where energy drops, and recommend B-roll prompts to cover jump cuts naturally.

**Platform Reformatting:** Tell the skill your original format (16:9 YouTube) and your target platform (9:16 TikTok or 1:1 Instagram). It will outline what to reframe, where to add text overlays to replace lost visual space, and how to adjust pacing for the new audience's scroll behavior.

**Batch Social Content:** Share one long video and a target post count. The skill maps out non-overlapping segments, writes unique captions for each, and suggests platform-specific tweaks so each clip feels native — not recycled.
