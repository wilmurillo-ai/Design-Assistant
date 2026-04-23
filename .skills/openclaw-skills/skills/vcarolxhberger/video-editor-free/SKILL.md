---
name: video-editor-free
version: "1.0.0"
displayName: "Video Editor Free — Edit, Trim & Export Videos Without Paying a Cent"
description: >
  Turn raw, unpolished footage into share-ready videos without spending anything. This video-editor-free skill helps creators, students, and small business owners cut clips, add text overlays, merge scenes, and export clean video files — all through simple conversational prompts. No subscriptions, no watermarks, no paywalls. Whether you're editing a YouTube vlog, a product demo, or a school project, get precise editing guidance and automation in seconds.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! You're one step away from turning your raw footage into a polished, share-ready video — completely free. Tell me what you're working on and what you'd like to do with it, and let's start editing right now.

**Try saying:**
- "Trim the first 15 seconds and last 8 seconds from my video clip and export it as an MP4"
- "Merge three separate video clips into one video with a smooth fade transition between each"
- "Add a white text title card at the beginning of my video that says 'Summer 2024' for 3 seconds"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/video-editor-free/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit Videos Freely — Zero Cost, Full Control

Not everyone needs a $300-a-year subscription to make a great video. This skill was built for the everyday creator who wants real editing power without the price tag. Whether you're stitching together a travel montage, cleaning up a podcast recording, or producing a quick social media clip, this tool walks you through every step — or handles it for you.

Using this video-editor-free skill, you can trim the dead air from the beginning and end of clips, merge multiple video files into one seamless sequence, add captions or title cards, adjust audio levels, and export in formats that actually work on Instagram, TikTok, YouTube, or your company's website.

The skill is designed for people who don't have time to watch hours of tutorials or learn complex software interfaces. You describe what you want in plain language — 'cut the first 10 seconds', 'add a fade between clips', 'export as MP4 at 1080p' — and it delivers. No prior editing experience required.

## Routing Your Edit Requests

When you submit a trim, cut, merge, or export command, the skill parses your intent and routes it to the matching free-tier processing endpoint based on the operation type and output format specified.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

Video Editor Free runs on a serverless cloud backend that handles transcoding, frame extraction, and codec rendering without local processing — your raw footage is temporarily staged in an encrypted buffer, processed, then purged after export. Free-tier requests are queued through shared render nodes, so complex timelines or high-resolution exports may take slightly longer than premium lanes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-editor-free`
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

## Troubleshooting

**Video won't export or keeps failing?** The most common cause is an unsupported source format. This video-editor-free skill works best with MP4, MOV, and WebM files. If your file is in MKV, AVI, or a camera-native format like HEVC (.hevc), convert it to MP4 first using a free tool like HandBrake before uploading.

**Audio is out of sync after merging clips?** This typically happens when the source clips have different frame rates (e.g., one at 24fps and another at 60fps). Always confirm that your clips share the same frame rate before merging. You can ask the skill to check and normalize frame rates as part of the merge process.

**Text overlay not showing on export?** Make sure the font and text duration you specified doesn't exceed the clip length. If your video is 5 seconds and you set a text overlay for 8 seconds, it will silently fail. Specify an end time shorter than the total clip duration.

**File size too large after export?** Ask the skill to re-export using H.264 compression at a slightly lower bitrate — for most social media uses, 8–12 Mbps is more than sufficient and cuts file sizes dramatically.

## FAQ

**Is this actually free — no hidden costs?** Yes. The video-editor-free skill does not require a paid plan, subscription, or any in-app purchase to use its core editing features including trimming, merging, text overlays, and exporting.

**Will my exported video have a watermark?** No. Unlike many free online editors that stamp their logo on your video, this skill exports clean, watermark-free files.

**What's the maximum video length I can edit?** There is no hard cap on video length, but very long files (over 2 hours) may take longer to process. For best performance, work with clips under 30 minutes when possible.

**Can I edit vertical videos for TikTok or Reels?** Absolutely. Just let the skill know your target aspect ratio (9:16 for vertical) when you start, and it will handle framing, cropping, and export settings accordingly.

**Does it support background music or voiceover?** Yes. You can provide an audio file and specify whether you want it as background music (with volume ducking) or as a full voiceover replacement for the original clip audio.

## Best Practices

**Start with organized source files.** Before you begin, rename your clips in sequence (clip_01.mp4, clip_02.mp4) so it's easy to reference them in prompts. Ambiguous file names slow down the editing process and increase the chance of errors.

**Work in stages, not all at once.** Rather than asking for trimming, transitions, text, color correction, and export in a single prompt, break your edit into steps. Trim first, preview, then add effects. This gives you checkpoints to catch mistakes early.

**Use specific timecodes.** Instead of saying 'cut the boring part at the start,' say 'trim from 0:00 to 0:12.' The more precise your instructions, the cleaner your output. Vague requests produce vague results.

**Export for your platform.** Different platforms have different sweet spots. For TikTok and Instagram Reels, export at 1080x1920 (vertical, 9:16). For YouTube, use 1920x1080 (horizontal, 16:9). Always specify your target platform when requesting an export so the skill can automatically apply the right resolution and aspect ratio.
