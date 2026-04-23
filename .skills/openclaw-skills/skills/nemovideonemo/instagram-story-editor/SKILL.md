---
name: instagram-story-editor
version: "1.0.0"
displayName: "Instagram Story Editor — Craft Scroll-Stopping Vertical Stories from Any Video"
description: >
  Drop a video and describe the vibe you want — this instagram-story-editor skill transforms raw footage into polished, vertical-format Instagram Stories ready to post. Crop to 9:16, add bold captions, apply mood-matching color grades, overlay sticker-style text, and trim clips to the ideal 15-second punch. Works with mp4, mov, avi, webm, and mkv files. Built for creators, small businesses, and social media managers who need eye-catching Stories without a design degree.
metadata: {"openclaw": {"emoji": "📱", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your video into an Instagram Story that stops thumbs mid-scroll? Drop your clip, tell me the look and feel you're going for, and I'll handle the cropping, captions, and style — let's make something worth watching.

**Try saying:**
- "Crop this mp4 to vertical 9:16, add a bold yellow caption at the bottom saying 'New Drop Friday', and apply a cool-toned color grade"
- "Trim this clip to 15 seconds, add a countdown timer overlay in the top corner, and make it feel high-energy with fast cuts and vibrant colors"
- "Take this horizontal product video and reformat it for Instagram Stories — keep the product centered, add a swipe-up text prompt, and use warm pastel tones"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Any Clip Into an Instagram Story Worth Watching

Most video footage wasn't shot with Instagram Stories in mind — it's horizontal, unbranded, and way too long. This skill bridges that gap by intelligently reformatting your video for the vertical canvas that Stories demand, while giving you creative control over every visual detail.

Describe what you want in plain language: 'make it feel cinematic with warm tones and a countdown sticker,' or 'add bold white captions and cut it to 15 seconds for a product reveal.' The skill interprets your intent and applies the right crops, color treatments, text overlays, and pacing to match.

Whether you're promoting a weekend sale, sharing a behind-the-scenes moment, or building a personal brand, this tool helps you produce Stories that feel intentional and on-brand — not hastily cropped from a YouTube clip. No timeline scrubbing, no layer panels, no design software required. Just your footage, your words, and a Story that actually gets tapped.

## Story Request Routing Logic

Every prompt you send — whether you're asking to crop to 9:16, add animated text overlays, apply a cinematic filter, or trim a highlight reel — gets parsed and routed to the matching Story editing action automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles all vertical reformat processing, frame-safe cropping, and Story-optimized rendering under the hood. Requests hit the NemoVideo API endpoints directly, so output quality and export speed depend on your active session and credit balance.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `instagram-story-editor`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=instagram-story-editor&skill_version=1.0.0&skill_source=<platform>`

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

For the sharpest results, start with the highest-resolution version of your video — even if the final output is for mobile, more source detail means cleaner crops and text rendering. When describing your Story, be specific about where you want text placed (top, bottom, center) and what tone or color palette you have in mind.

Keep your Story content focused on a single message. Trying to pack too much into 15 seconds dilutes impact — one hook, one visual, one call-to-action is the sweet spot. If your clip is longer, mention the key moment you want to highlight and the skill will prioritize trimming around it.

For branded content, describe your brand colors or reference a mood (e.g., 'clean minimalist with navy and white') so the text and color grade stay consistent with your existing feed. Consistency across Stories builds recognition faster than any single viral post.

## Use Cases

This instagram-story-editor skill fits naturally into dozens of real-world workflows. Retailers can take a standard product demo video and reformat it into a punchy 15-second Story with a price overlay and a call-to-action prompt. Event organizers can trim highlight reels into vertical teasers with date and venue text baked in.

Content creators use it to repurpose YouTube or TikTok footage into Stories without losing the focal point during the crop. Fitness coaches, food bloggers, and travel influencers can quickly add branded caption styles and color filters that match their aesthetic across every post.

Small business owners who don't have a dedicated social media team find it especially valuable — they can go from raw phone footage to a publish-ready Story in minutes, maintaining a consistent visual identity without hiring a designer.

## Quick Start Guide

Getting started is straightforward. Upload your video file — mp4, mov, avi, webm, or mkv all work — and write a short description of what you want the finished Story to look like. You don't need to use technical terms; plain descriptions like 'bright and energetic with a sale announcement' give the skill enough direction to work with.

If you have specific requirements — exact caption text, a particular aspect ratio crop focus, or a specific clip duration — include those in your message. The more context you provide, the closer the first output will be to your vision.

Once you receive the edited Story, you can request adjustments: change the font style, shift the text position, tweak the color warmth, or re-trim to a different moment. Think of it as a fast back-and-forth with a social media editor who already knows Instagram's format rules inside and out.
