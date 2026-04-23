---
name: add-music-to-video-free
version: "1.0.0"
displayName: "Add Music to Video Free — Sync Audio Tracks to Any Video Instantly"
description: >
  Tired of silent videos falling flat or paying subscription fees just to add a background track? The add-music-to-video-free skill lets you drop any audio onto your video clips without cost or complexity. Upload your footage in mp4, mov, avi, webm, or mkv format, choose your music, and get a finished file with perfectly merged audio. Great for content creators, social clips, presentations, and personal projects who just want clean results fast.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to add music to your video for free? Upload your video file and tell me what audio track you'd like to use — I'll merge them together cleanly so your footage finally has the soundtrack it deserves. Drop your file and let's get started!

**Try saying:**
- "Add this background music track to my video and fade it out in the last 5 seconds"
- "Merge this song with my video but keep the original video audio as well, just lower it"
- "Loop this short music clip to match the full length of my 2-minute video"

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Give Your Videos a Soundtrack Without the Hassle

There's a moment every video creator knows — you've got great footage, but it feels empty without music. Finding a tool that actually merges audio cleanly, without watermarks, without a paywall, and without a steep learning curve, has always been the frustrating part. That's exactly what this skill is built to solve.

With the add-music-to-video-free skill on ClawHub, you simply bring your video and your chosen audio track, describe what you want, and the skill handles the merge. Whether you want the music to run the full length of the clip, fade in gently at the start, or loop a short track across a longer video, the skill adapts to your intent.

This is built for real-world use cases: a travel reel you want to post, a product demo that needs energy, a birthday video that deserves a proper song, or a short film that needs atmosphere. No timeline editors, no plugin installs, no confusing export settings — just your video, your music, and a result you can actually use.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Audio Sync Requests

When you describe your audio-video pairing goal — whether trimming a background track, looping a beat, or fading music into a clip — ClawHub routes your request directly to the NemoVideo audio sync engine for instant processing.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles audio-to-video binding by analyzing your clip's duration and automatically aligning the music track's entry and exit points, supporting formats like MP4, MOV, MP3, and WAV. All free-tier rendering jobs are queued through NemoVideo's cloud transcoder, which merges audio layers without re-encoding your original video quality.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If your token expires mid-session, simply re-authenticate through ClawHub to refresh your NemoVideo credentials and resume your audio sync job. A 'session not found' error means your previous workspace timed out — start a fresh session and re-upload your video and music files. If you're out of credits, head to nemovideo.ai to register or upgrade your plan and unlock continued free music-to-video rendering.

## FAQ

**What video formats are supported?**
You can upload videos in mp4, mov, avi, webm, or mkv format. Most common camera and phone exports will work without any conversion needed.

**Can I keep the original sound from my video?**
Yes. Just let the skill know you want to mix the original audio with the new music rather than replace it. You can also specify a rough balance, like 'keep my voice loud and make the music quieter in the background.'

**What if my music track is shorter than my video?**
The skill can loop the audio track automatically to fill the full video duration. Just mention it in your request and it will handle the repetition seamlessly.

**Is there a file size limit?**
Large files may take longer to process, but the skill is designed to handle typical video lengths used for social media, presentations, and short films without issue.

## Best Practices

**Choose audio that matches your video's pace.** Fast cuts and action scenes pair well with upbeat tracks, while slower, scenic footage benefits from ambient or instrumental music. Describing the mood you're going for helps the skill make smarter decisions about fade timing and volume.

**Use royalty-free music to stay safe.** If you're posting the finished video publicly, make sure your audio track is cleared for use. Sites like Pixabay, Free Music Archive, and ccMixter offer free tracks with no copyright issues.

**Trim your video before uploading if possible.** If you only want music on a specific segment, cutting the clip down first gives you cleaner control over where the audio starts and ends.

**Be specific in your request.** Instead of saying 'add music,' try 'add this track starting at 3 seconds in, fade it in over 2 seconds, and cut it when the video ends.' The more detail you give, the closer the result will be to exactly what you had in mind.
