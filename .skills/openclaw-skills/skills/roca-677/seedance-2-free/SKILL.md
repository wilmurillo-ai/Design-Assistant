---
name: seedance-2-free
version: "1.0.0"
displayName: "Seedance 2 Free Video Generator — Create Stunning AI Videos From Text or Images"
description: >
  Turn simple text prompts or still images into fluid, cinematic AI-generated videos with seedance-2-free. This skill taps into ByteDance's Seedance 2 free-tier model to produce smooth, high-quality video clips without complex setup. Whether you're a content creator, marketer, or storyteller, you can generate expressive motion video from a single description or photo — fast, free, and surprisingly polished.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to the Seedance 2 Free video generator — describe a scene or share an image and I'll turn it into a smooth AI-generated video clip. Ready to create? Tell me what you want to bring to life!

**Try saying:**
- "Generate video from my product photo"
- "Animate this still image scene"
- "Create cinematic clip from description"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Generate Real Video Motion From Words and Images

Seedance 2 Free brings ByteDance's powerful video generation model to your fingertips — no rendering farm, no expensive software, no steep learning curve. Just describe a scene or upload a reference image, and this skill transforms your input into a short, cohesive video clip with natural motion and visual consistency.

The seedance-2-free model is particularly strong at preserving subject identity across frames, making it ideal for product showcases, character animations, and scene visualizations. Unlike older AI video tools that produce choppy or dreamlike results, Seedance 2 delivers footage that holds together visually — movement feels grounded and purposeful.

Whether you're prototyping a commercial concept, building social media content, or exploring creative storytelling, this skill gives you a fast lane from idea to moving image. You don't need to be a filmmaker or animator — just bring your concept and let the model handle the motion.

## Routing Text and Image Prompts

When you submit a request, ClawHub reads whether you've provided a text prompt, a source image, or both, then routes your generation job to the appropriate Seedance 2 Free pipeline endpoint automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance 2 Free API Reference

Seedance 2 Free runs on a cloud-based diffusion backend that queues your video generation job, processes frame synthesis remotely, and streams the finished MP4 back to your session once rendering completes. Because processing happens server-side, generation times vary with queue depth and clip length.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-2-free`
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

## Use Cases

Social media creators use seedance-2-free to produce scroll-stopping short clips for Instagram Reels, TikTok, and YouTube Shorts without hiring a video production team. A single well-crafted prompt can yield content that looks intentionally shot.

Marketers and brand teams use it to prototype video ad concepts before committing to a full shoot. Visualizing a campaign idea as a rough AI clip saves time in stakeholder reviews and creative briefings.

Game developers and indie storytellers use the image-to-video feature to animate concept art, bringing characters and environments to life during early production phases. It's a fast way to pitch a visual tone or test an animation direction.

Educators and presenters use it to create illustrative video snippets that make abstract concepts tangible — a chemical reaction, a historical scene, a physical process — without sourcing stock footage.

## Tips and Tricks

When writing prompts for seedance-2-free, always include a camera movement descriptor — words like 'zoom in,' 'tracking shot,' 'static wide angle,' or 'aerial descent' give the model a strong motion anchor and dramatically improve output coherence.

For image-to-video, use clean, well-lit source images with a clear subject. Busy backgrounds or low-contrast photos tend to produce muddier motion. Cropping your image to focus on the key subject before uploading often yields sharper animation.

Keep your subject description early in the prompt. The model weights the beginning of your text more heavily, so lead with what matters most: 'A silver robot walking through a foggy forest at dawn' will outperform 'At dawn, in a foggy forest, there is a silver robot walking.'

If the generated clip has the right look but wrong motion speed, try adding 'slow motion,' 'time-lapse,' or 'real-time' explicitly — seedance-2-free responds well to pacing cues embedded directly in the prompt.

## Common Workflows

The most common workflow with seedance-2-free starts with a detailed text prompt. Users describe the subject, environment, lighting, and motion style — the more specific, the better the output. For example, specifying 'slow dolly push toward a candlelit dinner table' yields far more intentional results than 'dinner table video.'

Image-to-video is the second major workflow. Drop in a still photo — a product shot, a portrait, a landscape — and the model generates believable motion around it. This is particularly useful for e-commerce teams animating product imagery or photographers adding life to portfolio shots.

Many creators also use seedance-2-free iteratively: generate a first clip, refine the prompt based on what worked, and regenerate until the motion and composition match their vision. Treat it like a creative loop, not a one-shot tool.
