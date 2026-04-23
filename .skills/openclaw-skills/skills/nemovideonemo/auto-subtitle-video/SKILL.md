---
name: auto-subtitle-video
version: 1.1.1
displayName: "Auto Subtitle Video — Add Subtitles to Video Automatically with AI Transcription"
description: >
  Add subtitles to any video automatically — just upload and NemoVideo transcribes, times, styles, and burns captions directly into your footage. No manual typing, no timeline editing, no SRT file formatting. Supports 90+ languages, word-level animated captions, multi-speaker detection, and batch processing for entire video libraries. Works with TikTok, YouTube, Instagram, LinkedIn, and any platform where your audience watches on mute.
metadata: {"openclaw": {"emoji": "🔤", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Auto Subtitle Video — Add Subtitles to Video Automatically

You have a video. It needs subtitles. That is the entire problem, and it should take less time to solve than it took to read this sentence — but traditional subtitle workflows make it feel like filing taxes: transcribe the audio by ear (5-10x the video duration), time each caption to the exact word (another 2-3x), format the SRT file without breaking the timestamp syntax (30 minutes of debugging colons vs commas), choose a font that's readable on every background in the video (15 minutes of second-guessing), position the captions where they won't be hidden by platform UI (knowing that TikTok, YouTube, and Instagram all have different safe zones), and render — hoping the export settings don't break the subtitle encoding. NemoVideo replaces this entire workflow with a single action: upload a video, receive it back with subtitles. The AI handles transcription (98% accuracy across 90+ languages), timing (word-level precision — each word synced to the exact millisecond it's spoken), styling (platform-appropriate fonts, colors, and positioning), and rendering (burned into the video or exported as SRT/VTT sidecar). The creator's only job is reviewing the output and clicking publish.

## Use Cases

1. **Quick Subtitle — Upload and Done (any length)** — A creator finishes editing a 60-second Reel and needs captions before posting. NemoVideo processes the video in seconds: transcribes, generates word-by-word animated captions in bold white with black outline, positions in the Instagram safe zone, and returns the captioned video ready to upload. Zero configuration needed — the defaults are optimized for social media.
2. **YouTube Tutorial with Clean Subtitles (10-30 min)** — A coding tutorial needs professional captions that don't distract from the screen share. NemoVideo generates: smaller font (36px), semi-transparent dark background bar, positioned at the bottom but not overlapping the code editor, with technical terminology handled accurately (function names, library names, error messages transcribed correctly). SRT exported alongside for YouTube's closed-caption system.
3. **Interview with Speaker Labels (5-20 min)** — A two-person interview for a company blog. NemoVideo detects both speakers by voice, labels captions ("Sarah, CEO:" / "Interviewer:"), and color-codes each speaker's text. The viewer always knows who is speaking even when both speakers are off-screen during B-roll cutaways.
4. **Social Media Batch — 10 Videos at Once** — A social media manager has 10 short-form videos due this week. NemoVideo batch-processes all 10: consistent caption styling across the batch (same font, color, position), individual SRT files for each, and burned-in versions ready for scheduling. What would take 3-4 hours of manual captioning is done while the manager works on something else.
5. **Event Keynote — Multilingual Captions (30-60 min)** — A tech conference publishes speaker recordings. NemoVideo transcribes the English keynote and generates subtitle tracks in English, Spanish, Mandarin, Japanese, and French. Each language exported as both burned-in video (for social media clips) and SRT (for the conference's video-on-demand platform with language switching).

## How It Works

### Step 1 — Upload Video
Drag and drop or provide a URL. Any format, any duration. NemoVideo detects the language automatically.

### Step 2 — Customize (Optional)
The defaults work for most social media use cases. Customize if you need: specific font, custom colors, translation, speaker labels, or sidecar-only export.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "auto-subtitle-video",
    "prompt": "Add subtitles to a 2-minute Instagram Reel. Auto-detect language (English). Word-by-word highlight animation: active word in yellow (#FBBF24), base text white with 2px black outline. Font: bold sans-serif 44px. Position: bottom 20% (Instagram safe zone). Remove filler words. Burn into video and also export SRT.",
    "auto_detect": true,
    "style": "word-highlight",
    "burn_in": true,
    "srt_export": true,
    "filler_filter": true,
    "format": "9:16"
  }'
```

### Step 4 — Review and Post
Preview. NemoVideo flags any low-confidence words for quick correction. Export and upload.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the video and caption preferences |
| `auto_detect` | boolean | | Auto-detect spoken language (default: true) |
| `language` | string | | Force language: "en", "es", "fr", "de", "ja", "zh" |
| `translate_to` | array | | Target languages for translation |
| `style` | string | | "word-highlight", "full-sentence", "clean-bar", "minimal", "karaoke" |
| `font` | string | | "bold-sans", "helvetica-light", "monospace", "serif" |
| `font_size` | integer | | Size in pixels (default: 44) |
| `text_color` | string | | Base text hex (default: "#FFFFFF") |
| `highlight_color` | string | | Active word hex (default: "#FBBF24") |
| `position` | string | | "bottom-20", "bottom-center", "center", "top" |
| `filler_filter` | boolean | | Remove um/uh/like (default: false) |
| `speaker_labels` | boolean | | Identify speakers (default: auto) |
| `burn_in` | boolean | | Render into video (default: true) |
| `srt_export` | boolean | | Export SRT sidecar (default: true) |
| `batch` | boolean | | Process multiple videos with consistent styling (default: false) |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "asv-20260328-001",
  "status": "completed",
  "duration_seconds": 122,
  "format": "mp4",
  "resolution": "1080x1920",
  "file_size_mb": 28.4,
  "transcription": {
    "language": "en",
    "confidence": 0.979,
    "word_count": 312,
    "filler_words_removed": 8
  },
  "outputs": {
    "burned_in": "reel-subtitled.mp4",
    "srt": "reel-en.srt"
  },
  "processing_time_seconds": 6.2
}
```

## Tips

1. **The default settings are optimized for social media** — Bold white text, black outline, bottom-safe-zone positioning, word-by-word highlight. If you're posting to TikTok, Reels, or Shorts, the defaults produce professional results without any customization.
2. **Batch processing saves hours for content teams** — 10 videos with consistent styling, processed simultaneously. Every caption uses the same font, size, color, and position — visual brand consistency across all content.
3. **Filler word removal makes speakers sound polished** — "Um," "uh," "you know," and "like" in captions are more noticeable than in audio. Removing them makes the speaker appear more articulate without changing what the viewer hears.
4. **Semi-transparent bar for busy backgrounds** — When the video has varying backgrounds (outdoor footage, screen shares, product shots), a dark semi-transparent bar behind the text ensures readability everywhere. Outline-only captions disappear on bright scenes.
5. **Always export SRT alongside burned-in** — Social platforms can index SRT text for search discovery. Burned-in ensures the viewer sees captions regardless of settings. Both serve different purposes — generate both with one command.

## Output Formats

| Format | Description | Use Case |
|--------|------------|----------|
| MP4 (burned-in) | Captions rendered into video pixels | Social media direct upload |
| SRT | Time-coded subtitle file | YouTube / LinkedIn / LMS upload |
| VTT | Web Video Text Tracks | Website player / accessibility |
| JSON | Word-level transcript + timestamps | Developer integration / search |

## Related Skills

- [auto-subtitle-generator](/skills/auto-subtitle-generator) — Full subtitle generation pipeline
- [subtitle-generator-ai](/skills/subtitle-generator-ai) — AI subtitle creation
- [video-caption-tool](/skills/video-caption-tool) — Video captioning tool
