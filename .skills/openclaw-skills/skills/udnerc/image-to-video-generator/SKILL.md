---
name: image-to-video-generator
version: "1.0.0"
displayName: "Image to Video Generator — Bring Still Photos to Life with AI Motion"
description: >
  Turn static images into dynamic, eye-catching videos in seconds with this image-to-video-generator skill. Upload a single photo or a series of images and watch them transform into smooth, animated video clips complete with motion effects, transitions, and customizable pacing. Built for content creators, marketers, and social media managers who need compelling video content without filming a single frame. Supports product photos, portraits, landscapes, and more.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! Ready to turn your photos into captivating videos? This image-to-video-generator skill can animate a single image or sequence an entire photo set into a polished video clip — just share your images and tell me what kind of video you're going for!

**Try saying:**
- "Take these 8 product photos and create a 15-second promotional video with smooth zoom transitions and a fast-paced rhythm suitable for Instagram Reels."
- "Animate this single portrait photo with a slow Ken Burns effect and a cinematic fade-in to make it feel like a movie still."
- "Turn my 12 travel photos from Japan into a 30-second highlight reel with a calm, flowing pace and soft cross-dissolve transitions."

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# From Still Frames to Stunning Video Stories

Most great visual stories start with a single photograph — a product shot, a travel photo, a portrait. But in today's content landscape, static images often get scrolled past while videos stop thumbs mid-swipe. That's exactly the gap this skill was built to close.

The image-to-video-generator skill takes your existing photos and breathes motion into them. Whether you're working with a single hero image or a curated collection of shots, the skill intelligently applies cinematic movement, smooth transitions, and timed sequencing to produce a video that feels intentional and professionally crafted — not like a slideshow your uncle made in 2007.

This is especially powerful for e-commerce brands showcasing products, real estate agents creating property tours, event photographers building highlight reels, or anyone who wants to repurpose their photo library into short-form video content for Instagram Reels, TikTok, YouTube Shorts, or presentations. No camera. No editing suite. Just your images and a prompt.

## Motion Request Routing Logic

When you submit a still image with a motion prompt, ClawHub parses your animation intent — camera movement, subject motion, or scene dynamics — and routes the request to the optimal AI video synthesis endpoint based on clip length, resolution, and motion complexity.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering Pipeline Reference

Image-to-video generation runs on a distributed GPU cloud backend that handles frame interpolation, temporal coherence, and diffusion-based motion synthesis entirely server-side — no local rendering required. Your source image is securely uploaded, processed through the motion model, and returned as a rendered video clip, typically in MP4 format.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `image-to-video-generator`
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

## FAQ

**How many images can I use at once?** You can work with anywhere from a single image up to a full collection. For longer sequences, providing a rough order or narrative direction helps produce a more cohesive result.

**What image formats work best?** High-resolution JPGs and PNGs produce the sharpest output. Blurry or heavily compressed source images will affect the final video quality, so starting with the best available files is recommended.

**Can I control the video length and pacing?** Yes — simply specify your target duration (e.g., '15 seconds', '30 seconds') and describe the pacing feel you want (fast-cut, slow and cinematic, rhythmic, etc.). The skill will adapt the timing accordingly.

**Can I add text, music, or voiceover to the generated video?** You can request on-screen text overlays and describe the tone or energy of background music you'd like suggested or paired. For voiceover, you can provide a script and request it be incorporated into the video sequence.

**What's the best use case for a single photo?** Single-image animation shines for creating eye-catching social posts, YouTube thumbnails with motion, or professional headshot animations where you want movement without a full video shoot.

## Common Workflows

**Single Image Animation:** The most straightforward use case — drop in one photo and request a specific motion style. Ken Burns (slow pan and zoom), parallax depth effects, and subtle drift motions work especially well for portraits, landscapes, and product hero shots. Great for thumbnails, intro sequences, or social media posts.

**Multi-Image Slideshow to Video:** Provide a batch of images in sequence and describe the story arc or mood you want. The skill will sequence them with appropriate transitions, pacing, and timing. Ideal for event recaps, portfolio showcases, real estate walkthroughs, or brand storytelling campaigns.

**Social Media Content Production:** Many creators use this skill on a weekly basis to repurpose photo content into Reels, Shorts, or Stories. You can specify aspect ratios (9:16 for vertical, 16:9 for landscape, 1:1 for square) and target durations to match platform requirements without manual reformatting.

**Presentation and Pitch Deck Enhancement:** Replace static image slides with short animated video clips to make decks more engaging. Upload your key visual assets and request subtle motion treatments that add polish without being distracting.
