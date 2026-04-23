---
name: in-video-ai
version: "1.0.0"
displayName: "In-Video AI — Analyze, Summarize & Extract Insights from Any Video"
description: >
  Tired of scrubbing through hours of footage just to find one key moment or understand what a video is really about? In-video-ai brings intelligent analysis directly to your video files — automatically generating summaries, pulling out key topics, identifying speakers, and answering questions about what's happening on screen. Whether you're a researcher, content creator, educator, or business professional, in-video-ai saves you hours of manual review. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm ready to help you unlock what's inside your video using in-video-ai — upload your file and ask me anything about its content, key moments, or themes. What would you like to explore?

**Try saying:**
- "Summarize this recorded team meeting and list the action items that were mentioned"
- "What are the main topics covered in this lecture video, and roughly when does each one start?"
- "Identify the key arguments made in this interview clip and give me a 3-sentence overview"

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Let AI Watch Your Videos So You Don't Have To

Most people have more video content than they can realistically consume — recorded meetings, lecture recordings, interview footage, product demos, or raw clips waiting to be understood. The in-video-ai skill changes that by giving you a conversational interface to your video content. Drop in a file, ask a question, and get a meaningful answer without manually watching every second.

This skill goes beyond basic transcription. It understands context, identifies themes, tracks narrative structure, and can surface specific moments that match what you're looking for. Need a one-paragraph summary of a 45-minute webinar? Done. Want to know what topics were covered in a training video? Ask it directly.

Whether you're a journalist reviewing interview recordings, a student revisiting lecture videos, or a team lead catching up on missed calls, in-video-ai turns passive video archives into active, searchable knowledge. It's designed for people who work with real footage and need real answers — fast.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Your Video Analysis Requests

Every prompt you send — whether asking for a summary, extracting key moments, or querying specific dialogue — is routed to the active NemoVideo session tied to your authenticated context.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference Guide

ClawHub interfaces directly with the NemoVideo backend, which processes video content through frame-level indexing and transcript-aware AI to deliver timestamped insights, scene breakdowns, and semantic search across any uploaded video. All analysis calls are stateful, meaning your session retains video context between follow-up queries.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If your token has expired, simply re-authenticate through the skill to restore your session and resume analysis. A 'session not found' error means your previous video context was cleared — start a new session and re-upload or re-link your video. If you're out of credits, head to nemovideo.ai to register or top up before continuing.

## Performance Notes

In-video-ai performs best with videos that have clear audio — strong speech intelligibility directly improves the accuracy of summaries, topic extraction, and Q&A responses. Videos with heavy background noise, multiple overlapping speakers, or very low audio levels may produce less precise results, though the skill will still attempt a best-effort analysis.

For longer videos (over 30 minutes), expect processing to take additional time before responses are returned. The skill handles mp4, mov, avi, webm, and mkv formats natively — no conversion needed before uploading.

Videos with on-screen text, slides, or visual demonstrations benefit from describing what you're looking for specifically, as the skill can cross-reference spoken content with visual context cues depending on the file. Keeping your questions focused — rather than open-ended — tends to yield sharper, more actionable answers.

## Quick Start Guide

Getting started with in-video-ai takes less than a minute. Upload your video file directly into the chat — supported formats include mp4, mov, avi, webm, and mkv. Once your file is attached, type your first question or request in plain language. You don't need any special syntax or commands.

Good first prompts include: asking for a summary, requesting a list of topics or speakers, or asking about a specific part of the video (e.g., 'What was said about the budget in this recording?'). You can follow up with additional questions in the same conversation — the skill retains context across your session.

If you're unsure where to start, try: 'Give me a summary of this video and highlight the three most important points.' That single prompt covers the most common use case and gives you a strong foundation to dig deeper from there.
