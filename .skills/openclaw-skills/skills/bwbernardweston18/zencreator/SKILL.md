---
name: zencreator
version: "1.0.0"
displayName: "ZenCreator — AI-Powered Calm & Mindful Video Content Creation Suite"
description: >
  Tell me what you need and ZenCreator will help you craft thoughtful, polished video content designed for mindful creators and wellness brands. ZenCreator specializes in transforming raw footage into serene, purposeful videos — whether you're building meditation guides, yoga tutorials, or branded wellness content. Features include ambient pacing adjustments, soft transition curation, and tone-aware editing. Supports mp4, mov, avi, webm, and mkv formats. Built for creators who want their content to feel as intentional as their message.
metadata: {"openclaw": {"emoji": "🧘", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome to ZenCreator — your space for crafting intentional, calming video content that truly connects with your audience. Upload your footage or describe what you're working on, and let's build something meaningful together.

**Try saying:**
- "I have a 20-minute yoga session recorded in mp4 — can you help me trim it into a focused 10-minute beginner flow with smooth transitions?"
- "I want to create a short meditation intro video with a slow, calming pace and soft scene changes between nature clips I've recorded."
- "Can you help me structure my wellness brand's weekly content into a 3-minute highlight reel that feels cohesive and serene?"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Create Videos That Feel as Good as They Look

ZenCreator is built for a specific kind of creator — one who cares not just about what their video says, but how it makes viewers feel. Whether you run a wellness brand, teach mindfulness practices, or simply want your content to carry a sense of calm and intention, ZenCreator gives you the tools to shape your footage into something that resonates on a deeper level.

Unlike general-purpose video editors, ZenCreator understands the rhythm and pacing that mindful content demands. It helps you slow things down where it matters, layer in breathing room between segments, and ensure your visual story flows with the same ease you'd want your audience to carry away.

From solo creators recording morning yoga flows on their phones to small wellness studios producing professional course content, ZenCreator meets you where you are. Upload your raw footage in any major format and let ZenCreator help you shape it into content your audience will want to return to again and again.

## Routing Your Mindful Creation Requests

Every ZenCreator prompt — whether you're generating a breathwork visualization, a lo-fi study backdrop, or a guided meditation sequence — is parsed by intent and routed to the appropriate NemoVideo generation pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend API Reference

ZenCreator runs entirely on the NemoVideo backend, which handles video synthesis, ambient audio layering, and scene pacing optimized for calm, mindful content. All render jobs, asset queues, and style presets communicate directly through NemoVideo's API endpoints — no third-party processing involved.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `zencreator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=zencreator&skill_version=1.0.0&skill_source=<platform>`

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

## Frequently Asked Questions

**What types of content works best with ZenCreator?** ZenCreator is optimized for wellness, mindfulness, yoga, breathwork, meditation, and intentional lifestyle content. It understands the pacing and tone these genres require better than a general editor would.

**What video formats does ZenCreator support?** You can upload footage in mp4, mov, avi, webm, or mkv format — the most common formats used by phone cameras, DSLRs, and screen recorders alike.

**Can I use ZenCreator if I have no editing experience?** Absolutely. ZenCreator is designed to guide you through the process conversationally. Just describe what you want to achieve, and it will walk you through each step without requiring any prior editing knowledge.

**Does ZenCreator work for longer-form content like online courses?** Yes — ZenCreator can help you structure multi-segment course videos, ensuring consistent pacing and tone across all your lessons.

## Use Cases

**Yoga & Movement Instructors:** Turn a full recorded class into a clean, shareable tutorial by trimming transitions, removing dead air, and ensuring the pacing mirrors the natural flow of a practice — without losing the organic feel students love.

**Meditation & Breathwork Coaches:** ZenCreator helps you build guided audio-visual experiences where silence and stillness are treated as features, not problems to fix. Perfect for creating downloadable or streaming meditation content.

**Wellness Brands & Studios:** Use ZenCreator to produce consistent, on-brand video content for social media, websites, or digital courses — maintaining a calm, professional aesthetic across every piece you publish.

**Personal Development Creators:** Whether you're documenting a journaling practice, morning routine, or mindful travel experience, ZenCreator helps you shape personal footage into content that feels curated and intentional rather than raw and unpolished.

## Best Practices for ZenCreator

**Start with clear intention.** Before uploading your footage, spend a moment defining how you want your viewer to feel at the end of the video. Sharing that context with ZenCreator helps it make better pacing and transition decisions tailored to your goal.

**Record in natural light when possible.** ZenCreator's tone-aware editing responds well to footage with consistent, soft lighting — something natural light provides naturally. This makes color and mood adjustments more cohesive throughout your final piece.

**Batch your raw clips by theme.** If you're creating a series, upload clips grouped by session or topic. ZenCreator can maintain a consistent visual and emotional thread across multiple videos, giving your channel or course a unified identity.

**Describe your audience.** Whether you're speaking to stressed-out beginners or advanced practitioners, telling ZenCreator who you're creating for helps it calibrate pacing, segment length, and overall energy to match what your viewers actually need.
