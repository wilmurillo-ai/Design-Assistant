---
name: ai-video-denoiser
version: "1.0.0"
displayName: "AI Video Denoiser — Remove Grain, Noise & Artifacts from Any Footage"
description: >
  Tell me what you need and I'll help you clean up noisy, grainy, or visually degraded video footage using ai-video-denoiser. Whether you shot in low light, used a high ISO setting, or recorded with a budget camera, this skill analyzes your footage and guides you through removing visual noise, compression artifacts, and grain — without washing out detail or softening important edges. Built for filmmakers, content creators, and video editors who need cleaner results fast.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to AI Video Denoiser — your go-to tool for removing grain, noise, and compression artifacts from video footage. Share your footage details or describe your noise problem and let's get your video looking clean and professional.

**Try saying:**
- "Remove grain from low-light footage"
- "Fix compression artifacts in my clip"
- "Denoise without losing sharp details"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Clean Footage, Zero Grain — Restore Every Frame

Noisy video is one of the most frustrating problems in post-production. Whether it crept in from a dark shooting environment, an older camera sensor, or heavy compression from a streaming platform, grain and noise can make otherwise great footage look unprofessional. The AI Video Denoiser skill is designed to help you tackle this problem directly — without needing a film school background or an expensive suite of plugins.

This skill walks you through identifying the type of noise in your video (luminance, chroma, or compression artifacts), choosing the right denoising approach for your footage type, and applying settings that preserve fine detail like hair, textures, and skin tones. It's not a one-size-fits-all filter — it's a guided process tailored to your specific clip.

Content creators uploading to YouTube, indie filmmakers working with mirrorless cameras, and archivists restoring old recordings all face different noise challenges. This skill speaks to all of them, offering practical, footage-specific guidance that gets your video looking sharp, clean, and ready for delivery.

## Routing Denoising Requests Intelligently

Each request — whether targeting temporal noise, chroma grain, compression artifacts, or luminance flickering — is parsed and routed to the appropriate denoising pipeline based on detected footage characteristics and user-specified parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

The backend leverages a GPU-accelerated cloud inference engine trained on multi-frame temporal analysis, applying adaptive noise reduction across spatial and frequency domains without degrading fine edge detail or motion sharpness. Frame batches are processed asynchronously, with per-frame denoise strength dynamically calibrated to your source footage's noise profile.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-denoiser`
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

## FAQ

**Will denoising make my footage look soft or blurry?** It can, if applied too aggressively. The key is balancing noise reduction strength with a light sharpening pass afterward to recover edge definition. This skill helps you find that balance for your specific footage.

**What's the difference between luminance and chroma noise?** Luminance noise appears as grainy brightness variation — similar to film grain. Chroma noise shows up as random colored speckles, usually green and magenta. They require different treatment settings, and many tools let you adjust them independently.

**Can I denoise footage that's already been exported or compressed?** Yes, but results depend on how heavily compressed the source is. Very low-bitrate files have lost data permanently, so denoising can reduce visual distraction but can't fully restore lost detail.

**Does this work on all video formats?** The denoising guidance works across common formats — MP4, MOV, MXF, and others. The specific tools you use may have format limitations, but the technique recommendations remain consistent regardless of container format.

## Common Workflows

The most frequent use case for AI Video Denoiser is cleaning up low-light footage — think indoor events, night shoots, or candlelit scenes recorded at ISO 3200 and above. The workflow here typically involves separating luminance noise (the grainy texture) from chroma noise (the colored speckles) and addressing each independently for the cleanest result.

Another common workflow is artifact removal from compressed video — footage that's been exported at low bitrates, downloaded from social media, or re-encoded multiple times. These clips develop blocky, macroblocked patches especially in smooth gradients like skies or skin. The denoising approach here is different from grain removal and requires targeted artifact-reduction techniques.

For archival and restoration work, users often bring in old camcorder or VHS footage with a mix of tape noise, scan lines, and analog distortion. This workflow involves layered denoising passes combined with careful sharpening to recover usable detail without creating an overly processed, artificial look.

## Tips and Tricks

Always work on a copy of your original footage. Denoising is a destructive process in many workflows, and having your raw files intact means you can re-approach the settings if the result looks over-smoothed or unnatural.

Avoid over-denoising — it's one of the most common mistakes. Pushing noise reduction too hard removes the natural texture that makes footage look real. Skin tones, fabric, and foliage all need a degree of micro-detail to look believable. Start conservative and increase strength only where you need it.

Use masking or selective denoising when possible. Backgrounds and out-of-focus areas can handle aggressive noise reduction, while subjects in sharp focus benefit from lighter treatment. This approach dramatically improves output quality compared to applying a single global setting.

If your editing software supports temporal denoising (analyzing multiple frames over time), use it — it's far more effective than spatial-only denoising for video because it leverages motion consistency to distinguish true detail from random noise.
