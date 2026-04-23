---
name: video-trimmer
version: "1.0.8"
displayName: "Video Trimmer — Cut and Export MP4 Clips Free, No Watermark"
description: >
  The video-trimmer skill handles the most common editing request on ClawHub — cutting a long recording down to just the usable parts and exporting a clean MP4. Tell it your start and end timestamps (like 0:14 to 2:47) and it trims the clip, no fluff. Ideal for YouTubers, TikTok creators, and anyone who needs to shorten footage fast — think clip cutter, video splitter, or quick-trim tool all rolled in. Output stays at your source resolution, up to 4K.
metadata: {"openclaw": {"emoji": "✂️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Drop your video file and tell me the start and end timestamps — I'll trim it to a clean MP4. No file yet? Just describe what you want cut.

**Try saying:**
- "trim my video from 0:30 to 2:45 and export as MP4"
- "cut out the first 10 seconds of my clip no watermark"
- "remove middle section of video between 1:20 and 3:00"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Cut Raw Footage Down to a Clean MP4

Drop your video file and give the trimmer two timestamps — a start point and an end point. It cuts exactly there and hands back an MP4. No re-encoding guesswork, no fiddling with a timeline.

Say you've got a 45-minute Zoom recording and you only need the 3-minute product demo at the 12:30 mark. You'd say: 'Trim from 12:30 to 15:30.' Done in under 60 seconds.

The skill also handles multi-cut requests — ask it to remove a dead-air section in the middle and keep the rest. It processes the segments in order and stitches them into one continuous MP4 file at the original frame rate.

## Trim Request Routing Logic

Your start/end timestamps and uploaded MP4 filename get parsed into a trim job that routes to the correct processing queue based on file size — files under 500MB go to the fast queue, larger ones to the batch queue.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Render Pipeline Technical Notes

Trim jobs run on cloud GPU instances using FFmpeg with `-ss` and `-to` flags for frame-accurate cuts; the output container is re-muxed, not re-encoded, so a 2-minute clip from a 1-hour file exports in under 4 seconds. No watermark is applied at any stage of the pipeline — the output MP4 is byte-for-byte clean.

All calls go to `https://mega-api-prod.nemovideo.ai`. The main endpoints:

1. **Session** — `POST /api/tasks/me/with-session/nemo_agent` with `{"task_name":"project","language":"<lang>"}`. Gives you a `session_id`.
2. **Chat (SSE)** — `POST /run_sse` with `session_id` and your message in `new_message.parts[0].text`. Set `Accept: text/event-stream`. Up to 15 min.
3. **Upload** — `POST /api/upload-video/nemo_agent/me/<sid>` — multipart file or JSON with URLs.
4. **Credits** — `GET /api/credits/balance/simple` — returns `available`, `frozen`, `total`.
5. **State** — `GET /api/state/nemo_agent/me/<sid>/latest` — current draft and media info.
6. **Export** — `POST /api/render/proxy/lambda` with render ID and draft JSON. Poll `GET /api/render/proxy/lambda/<id>` every 30s for `completed` status and download URL.

Formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-trimmer`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

Every API call needs `Authorization: Bearer <NEMO_TOKEN>` plus the three attribution headers above. If any header is missing, exports return 402.

Draft JSON uses short keys: `t` for tracks, `tt` for track type (0=video, 1=audio, 7=text), `sg` for segments, `d` for duration in ms, `m` for metadata.

Example timeline summary:
```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

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

## Video Trimmer Best Practices — Get the Cleanest Cut

Always give timestamps in HH:MM:SS or MM:SS format — '1:24:10' is unambiguous, '84 minutes in' is not. The trimmer reads exact numbers, so be specific.

If your source file is 1080p, the output MP4 stays 1080p. There's no automatic downscaling unless you ask for it. Want a smaller file size? Say '720p export' explicitly and the trimmer re-encodes at that resolution instead.

For multi-segment cuts — like keeping clips at 0:10–0:45 and then 2:00–3:30 from the same file — list both ranges in one message. The trimmer processes them as a batch and returns a single stitched MP4, not two separate files. That saves a re-upload step.

## Video Trimmer Use Cases — YouTubers, Clips, and Reels

YouTubers use this skill the most — specifically for cutting intros off repurposed content or trimming a 20-minute vlog down to a 8-minute highlight cut before upload.

TikTok and Reels creators need clips under 60 seconds, so the video-trimmer is basically a daily tool. Feed it a longer clip, give it a 0:00–0:58 range, and the short-form cut is ready to post.

Podcast editors also show up here — they upload the video recording of an episode and use the clip cutter to extract a 90-second highlight for social. One MP4 in, one shareable clip out, no extra software. It's a clean 3-step process: upload, timestamp, download.

## Troubleshooting Your Video Trim — Common Issues Fixed

If the output MP4 has no audio, the source file's audio track is likely in a format that got dropped during the cut. Re-upload and add 'keep audio as AAC' to your request. That forces the trimmer to transcode the audio track rather than copy it.

Getting a black frame at the cut point? That's a keyframe alignment issue — it happens with heavily compressed files like screen recordings at 30fps. Ask for a 'keyframe-accurate trim' and the skill adjusts the cut to the nearest keyframe within 2 frames of your timestamp.

File too large to upload? The upload cap is 500MB. Compress the source to under that threshold first, then trim — the output MP4 will be proportionally smaller once the unwanted footage is gone.
