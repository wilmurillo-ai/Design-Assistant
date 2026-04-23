---
name: yoga-for-beginners-video
version: "1.0.1"
displayName: "Yoga for Beginners Video Maker — Create Guided Yoga Flow and Pose Tutorial Videos"
description: >
  Yoga for Beginners Video Maker — Create Guided Yoga Flow and Pose Tutorial Videos.
metadata: {"openclaw": {"emoji": "🧘", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎥 Welcome! I can yoga for beginners video for you. Share a video file or tell me your idea!

**Try saying:**
- "add effects to this clip"
- "edit my video"
- "help me create a short video"

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


# Yoga for Beginners Video Maker — Guided Flow and Pose Tutorial Videos

Your first Sun Salutation looked more like a controlled fall than a flow — and that's completely fine. The problem isn't the practice, it's the footage: forty minutes of a phone propped against a yoga block filming mostly your mat and occasionally your elbow. Beginner yoga content is the fastest-growing wellness sub-genre on YouTube, but producing it means capturing alignment details that matter to someone who doesn't yet know the difference between Warrior I and Warrior II. This tool turns raw practice footage or simple text descriptions into polished beginner-friendly yoga videos — complete with pose-name overlays, breath-cue timing, alignment annotations, modification callouts for stiff hips and tight hamstrings, and chapter markers for each segment of the flow. Whether you're a newly certified RYT-200 building an online library, a studio owner offering virtual memberships, or a physical therapist incorporating gentle yoga into rehab protocols, describe the sequence and the AI handles the rest.

## Example Prompts

### 1. Morning Sun Salutation for Complete Beginners
"Create a 10-minute beginner Sun Salutation A video. Start with Mountain Pose — feet hip-width, micro-bend in knees, palms forward. Cue each transition with an inhale or exhale label on screen. Show modifications: Forward Fold with bent knees for tight hamstrings, Plank on knees for weak wrists, Cobra instead of Upward Dog. Display Sanskrit and English names side by side — 'Tadasana / Mountain Pose'. Use a warm sunrise color grade. Add a 3-breath hold overlay at each static pose. Background music: gentle acoustic guitar, 60 BPM. End with Savasana, hold for 90 seconds with a singing-bowl fade-out."

### 2. Desk Worker Hip-Opener Sequence
"Build a 15-minute hip-opener flow for people who sit 8+ hours a day. Open with a 'Why Your Hips Are Tight' anatomy card showing the psoas and hip flexors highlighted on a body outline. Sequence: Reclined Figure Four → Low Lunge with back knee down → Lizard Pose with forearm option → Pigeon Pose with bolster modification → Supine Twist. Each pose held for 5 breaths with a breath counter on screen. Add alignment cues as timed text: 'Square your hips forward' at the exact frame. Include a 'Desk Break' chapter marker at the halfway point for people who only have 7 minutes. Grade for calm afternoon light — warm amber, soft shadows."

### 3. Prenatal Gentle Yoga — Second Trimester
"Produce a 20-minute prenatal yoga session for second trimester. Safety disclaimer card at the start: 'Consult your OB-GYN before beginning any exercise program.' Avoid all prone poses and deep twists — flag them with a red X if they appear in source footage. Sequence: Cat-Cow with wider knee stance → Modified Warrior II with chair support → Side Angle with block → Seated Butterfly with bolster → Legs Up the Wall with blanket. Overlay trimester-specific notes: 'Relaxin hormone increases joint laxity — avoid overstretching.' Breath cues synced to diaphragmatic breathing pattern. Closing meditation with hand-on-belly visualization, 2 minutes. Gentle piano soundtrack, no percussion."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the yoga sequence, level, modifications, and style |
| `duration` | string | | Target video length (e.g. "10 min", "20 min") |
| `style` | string | | Visual style: "studio", "outdoor", "home", "sunrise" |
| `music` | string | | Background music mood or BPM preference |
| `language` | string | | Subtitle/cue language (default: English) |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `modifications` | boolean | | Show pose modifications for beginners (default: true) |

## Workflow

1. **Describe** — Write your sequence with pose names, breath cues, hold durations, and modification needs
2. **Upload (optional)** — Add reference footage, studio clips, or demonstration photos
3. **Generate** — AI assembles the flow with pose overlays, alignment cues, breath timing, and chapter markers
4. **Review** — Preview the video, adjust pacing, modify transitions between poses
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "yoga-for-beginners-video",
    "prompt": "Create a 10-minute beginner Sun Salutation A video with Sanskrit pose names, breath cue overlays, and knee-down modifications for Plank and Cobra",
    "duration": "10 min",
    "style": "sunrise",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Name every pose in your prompt** — "Warrior II" gives the AI an exact overlay; "that standing one with arms out" does not. Sanskrit names are optional but improve accuracy of pose-identification.
2. **Specify breath timing explicitly** — "Hold for 5 breaths" produces a visible breath counter; "hold for a bit" produces a guess. The AI maps inhale/exhale labels to transitions when you describe them.
3. **Call out modifications by body limitation** — "Bent-knee Forward Fold for tight hamstrings" is more useful than "easy version." The AI generates a split-screen showing full pose and modification side by side.
4. **Set a BPM for background music** — Yoga videos perform best with music at 60-70 BPM (resting heart rate range). Faster tracks unconsciously rush the viewer's breathing and hurt watch time.
5. **Include a safety disclaimer for specialty audiences** — Prenatal, post-surgical, and senior yoga videos need an opening medical-disclaimer card. Mention it in the prompt and the AI places it before the first pose.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube full-length class |
| MP4 9:16 | 1080p | TikTok / Instagram Reels / YouTube Shorts |
| MP4 1:1 | 1080p | Instagram feed post |
| MP3 | — | Audio-only guided session (podcast / app) |

## Related Skills

- [fitness-video-maker](/skills/fitness-video-maker) — General fitness and exercise videos
- [meditation-video-maker](/skills/meditation-video-maker) — Guided meditation and breathwork
- [personal-trainer-video](/skills/personal-trainer-video) — Personal training session recordings
