---
name: ai-image-editor
version: "1.0.0"
displayName: "AI Image Editor — Smart Photo Editing, Retouching & Visual Enhancements in Seconds"
description: >
  Tell me what you need and I'll help you transform any image with precision and speed. This ai-image-editor skill handles everything from background removal and color correction to object removal, style transfers, and creative retouching — without requiring design experience. Whether you're a content creator cleaning up product photos, a marketer refreshing visuals, or someone who just wants a better-looking picture, describe your edit and get results fast.
metadata: {"openclaw": {"emoji": "🖼️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to your AI-powered image editing workspace — whether you want to remove a background, fix lighting, retouch a portrait, or completely reimagine a photo's style, just tell me what you're going for and we'll get it done. Drop your image and describe your edit to get started!

**Try saying:**
- "Remove background from product photo"
- "Fix the lighting on this portrait"
- "Make this image look cinematic"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Edit Any Image With Just a Description

Most image editing tools demand hours of learning curves, layer management, and manual adjustments. This skill flips that entirely — you describe the change you want, and it handles the execution. Want the background swapped to a clean white studio look? Need the lighting warmed up and the shadows softened? Just say so.

The ai-image-editor skill is built for people who care about the outcome, not the process. It understands natural language instructions and translates them into precise visual edits. Crop, recolor, retouch, resize, remove unwanted elements, enhance sharpness, or apply a completely new aesthetic — all through conversation.

It works equally well for quick fixes and complex transformations. A product photographer might use it to batch-standardize backgrounds, while a social media manager might use it to adapt a single image for multiple platform dimensions. Whatever your goal, the workflow stays simple: describe what you want, review the result, refine if needed.

## Routing Your Edit Requests

Each prompt you send — whether it's background removal, inpainting, style transfer, or upscaling — is parsed for intent and dispatched to the matching image processing pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All edits run through a cloud-hosted vision API that applies diffusion models, segmentation masks, and enhancement algorithms on the server side, so no heavy processing happens on your device. Rendered outputs are returned as high-resolution image URLs or base64 payloads depending on your configured response format.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-image-editor`
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

## Common Workflows

The most frequent use case for this ai-image-editor skill is product photography cleanup — sellers on platforms like Etsy, Shopify, or Amazon regularly need backgrounds removed, colors normalized, and images resized to spec. A single clear instruction handles what would otherwise take 20 minutes in Photoshop.

Portrait retouching is another high-demand workflow. Rather than manually masking skin or adjusting curves, users describe the look they want: 'soften the skin without losing texture,' 'reduce redness around the nose,' or 'make the eyes pop a little more.' The skill interprets these naturally and applies targeted adjustments.

Social media teams frequently use this skill to repurpose a single image across formats — cropping a 4:3 photo to a 9:16 Story, adjusting the focal point, and adapting the color palette for brand consistency. Describe the platform and the vibe, and the edits follow automatically.

## Integration Guide

This ai-image-editor skill fits naturally into content production pipelines. If you're managing a brand with recurring image needs — product launches, campaign assets, blog visuals — you can build a repeatable editing brief and apply it consistently across every image batch.

For teams, the skill works well as a first-pass editing layer before final human review. Feed in raw images with a standard prompt describing your brand's visual style, and receive consistently edited outputs ready for approval. This cuts review time significantly compared to starting edits from scratch.

If you're using ClawHub alongside other tools like Notion, Slack, or a CMS, you can paste image URLs or upload files directly within your workflow context. The skill accepts both uploaded files and linked images, making it easy to slot into wherever your content lives without switching between platforms.
