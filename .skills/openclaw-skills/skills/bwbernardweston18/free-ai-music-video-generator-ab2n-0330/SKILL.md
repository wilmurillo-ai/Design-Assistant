---
name: free-ai-music-video-generator-ab2n-0330
version: "1.0.0"
displayName: "Free AI Music Video Generator — Create Stunning Music Videos from Your Tracks"
description: >
  Tell me what you need and I'll help you build a music video that actually matches your sound — no studio budget required. This free-ai-music-video-generator turns your audio tracks into visually synchronized videos using AI-driven scene generation, beat detection, and style matching. Upload your mp4, mov, avi, webm, or mkv footage and let the AI align cuts, effects, and transitions to your music's rhythm. Perfect for independent artists, content creators, and producers who want professional-looking music videos without the cost.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you create a free AI music video that brings your track to life visually. Drop your audio file or footage and tell me the vibe you're going for — let's build something worth watching.

**Try saying:**
- "Generate a music video for my lo-fi hip hop track using dreamy, pastel-colored visuals with slow cuts that match the beat"
- "I have a live concert recording in mp4 format — edit it into a polished music video with color grading and synced transitions"
- "Create an abstract, high-energy music video for my electronic dance track with neon visuals and fast cuts on every kick drum hit"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Your Music Into a Visual Experience

Creating a music video used to mean hiring a director, renting equipment, and spending thousands of dollars on post-production. This skill flips that entirely. By combining your audio track with uploaded footage or AI-generated visuals, you get a finished music video that feels intentional — not like a slideshow with a song playing over it.

The AI analyzes your track's tempo, energy shifts, and key moments, then syncs visual cuts and effects to match. Whether you're working with raw performance footage, abstract visuals, or a mix of both, the output is timed to your music in a way that feels natural and dynamic. You can guide the mood, color palette, and visual style through simple text prompts.

This is built for artists who are self-releasing, creators building a YouTube or social media presence, and producers who want a visual component for their beats. No editing experience is needed — just your music, your vision, and a few words describing what you want.

## Routing Your Video Requests

Every prompt you send — whether you're describing a visual style, uploading a track, or tweaking scene transitions — gets parsed and routed to the appropriate NemoVideo generation pipeline based on intent, media type, and complexity.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

Under the hood, ClawHub calls the NemoVideo backend to sync your audio waveform with AI-generated visuals, handling beat detection, scene rendering, and style transfer automatically. The API processes your music file alongside your visual prompt to produce frame-accurate, rhythm-driven video output.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-ai-music-video-generator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=free-ai-music-video-generator&skill_version=1.0.0&skill_source=<platform>`

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

## FAQ — Free AI Music Video Generator

**Do I need to upload footage, or can the AI generate visuals from scratch?** Both options work. You can upload your own video files in mp4, mov, avi, webm, or mkv format, or describe the kind of visuals you want and let the AI build them around your audio.

**Will the cuts actually sync to my music?** Yes — beat detection analyzes your track and aligns visual transitions to rhythmic cues. The tighter and cleaner your audio mix, the more precise the sync.

**Can I use this for a full-length song or just short clips?** Full songs are supported. For longer tracks, breaking the video into sections by mood or energy level (verse, chorus, bridge) in your prompt can help produce more varied and interesting results.

**What video formats are supported for upload?** You can upload mp4, mov, avi, webm, and mkv files. Standard resolution and HD footage both work well.

## Integration Guide — Using This Skill in Your Workflow

This skill fits naturally into a release workflow for independent musicians. Once your track is mixed and mastered, bring it here before you start thinking about promotional content. A finished music video can be repurposed across YouTube, Instagram Reels, TikTok, and Spotify Canvas — so one generation session can fuel multiple platforms.

If you're a producer selling beats, use this skill to create visual previews that play automatically on your beat store or social profiles. A looping, beat-synced video clip is far more engaging than a static waveform image.

For content creators working with licensed music, you can upload your own footage alongside the audio and describe the editing style you want. The AI handles the heavy lifting of timing and transitions, so you spend less time in a timeline and more time creating. Export your finished video and bring it directly into your publishing platform of choice.

## Best Practices for Getting Great Results

The more specific you are about the mood and style, the better your music video will turn out. Instead of saying 'make it look cool,' try describing a reference point — like 'cinematic and dark like a noir film' or 'bright and energetic like a pop concert.' These kinds of descriptors give the AI real direction.

For audio, clean exports work best. If your track has a strong, consistent beat, the AI's sync detection performs noticeably better. Tracks with lots of dynamic variation — quiet verses and loud choruses — produce especially compelling results because the visuals can breathe and then explode in energy.

If you're uploading your own footage in mp4, mov, avi, webm, or mkv format, try to provide more raw material than you think you'll need. Having extra clips gives the AI more options when matching moments to specific musical beats or transitions. Short clips under 10 seconds tend to cut together more cleanly than long unbroken takes.
