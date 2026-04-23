---
name: gemini-ai-video-editor
version: "1.0.0"
displayName: "Gemini AI Video Editor — Intelligent Video Editing Powered by Google Gemini"
description: >
  Tell me what you need and I'll help you craft, refine, and transform your video content using gemini-ai-video-editor. Whether you're trimming footage, writing scene descriptions, generating edit scripts, or brainstorming creative cuts, this skill taps into Gemini's multimodal understanding to make video editing smarter. Built for creators, marketers, and storytellers who want AI-driven editing guidance without the guesswork.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to Gemini AI Video Editor — your AI-powered editing partner for smarter cuts, tighter scripts, and more compelling visuals. Tell me about your video project and let's start building something great together.

**Try saying:**
- "Write a YouTube intro script"
- "Suggest B-roll for my interview"
- "Cut this to 60 seconds"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Edit Smarter, Not Harder With Gemini AI

Video editing has always demanded both technical skill and creative instinct. Gemini AI Video Editor bridges that gap by giving you an intelligent collaborator that understands your footage, your goals, and your audience — all at once.

Whether you're working on a YouTube documentary, a product launch reel, a short-form social clip, or a full-length brand film, this skill helps you think through your edit structure, generate narration scripts, suggest pacing improvements, and describe visual transitions that actually serve your story. You don't have to be a professional editor to produce professional-quality results.

Gemini AI Video Editor is designed for creators who move fast and think visually. Describe your raw footage, share your timeline, or paste in your script — and get back actionable editing direction, creative suggestions, and polished copy that makes your final cut land harder.

## Routing Your Edit Requests

Every prompt you send — whether trimming a sequence, generating captions, or applying a color grade — is parsed by Gemini's multimodal understanding layer and routed to the appropriate editing pipeline based on intent, timeline context, and asset type.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Gemini API Backend Reference

Gemini AI Video Editor offloads all heavy compute — frame analysis, generative B-roll synthesis, audio-visual alignment — to Google's Gemini cloud backend via authenticated API calls, so your local machine never bottlenecks the render. Processing latency scales with clip length and the complexity of your prompt, not your hardware.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `gemini-ai-video-editor`
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

## Integration Guide for Gemini AI Video Editor

Gemini AI Video Editor works best as a creative layer on top of your existing editing workflow. Use it alongside tools like DaVinci Resolve, Adobe Premiere Pro, or CapCut — not as a replacement, but as your pre-edit planner and script generator.

Start your project by describing your raw footage to the skill and asking for an edit structure. Export that structure as a shot list or sequence outline, then use it to guide your actual timeline assembly in your editing software. This saves significant time during the rough cut phase.

For teams, Gemini AI Video Editor can serve as a shared creative brief generator. Have one team member run the footage description through the skill, generate a structured edit plan and narration draft, then hand that document off to editors and voiceover artists as a production reference.

Content creators running high-volume channels can use the skill to batch-generate intro scripts, outro CTAs, and chapter markers across multiple videos at once — keeping output consistent without burning creative energy on repetitive copy tasks.

## Best Practices for Gemini AI Video Editor

To get the most precise and useful output from Gemini AI Video Editor, give it as much context as possible about your footage. Instead of saying 'edit my video,' describe what you've shot: the number of clips, their approximate length, the mood you're going for, and your target platform (Instagram Reels, YouTube, LinkedIn, etc.).

When asking for scripts or narration, specify your tone — casual, authoritative, emotional, energetic — and mention your audience. A script for a B2B SaaS demo needs completely different pacing than one for a travel vlog or a nonprofit appeal.

For structural editing guidance, share your current timeline or scene list if you have one. Gemini AI Video Editor can identify pacing issues, flag redundant sections, and recommend where to place music breaks or visual emphasis points when it knows what you're working with.

Finally, iterate. Use follow-up prompts to refine suggestions — ask for a shorter version, a different tone, or alternative transition ideas until the direction feels exactly right.
