---
name: youtube-video-editor-app
version: "1.0.0"
displayName: "YouTube Video Editor App — Edit, Trim & Enhance Videos Ready for Upload"
description: >
  Turn raw footage into polished, upload-ready YouTube content without leaving your browser. This youtube-video-editor-app skill handles trimming, cutting, captioning, color correction, and pacing adjustments tailored specifically for YouTube's audience retention standards. Works with mp4, mov, avi, webm, and mkv files. Built for creators, educators, and marketers who need clean, engaging videos fast — no desktop software required.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your YouTube Video Editor — ready to help you trim, cut, caption, and polish your footage into a video your audience will actually finish watching. Drop your clip and tell me what you need done.

**Try saying:**
- "Trim the first 8 seconds of silence from my mp4 and add a bold title card at the start that says 'How to Build a Budget PC in 2025'"
- "Cut out the section between 2:14 and 3:40 where I fumbled the explanation, then smooth the audio transition so the jump isn't noticeable"
- "Add auto-generated captions to my tutorial video and highlight keywords in yellow to improve accessibility and viewer retention"

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Edit YouTube Videos That Actually Keep Viewers Watching

Most video editors are built for filmmakers. This skill is built for YouTube creators. Whether you're producing tutorials, vlogs, product reviews, or educational content, the youtube-video-editor-app skill understands the rhythm and structure that YouTube audiences expect — tight cuts, clear pacing, and visual hooks that hold attention past the first 30 seconds.

You can trim dead air from the beginning and end of clips, cut out filler moments mid-video, adjust playback pacing, add text overlays or captions, and apply basic color grading — all through simple conversational prompts. There's no timeline scrubbing or complex layer management. Just describe what you want and let the skill do the heavy lifting.

This tool is particularly useful for solo creators and small teams who publish consistently and can't afford to spend hours in post-production on every upload. Upload your raw footage in mp4, mov, avi, webm, or mkv format and get back a video that's ready to drop into YouTube Studio.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Edits and Trim Requests

Every cut, trim, caption overlay, color grade, or export request you describe gets parsed and routed to the appropriate NemoVideo processing pipeline based on the detected edit intent.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Backend Reference

The NemoVideo backend handles all heavy lifting — frame-accurate trimming, timeline rendering, and format optimization — so your edited footage comes back upload-ready for YouTube's codec and resolution requirements. API calls are session-bound, meaning your project state, cut points, and enhancement settings persist across the editing workflow.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If your token expires mid-session, simply re-authenticate to restore full editing access without losing your project timeline. A 'session not found' error means your editing session timed out — start a fresh session and re-import your footage to continue. Out of credits? Head to nemovideo.ai to register or top up so you can keep trimming and exporting without interruption.

## Best Practices for YouTube Video Editing

YouTube's algorithm rewards videos with strong audience retention, and that starts with tight editing. When using the youtube-video-editor-app skill, always trim your intro to under 15 seconds — viewers decide within the first few moments whether to stay or leave. Remove any pause longer than 2 seconds unless it serves a deliberate dramatic purpose.

For tutorials and how-to content, consider asking the skill to add chapter markers or text overlays at key transitions. This not only helps viewers navigate but also signals structure to YouTube's recommendation system. If your video runs longer than 8 minutes, pacing becomes critical — request a pacing review to identify segments that drag.

Always export in the highest resolution your source footage supports. The skill preserves original quality during edits and outputs files optimized for YouTube's preferred codec settings, reducing re-encoding artifacts after upload.

## Integration Guide for the YouTube Video Editor App

Getting started with the youtube-video-editor-app skill is straightforward. Upload your raw video file directly in the chat — supported formats include mp4, mov, avi, webm, and mkv. Files up to standard ClawHub size limits are processed entirely in-session, so nothing is stored beyond your active conversation.

For creators with an existing production workflow, this skill works well as a final-pass tool. Edit your footage in your preferred software first, export a draft, then use the skill for quick cleanup tasks like trimming handles, adding captions, or adjusting the opening hook before uploading to YouTube Studio.

If you're batch-producing content — say, a weekly series — describe your standard edit style once and the skill will apply consistent formatting across multiple clips in the same session. This makes it easy to maintain a recognizable visual identity across your channel without rebuilding your edit preferences from scratch each time.
