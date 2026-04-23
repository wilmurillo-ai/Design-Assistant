---
name: auto-video-editor-ai
version: "1.0.0"
displayName: "Auto Video Editor AI — Intelligent Automated Video Editing & Post-Production Assistant"
description: >
  Tell me what you need and I'll handle the heavy lifting of video editing for you. auto-video-editor-ai is your on-demand editing assistant that transforms raw footage descriptions, scripts, and creative briefs into polished, structured video edit plans. Whether you're cutting a YouTube vlog, trimming a product demo, or assembling a short-form reel, this skill generates precise editing instructions, scene sequencing, caption suggestions, and transition cues — no timeline wrestling required. Built for content creators, marketers, and social media managers who want faster turnarounds without sacrificing quality.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your footage description, script, or video concept and I'll build you a detailed auto-video-editor-ai edit plan with cuts, transitions, captions, and pacing. No footage details? Just describe the style and platform you're targeting.

**Try saying:**
- "I have 12 minutes of raw interview footage and need a 3-minute YouTube highlight cut. The guest talks about startup funding. Give me a scene-by-scene edit plan with suggested cuts and where to add B-roll."
- "Create an editing plan for a 60-second Instagram Reel promoting a skincare product. It should open with a hook, show the product in use, include text overlays, and end with a CTA. Vertical format, upbeat pacing."
- "I filmed a 45-minute cooking tutorial and want to turn it into a 10-minute YouTube video. Help me structure the edit: which sections to keep, where to speed ramp, what captions to add, and how to handle the intro and outro."

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Edit Smarter, Not Harder — AI Does the Work

Raw footage sitting on your drive doesn't become content until someone edits it. That process — trimming dead air, sequencing scenes, writing captions, choosing transitions — eats hours that most creators and marketers simply don't have. Auto Video Editor AI changes that equation by turning your ideas, scripts, and footage descriptions into detailed, actionable editing plans you can execute immediately or hand off to an editor.

This skill understands the language of video production. Give it a rough outline of your footage and your target platform — TikTok, YouTube, Instagram Reels, LinkedIn — and it will generate a structured edit plan tailored to that format's pacing, aspect ratio requirements, and audience expectations. It suggests where to cut, where to add B-roll, what on-screen text to include, and how to open and close for maximum retention.

Whether you're a solo creator editing everything yourself or a team lead delegating post-production, Auto Video Editor AI becomes the first step in your workflow — the thinking layer that turns chaos into a clear, repeatable editing roadmap.

## Routing Cuts, Edits & Renders

Every request — whether you're trimming dead air, syncing B-roll, color grading a sequence, or exporting a final render — is parsed by the intent engine and dispatched to the appropriate editing pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All transcoding, timeline rendering, and AI-driven scene detection run on distributed cloud GPU nodes, meaning heavy exports and multi-track compositions process server-side without taxing your local machine. Requests are queued, prioritized by job type, and returned as streamable or downloadable output assets.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `auto-video-editor-ai`
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

## Integration Guide — Fitting Auto Video Editor AI Into Your Workflow

Auto Video Editor AI is designed to slot into the beginning of your post-production workflow, right after footage capture and before you open your editing software. Use it to generate your edit plan first, then execute that plan inside your preferred editor — whether that's DaVinci Resolve, Premiere Pro, CapCut, or a mobile app like InShot.

For teams, the edit plans generated by this skill make excellent briefing documents. Copy the output into your project management tool (Notion, Trello, Asana) and assign specific editing tasks to team members with clear instructions already written out. This eliminates back-and-forth between directors and editors about what the final cut should look like.

If you repurpose content across platforms, run the same footage description through multiple prompts — one for YouTube, one for TikTok, one for LinkedIn — to get platform-specific edit plans from the same source material. This multi-format approach saves hours compared to re-editing from scratch each time and ensures every version is optimized for its intended audience and format.

## Tips and Tricks for Getting the Best Edits

The more context you give Auto Video Editor AI, the more precise your edit plan will be. Instead of saying 'edit my video,' describe your footage in segments — for example, 'I have a 2-minute intro, 8 minutes of demo, and a 1-minute outro' — so the AI can make smart sequencing decisions based on real structure.

Always specify your target platform. A LinkedIn thought-leadership clip needs completely different pacing and text overlay strategy than a TikTok trend video. Mentioning your platform upfront means the edit plan will account for optimal video length, caption placement, and hook timing specific to that audience.

Use the skill iteratively. Start with a full edit plan, then ask follow-up prompts like 'rewrite the caption for the opening scene to be more punchy' or 'suggest three alternative ways to open this video.' Auto Video Editor AI works best as a back-and-forth collaborator, not a one-shot tool. The more you refine, the sharper your final output becomes.
