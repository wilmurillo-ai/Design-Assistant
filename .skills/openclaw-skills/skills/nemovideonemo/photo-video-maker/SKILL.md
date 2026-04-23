---
name: photo-video-maker
version: "1.0.4"
displayName: "Photo Video Maker — Transform Your Photos Into Cinematic Slideshows & Stories"
description: >
  Turn a collection of still images into polished, shareable videos with the photo-video-maker skill. Upload your photos and let ClawHub sequence them into smooth, timed slideshows complete with transitions, captions, and pacing control. Ideal for photographers, content creators, event planners, and social media managers who need to produce engaging video content without complex editing software. Supports mp4, mov, avi, webm, and mkv output formats.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your photos into a compelling video? Share your images and tell me the vibe you're going for — I'll help you build a photo video maker sequence that looks and feels exactly right. Let's get started!

**Try saying:**
- "Create a 30-second slideshow from these 12 vacation photos with smooth crossfade transitions and a relaxed pace."
- "Make a product highlight video from my 8 product photos — fast cuts, clean look, suitable for Instagram Reels."
- "Turn these wedding reception photos into a 60-second tribute video with a warm, cinematic feel and subtle zoom effects."

**Setup**: This skill connects to the NemoVideo API at `mega-api-prod.nemovideo.ai`. Set the `NEMO_TOKEN` environment variable to authenticate. New users can get 100 free credits at nemovideo.ai.

# From Still Moments to Moving Stories Worth Sharing

The photo-video-maker skill exists for one clear purpose: closing the gap between a folder of great photos and a video people actually want to watch. Whether you're assembling a wedding recap, a product launch reel, a travel montage, or a birthday tribute, this skill handles the sequencing, timing, and transitions so you don't have to.

You bring the images — in whatever order you want them — and describe the mood, pace, or style you're going for. The skill interprets your intent and builds a cohesive video that feels intentional rather than auto-generated. Want a slow, cinematic drift between landscape shots? A punchy, fast-cut sequence for a product showcase? Both are within reach through simple, conversational instructions.

This isn't a template-filler that stamps a generic theme over your photos. It's a responsive tool that adapts to your specific content and use case, giving you a video output that reflects the story you actually want to tell. No prior video editing experience required.

## Routing Your Slideshow Requests

Every request — whether you're building a cinematic montage, a story reel, or a music-synced photo slideshow — is parsed by intent and routed to the matching NemoVideo workflow automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

Photo Video Maker runs on the NemoVideo rendering engine, which handles frame sequencing, transition timing, audio sync, and export resolution for every slideshow or story you generate. All media processing happens server-side, so your photos are compiled and rendered without any local encoding overhead.

Include on every request: `Authorization: Bearer $NEMO_TOKEN`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`.

**Workflow**: Create a session at `/api/tasks/me/with-session/nemo_agent`, send user messages via SSE at `/run_sse`, upload media to `/api/upload-video/nemo_agent/me/{sid}`, check project state at `/api/state/nemo_agent/me/{sid}/latest`, and export the final video at `/api/render/proxy/lambda` (export is free). Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### Troubleshooting

If your token has expired, simply re-authenticate to restore your session and pick up right where you left off. A 'session not found' error means your previous render session timed out — start a fresh session and re-submit your photo set. Out of credits? Head to nemovideo.ai to register or top up so you can keep creating.

## Performance Notes

The photo-video-maker skill performs best when input images are consistently sized or at least share a similar aspect ratio. Mixing portrait and landscape photos in the same sequence can cause letterboxing or cropping artifacts — it's worth deciding on a target aspect ratio (16:9 for YouTube/TV, 9:16 for mobile Stories, 1:1 for feeds) before uploading.

Processing time scales with the number of images and the complexity of transitions requested. A 10-photo slideshow with simple cuts renders significantly faster than a 50-image sequence with motion effects and text overlays. For large batches, consider breaking the project into segments and merging the outputs.

Output file size depends on resolution and duration. If you're targeting a platform with upload size limits — TikTok, for instance — specify your target file size or bitrate in your prompt and the skill will optimize accordingly. Supported output formats include mp4, mov, avi, webm, and mkv.

## Integration Guide

The photo-video-maker skill fits naturally into content workflows where photos are already being produced — real estate listings, e-commerce catalogs, event photography, and social media content calendars are common entry points. You can pipe image URLs or uploaded files directly into a prompt alongside your instructions, making it straightforward to trigger the skill from a broader automation pipeline.

If you're working with a content team, the skill supports descriptive briefs as input, meaning a non-technical team member can write the creative direction in plain language and the skill will interpret it. There's no need to pre-configure transitions or timings in a separate tool.

For recurring use cases — say, a weekly product roundup video — you can standardize a prompt template with fixed style parameters and swap in new image sets each time. This makes the skill behave like a lightweight, repeatable production tool rather than a one-off request, reducing turnaround time for routine video content significantly.
