---
name: best-ai-video-generation
version: "1.0.0"
displayName: "Best AI Video Generation — Create Stunning Videos from Text, Images & Ideas"
description: >
  Turn your concepts, scripts, and raw assets into polished, publish-ready videos using the best-ai-video-generation tools available today. This skill helps creators, marketers, and teams generate high-quality video content — from cinematic scenes to social clips — without a production crew. Features include text-to-video prompting, style selection, scene structuring, voiceover pairing, and platform-specific formatting. Built for anyone who needs video output fast, without sacrificing quality.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your script, concept, or images and I'll craft the best AI video generation prompt to bring it to life. No assets? Just describe your video idea and we'll start from scratch.

**Try saying:**
- "I have a 200-word product description for a skincare brand — help me turn it into a 30-second AI-generated video with a clean, modern aesthetic for Instagram Reels."
- "Generate a detailed text-to-video prompt for a cinematic nature documentary intro showing a misty forest at dawn with slow camera movement and ambient sound cues."
- "I want to create an AI explainer video for a SaaS onboarding flow — help me structure the scenes, choose a visual style, and write generation prompts for each segment."

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Generate Professional Videos From Any Starting Point

Whether you have a fully written script, a rough idea, or just a handful of images, this skill transforms your input into compelling video content. Using the best AI video generation approaches available, it guides you through prompt crafting, scene sequencing, visual style selection, and output formatting — so your final video matches your vision and your platform.

This isn't a one-size-fits-all generator. The skill adapts to your specific use case — whether you're producing a product demo, a short-form social reel, an explainer video, a cinematic brand story, or a training module. You describe what you want, and the skill helps you build the most effective generation prompt or workflow to get there.

Creators who are new to AI video tools will find clear guidance on how to structure requests for maximum quality. Experienced users can go deeper — fine-tuning motion styles, aspect ratios, pacing cues, and narrative arcs. The goal is always the same: fewer iterations, better results, and video that actually gets used.

## Routing Your Video Prompts

Each request — whether text-to-video, image-to-video, or style transfer — is parsed and dispatched to the optimal generation model based on your input type, resolution target, and motion complexity.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Video Generation API Reference

All rendering jobs run on distributed GPU clusters in the cloud, handling diffusion sampling, temporal coherence, and frame interpolation server-side so your device never bottlenecks the output quality. Latency scales with clip duration, resolution, and the number of motion keyframes requested.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `best-ai-video-generation`
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

## Performance Notes

AI video generation quality varies significantly based on how prompts are structured. Vague inputs like 'make a cool video' produce inconsistent, generic results — while specific prompts that define subject, motion, lighting, mood, camera angle, and duration consistently yield higher-quality outputs across all major generation platforms.

This skill is optimized to help you extract the best performance from tools like Runway, Sora, Kling, Pika, and Luma by building prompts with the right level of detail. Longer videos (over 10 seconds) benefit from scene-by-scene breakdowns rather than single monolithic prompts. For character consistency across scenes, the skill will flag when you need to use reference images or seed locking features.

Expect the best results when you provide clear context: the platform you're publishing to, the audience you're targeting, and any brand style guidelines. The more specific your input, the fewer generation attempts you'll need to reach a usable final output.

## Integration Guide

This skill works as a prompt engineering and creative direction layer that sits in front of any AI video generation platform you're already using. You don't need to switch tools — you use this skill to build better inputs for the generator of your choice.

For teams using Runway Gen-3 or Kling, the skill produces motion-aware prompts that respect each platform's syntax preferences, including camera motion descriptors and negative prompt fields. For text-to-video workflows in Pika or Luma Dream Machine, it structures prompts around their scene duration limits and style tokens.

If you're building a content pipeline — for example, generating weekly social videos from a content calendar — this skill can help you create a reusable prompt template system so your outputs stay visually consistent across batches. Bring your content brief, brand guidelines, or existing video examples and the skill will reverse-engineer a repeatable generation framework for your team.
