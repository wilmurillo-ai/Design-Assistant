---
name: video-caption-generator-ai-ab2n-0330
version: "1.0.0"
displayName: "Video Caption Generator AI — Auto-Generate Accurate Subtitles & Captions for Any Video"
description: >
  Tell me what you need and I'll generate precise, readable captions for your video in seconds. This video-caption-generator-ai skill transcribes spoken dialogue, formats it into timed subtitle blocks, and delivers clean caption files ready for publishing. Whether you're subtitling a tutorial, a short film, or social content, it handles mp4, mov, avi, webm, and mkv formats. Ideal for content creators, educators, and accessibility advocates who need accurate captions without the manual grind.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your Video Caption Generator AI — drop your video file and tell me what kind of captions you need, and I'll have timed, readable subtitles ready for you right away. Ready to get started?

**Try saying:**
- "Generate English captions for this mp4 interview and export them as an SRT file."
- "Create subtitles for my YouTube tutorial video and keep each caption line under 42 characters."
- "Transcribe the dialogue in this webm clip and add captions with a reading speed suitable for a general audience."

### Getting Connected

Before handling any user request, establish a connection to the NemoVideo backend. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/nemovideo/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Any Video Into a Captioned, Accessible Experience

Getting captions onto your videos used to mean hours of manual transcription, awkward timing adjustments, and expensive third-party services. This skill changes that entirely. Upload your video — whether it's a polished YouTube tutorial, a raw interview recording, or a social media clip — and the AI listens, transcribes, and formats captions with accurate timing so every word appears exactly when it's spoken.

Captions aren't just a nice-to-have anymore. They improve watch time, boost SEO discoverability, and make your content accessible to deaf and hard-of-hearing viewers, non-native speakers, and anyone watching without sound. This skill was built with that full picture in mind — not just dumping text on screen, but producing captions that feel natural and readable.

You stay in control throughout. Want captions in a specific language, formatted for a particular platform, or adjusted for reading pace? Just ask. The skill adapts to your content type, your audience, and your workflow — so you spend less time on logistics and more time creating.

## Caption Request Routing Logic

Every caption request — whether you're submitting a raw video file, a YouTube URL, or a pre-uploaded asset — gets parsed and routed to the appropriate transcription pipeline based on media type, language detection settings, and subtitle format preference.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles frame-accurate speech-to-text processing, applying speaker diarization and timecode alignment to produce SRT, VTT, or ASS caption files ready for direct embedding or export. Requests are authenticated via bearer token and processed asynchronously, with webhook callbacks delivering the completed caption payload once transcription and formatting are finalized.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-caption-generator-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=video-caption-generator-ai&skill_version=1.0.0&skill_source=<platform>`

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

## Troubleshooting

If your captions are coming out misaligned or missing words, the most common cause is poor audio quality in the source video. Background noise, overlapping speakers, or very low volume can confuse the transcription engine. Try uploading a version of the video with cleaner audio if possible, or let me know the problematic sections so I can focus on those specifically.

For videos with heavy accents, technical jargon, or domain-specific terminology, the first pass may not be perfect. You can paste in corrections or a glossary of key terms and I'll revise the caption file accordingly.

If your video file is very large (over 1GB), processing may take longer than expected. Formats like mkv with unusual codec configurations can occasionally cause issues — converting to mp4 first usually resolves this. If a file fails to process at all, describe the file details and I'll help you troubleshoot the specific issue.

## Performance Notes

Caption accuracy is highest when the source audio is recorded at 44.1kHz or above with minimal background noise and one primary speaker. Videos with clear, unaccented speech in English typically achieve the strongest out-of-the-box results, though the skill performs well across a wide range of languages and accents.

For longer videos — think webinars, full-length courses, or feature-length content — processing is handled in segments to maintain timing accuracy throughout. This means you may notice a brief delay before the complete caption file is returned, but it ensures the timestamps stay locked to the right moments even in a 90-minute video.

Caption line length and reading speed are automatically calibrated based on standard broadcast guidelines (roughly 17 characters per second for adult audiences), but you can override these defaults for specific platforms like TikTok or Instagram Reels, which benefit from shorter, punchier caption blocks.

## Quick Start Guide

Getting your first set of captions takes only a few steps. Start by uploading your video file — mp4, mov, avi, webm, and mkv are all supported. Then tell me the output format you need: SRT is the most universally compatible, but VTT works well for web players and ASS/SSA for more stylized caption overlays.

Next, specify your preferences: target language, maximum characters per line, and whether you want speaker labels if there are multiple people talking. If you have no strong preferences, just say 'default settings' and I'll apply sensible defaults for general-purpose captions.

Once the captions are generated, review the output and flag any sections that need adjustment. You can request changes like 'shorten the lines in the first two minutes' or 'fix the spelling of the product name throughout' and I'll update the file. The whole process from upload to finished caption file typically takes under two minutes for videos up to 30 minutes long.
