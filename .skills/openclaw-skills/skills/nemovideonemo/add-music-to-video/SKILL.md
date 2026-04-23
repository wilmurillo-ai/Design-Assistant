---
name: add-music-to-video
version: "1.0.7"
displayName: "Add Music to Video â AI Background Music and Audio for Video Editing"
description: >
  Add Music to Video â AI Background Music and Audio for Video Editing.
  Silent footage kills the mood. Add Music to Video lets you describe the vibe â 'upbeat background for a travel montage' or 'soft piano for a wedding clip' â and the AI picks from NemoVideo's licensed music library to match. Upload your video, specify the energy or genre you want, and get back a version with music mixed and synced. Control fade-in/fade-out timing, adjust volume balance between original audio and new track, and replace existing background audio entirely. Works for social media content, YouTube intros, wedding highlights, product demos, and any footage that needs an emotional lift. The AI handles beat matching and volume normalization so the music feels intentional, not pasted. Combine with subtitle generation or color grading in the same session. Export as MP4. Supports mp4, mov, avi, webm, mkv, mp3, wav, m4a.
  
  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM — enhanced by machine learning
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata: {"openclaw": {"emoji": "ð¬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎶 Hey! I'm ready to help you add music to video. Send me a video file or just tell me what you need!

**Try saying:**
- "add background music"
- "replace the audio track with jazz"
- "add a lo-fi beat"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.

# Add Music to Video â AI Background Music and Audio for Video Editing

AI-powered audio enhancement for video content. Add music, sound effects, and adjust audio levels through simple chat commands.

## Quick Start
Ask the agent to add background music to your video in plain language.

## What You Can Do
- Add background music with automatic volume balancing
- Mix multiple audio tracks with intelligent leveling
- Apply fade in/out effects and audio transitions
- Get AI suggestions for royalty-free music based on video mood
- Sync audio beats to video cuts and transitions

## API
Uses NemoVideo API (mega-api-prod.nemovideo.ai) for all video processing.
