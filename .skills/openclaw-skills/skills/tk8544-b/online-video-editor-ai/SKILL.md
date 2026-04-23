---
name: online-video-editor-ai
version: "1.0.0"
displayName: "Online Video Editor AI — Edit, Enhance & Export Videos Instantly Without Software"
description: >
  Tired of wrestling with complicated desktop software just to trim a clip or add a caption? online-video-editor-ai takes the friction out of video editing by letting you describe what you want in plain language and getting polished results fast. Cut footage, write scripts, generate captions, suggest music cues, reformat for social platforms, and craft compelling titles — all through a conversational interface built for creators, marketers, and small teams who need professional-quality output without a steep learning curve.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to your AI-powered video editing assistant — built to help you cut, caption, reformat, and polish videos without touching complicated software. Tell me what you're working on and let's get your video production-ready!

**Try saying:**
- "Trim my video to 60 seconds"
- "Write captions for product demo"
- "Reformat landscape video for TikTok"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit Videos Smarter — Just Describe What You Need

Most video editing tools demand you already know what you're doing. Timelines, keyframes, export codecs — the learning curve alone can kill your momentum before you've made a single cut. online-video-editor-ai flips that experience entirely. Instead of hunting through menus, you describe your goal in plain language and get back actionable editing instructions, scripts, captions, and creative direction you can apply immediately.

Whether you're repurposing a long-form interview into punchy social clips, adding subtitles to a product demo, or figuring out the best pacing for a YouTube intro, this skill walks you through every decision with context-aware guidance. It understands the difference between a TikTok hook and a LinkedIn explainer — and tailors its suggestions accordingly.

This isn't a one-size-fits-all template generator. It responds to your specific footage description, target audience, platform requirements, and creative vision. Think of it as having an experienced video editor in the room who speaks plain English and never charges by the hour.

## Routing Edits to the Right Pipeline

When you submit a prompt — whether it's a trim command, color grade request, subtitle burn-in, or AI scene cut — ClawHub parses the intent and routes it to the matching video processing endpoint automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All video operations run on a distributed cloud transcoding backend, meaning your timeline edits, AI enhancements, and export renders are processed server-side with no local GPU required. Requests are queued, encoded, and returned as streamable or downloadable output links via the API response payload.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `online-video-editor-ai`
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

## Best Practices for Getting the Most Out of Online Video Editor AI

The more specific you are about your footage, the sharper the output. Instead of saying 'edit my video,' describe the content type (interview, tutorial, vlog, ad), the target platform (YouTube, Instagram Reels, LinkedIn), and the desired length or mood. This context lets the skill tailor its editing recommendations precisely rather than offering generic advice.

When requesting captions or scripts, always mention your audience. A B2B SaaS explainer needs different language than a fitness motivation reel — and the skill adjusts tone, pacing cues, and vocabulary accordingly.

If you're repurposing content across multiple platforms, tackle one format at a time. Ask for the YouTube version first, then request a separate pass optimized for vertical mobile viewing. Batching platform-specific requests separately produces cleaner, more targeted results than asking for everything at once.

Finally, treat the first response as a draft. Paste back the section you want refined and ask for alternatives — the skill iterates quickly and can offer multiple creative directions for intros, CTAs, or transition suggestions until one fits your vision.

## Use Cases — Who Uses Online Video Editor AI and How

Content creators use online-video-editor-ai to break down long recordings into shareable clips, write timestamp descriptions for YouTube chapters, and generate hook scripts for the first five seconds of a Reel or Short — the make-or-break window for algorithm performance.

Marketing teams rely on it to repurpose webinar recordings into bite-sized social proof clips, draft lower-third text overlays for product videos, and align video pacing with ad campaign objectives. It's especially useful when a small team needs to produce high volumes of video content without a dedicated editor on staff.

Educators and course creators use it to structure tutorial scripts, suggest where to insert visual callouts or screen recording pauses, and generate accessible captions that match their teaching tone. It reduces the post-production bottleneck that often delays course launches.

Freelancers and agencies use it as a pre-edit planning tool — describing client footage and getting a proposed cut structure, B-roll placement suggestions, and music mood recommendations before opening their editing software. This saves hours of decision-making time on every project.
