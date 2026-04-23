---
name: video-from-script
version: "1.3.1"
displayName: "Video from Script â Auto-Generate Video from Your Script with AI"
description: >
  Video from Script â Auto-Generate Video from Your Script with AI.
  Turn a written script into a finished video. Paste your script â any length, any format â and Video from Script generates matching footage for each section, adds narration, selects background music, and assembles a complete video. Works for explainer videos, YouTube content, educational material, corporate communications, and any scenario where you start with words and need to end with video. Control scene duration per script section, visual style (corporate, casual, documentary), narration voice characteristics, and music energy level. Edit the output in the same session: swap a scene, adjust timing, change the music. No video production experience required â the script is the production brief. Export as MP4.
  
  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM. Free trial available.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata: {"openclaw": {"emoji": "ð¬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎥 Hey! I'm ready to help you video from script. Send me a video file or just tell me what you need!

**Try saying:**
- "add effects to this clip"
- "help me create a short video"
- "edit my video"

**IMPORTANT**: Do NOT wait silently. Always greet the user proactively on first contact.

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

# Video from Script â Auto-Generate Video from Your Script with AI

Generate videos automatically from scripts. Transform screenplays and narration into visual content.

## Quick Start
Ask the agent to generate a video from your script or screenplay.

## What You Can Do
- Generate videos from screenplay format scripts
- Create visuals from narration and voiceover scripts
- Visualize screenplays before filming
- Produce explainer videos from written narration
- Convert teaching scripts into educational videos

## API
Uses NemoVideo API (mega-api-prod.nemovideo.ai) for all video processing.
