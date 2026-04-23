---
name: auto-subtitles
version: "1.0.0"
displayName: "Auto-Subtitles Generator — Instantly Caption Any Video with Accurate Subtitles"
description: >
  Turn raw footage into fully captioned videos in minutes with ClawHub's auto-subtitles skill. Upload your mp4, mov, avi, webm, or mkv file and get accurate, time-synced subtitles generated automatically — no manual transcription needed. Supports multiple languages, custom styling, and burned-in or exported caption formats. Perfect for content creators, educators, marketers, and anyone who needs accessible, subtitle-ready videos fast.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! This skill automatically generates accurate, time-synced subtitles for your videos — just upload your file and tell me how you'd like the captions styled or formatted. Ready to caption your first video?

**Try saying:**
- "Add auto-subtitles to my interview video and burn them into the footage with white text and a dark background"
- "Generate subtitles for my Spanish tutorial video and export them as an SRT file"
- "Create captions for this 10-minute webinar recording with large text positioned at the bottom of the screen"

**Setup**: This skill connects to the NemoVideo API at `mega-api-prod.nemovideo.ai`. Set the `NEMO_TOKEN` environment variable to authenticate. New users can get 100 free credits at nemovideo.ai.

# Caption Every Video Without the Manual Grind

Subtitling a video by hand is one of the most time-consuming parts of post-production. You scrub through the timeline, type out every word, nudge timestamps, and repeat — sometimes for hours. The auto-subtitles skill eliminates that entire process by listening to your video's audio and generating accurate, time-coded captions automatically.

Whether you're publishing a tutorial on YouTube, creating training content for your team, or making social media clips accessible to a broader audience, subtitles are no longer optional. Studies consistently show that captions increase viewer retention, improve comprehension for non-native speakers, and make content usable in sound-off environments like office lobbies or public transport.

With this skill, you simply upload your video — in any common format including mp4, mov, avi, webm, or mkv — and the captions come back ready to use. You can choose to burn them directly into the video or receive them as a separate subtitle file. Adjust the font, size, and positioning to match your brand, or let the defaults handle it. It's the fastest path from raw footage to fully captioned, publish-ready video.

## Routing Caption Requests Intelligently

Each subtitle request is parsed for language, video source, and caption style, then dispatched to the appropriate NemoVideo transcription pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Subtitle API Reference

The NemoVideo backend uses frame-accurate speech recognition combined with forced alignment to sync captions to the exact millisecond. Subtitle burns, SRT exports, and multi-language tracks are all handled server-side without manual timecoding.

Include on every request: `Authorization: Bearer $NEMO_TOKEN`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`.

**Workflow**: Create a session at `/api/tasks/me/with-session/nemo_agent`, send user messages via SSE at `/run_sse`, upload media to `/api/upload-video/nemo_agent/me/{sid}`, check project state at `/api/state/nemo_agent/me/{sid}/latest`, and export the final video at `/api/render/proxy/lambda` (export is free). Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### Troubleshooting

If your token expires mid-session, simply re-authenticate through the skill prompt to resume without losing your subtitle job queue. A 'session not found' error means your context was cleared — start a fresh session and re-upload your video source. Out of credits? Head to nemovideo.ai to register or top up your account before resubmitting.

## Quick Start Guide

Getting subtitles onto your video takes just a few steps. Start by uploading your video file — mp4, mov, avi, webm, and mkv are all supported. Then tell the skill what you need: do you want the subtitles burned directly into the video, or would you prefer a separate SRT or VTT caption file you can upload to YouTube, Vimeo, or your LMS?

If your video is in a language other than English, mention the language upfront so the transcription is tuned correctly from the start. You can also specify styling preferences at this stage — font size, text color, background opacity, and vertical positioning.

Once processing is complete, review the generated captions. If any words were misheard or names were transcribed incorrectly, you can request targeted corrections without regenerating the entire subtitle track. For videos with heavy background noise or strong accents, providing a rough transcript or key terminology in your prompt will noticeably improve accuracy.

## Tips and Tricks

For the cleanest results, use video files with clear, uncompressed audio. If your original recording has significant background noise, consider running it through a noise-reduction tool before uploading — this directly improves transcription accuracy.

When captioning content for social media, request shorter line lengths and larger font sizes. Most viewers on Instagram Reels or TikTok are watching on small screens, and captions that wrap awkwardly or sit too small get ignored entirely.

If you're producing multilingual content, you can request subtitle generation in the spoken language and then ask for a translated version in a second language in the same session — great for reaching international audiences without a separate workflow.

Finally, if you need captions for a video series, mention that upfront. Consistent styling across episodes — same font, same positioning, same color scheme — reinforces your brand and saves you from specifying preferences every single time.
