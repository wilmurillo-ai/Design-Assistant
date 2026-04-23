---
name: wedding-video-editor
version: "1.0.4"
displayName: "Wedding Video Editor — Cinematic Highlight Reels Ceremony Cuts and Reception Montages from Raw Footage"
description: >
  The ceremony photographer shot six hours of raw footage across three cameras. The videographer captured the reception from two angles. The couple wants a three-minute highlight reel for Instagram, a fifteen-minute cinematic film for the family, and individual clips of the vows, first dance, and cake cutting to send to guests who couldn't attend. Without a dedicated editor, that request takes thirty hours of manual work. Wedding Video Editor processes multi-camera wedding footage and produces all three outputs in a single session: the algorithm identifies the emotionally significant moments (tear-wiping during vows, laughter at the speeches, first dance dips), syncs them across camera angles for the best coverage, matches the edit rhythm to the chosen soundtrack, applies cinematic color grading suited to the venue lighting, and exports each deliverable at the correct resolution and aspect ratio for its destination platform. The couple gets their social reel, their archival film, and their family clips without waiting six months for a freelance editor.
metadata: {"openclaw": {"emoji": "💍", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Wedding Video Editor — From Raw Footage to Cinematic Wedding Films

## Use Cases

1. **Highlight Reels for Social Media** — Instagram and TikTok reels need the ceremony's best sixty seconds: the ring exchange, the first kiss, the confetti exit. Wedding Video Editor selects the peak emotional moments, matches cuts to the music's beat drops, and exports vertical 9:16 and square 1:1 formats ready for posting the same evening.

2. **Full Ceremony Film** — Parents and grandparents want to watch the complete ceremony later. Wedding Video Editor assembles the multi-camera edit with synchronized audio, smooth angle transitions, and title cards for each chapter (Processional, Vows, Ring Exchange, Recessional) into a single polished file.

3. **Reception Montage** — First dance, parent dances, speeches, cake cutting, and the final send-off each need their own clip. Wedding Video Editor identifies each reception segment from the footage timeline, applies consistent color grading across all clips, and exports a folder of shareable MP4s for the couple to distribute to guests.

4. **Destination Wedding Content** — Couples who travel to film their wedding often have drone footage, venue B-roll, and candid clips alongside ceremony footage. Wedding Video Editor weaves the location visuals into a travel-meets-wedding cinematic short that doubles as content for travel and wedding inspiration audiences.

## How It Works

1. **Upload footage** — Drop your raw video files (ceremony, reception, drone shots, candids). Multiple files and cameras supported.
2. **Describe your deliverables** — "Three-minute Instagram highlight reel with our chosen song, plus a ten-minute full film with vows chapter and first dance chapter."
3. **Review the edit** — Wedding Video Editor returns a structured edit with the most emotionally resonant moments prioritized, music synced, and color graded.
4. **Export** — Download each deliverable at the correct spec for its platform.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "wedding-video-editor",
    "input": {
      "footage_urls": ["https://...ceremony.mp4", "https://...reception.mp4"],
      "deliverables": ["3min highlight reel", "15min full film"],
      "music_url": "https://...chosen-song.mp3",
      "style": "cinematic"
    }
  }'
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `footage_urls` | array | Raw video file URLs (multi-camera supported) |
| `deliverables` | array | Output types: highlight reel, full film, individual clips |
| `music_url` | string | Optional: background music for highlight reel |
| `style` | string | `cinematic`, `romantic`, `documentary`, `upbeat` |
| `chapters` | array | Optional: label segments (vows, first dance, speeches) |

## Tips

- Include footage from multiple angles for the best coverage selection
- Specify the highlight reel duration for social platform optimization (60s for Instagram Reels, 90s max)
- Mention the venue lighting type (outdoor golden hour, indoor dim reception) for correct color grading
- Upload music with enough length to cover the highlight reel without abrupt cuts
- Label your files by segment (ceremony, reception, cocktail hour) to improve chapter accuracy
