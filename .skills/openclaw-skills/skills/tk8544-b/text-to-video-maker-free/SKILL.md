---
name: text-to-video-maker-free
version: "1.0.0"
displayName: "Text to Video Maker Free — Turn Written Ideas Into Stunning Videos Instantly"
description: >
  Type a script, paste a blog post, or drop a few lines of text — and watch it transform into a shareable video in seconds. This text-to-video-maker-free skill converts written content into visually engaging clips complete with scenes, captions, and flow. Perfect for content creators, educators, marketers, and small business owners who need video output without expensive tools or steep learning curves.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Paste your script, article, or text idea and I'll turn it into a structured video with scenes, captions, and visual flow. No text yet? Just describe the video topic you have in mind.

**Try saying:**
- "Turn this 300-word blog post about morning routines into a 60-second video script with scene descriptions and on-screen text overlays."
- "I have a product launch announcement written out — can you convert it into a short promotional video breakdown with title cards and a call-to-action at the end?"
- "Create a step-by-step how-to video from this written tutorial about setting up a home office, including visual cues and caption suggestions for each step."

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# From Words on a Page to Videos Worth Watching

Most people have ideas worth sharing but no easy way to turn them into video. Writing comes naturally — editing timelines, sourcing footage, and syncing captions does not. That's exactly the gap this skill fills. Drop in your text, and it gets structured into a video-ready format with logical scene breaks, visual pacing suggestions, and caption overlays that make your message land.

Whether you're repurposing a LinkedIn post into a short-form video, turning a product description into a promotional clip, or converting a how-to guide into a step-by-step visual walkthrough, this skill handles the translation from words to watchable content. You stay in control of the message while the heavy lifting of structuring and formatting gets done for you.

This is built for people who create content regularly but don't have hours to spend in editing software. Bloggers, social media managers, teachers building course content, and indie entrepreneurs all use this kind of tool to move faster without sacrificing quality. Write it once, watch it become a video.

## Routing Your Video Generation Requests

When you submit a text prompt, ClawHub parses your scene descriptions, style preferences, and duration settings, then routes each request to the appropriate video synthesis pipeline based on complexity and output format.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

The text-to-video backend runs on a distributed cloud rendering cluster that converts your natural language scripts into frame sequences using diffusion-based video models. Each API call packages your prompt tokens, aspect ratio, and voiceover parameters before dispatching them to the generation queue for processing.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `text-to-video-maker-free`
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

## Performance Notes — Getting the Best Video Output

The quality of your video output scales directly with the clarity of your input text. Structured writing — with a clear beginning, middle, and end — produces cleaner scene breakdowns and more natural caption pacing. Bullet points, numbered lists, and short paragraphs all translate especially well into on-screen text and scene transitions.

For longer pieces like full articles or detailed guides, consider specifying a target video length upfront (e.g., '90-second video' or '3-minute walkthrough'). This helps the skill prioritize which sections become prominent scenes versus supporting context. Vague or stream-of-consciousness text can still be worked with, but a quick edit pass on your source copy before submitting will noticeably improve the structured output.

If your text includes brand-specific terminology, product names, or technical language, flag those in your prompt so they're preserved accurately in captions and title cards rather than paraphrased.

## Integration Guide — Fitting This Into Your Content Workflow

This skill works best as a mid-stage tool in your content pipeline — after you've written your copy but before you hand anything off to a video editor or AI video generation platform. Use it to produce a structured video brief, shot list, or scene-by-scene script that any editor or tool can immediately act on.

Pair it with AI video generators like Runway, Pictory, or InVideo by feeding them the structured scene output this skill produces. The scene descriptions, caption text, and pacing notes map directly to the input formats those platforms expect, cutting your setup time significantly.

For teams, this skill works well as a standardization layer — everyone submits their written content and receives consistently formatted video scripts, reducing back-and-forth between writers and video producers. It's also useful for building a content calendar: draft your weekly posts, convert them all to video outlines in one session, and queue them for production without juggling multiple tools.

## Use Cases — Who Gets the Most Out of This Skill

Content creators repurposing written articles into YouTube Shorts or Instagram Reels get the most immediate value — one piece of writing becomes multiple video formats without starting from scratch. Social media managers use it to convert brand copy and campaign messaging into structured video scripts ready for production or AI video tools.

Educators and course creators turn lesson notes and written guides into clearly segmented video outlines, making it easier to record or animate without improvising on camera. Small business owners who write their own product descriptions, FAQs, or announcements can quickly reshape that content into short promotional videos that feel polished and intentional.

Even journalists, newsletter writers, and podcasters with written transcripts find this skill useful for repurposing long-form content into digestible visual formats. If you write regularly and wish your content could live in more places, this skill closes that gap efficiently.
