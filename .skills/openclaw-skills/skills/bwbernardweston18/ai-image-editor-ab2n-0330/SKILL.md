---
name: ai-image-editor-ab2n-0330
version: "1.0.0"
displayName: "AI Image Editor — Intelligent Photo Editing & Enhancement Powered by AI"
description: >
  Transform ordinary photos into polished, professional visuals with the ai-image-editor skill on ClawHub. This skill handles background removal, smart retouching, style transfers, color grading, object removal, and generative fill — all through natural language prompts. Whether you're a content creator cleaning up product shots or a designer iterating on concepts, ai-image-editor removes the repetitive manual work. Supports common image formats and works seamlessly inside your existing ClawHub workflows.
metadata: {"openclaw": {"emoji": "🖼️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your AI Image Editor — ready to help you retouch, transform, and perfect your photos using simple text prompts. Describe the edit you need and let's get started!

**Try saying:**
- "Remove the background from this product photo and replace it with a clean white studio backdrop"
- "Enhance the lighting and color grading on this portrait to give it a warm, cinematic look"
- "Erase the power lines from this landscape photo and fill in the sky naturally"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Edit Images Smarter, Not Harder with AI

The AI Image Editor skill brings professional-grade photo editing directly into your ClawHub workspace — no Photoshop expertise required. Simply describe what you want to change, and the skill interprets your intent and applies precise edits to your image. From removing a cluttered background to smoothing skin tones, adjusting white balance, or swapping out a sky, this skill handles the kind of tasks that used to take hours in a matter of seconds.

What makes this skill different from a standard filter or preset tool is its understanding of context. It doesn't just apply blanket adjustments — it reads the content of your image and makes targeted changes. Ask it to "make the product pop against a white background" or "give this portrait a warm golden-hour look" and it delivers results that feel intentional, not automated.

This skill is built for photographers, e-commerce teams, social media managers, graphic designers, and anyone who works with visual content at scale. Whether you're editing a single hero image or batching dozens of product photos, the AI Image Editor keeps your output consistent and your workflow moving.

## Routing Your Edit Requests

Each prompt you send — whether it's a background swap, style transfer, object removal, or upscale — is parsed and routed to the most appropriate AI editing pipeline based on detected intent and image context.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend powers every edit operation, handling diffusion-based inpainting, generative fill, and enhancement processing in real time. API calls are authenticated per session and metered against your active credit balance.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-image-editor`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=ai-image-editor&skill_version=1.0.0&skill_source=<platform>`

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

## Integration Guide

The AI Image Editor skill integrates directly into ClawHub workflows without any additional setup. Once enabled in your skill library, you can invoke it from any workflow node that handles image assets — simply pass the image file and your edit instruction as inputs.

For e-commerce teams, a common pattern is to connect the AI Image Editor to a product catalog pipeline: images are pulled from a storage bucket, processed through the skill for background removal and color normalization, then automatically pushed to a staging folder for review. This eliminates manual editing between catalog updates.

The skill also pairs naturally with the ClawHub Image Resizer and Watermark skills. A typical content workflow might run an image through the AI Image Editor for retouching, then resize it for multiple platforms, and finally apply a branded watermark — all in a single automated sequence.

Output images can be routed to any downstream node: file storage, email delivery, CMS publishing, or further AI processing. No manual file handling is required between steps.

## Performance Notes

The AI Image Editor skill performs best on high-resolution source images (1MP and above). Low-resolution or heavily compressed inputs may produce softer results, especially on tasks like background removal or fine detail retouching where edge precision matters.

Complex scenes with intricate hair, transparent objects, or overlapping subjects may require a follow-up prompt to refine the output. For best results with object removal, ensure the surrounding texture is relatively uniform — removing an object from a brick wall will yield cleaner results than removing one from a highly detailed, non-repeating background.

Generative fill tasks (replacing or extending parts of an image) are computationally heavier and may take slightly longer to process than basic adjustments like color grading or sharpening. Batch editing multiple images in sequence is supported, though processing time scales with image size and edit complexity.

## FAQ

**What image formats does the AI Image Editor support?**
The skill supports JPEG, PNG, WEBP, and TIFF formats. For transparency-preserving outputs (such as background removal), PNG is recommended as the export format.

**Can I apply multiple edits in a single prompt?**
Yes. You can chain instructions like "remove the background, brighten the subject, and add a subtle vignette" in one prompt. The skill will attempt all edits in sequence. For very complex multi-step edits, breaking them into two prompts often produces cleaner results.

**Will the skill alter the original file?**
No. The AI Image Editor always outputs a new edited version of your image. Your original file remains untouched in your workspace.

**Can I undo or iterate on an edit?**
Absolutely. Just describe what you'd like adjusted and the skill will apply a new round of edits to the previous output, or you can revert to the original and start fresh.
