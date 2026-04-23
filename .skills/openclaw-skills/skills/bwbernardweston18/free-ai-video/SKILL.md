---
name: free-ai-video
version: "1.0.0"
displayName: "Free AI Video Generator — Create Stunning Videos From Text or Ideas Instantly"
description: >
  Tell me what you need and I'll help you create, edit, or enhance videos using free AI-powered tools — no expensive software required. This free-ai-video skill connects you with the best zero-cost AI video platforms, guiding you from concept to finished clip. Whether you're a content creator, educator, marketer, or hobbyist, get help scripting, generating, captioning, and exporting videos without spending a dime.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! I help you create real videos using free AI tools — no subscriptions, no software downloads, no prior experience needed. Tell me what kind of video you want to make and let's get started right now.

**Try saying:**
- "Generate a video from my script"
- "Add captions to this video free"
- "Make a promo video no budget"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Any Idea Into a Real Video — Free

Creating videos used to mean expensive software, steep learning curves, or hiring a production team. With free AI video tools, that barrier is gone — and this skill is your guide to using them effectively. Whether you want to generate a video from a text prompt, animate a still image, add voiceover to a slideshow, or auto-caption a clip, there are free AI platforms built exactly for that.

This skill helps you figure out which free tool fits your specific goal, how to structure your prompt or input for the best output, and how to get from raw idea to shareable video as fast as possible. You don't need a background in video production. You just need to know what you want.

From short-form social content to explainer videos, product demos, and creative storytelling, free AI video generation has matured enough to produce results that genuinely impress. This skill walks you through the process step by step, tailored to exactly what you're trying to make.

## How Your Video Prompts Route

When you submit a text prompt or idea, ClawHub parses your input and routes it to the optimal free AI video generation model based on style, duration, and resolution parameters detected in your request.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All video synthesis runs on distributed cloud GPU nodes, so render jobs process asynchronously — your clip is queued, generated frame-by-frame, and returned as a streamable or downloadable file without any local processing on your device. Supported output formats include MP4 and WebM, with resolutions scaling up to 1080p depending on the active free tier limits.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-ai-video`
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

## Use Cases for Free AI Video Generation

Free AI video tools cover a surprisingly wide range of real-world needs. Social media creators use them to produce Reels, TikToks, and YouTube Shorts without a camera or editing suite. Educators build animated explainer videos for lessons, turning dense text into engaging visual content students actually watch.

Small business owners create product showcases, promotional clips, and testimonial-style videos without hiring videographers. Nonprofits produce awareness campaign videos on zero budget. Job seekers even use AI video to create standout video resumes or portfolio presentations.

Developers and indie hackers use free AI video tools to mock up app demo videos before building the actual product. Writers use them to visualize scenes from their stories. The common thread is that free-ai-video tools democratize production — the idea matters more than the budget.

## Best Practices for Getting Great Results

Always start with a clear script or storyboard before generating anything. AI video tools respond best when you know exactly what each scene should convey — emotion, setting, characters, and pacing. A two-sentence scene description will outperform a one-word topic every time.

Batch your generations. Free plans typically come with limited credits or daily quotas, so plan your shots in advance and generate multiple variations in one session rather than iterating one clip over many days.

Combine tools for better results: use one free AI tool for video generation, another for voiceover (like ElevenLabs free tier), and a free editor like CapCut or DaVinci Resolve to stitch everything together. No single free tool does everything perfectly, but the combination is powerful.

Always export at the highest resolution the free tier allows, and check aspect ratio requirements for your target platform before generating — vertical for TikTok, horizontal for YouTube, square for Instagram feed.

## Troubleshooting Common Free AI Video Problems

One of the most frequent issues with free AI video tools is output quality being lower than expected. This usually comes down to vague prompts — the more specific your description of scene, mood, pacing, and style, the better the result. Instead of 'a nature video,' try 'a calm forest at sunrise with soft light filtering through trees, slow cinematic movement.'

Free tiers on platforms like Runway, Pika, or Kling often have watermarks or time limits. If watermarks are a dealbreaker, look for tools that offer watermark-free exports on free plans, such as certain versions of Canva's AI video or CapCut's AI features.

If your generated video has choppy motion or unnatural transitions, try reducing the scene complexity in your prompt or breaking your concept into shorter individual clips and combining them. Free AI video tools perform best on focused, single-scene prompts rather than multi-scene narratives in one generation.
