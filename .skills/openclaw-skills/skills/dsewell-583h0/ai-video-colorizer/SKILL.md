---
name: ai-video-colorizer
version: "1.0.0"
displayName: "AI Video Colorizer — Restore & Colorize Black-and-White Footage Instantly"
description: >
  Turn dull, grayscale footage into rich, lifelike color with this ai-video-colorizer skill. Upload black-and-white clips or faded archival video and receive realistic, scene-aware colorization that respects skin tones, natural environments, and period-accurate palettes. Ideal for filmmakers, historians, content creators, and family archivists who want to breathe new life into old memories or classic footage without manual frame-by-frame editing.
metadata: {"openclaw": {"emoji": "🎨", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your black-and-white or faded video and I'll colorize it with realistic, scene-aware color. No video on hand? Just describe the footage and I'll walk you through your options.

**Try saying:**
- "I have a black-and-white family home video from the 1960s — can you colorize it to look natural and warm?"
- "Colorize this grayscale documentary clip and make sure the outdoor scenes have realistic sky and grass tones."
- "I want to restore a faded, desaturated wedding video from the 1980s — can you bring back vibrant, accurate colors?"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Give Your Old Footage the Color It Deserves

Black-and-white video carries history, emotion, and story — but color makes it feel alive. This skill uses advanced AI colorization to analyze each frame of your footage and intelligently assign realistic colors based on context, lighting, and scene content. Whether you're working with a grainy home movie from the 1950s or a classic film clip, the result is smooth, natural-looking color that feels intentional rather than artificial.

Unlike basic filters that slap a tint over everything, this ai-video-colorizer understands the difference between a blue sky and a gray coat, between warm indoor lighting and cool outdoor shadows. It adapts its palette dynamically across scenes, preserving motion continuity and avoiding the jarring color shifts that plague lesser tools.

This skill is built for anyone who wants professional colorization results without a professional budget or a steep learning curve. Archivists restoring historical footage, YouTubers adding visual flair to vintage clips, and families digitizing old home videos will all find this tool immediately useful. Just share your video, describe any color preferences, and let the AI do the heavy lifting.

## Colorization Request Routing Logic

When you submit a black-and-white clip, the skill parses your intent — whether full colorization, selective hue correction, or era-specific palette matching — and routes it to the appropriate processing pipeline via the AI Video Colorizer API.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

The backend leverages a deep learning colorization engine hosted on distributed GPU nodes, applying temporal consistency algorithms to ensure frame-to-frame color coherence across your footage. Each API call packages your video segment with metadata like frame rate, resolution, and target color profile before dispatching it to the inference cluster.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-colorizer`
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

## Common Workflows

**Family Archive Restoration:** Start by scanning or digitizing your old film reels or VHS tapes. Feed the resulting grayscale or faded footage into the ai-video-colorizer, specifying the decade and general setting. The AI will apply era-appropriate colors and you can then export the finished clip to share with family.

**Historical Documentary Production:** Editors working on history content frequently need to mix archival black-and-white clips with modern color footage. Use this skill to colorize the archival segments so the final cut feels visually cohesive. Describe the geographic region and time period for best results.

**Social Media Content Creation:** Creators on YouTube, TikTok, and Instagram often use colorized vintage footage for nostalgic or educational content. Run short clips through the colorizer, add captions, and you have a ready-to-post piece that stands out in feeds dominated by standard modern video.

**Film Studies and Education:** Teachers and students analyzing classic cinema can colorize scenes to explore how color theory would have applied, or simply to make older films more engaging for younger audiences.

## Quick Start Guide

**Step 1 — Prepare Your Footage:** Make sure your video file is accessible and in a common format (MP4, MOV, AVI). If it's a physical tape or film reel, digitize it first using a scanner or capture device.

**Step 2 — Describe Your Video:** Share the clip and include a brief description: the approximate decade, the main subjects (people, landscapes, interiors), and any specific color preferences you have. More detail means better results.

**Step 3 — Review and Refine:** Once the initial colorization is returned, watch through it and note any areas that feel off — a sky that looks too green, skin tones that appear unnatural, or objects colored incorrectly. Share that feedback and request targeted adjustments.

**Step 4 — Export and Use:** When you're happy with the result, export the colorized footage and integrate it into your project, whether that's a family album, a documentary, or a social media post. The ai-video-colorizer is designed to produce output that's immediately usable without further post-processing.

## Tips and Tricks

For the best colorization results, provide as much context about your footage as possible. Mentioning the era, location, or subject matter — like 'outdoor summer picnic, 1940s Midwest' — helps the AI assign historically accurate and visually appropriate colors rather than generic ones.

If your footage includes specific objects you want colored a certain way (a red dress, a green car, a blue uniform), call those out explicitly in your prompt. The AI can honor specific color requests when they're clearly stated.

For longer videos, consider breaking the footage into shorter segments by scene type — indoor vs. outdoor, day vs. night — so the colorization stays consistent within each environment. This is especially useful for archival documentary footage that jumps between locations.

Always preview a short test clip before processing your full video. This lets you confirm the color palette feels right before committing to the entire project.
