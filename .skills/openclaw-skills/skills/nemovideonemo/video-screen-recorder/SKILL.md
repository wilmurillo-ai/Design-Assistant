---
name: video-screen-recorder
version: "1.0.0"
displayName: "Video Screen Recorder — Capture, Annotate & Share Screen Recordings Instantly"
description: >
  Tired of juggling clunky software just to record your screen and share it? The video-screen-recorder skill lets you capture screen activity, trim recordings, add annotations, and export clean video files without the usual setup headache. Whether you're creating tutorials, bug reports, or product demos, this skill handles mp4, mov, avi, webm, and mkv formats. Built for developers, educators, and remote teams who need polished recordings fast.
metadata: {"openclaw": {"emoji": "🎥", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to capture your screen and turn it into a polished, shareable recording? Tell me what you'd like to record — a tutorial, a bug demo, a product walkthrough — and let's get started right now.

**Try saying:**
- "Record my screen for the next 5 minutes and export it as an mp4 with my mouse clicks highlighted"
- "Trim my screen recording to remove the first 30 seconds and the last 15 seconds, then save it as a webm file"
- "Add text annotations to my screen recording pointing out the key steps in the workflow I just captured"

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Record Your Screen, Share Your Story Effortlessly

Screen recording sounds simple until you're buried in software trials, codec errors, and files too large to share. The video-screen-recorder skill was built to cut through that friction. Whether you need to walk a colleague through a workflow, document a bug for your dev team, or produce a step-by-step tutorial for your audience, this skill gives you a clean, reliable way to capture exactly what's happening on screen.

You can record your full display, a specific application window, or a custom region — giving you precise control over what gets captured. Once recorded, you can trim the footage, add text callouts or highlight clicks, and export in your preferred format. No bloated timelines, no unnecessary complexity.

The skill is designed for people who need results quickly: educators building course content, product managers recording feature walkthroughs, support teams creating visual documentation, and developers logging reproducible bugs. If you've ever wished your screen recorder just worked without a learning curve, this is the skill you've been looking for.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Your Recording Requests

Every capture command — whether you're starting a full-screen recording, cropping a region, triggering annotation overlays, or exporting a shareable link — is parsed and routed to the matching NemoVideo endpoint based on intent and session context.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles real-time screen capture streams, frame-level annotation injection, and instant share-link generation via authenticated REST calls tied to your active recording session. All video data, timestamps, and annotation layers are processed server-side and returned as playback-ready assets.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If your token has expired, simply re-authenticate through your NemoVideo account to generate a fresh session token and resume recording without losing your project history. A 'session not found' error means your capture session has timed out — start a new session to continue. If you're out of recording credits, register or upgrade your plan at nemovideo.ai to restore full capture and export access.

## Frequently Asked Questions

**Can I record just one application window instead of my whole screen?** Yes. You can specify a full-screen capture, a single application window, or a custom rectangular region. Just describe what you want to capture when you start.

**What's the maximum recording length supported?** There's no hard time cap, but for best performance and manageable file sizes, recordings under 30 minutes are recommended. Longer sessions can be split into segments.

**Will the recording capture system audio and microphone at the same time?** You can choose to record system audio, microphone input, both, or neither. Specify your preference before starting the session.

**My recording came out as an mkv but I need mp4 — can I convert it?** Absolutely. You can request a format conversion after recording. Supported output formats include mp4, mov, avi, webm, and mkv, so switching between them is straightforward.

**Does the skill capture cursor movement and clicks?** Yes. Cursor visibility and click highlighting are both configurable, which is especially useful for tutorial and demo recordings where viewers need to follow along with your actions.

## Best Practices for Screen Recordings That Actually Get Watched

Before hitting record, close any tabs, notifications, or apps you don't want appearing on screen. Clutter in the background distracts viewers and makes your recording look unplanned. If you're recording a tutorial, rehearse the steps once so your mouse movements are deliberate and easy to follow.

Keep recordings focused and short. Viewers drop off quickly when a screen recording meanders — aim for under 5 minutes for instructional content and trim aggressively. Use the annotation tools to draw attention to key UI elements rather than relying solely on verbal explanation.

For file format, choose mp4 for maximum compatibility when sharing externally, webm for web embedding, and mov if you're working within a macOS or iOS ecosystem. If file size is a concern, webm typically delivers the best compression without visible quality loss for screen content.

Finally, record at your native resolution rather than scaling up. Upscaled recordings look blurry on high-density displays, and viewers on modern monitors will notice immediately.
