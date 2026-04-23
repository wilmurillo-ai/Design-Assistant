---
name: free-ai-music-video-generator
version: "1.0.0"
displayName: "Free AI Music Video Generator — Create Stunning Visuals for Any Song"
description: >
  Tell me what you need and I'll help you turn any track into a captivating music video using free-ai-music-video-generator. Describe your song's mood, genre, or story — and watch synchronized visuals come to life. Supports mp4, mov, avi, webm, and mkv formats. Perfect for indie artists, content creators, and music fans who want professional-looking videos without a production budget or complex software.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you create a free AI music video that matches your song's energy and story. Tell me about your track — the mood, genre, or visuals you're imagining — and let's start building something amazing together.

**Try saying:**
- "Generate a moody, cinematic music video for a slow indie rock song with rainy city visuals and warm amber tones"
- "Create an energetic music video for an upbeat pop track featuring colorful abstract animations synced to the beat"
- "Make a lo-fi aesthetic music video with cozy cafe scenes and soft lighting for a chill hip-hop instrumental"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Any Song Into a Visual Experience

Making a music video used to mean hiring a director, renting equipment, and spending thousands of dollars. This skill changes that entirely. Whether you're an independent musician dropping a new single, a content creator building a YouTube presence, or just someone who wants to give their favorite track a visual home — this tool was built for you.

Describe the vibe of your music: the tempo, the emotion, the imagery you imagine when you close your eyes and listen. From there, the skill helps you generate or arrange visuals that match the rhythm and feel of your track. You can work with existing footage, suggest scene styles, or build something from scratch using descriptive prompts.

The result is a polished, shareable music video you can export and post anywhere — no editing degree required. Whether your song is a lo-fi bedroom ballad or a high-energy EDM banger, this skill adapts to your creative vision and helps you produce something you're genuinely proud to share.

## Routing Your Visual Requests

When you describe your track's mood, genre, or aesthetic, the skill maps your prompt to the right generation pipeline — whether that's lyric-synced visuals, beat-matched animations, or full cinematic scene sequences.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

Under the hood, every music video render call hits the NemoVideo backend, which handles frame synthesis, audio-visual sync, and style transfer in real time. The API accepts tempo data, color palette hints, and scene descriptors to produce cohesive, beat-aware video output.

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

## Troubleshooting

If your generated video feels out of sync with the music, try breaking the song into sections and describing the visual intent for each part separately — verse, chorus, bridge. This gives the skill clearer guidance for pacing and transitions.

Uploaded video files that are very large or in less common codecs may process more slowly. Converting your footage to mp4 with H.264 encoding before uploading tends to produce the smoothest experience across all supported formats including mov, avi, webm, and mkv.

If the visual style doesn't match what you envisioned, try rephrasing your prompt with more contrast — for example, swap 'dark' for 'deep shadows with neon highlights' or 'vintage' for 'super 8 film grain with faded warm tones.' Precision in language translates directly into precision in output.

## Common Workflows

A popular workflow starts with uploading a rough cut of personal footage and asking the skill to suggest visual edits, color grades, and transition styles that match the song's BPM and emotional arc. This is great for artists who already have raw video from a live show or a shoot.

Another common approach is fully prompt-driven: describe your song in detail — genre, lyrics theme, target audience — and let the skill generate a complete visual concept from scratch. Many creators use this to build lyric videos, visualizers, or abstract art pieces that live on streaming platforms.

A third workflow is iterative refinement. Start with a broad concept, review the output, and then make targeted adjustments — swap a background, change the color temperature, tighten a cut. Treating the process as a back-and-forth conversation rather than a one-shot request consistently produces stronger final results.

## Tips and Tricks

The more specific your description, the better your results. Instead of saying 'make it look cool,' try describing the color palette, the camera movement style, or a specific emotion you want viewers to feel within the first ten seconds.

If you're uploading your own footage in mp4, mov, avi, webm, or mkv format, trim your clips beforehand so the strongest visual moments align with the song's chorus or key beats. This makes the sync feel intentional rather than accidental.

Experimenting with genre-specific visual styles goes a long way. Metal tracks tend to pop with high-contrast dark imagery, while acoustic folk songs breathe better with natural light and wide open spaces. Don't be afraid to name a specific film, photographer, or visual artist whose aesthetic inspires you — that kind of reference helps dial in the look quickly.
