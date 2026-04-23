---
name: free-ai-video-editor-online
version: "1.0.0"
displayName: "Free AI Video Editor Online — Edit, Enhance & Export Videos Instantly"
description: >
  Turn raw footage into polished, share-ready videos without downloading software or paying a subscription. This free-ai-video-editor-online skill helps creators, marketers, and students trim clips, add captions, apply transitions, adjust pacing, and generate scene suggestions — all through simple text commands. Whether you're cutting a highlight reel or repurposing long-form content into short clips, get professional results fast.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to your free AI video editor online — where rough clips become compelling content through smart, guided editing. Tell me about your footage and what you're trying to create, and let's start building your video right now!

**Try saying:**
- "Cut this down to 60 seconds"
- "Write captions for my video"
- "Convert landscape video to vertical"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Edit Videos Smarter — No Software, No Cost

Most people don't need a Hollywood editing suite — they need something that works right now, in a browser, without a learning curve. This skill brings the power of AI-assisted video editing into a simple conversation. Describe what you want your video to look like, and get back a clear editing plan, script for captions, cut list, or export-ready instructions tailored to your platform.

Whether you're a content creator trimming a 10-minute vlog into a punchy 60-second reel, a small business owner adding text overlays to a product demo, or a student assembling a presentation video, this tool adapts to your goal. You don't need to know timecodes or layer-based editing — just explain what you're working with and what you want to achieve.

The skill is especially useful for generating caption text, writing scene-by-scene cut instructions, suggesting background music moods, and structuring video scripts for voiceover. It's your free AI video editing co-pilot, available instantly online with zero setup required.

## Routing Edits to AI Engine

Each edit request — whether trimming clips, applying filters, generating captions, or upscaling resolution — is parsed by the intent router and dispatched to the matching AI processing pipeline in real time.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

The free AI video editor online backend runs on a distributed cloud rendering cluster that handles transcoding, frame interpolation, and generative enhancement through RESTful API calls — no local GPU required. Requests are queued, processed asynchronously, and returned as streamable output URLs once rendering completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-ai-video-editor-online`
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

## Integration Guide — Using Free AI Video Editor Online With Your Workflow

This skill fits naturally into browser-based video editing tools like CapCut Web, Clipchamp, or Adobe Express. Use the AI to generate your editing script and caption text first, then paste the output directly into your chosen editor's caption or text overlay panel — saving the manual transcription step entirely.

For creators working with tools like DaVinci Resolve or Final Cut Pro, use this skill to generate a cut list with approximate timecodes and scene descriptions. Export that list as your editing roadmap before you open your timeline, which dramatically reduces decision fatigue during the actual edit.

Content teams can integrate this skill into their publishing pipeline by using it to batch-generate caption variations for A/B testing across platforms. Generate three different caption styles for the same video clip and test engagement across TikTok, Instagram, and YouTube Shorts simultaneously.

For social media schedulers like Buffer or Later, use the skill to produce platform-optimized video descriptions, hashtag sets, and thumbnail text suggestions alongside your editing plan — turning one session into a complete content package ready for publishing.

## Troubleshooting Common Free AI Video Editor Online Issues

If the editing plan you receive doesn't match your footage length or format, the most common fix is to provide more specific details upfront — include your video's total duration, the platform you're editing for (YouTube, TikTok, Instagram Reels), and the aspect ratio of your original file.

For caption generation, if the text feels off-tone or too formal, specify your audience and content style (e.g., 'casual Gen Z humor' or 'professional B2B explainer'). The AI adjusts its language register based on context you provide.

If you're getting cut suggestions that seem too aggressive or too conservative, describe the emotional pacing you want — 'fast and energetic' versus 'slow and documentary-style' makes a significant difference in how the editing structure is recommended.

For export format questions, always mention the destination platform first. Each platform has different resolution, bitrate, and duration requirements, and specifying this upfront ensures the guidance you receive is immediately actionable rather than generic.
