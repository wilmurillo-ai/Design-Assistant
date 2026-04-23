---
name: fps-highlight-video
version: 1.0.3
displayName: "FPS Highlight Video Maker"
description: >
  Describe your best FPS plays and NemoVideo creates the video. CS2 aces, Valorant clutches, Apex Legends squad wipes, Warzone final circle wins — narrate the play, the weapon, the context, and the outcome, and get an FPS highlight that communicates your skill to everyone who plays the game.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: ["NEMO_TOKEN"]
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 📹 Welcome! I can fps highlight video for you. Share a video file or tell me your idea!

**Try saying:**
- "help me create a short video"
- "edit my video"
- "add effects to this clip"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# FPS Highlight Video Maker — Create First-Person Shooter Clip and Montage Content

Describe your best FPS plays and NemoVideo creates the video. CS2 aces, Valorant clutches, Apex Legends squad wipes, Warzone final circle wins — narrate the play, the weapon, the context, and the outcome, and get an FPS highlight that communicates your skill to everyone who plays the game.

## When to Use This Skill

Use this skill for FPS-specific gaming content:
- Create clutch round and ace highlight clips for tactical FPS games (CS2, Valorant)
- Film squad play and coordination highlights in battle royale games
- Build weapon mastery and skill demonstration content
- Document ranked climb milestones with the highlight plays that got you there
- Create "how I do it" educational content breaking down the play for viewers
- Produce FPS channel montage content with music-synced kills

## How to Describe Your FPS Highlight

Be specific about the game, the weapon, the tactical situation, and what made the play impressive.

**Examples of good prompts:**
- "Valorant Operator highlight: one-shot, one-kill style. Played as Jett on Breeze, activated dash to peak A main, one-tapped first player mid-air, reset immediately, peaked again from a different angle, one-tapped the second. Both kills were in under 3 seconds. The third player swung expecting a reload and got one-tapped. Three kills with Operator in 4 seconds while dashing."
- "Apex Legends squad wipe on final ring: three squads converged at the same time, we were the last full squad standing. I popped off with an R-99, my duo partner used Caustic gas to separate them, and our third cleaned up with a Mastiff. We won the game. Show the chaos, the squad coordination, and the win screen."
- "CS2 AWP montage from 3 months of ranked play: 12 clips, all long-range picks, no close-range spam. Show the prefire through smokes, the noscopes that landed, the double-peek one-tap, and the 4k from CT side Mirage. BGM synced to kills."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `game_title` | FPS game | `"CS2"`, `"Valorant"`, `"Apex Legends"`, `"Warzone"`, `"R6 Siege"` |
| `weapon_used` | Weapon featured | `"Operator"`, `"AWP"`, `"R-99"`, `"Vandal"` |
| `play_type` | Highlight category | `"clutch"`, `"ace"`, `"montage"`, `"squad_wipe"`, `"ranked_peak"` |
| `tactical_context` | Situation details | `"1v4 eco round"`, `"final ring"`, `"last buy of the half"` |
| `show_crosshair` | Crosshair overlay | `true` |
| `slow_motion_kills` | Slow-mo on peaks | `true` |
| `music_style` | Audio | `"hype"`, `"synced_kills"`, `"no_music"` |
| `duration_seconds` | Video length | `30`, `45`, `60`, `120` |
| `platform` | Target platform | `"tiktok"`, `"youtube"`, `"twitter"` |

## Workflow

1. Describe the game, weapon, play type, and tactical context
2. NemoVideo sequences the FPS footage with competitive gaming pacing
3. Crosshair, health bar, ability HUD, and kill callouts added automatically
4. Export with music timed to kills for maximum hype impact

## API Usage

### Clutch Highlight Clip

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "fps-highlight-video",
    "input": {
      "prompt": "CS2 deagle clutch, 1v3 on Inferno, anti-eco. I was holding banana with a Deagle. Three players pushed at once — got the first headshot through the smoke on banana, repositioned to B site, prefired the door and got the second mid-movement, then 1v1 on B with 12 HP. The last guy had an AK-47. Peaked aggressively, hit the headshot before he could spray. We were down 12-14, this clutch extended to 13-14. Show the play in real time first, then slow motion on each kill, then back to real time for the final 1v1.",
      "game_title": "CS2",
      "weapon_used": "Deagle",
      "play_type": "clutch",
      "tactical_context": "1v3 anti-eco, down 12-14 in match",
      "show_crosshair": true,
      "slow_motion_kills": true,
      "music_style": "no_music",
      "duration_seconds": 45,
      "platform": "tiktok",
      "hashtags": ["CS2", "CounterStrike", "Clutch", "Deagle", "FPS"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "fps_jkl012",
  "status": "processing",
  "estimated_seconds": 75,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/fps_jkl012"
}
```

### Weapon Montage

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "fps-highlight-video",
    "input": {
      "prompt": "Valorant Phantom montage, Act 3 collection: 15 clips showing different aspects of the gun — the close range spray control on B site Ascent, the medium range tap-tapping on A main Bind, three clips of through-smoke line-up kills, two clips of the 4k in a single round (both Phantom), and the three clips from Diamond lobby where the Phantom outdueled Vandals. No facecam, crosshair visible, music synced so each kill lands on a beat.",
      "game_title": "Valorant",
      "weapon_used": "Phantom",
      "play_type": "montage",
      "show_crosshair": true,
      "slow_motion_kills": false,
      "music_style": "synced_kills",
      "duration_seconds": 120,
      "platform": "youtube",
      "hashtags": ["Valorant", "Phantom", "ValorantMontage", "FPS", "Diamond"]
    }
  }'
```

## Tips for Best Results

- **FPS community speaks weapon**: "Deagle headshot" means something different from "pistol kill" — use the actual weapon name and the play communicates instantly to people who play the game
- **Tactical context is the story**: "1v3 anti-eco" or "1v4 with 12 HP" tells viewers the odds before the play begins — the difficulty context is what makes the highlight impressive
- **Slow motion on the key peak**: Set `slow_motion_kills: true` for pistol clutches and no-scope moments — the mechanics that look effortless in real-time are clearly skilled in slow motion
- **Crosshair placement is the skill indicator**: Set `show_crosshair: true` — experienced FPS players watch the crosshair to assess pre-aim and game sense, not just whether the shot landed
- **Music-synced montages are the format**: For multi-clip montages, `music_style: "synced_kills"` — kills that land on beat drops are the definitive FPS montage format

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| TikTok | 1080×1920 | 15–60s |
| Twitter/X | 1920×1080 | 15–140s |
| YouTube | 1920×1080 | 1–8 min |
| YouTube Shorts | 1080×1920 | up to 60s |

## Related Skills

- `gaming-highlight-video` — General multi-game highlight content
- `esports-video-maker` — Competitive team and tournament content
- `twitch-clip-editor` — Stream highlight compilation from FPS sessions

## Common Questions

**What FPS games work best with this skill?**
Any FPS — CS2, Valorant, Apex Legends, Warzone, R6 Siege, Overwatch 2, Halo Infinite. Mention the specific game and NemoVideo uses the correct UI overlays and game-specific terminology.

**Can I create educational content breaking down the play?**
Yes — describe "show each kill with a slow-motion breakdown explaining the read (why I peeked when I did)" and set `duration_seconds: 60`. FPS educational content performs well on YouTube with the demographic that wants to improve.

**Should I use music or game audio for clutch clips?**
For single clutch clips, `music_style: "no_music"` often works better — the in-game audio (kill sounds, utility pops, heavy breathing) creates its own tension. For montages, use `synced_kills`.
