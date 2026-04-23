---
name: free-ai-video-generation
version: "1.0.0"
displayName: "Free AI Video Generation — Create Stunning Videos From Text or Images Instantly"
description: >
  Drop a concept, script, or set of images and watch free-ai-video-generation turn your ideas into polished, shareable videos without spending a cent. This skill handles everything from text-to-video conversion and image animation to scene composition and voiceover sync. Built for creators, marketers, educators, and entrepreneurs who need professional-quality video output fast — no studio, no budget, no bottleneck.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! You're one prompt away from generating a real video — no software, no cost, no waiting. Describe your concept, share your images or script, and let's build something worth watching right now.

**Try saying:**
- "Generate video from my product photos"
- "Turn this script into a video"
- "Create a 60-second explainer video"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Ideas Into Videos Without Spending Anything

Most people assume high-quality video production requires expensive software, a creative team, or hours of editing. Free AI video generation flips that assumption entirely. With this skill, you describe what you want — a product showcase, a social media reel, an explainer clip — and the AI handles the heavy lifting: scene selection, transitions, timing, and visual style.

This isn't a template filler or a slideshow generator. The skill interprets your creative intent and builds video content that feels intentional and crafted. Whether you're starting from a written script, a pile of product photos, or just a rough idea typed into a prompt, the output is a cohesive video ready for publishing.

The target audience is broad by design: solo entrepreneurs promoting their brand, teachers creating lesson content, social media managers racing against a content calendar, and developers prototyping video features. Free access means no gatekeeping — anyone with an idea can produce something worth watching.

## Routing Your Video Prompts

When you submit a text prompt or source image, ClawHub parses your intent and routes the request to the optimal free AI video generation model based on content type, duration, and style parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All video synthesis jobs are offloaded to a distributed cloud rendering backend that queues your diffusion-based generation requests and streams the rendered MP4 output back once frames are fully composited. Latency varies by model — lightweight text-to-video pipelines typically resolve in under 60 seconds, while image-to-video with motion interpolation may take longer depending on queue depth.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-ai-video-generation`
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

## Best Practices

Structure your prompt like a brief to a video editor: mention the purpose (promotional, educational, entertaining), the intended platform (Instagram Reel, YouTube, LinkedIn), the desired length, and any visual preferences like color palette or mood. The more context you give, the closer the first output lands to your vision.

For image-based video generation, organize your photos in the order you want them to appear and describe any transitions or timing preferences. If you have a voiceover script, paste it alongside your visual inputs so the AI can sync narration to scene changes naturally.

Iterate quickly. Free AI video generation is designed for rapid prototyping — if the first version isn't quite right, refine one element at a time rather than rewriting the entire prompt. Small adjustments to pacing, tone, or scene order often produce dramatically different results.

## Performance Notes

Free AI video generation performs best when your input is specific. Vague prompts like 'make a cool video' produce generic results, while prompts that describe tone, pacing, audience, and visual style produce videos that feel intentional. The AI processes text prompts, image sequences, and script documents — mixing input types in a single request often yields the most dynamic output.

Render times vary based on video length and complexity. Short clips under 60 seconds typically process faster than multi-scene productions. If you're generating a video with voiceover sync or custom transitions, allow a few extra moments for the AI to align audio and visual layers properly. For best quality, provide high-resolution source images when available — the AI upscales where possible, but starting with clear assets always improves the final frame quality.

## Integration Guide

Free AI video generation fits naturally into existing content workflows without requiring any platform migration. If you're running a social media content calendar, use this skill to batch-produce video drafts for the week in a single session — describe each video concept in sequence and export each output for scheduling.

For e-commerce teams, the skill integrates cleanly into product launch pipelines. Feed it product photography and feature descriptions to generate ready-to-post video ads across multiple formats simultaneously. Pair it with a caption-writing tool to complete the full content package in one workflow.

Educators and course creators can use the skill to transform written lesson plans or slide decks into video summaries, making content accessible to visual learners without rebuilding materials from scratch. The output files are standard formats compatible with all major video hosting and editing platforms, so dropping generated videos into a larger production pipeline requires no conversion or reformatting.
