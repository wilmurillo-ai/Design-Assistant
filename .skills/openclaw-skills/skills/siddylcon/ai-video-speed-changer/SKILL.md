---
name: ai-video-speed-changer
version: 1.0.1
displayName: "AI Video Speed Changer — Speed Up Slow Down and Ramp Video Playback with AI"
description: >
  Speed up, slow down, and ramp video playback with AI — create slow motion, time-lapse, speed ramps, and custom velocity edits from any footage. NemoVideo uses AI frame generation for smooth slow motion from standard frame rate video and intelligent speed compression that preserves audio quality. Adjust playback from 0.1x extreme slow-mo to 16x time-lapse, with smooth transitions between speeds. Change video speed online, slow motion maker, speed up video, time lapse creator, video speed controller, velocity edit maker, playback speed changer, slow down video AI.
metadata: {"openclaw": {"emoji": "⏩", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Speed Changer — Control Time in Any Video

Speed is a storytelling tool. Slow motion reveals beauty invisible at normal speed — the precise moment a raindrop hits water, the expression on a face at the instant of surprise, the technique in an athlete's movement. Fast motion compresses tedium into entertainment — a 4-hour sunset becomes 10 mesmerizing seconds, a 2-hour cooking process becomes 30 satisfying seconds, a week of plant growth becomes 5 magical seconds. Speed ramps create cinematic rhythm — normal approach, snap to slow-mo at impact, snap back to fast — the editing technique behind every action movie trailer and viral TikTok montage. Traditional speed changes in editing software produce poor results at extreme values. Slowing 30fps footage to 0.25x creates 7.5fps playback — choppy and unwatchable. Speeding up audio makes voices sound like chipmunks. Speed transitions create jarring jumps instead of smooth ramps. NemoVideo solves every speed change problem with AI. Slow motion uses AI frame generation to create intermediate frames that never existed in the original recording — producing smooth 240fps-equivalent playback from standard 30fps footage. Speed-up preserves natural audio through pitch correction. Speed ramps use smooth mathematical curves instead of hard jumps. Every speed change feels intentional and professional.

## Use Cases

1. **Slow Motion — Reveal Hidden Detail (any footage)** — A 30fps phone recording of a dog shaking off water. At normal speed: a blur lasting 0.5 seconds. At 0.1x with AI frame generation: 5 seconds of visible detail — every water droplet trajectory, the ripple traveling through the dog's fur, the spray pattern in sunlight. NemoVideo generates 270 new frames between every 30 original frames, producing smooth playback that reveals what was always there but too fast to see. Phone footage with the slow-mo quality of a $50,000 Phantom camera.

2. **Time-Lapse — Compress Hours into Seconds (long recordings)** — A 6-hour recording of a sunset from a fixed camera. At normal speed: unwatchable. At 360x (6 hours → 60 seconds): a mesmerizing transformation of sky colors, cloud movement, and light change that holds attention for the full minute. NemoVideo: applies 360x speed, smooths frame-to-frame transitions (removes flicker from auto-exposure changes), stabilizes any tripod drift, and adds optional time counter overlay showing real-time progression. Hours of patience compressed into seconds of beauty.

3. **Speed Ramp — Cinematic Action Moment (any footage)** — A skateboarder approaching a rail, grinding, and landing. NemoVideo applies: approach at 1.5x (compresses the setup, builds anticipation), snap to 0.2x at the moment feet hit the rail (the skill becomes visible), hold slow-mo through the grind (2 seconds of technique appreciation), snap to 1.0x on the landing (satisfying return to reality). The speed ramp creates a rhythm — fast-SLOW-fast — that the brain finds cinematic. One speed change, and phone footage feels like a professional skate video.

4. **Velocity Edit — Gaming/Music Montage Style (1-5 min)** — A gaming montage or music video needs the "velocity edit" treatment: fast-forward through low-action moments, snap to slow-mo on every peak moment, beat-synced speed changes. NemoVideo: analyzes the footage (or music beat structure), applies automatic speed changes — 3-4x during transitions and setup, 0.2-0.3x on key moments (kills, dance moves, dramatic beats), smooth ramps between speeds rather than hard jumps, and audio pitch correction throughout. The editing style that dominates gaming content and music edits — applied automatically.

5. **Tutorial Speed-Up — Show Process Efficiently (any length)** — A 30-minute cooking tutorial has 10 minutes of active instruction and 20 minutes of passive waiting (baking, simmering, resting). NemoVideo: keeps instruction segments at 1.0x (viewer needs to follow along), speeds waiting segments to 8x with a timer overlay ("Bake for 25 minutes" fast-forwarding with visible clock), transitions smoothly between speeds (gradual ramp, not hard cut), and produces a tight 12-minute tutorial from 30 minutes of recording. Every second teaches; no second wastes.

## How It Works

### Step 1 — Upload Video
Any footage from any source at any frame rate. NemoVideo handles the frame generation and audio processing regardless of source quality.

### Step 2 — Define Speed Changes
Global speed (entire video at one speed), segment-based (different speeds for different sections), or automatic (AI detects peak moments for slow-mo and low-action for speed-up).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-speed-changer",
    "prompt": "Apply speed changes to a 2-minute skateboarding video. Speed map: 0:00-0:08 normal (1x, setup), 0:08-0:10 ramp up to 1.5x (approach), 0:10-0:14 snap to 0.2x slow-mo (trick 1 — kickflip), 0:14-0:22 ramp back to 1.5x (skate to next spot), 0:22-0:27 snap to 0.15x (trick 2 — rail grind, extreme slow-mo), 0:27-0:35 1x (celebration). AI frame generation for all slow-mo segments. Audio: pitch-corrected throughout. Add bass impact sound at each slow-mo snap point. Export 16:9 + 9:16.",
    "speed_map": [
      {"start": "0:00", "end": "0:08", "speed": 1.0},
      {"start": "0:08", "end": "0:10", "speed": 1.5, "curve": "ease-in"},
      {"start": "0:10", "end": "0:14", "speed": 0.2, "curve": "snap"},
      {"start": "0:14", "end": "0:22", "speed": 1.5, "curve": "ease"},
      {"start": "0:22", "end": "0:27", "speed": 0.15, "curve": "snap"},
      {"start": "0:27", "end": "0:35", "speed": 1.0, "curve": "ease-out"}
    ],
    "frame_generation": "ai-smooth",
    "audio": {"pitch_correct": true},
    "sound_effects": [{"type": "bass-impact", "at": "slow-mo-snap"}],
    "formats": ["16:9", "9:16"]
  }'
```

### Step 4 — Preview Speed Transitions
Watch each speed change. Verify: slow-mo is smooth (no stuttering), speed transitions feel natural, audio sounds correct. Export.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Speed change description |
| `speed` | float | | Global speed: 0.1-16.0 |
| `speed_map` | array | | [{start, end, speed, curve}] per-segment |
| `frame_generation` | string | | "ai-smooth", "optical-flow", "blend" |
| `audio` | object | | {pitch_correct, mute, music_replace} |
| `auto_detect` | boolean | | AI finds peak moments for slow-mo |
| `beat_sync` | boolean | | Sync speed changes to music |
| `sound_effects` | array | | [{type, at}] impact sounds at transitions |
| `time_overlay` | boolean | | Show time counter for time-lapse |
| `formats` | array | | ["16:9", "9:16", "1:1"] |

## Output Example

```json
{
  "job_id": "avsc-20260328-001",
  "status": "completed",
  "source_duration": "0:35",
  "output_duration": "0:58",
  "speed_changes": 5,
  "speed_range": "0.15x — 1.5x",
  "ai_frames_generated": 892,
  "audio": "pitch-corrected throughout",
  "outputs": {
    "landscape": {"file": "skate-speed-edit-16x9.mp4", "resolution": "1920x1080"},
    "vertical": {"file": "skate-speed-edit-9x16.mp4", "resolution": "1080x1920"}
  }
}
```

## Tips

1. **AI frame generation makes any camera a high-speed camera** — Standard 30fps phone footage becomes smooth 240fps-equivalent slow motion through AI-generated intermediate frames. No special camera needed for cinematic slow-mo.
2. **The snap into slow-mo is what creates the cinematic moment** — A gradual deceleration feels soft. An instant snap from 1.5x to 0.2x in one frame creates visceral impact. Use "snap" curve for dramatic moments, "ease" for gentle transitions.
3. **Pitch correction is mandatory for speed changes** — Without it: slow-mo sounds demonic, fast-forward sounds like chipmunks. With it: audio sounds natural at any speed. Always enable.
4. **Speed up the boring parts, slow down the interesting parts** — This is the fundamental principle. Every second at normal speed should earn its place. If a segment is not interesting enough for normal speed, speed it up or cut it entirely.
5. **Beat-synced speed changes create addictive viewing** — When slow-mo snaps align with bass drops and fast sections align with buildups, the visual rhythm matches the musical rhythm. This synchronization is what makes viewers replay speed-edited content obsessively.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |

## Related Skills

- [ai-video-zoom](/skills/ai-video-zoom) — Zoom effects
- [ai-video-mirror](/skills/ai-video-mirror) — Mirror effects
- [ai-video-flip](/skills/ai-video-flip) — Flip video
