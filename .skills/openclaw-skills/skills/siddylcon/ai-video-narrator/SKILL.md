---
name: ai-video-narrator
version: "1.0.0"
displayName: "AI Video Narrator — Add Professional AI Narration and Voiceover to Any Video"
description: >
  Add professional AI narration and voiceover to any video — generate natural-sounding narration from text or scripts, match voice tone to video mood, synchronize narration with visual timing, and produce documentary-quality voiceover without hiring talent. NemoVideo creates narration that sounds human: varied pacing, emotional inflection, natural pauses, breath sounds, and style matching. Narrate product demos, documentaries, explainer videos, tutorials, presentations, and social content with AI voices indistinguishable from professional voice actors. AI narrator video, add narration to video, video voiceover generator, documentary narrator AI, text to narration video, auto narrate video, video storyteller AI.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video Narrator — Give Any Video a Voice It Deserves

Narration transforms video. A silent product demo becomes a persuasive sales tool when a confident voice explains each feature. A montage of travel footage becomes a documentary when a warm narrator weaves the story. A tutorial becomes accessible when a clear voice guides the viewer step by step. Raw footage is ingredients — narration is the recipe that makes them a meal. Professional voice actors charge $100-500+ per finished minute. A 5-minute explainer video costs $500-2,500 for voiceover alone. Recording takes scheduling, studio time, direction, retakes, and editing. Changes mean re-recording. Translation means hiring different actors for each language. The cost and friction mean most video content ships silent or with amateur narration that undermines the visual quality. NemoVideo generates narration that sounds like a professional voice actor recorded it in a studio. Not robotic text-to-speech — actual narration with pacing that matches the visual rhythm, emphasis on key words, emotional tone that fits the content, natural pauses between ideas, and the subtle vocal qualities that make a voice sound human and trustworthy.

## Use Cases

1. **Product Demo — Feature Walkthrough Narration (2-10 min)** — A software company has a screen recording showing their product in action. Silent, it is a confusing sequence of clicks. With narration: each click is contextualized, each feature is explained, benefits are articulated. NemoVideo: takes the script ("Here you can see the dashboard. Notice how the analytics update in real-time..."), generates narration timed to the visual actions on screen, uses a confident and professional voice tone (trustworthy, not salesy), pauses when visual transitions happen (letting the viewer absorb what they see), and mixes the narration with subtle background music. A screen recording becomes a polished product tour.

2. **Documentary Style — Travel or Nature Footage (5-30 min)** — A filmmaker has 20 minutes of stunning mountain landscape footage and wants it to tell a story. NemoVideo: generates narration from the script in a warm, contemplative documentary voice (think David Attenborough's pacing — unhurried, wonder-filled), times narration to match scene changes (speaking during wide establishing shots, pausing during intimate close-ups), varies the delivery pace (slower for dramatic moments, slightly faster for action sequences), and mixes voice with ambient nature sounds. Footage becomes a documentary that audiences watch from beginning to end.

3. **Tutorial — Step-by-Step Instruction (any length)** — A cooking channel needs voiceover for a recipe video showing each step. NemoVideo: uses a clear, friendly, instructional voice, paces each instruction to match the visual action ("Now fold the dough over itself" — spoken as the hands on screen do exactly that), pauses between steps (giving viewers time to follow along), emphasizes important warnings ("Be careful — the oil is extremely hot"), and maintains a consistent, encouraging tone throughout. A tutorial that viewers can follow without pausing or rewinding.

4. **Social Content — Quick Narrated Story (15-60s)** — A TikTok or Reel needs a narrated story over footage clips. NemoVideo: uses the conversational, slightly energetic voice style that performs on short-form platforms, paces for short attention spans (no pauses longer than 0.5 seconds), hits key story beats in sync with visual cuts, and adds the natural vocal quirks (slight emphasis, casual tone) that make narration feel authentic rather than generated. Social narration that sounds like a creator telling a story, not a robot reading a script.

5. **Multilingual — One Video, Many Language Narrations (any length)** — An international company needs the same explainer video narrated in English, Spanish, German, Japanese, and Portuguese. NemoVideo: generates all five narrations from translated scripts, matches voice characteristics across languages (similar pitch, pacing, and tone in each), adjusts timing per language (German and Japanese run longer than English for the same content), and exports five language versions. One production effort, global reach.

## How It Works

### Step 1 — Upload Video and Script
Upload the video. Provide the narration script (full text or bullet points that NemoVideo expands).

### Step 2 — Choose Voice and Style
Select voice character (warm, authoritative, casual, energetic), gender, age range, and accent. Or describe the voice you want in natural language.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-narrator",
    "prompt": "Narrate a 3-minute product demo video. Script: [Section 1, 0:00-0:45] Welcome to DataFlow — the analytics platform that turns raw data into decisions. Watch as we connect a data source in under 10 seconds. [Section 2, 0:45-1:30] The dashboard updates in real-time. Every chart, every metric, every insight — live. No refresh needed. [Section 3, 1:30-2:30] Custom reports take 30 seconds to build. Drag the metrics you care about, set the date range, and share with your team instantly. [Section 4, 2:30-3:00] DataFlow. From data to decision in minutes, not days. Voice: confident male, mid-30s, warm but professional. Pacing: match visual actions. Background music: subtle corporate ambient.",
    "voice": {"gender": "male", "age": "mid-30s", "style": "warm-professional", "accent": "neutral-american"},
    "timing": "sync-to-sections",
    "background_music": "subtle-corporate-ambient",
    "music_ducking": true
  }'
```

### Step 4 — Review Timing and Tone
Listen to the full narration synced with video. Check: voice matches content mood, timing aligns with visual actions, pacing feels natural. Adjust any section if needed.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Script and narration instructions |
| `voice` | object | | {gender, age, style, accent, language} |
| `timing` | string | | "sync-to-sections", "auto-pace", "manual-timestamps" |
| `background_music` | string | | Music style or "none" |
| `music_ducking` | boolean | | Lower music during narration |
| `emphasis` | array | | [{word, style}] word-level emphasis |
| `pauses` | object | | {between_sections, between_sentences} in seconds |
| `languages` | array | | ["en", "es", "de", "ja"] for multilingual |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "avn-20260328-001",
  "status": "completed",
  "source_duration": "3:00",
  "narration": {
    "voice": "male, mid-30s, warm-professional",
    "sections_synced": 4,
    "total_narration": "2:42",
    "silence_gaps": "0:18 (intentional pauses)"
  },
  "background_music": "corporate-ambient, ducked during voice",
  "output": {"file": "product-demo-narrated.mp4", "resolution": "1920x1080"}
}
```

## Tips

1. **Voice style must match content mood** — A warm documentary voice on a fast-paced tech demo feels disconnected. An energetic voice on a meditation video is jarring. Voice style is as important as the words spoken.
2. **Sync narration to visual actions, not just timecodes** — "Click the blue button" should be heard the moment the cursor clicks the blue button on screen. Visual-audio sync creates the feeling of a guided tour rather than a disconnected voiceover.
3. **Pauses are as important as words** — A 1-second pause after a key statement lets the information land. Continuous talking without pauses creates cognitive overload. Strategic silence makes narration more impactful.
4. **Music ducking prevents voice competition** — Background music should drop 10-15dB when narration begins and rise during visual-only moments. This keeps the voice always clear while music fills the silent gaps.
5. **Multilingual narration from one script saves 80% vs. hiring per-language actors** — One script translated and narrated by AI in five languages costs a fraction of hiring five voice actors, scheduling five sessions, and editing five recordings.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website / presentations |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |
| MP3 only | — | Audio narration track (for external editing) |

## Related Skills

- [ai-video-voice-over](/skills/ai-video-voice-over) — Voiceover
- [ai-video-presenter](/skills/ai-video-presenter) — AI presenter
- [ai-video-dubbing-tool](/skills/ai-video-dubbing-tool) — Video dubbing
