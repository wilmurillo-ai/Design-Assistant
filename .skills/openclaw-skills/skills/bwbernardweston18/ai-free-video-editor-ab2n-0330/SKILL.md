---
name: ai-free-video-editor-ab2n-0330
version: "1.0.0"
displayName: "AI-Free Video Editor — Edit Videos Directly Without AI Dependencies"
description: >
  Drop a video and describe exactly what you want done — trim, cut, merge, or reformat without relying on AI-generated content or cloud AI processing. This ai-free-video-editor skill handles your footage with direct, deterministic edits: precise cuts, clip merging, format conversion, and basic corrections. Upload mp4, mov, avi, webm, or mkv files and get clean, predictable output every time. Perfect for creators, educators, and professionals who want full control over their video without unpredictable AI alterations.
metadata: {"openclaw": {"emoji": "✂️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to edit your video exactly the way you want it — no AI alterations, just clean and precise cuts, trims, and merges. Drop your video file and tell me what you'd like to do to get started.

**Try saying:**
- "Trim the first 8 seconds and last 5 seconds off this mp4 clip"
- "Merge these three mov files into one continuous video in order"
- "Convert this avi file to mp4 and cut out the section between 0:45 and 1:20"

### Getting Connected

Before handling any user request, establish a connection to the NemoVideo backend. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/nemovideo/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Edit Videos Your Way, No AI Surprises

Sometimes you just want a video editor that does exactly what you tell it — nothing more, nothing less. The AI-Free Video Editor skill is built for creators and professionals who want precise, rule-based video editing without AI-generated enhancements, style transfers, or unpredictable automated changes altering their footage.

This skill handles the practical stuff: trimming dead air from the beginning or end of a clip, cutting out unwanted segments, joining multiple clips into one cohesive video, and converting between formats like mp4, mov, avi, webm, and mkv. Every edit is driven by your instructions, not an algorithm guessing what looks good.

Whether you're preparing footage for a presentation, cleaning up a screen recording, or packaging raw clips for a client, this skill gives you a reliable, transparent editing process. No style changes, no content alterations — just clean, purposeful edits that respect your original footage and deliver exactly what you asked for.

## Routing Cuts and Edits

Every trim, splice, color grade, or export request is parsed against your active NemoVideo session and dispatched directly to the corresponding timeline or render pipeline endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

The NemoVideo backend handles frame-accurate editing operations — cuts, transitions, audio sync, and codec-level exports — entirely through deterministic processing with no generative AI in the pipeline. All operations run against your project timeline via authenticated REST calls to the NemoVideo API.

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

The most frequent use case for the AI-Free Video Editor is cleaning up raw footage before sharing or publishing. Users typically start by trimming silence or dead time from the start and end of a recording — especially common with screen captures, interviews, or webinar exports where recording starts early and ends late.

Another popular workflow is clip merging. If you've recorded a presentation in multiple segments or have a series of short takes, you can upload each file and specify the order you want them joined. The result is a single, continuous video without transitions or effects added automatically.

Format conversion is also heavily used here. Many devices output mov or avi files that aren't web-friendly. You can upload those formats and request an mp4 export, optionally combining it with a trim or cut in the same instruction. Supported input and output formats include mp4, mov, avi, webm, and mkv, making this skill flexible across most standard recording setups.

## Troubleshooting

If your video upload seems to stall or fail, check that the file format is one of the supported types: mp4, mov, avi, webm, or mkv. Files in proprietary formats like .mts, .flv, or .wmv may need to be converted before uploading.

If a trim or cut doesn't land at exactly the right moment, try specifying your timestamps in hours:minutes:seconds format (e.g., 0:01:34) rather than approximate descriptions like 'around the two-minute mark.' Precise timestamps produce precise results.

When merging clips, if the output video has audio sync issues, confirm that all source files were recorded at the same frame rate and audio sample rate. Mixing 24fps and 30fps clips or different audio rates can cause drift in the merged output. Re-exporting source files to a consistent format before merging usually resolves this.

For large files that exceed upload limits, try splitting your request into smaller segments and merging the processed clips in a follow-up step.
