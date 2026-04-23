---
name: ai-free-video-editor
version: "1.0.0"
displayName: "AI-Free Video Editor — Edit Videos Simply Without AI Processing"
description: >
  Tell me what you need and I'll help you edit your videos without relying on AI-generated effects or automated processing. This ai-free-video-editor skill gives you direct, manual control over your footage — trimming clips, adjusting audio, merging scenes, and exporting clean results. Built for creators who want predictable, transparent edits on their terms. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your AI-Free Video Editor — here to help you trim, merge, cut, and export your footage exactly the way you want it, no automated guesswork involved. Drop your video file and tell me what edit you need done today.

**Try saying:**
- "Trim my mp4 file to remove the first 15 seconds and the last 30 seconds"
- "Merge these three mov clips into one video in the order I provide"
- "Remove the audio track from my webm file and export it as a silent mp4"

### Getting Connected

Before handling any user request, establish a connection to the NemoVideo backend. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/nemovideo/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Take Full Control of Your Video Edits

Not every video project needs AI to make decisions for you. Sometimes you just want to cut a clip at a specific frame, merge two recordings without surprises, or strip out background audio — all without an algorithm guessing what you meant. That's exactly what this skill is built for.

The AI-Free Video Editor gives you precise, instruction-based editing where you describe what you want done and the tool executes it faithfully. No auto-enhancements, no style suggestions, no unsolicited filters. If you say trim the first 10 seconds, that's what happens. If you want to merge three clips in a specific order, they'll appear exactly as you arranged them.

This skill is ideal for journalists, educators, small business owners, and indie creators who need reliable, repeatable edits without the unpredictability of generative tools. Whether you're preparing a product demo, cleaning up a recorded meeting, or assembling a short film, you stay in the driver's seat from start to finish.

## Routing Your Edit Requests

Each request — whether trimming footage, merging clips, adjusting audio levels, or exporting in a specific format — is parsed and routed directly to the appropriate NemoVideo editing endpoint based on the operation type you specify.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

The NemoVideo backend handles all cut, splice, transcode, and render operations server-side without any AI inference pipeline — your footage is processed through deterministic editing logic, so what you input is exactly what gets output. Timeline edits, codec settings, and frame-accurate cuts are executed via direct API calls to NemoVideo's processing engine.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-free-video-editor`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=ai-free-video-editor&skill_version=1.0.0&skill_source=<platform>`

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

## Common Workflows

One of the most frequent uses of the AI-Free Video Editor is cleaning up recorded meetings or webinars — trimming the awkward start, cutting dead air in the middle, and removing the post-meeting chatter at the end before sharing a recording with a team.

Another popular workflow is assembling multi-part recordings into a single deliverable. Creators who record in segments — whether due to file size limits or shooting in multiple takes — can merge their clips in sequence and export one cohesive file without re-encoding quality loss.

For social media repurposing, users often extract a short highlight clip from a longer video by specifying exact in and out points, then export in a web-optimized format like mp4. This is especially useful for pulling a 60-second excerpt from a 30-minute presentation to share on a business profile or embed on a website.

## Troubleshooting

If your exported file doesn't look right, the most common cause is a mismatch between the timestamp format you used and the actual video duration. Always double-check your clip's total length before specifying cut points — requesting a trim beyond the video's end time can result in a shorter-than-expected output.

For merge issues, confirm that all clips share the same resolution and frame rate when possible. Combining a 1080p clip with a 480p clip without specifying a target resolution may produce inconsistent results. Mention your preferred output resolution upfront to avoid this.

If an avi or mkv file fails to process, try re-uploading it — older codec versions in these containers occasionally cause compatibility hiccups. Converting to mp4 before uploading is a reliable workaround if the issue persists. When in doubt, describe the problem and the skill will guide you toward a solution.

## Quick Start Guide

Getting started with the AI-Free Video Editor is straightforward. Upload your video file in any supported format — mp4, mov, avi, webm, or mkv — and describe your edit in plain language. You don't need to learn any special syntax or commands.

For trimming, specify your start and end timestamps clearly (e.g., 'keep only 0:30 to 2:45'). For merging, list your files in the order you want them combined. For audio edits, describe whether you want to remove, replace, or adjust volume levels.

Once your edit is processed, you'll receive the output file ready for download. If you need a different format on export, just mention it upfront — for example, 'export as mp4 at 1080p'. The more specific your instructions, the more precisely your edit will match your expectations.
