---
name: ai-video-editor-online
version: "1.0.0"
displayName: "AI Video Editor Online — Edit, Trim, and Transform Videos with Smart AI Tools"
description: >
  Tell me what you need and I'll help you edit your videos faster than any traditional timeline editor. This ai-video-editor-online skill handles everything from trimming clips and adding captions to reframing footage and generating scene descriptions. Whether you're a content creator racing a deadline, a marketer repurposing long-form video, or a small business owner making your first promo reel — no software downloads, no steep learning curve, just results.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your video details, a transcript, or a description of your footage and I'll give you edit suggestions, cut points, captions, or a full structure plan. No video file yet? Just describe what you're working on and what you want it to become.

**Try saying:**
- "I have a 15-minute product demo recording. Help me cut it down to a 90-second highlight reel for Instagram, focusing on the key features and a strong closing CTA."
- "Here's a transcript from my YouTube video — can you suggest where to add text overlays, chapter markers, and which sections feel too slow and should be trimmed?"
- "I'm editing a wedding video and need help writing lower-third captions for each speaker during the speeches. Here are their names and roles."

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Edit Smarter: AI That Actually Understands Your Video

Most video editing tools hand you a timeline and wish you luck. This skill works differently — you describe what you want, and the AI figures out how to get there. Want to cut a 10-minute interview down to the three best soundbites? Describe your goal and get a scene-by-scene breakdown with suggested cut points. Need captions that match your brand voice? Tell me the tone and the transcript does the heavy lifting.

The ai-video-editor-online skill is built for people who need professional-quality edits without professional-level software training. It's particularly useful for social media managers turning webinar recordings into short clips, educators breaking lectures into digestible segments, and indie filmmakers who want a second opinion on pacing before the final cut.

Beyond basic cuts and trims, this skill helps you think through structure — suggesting where to add B-roll, how to tighten a slow opening, or what text overlays would reinforce your message. Think of it as a video editor you can have a conversation with.

## Smart Request Routing Explained

When you submit an edit — whether trimming dead air, applying an AI color grade, or auto-generating captions — ClawHub parses your intent and routes it to the matching AI video processing pipeline based on task type, clip length, and output format.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All video transformations run through a distributed cloud rendering backend that handles frame extraction, model inference, and re-encoding in parallel — so heavy tasks like background removal or scene detection don't bottleneck your timeline. Requests are queued, processed asynchronously, and returned as a signed media URL once the render job completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-editor-online`
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

## Troubleshooting: When Results Don't Match What You Expected

If the edit suggestions feel too generic, the most common fix is adding more context upfront. Instead of saying 'trim this video,' try specifying the platform (YouTube vs. TikTok), the target audience, and the tone you're going for. The more the skill knows about your goal, the more targeted the output.

For caption or transcript work, accuracy improves significantly when you paste in the raw transcript yourself rather than asking the skill to guess from a description. Even a rough, unedited transcript gives the AI something concrete to work with.

If you're getting cut suggestions that don't reflect the actual content, try breaking your request into smaller pieces — one scene or segment at a time rather than the full video at once. This keeps the context tight and the suggestions more precise.

Finally, if you're working with technical formats (vertical vs. horizontal reframing, specific aspect ratios, or platform-specific specs), mention those requirements explicitly at the start of your prompt so the skill factors them into every recommendation it makes.

## Use Cases: What You Can Actually Do With This Skill

The ai-video-editor-online skill covers a wide range of real editing tasks that creators and professionals run into every week. Content repurposing is one of the most popular — take a 45-minute podcast recording and get a structured breakdown of the five best 60-second clips worth extracting for Reels or Shorts, complete with suggested captions and hook lines for each.

Marketers use it to audit video scripts before shooting, catching pacing issues or weak CTAs before they're baked into footage. Educators use it to outline lecture videos into timestamped segments with descriptive titles, making content more searchable and accessible.

Small business owners with no editing background use it to plan their first promotional video from scratch — describing their product, audience, and goal, then receiving a shot list, suggested music mood, and a rough cut structure they can hand off to a freelancer or follow themselves. Wherever you are in the editing process, this skill meets you there.
