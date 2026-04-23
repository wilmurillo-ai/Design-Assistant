---
name: gaming-video-editor
version: "1.0.0"
displayName: "Gaming Video Editor — AI Video Editor for Gaming Clips Montages and Highlights"
description: >
  Edit gaming videos with AI — create highlight reels, montage compilations, kill compilations, funny moments, clutch plays, and stream clips from raw gameplay footage. NemoVideo analyzes your gameplay recordings to find the best moments automatically: multi-kills, clutch rounds, epic saves, funny deaths, and high-action sequences. Then it edits them into polished gaming content with beat-synced transitions, zoom effects on key moments, meme-style captions, webcam overlay optimization, and platform-specific formatting for YouTube, TikTok, and Twitch clips.
metadata: {"openclaw": {"emoji": "🎮", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Gaming Video Editor — Turn Raw Gameplay into Content That Goes Viral

Gaming content is the largest category on YouTube and the most competitive on TikTok. Every day, millions of hours of gameplay are recorded — and 99% of it never gets edited. The raw footage sits on hard drives because the editing process is brutal: scrubbing through 3 hours of stream footage to find 5 minutes of highlights, syncing cuts to music beats, adding zoom effects on kill moments, positioning the webcam overlay, writing captions, and exporting at the right settings for each platform. A 5-minute montage from a 3-hour session takes 4-6 hours to edit manually. NemoVideo watches your gameplay and does the editing for you. The AI analyzes audio spikes (kill sounds, celebration, surprise reactions), visual events (score changes, elimination feeds, objective captures), and game-specific patterns to identify the moments worth keeping. Then it assembles those moments into polished gaming content: beat-synced transitions that land on every kill, zoom-and-shake effects on clutch plays, meme-caption overlays on funny moments, webcam footage intelligently cropped and positioned, and export formatted for YouTube (16:9), TikTok (9:16), and Twitch clips.

## Use Cases

1. **Highlight Reel — Best Moments from a Session (3-8 min)** — A player has 4 hours of Valorant footage from a ranked session. NemoVideo: scans the entire recording using audio analysis (gunfire spikes, elimination sounds, voice chat reactions) and visual analysis (kill feed, round wins, ability activations), identifies the 15-20 best moments, arranges them chronologically with smooth transitions, applies zoom-and-slow-mo on multi-kill sequences, syncs transition cuts to an energetic soundtrack, overlays round context ("Round 12 — Match Point, 1v3"), positions the webcam feed in optimal corner (resized, rounded), and exports a 6-minute highlight reel. Four hours of gameplay → 6 minutes of the best moments, professionally edited.
2. **Montage — Beat-Synced Compilation (2-4 min)** — A creator wants a cinematic montage of their best clips across multiple game sessions. NemoVideo: takes 30+ individual clips uploaded in batch, selects the strongest moments from each, arranges by escalating intensity (good → great → incredible), syncs every cut and transition to the beat of a chosen soundtrack (cut on kick drum, transition on snare, slow-mo on drop), applies cinematic color grade (high contrast, slightly desaturated for that "pro montage" look), adds velocity edits (speed up → slow-mo → snap back to full speed), and titles each clip with the game and map. The classic gaming montage format, assembled automatically.
3. **TikTok/Shorts — Viral Gaming Clip (15-55s)** — A streamer has a clutch 1v5 round and needs it on TikTok immediately. NemoVideo: extracts the clip (10 seconds before the clutch to 5 seconds after), crops to 9:16 vertical with game footage filling the top 70% and webcam reaction filling the bottom 30%, adds zoom effect at the final kill, slow-mo on the winning moment (0.25x for 2 seconds), bold caption overlay ("1v5 CLUTCH 🤯"), trending gaming music synced to the action, and exports ready for TikTok. From gameplay moment to viral clip in minutes.
4. **Stream Highlights — Auto-Generated VOD Edit (10-20 min)** — A Twitch streamer finished a 6-hour stream and needs a YouTube highlights video. NemoVideo: analyzes the entire VOD, identifies moments by chat activity spikes (emote floods, "POG" clusters), streamer reaction volume, gameplay events, and donation/sub alerts, extracts the 20-25 best moments, adds context cards between clips ("Playing Elden Ring — First Boss Attempt"), applies consistent editing style, and creates chapter timestamps for YouTube navigation. The stream VOD edit that usually takes 8 hours, produced automatically.
5. **Funny Moments — Comedy Compilation (3-8 min)** — A group of friends records their game nights and wants a "funny moments" video. NemoVideo: identifies laughter spikes, voice chat screaming, unexpected in-game events (team kills, glitches, absurd deaths), adds meme-style captions ("he did NOT just do that"), comic zoom effects, and sound effects (record scratch, sitcom laugh track on request). The friend-group gaming compilation format that drives the most engagement in gaming communities.

## How It Works

### Step 1 — Upload Gameplay Footage
Raw recordings from any source: OBS, ShadowPlay, Xbox/PS captures, Medal clips, or full stream VODs. Any game, any platform.

### Step 2 — Choose Edit Type
Select: highlight reel, montage, TikTok clip, stream highlights, or funny moments. Set: music preference, edit intensity, and webcam handling.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "gaming-video-editor",
    "prompt": "Create a 5-minute highlight reel from 3 hours of Valorant ranked gameplay. Find the best kills, clutch rounds, and ace moments. Beat-sync all cuts to energetic music. Zoom-and-slow-mo on multi-kills (0.3x for 1.5 sec). Webcam overlay: bottom-right corner, rounded, 20%% frame size. Add kill counter overlay. Context cards between clips (map name, round number). Color grade: high contrast gaming look. Export 16:9 for YouTube + extract top 3 moments as 9:16 TikTok clips (30 sec each, bold captions).",
    "edit_type": "highlight-reel",
    "game": "valorant",
    "music": "energetic-edm",
    "beat_sync": true,
    "slow_mo": {"trigger": "multi-kill", "speed": 0.3, "duration": 1.5},
    "webcam": {"position": "bottom-right", "size": "20%%", "shape": "rounded"},
    "overlays": ["kill-counter", "context-cards"],
    "color_grade": "high-contrast-gaming",
    "outputs": ["youtube-16x9", "tiktok-clips"],
    "tiktok_clips": 3
  }'
```

### Step 4 — Review and Upload
Preview the highlight reel and TikTok clips. Adjust: clip selection, music sync, transition timing. Upload to YouTube and TikTok.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Footage description and edit requirements |
| `edit_type` | string | | "highlight-reel", "montage", "tiktok-clip", "stream-highlights", "funny-moments" |
| `game` | string | | Game name for genre-specific detection |
| `music` | string | | "energetic-edm", "trap", "cinematic", "lo-fi", "custom" |
| `beat_sync` | boolean | | Sync cuts to music beats (default: true) |
| `slow_mo` | object | | {trigger, speed, duration} |
| `webcam` | object | | {position, size, shape} |
| `overlays` | array | | ["kill-counter","context-cards","meme-captions"] |
| `color_grade` | string | | "high-contrast-gaming", "cinematic", "vibrant" |
| `outputs` | array | | ["youtube-16x9","tiktok-clips","twitch-clip"] |

## Output Example

```json
{
  "job_id": "gve-20260328-001",
  "status": "completed",
  "source_duration": "3:04:22",
  "moments_detected": 47,
  "moments_selected": 18,
  "outputs": {
    "highlight_reel": {
      "file": "valorant-highlights.mp4",
      "duration": "5:12",
      "resolution": "1920x1080",
      "moments": 18,
      "beat_synced_cuts": 42,
      "slow_mo_moments": 6,
      "webcam": "bottom-right rounded"
    },
    "tiktok_clips": [
      {"file": "clip-1-ace.mp4", "duration": "0:32", "caption": "ACE IN RANKED 🎯"},
      {"file": "clip-2-clutch.mp4", "duration": "0:28", "caption": "1v4 CLUTCH ROUND 🤯"},
      {"file": "clip-3-flick.mp4", "duration": "0:24", "caption": "THE FLICK OF THE YEAR"}
    ]
  }
}
```

## Tips

1. **Beat-synced cuts are what separate amateur montages from professional ones** — Every cut landing on a beat creates rhythm. Random cuts feel chaotic. The music drives the edit, not the other way around.
2. **Slow-mo only on peak moments** — Multi-kills, clutch final kills, and impossible shots deserve slow-mo. Regular kills do not. Over-using slow-mo makes every moment feel the same.
3. **Webcam at 20% frame size in a corner** — Large webcam overlays block gameplay. Small overlays in a corner capture reactions without competing with the action. Round the corners for a clean look.
4. **Context cards between clips prevent viewer confusion** — "Ranked — Ascent — Round 18" tells the viewer the stakes. Without context, a kill is just a kill. With context, it is a match-point clutch.
5. **Vertical crops for TikTok need the gameplay on top, webcam on bottom** — The 70/30 split (gameplay top, face cam bottom) is the standard gaming TikTok layout. Both elements visible, neither cropped awkwardly.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube gaming video |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 16:9 | 720p60 | Twitch clip |
| GIF | 720p | Discord / Reddit preview |

## Related Skills

- [video-splitter](/skills/video-splitter) — Split videos into segments
- [speed-ramp-video](/skills/speed-ramp-video) — Speed ramp effects
- [online-video-editor](/skills/online-video-editor) — General video editing
