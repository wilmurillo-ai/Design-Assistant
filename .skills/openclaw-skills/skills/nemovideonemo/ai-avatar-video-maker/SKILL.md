---
name: ai-avatar-video-maker
version: 1.0.3
displayName: "AI Avatar Video Maker — Create AI Spokesperson and Digital Avatar Videos"
description: >
  AI Avatar Video Maker — Create AI Spokesperson and Digital Avatar Videos.
metadata: {"openclaw": {"emoji": "🤖", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Avatar Video Maker — AI Spokesperson and Digital Avatar Videos

The training video needs a presenter, the budget doesn't include a presenter, and the last time someone from the team volunteered to be on camera they read the script like a hostage reading a ransom note — eyes darting to the teleprompter, hands frozen at their sides, delivering the phrase "we're excited to announce" with the enthusiasm of someone announcing a dentist appointment. AI avatar content solves the on-camera problem that every organization faces: not everyone is comfortable on camera, professional presenters cost thousands per day, and reshooting because someone mispronounced "synergy" for the fourth time is a budget line item nobody planned for. The technology generates realistic digital presenters from text scripts — a typed paragraph becomes a video of a human-looking avatar delivering that paragraph with natural lip sync, appropriate gestures, and the consistent delivery that real humans achieve approximately never on the first take. This tool transforms written scripts into polished AI avatar videos — digital spokesperson presentations with natural facial expressions and lip-synced speech, multi-language versions of the same video using the same avatar with different voice tracks, personalized video messages at scale where each recipient gets a video addressing them by name, training-module presenters who deliver consistent content across hundreds of lessons without fatigue or scheduling conflicts, product-demo narrators who walk through features while appearing on screen beside the interface, and the always-available virtual presenter who doesn't need makeup, doesn't have a bad-hair day, and never asks for a fifth take because they sneezed. Built for corporate communications teams producing internal announcements, L&D departments scaling training content, marketing teams creating personalized outreach, SaaS companies building product-tour libraries, e-commerce brands generating product-description videos, and anyone who needs a consistent, professional on-camera presence without the complexity of actual on-camera production.

## Example Prompts

### 1. Corporate Announcement — AI Presenter Video
"Create a 3-minute corporate announcement video using an AI avatar. Opening (0-10 sec): the avatar appears — professional attire, neutral background with subtle company branding. Lower-third: name and title. 'Good morning, team. I have three updates that affect everyone, and I want to walk you through each one clearly.' Update 1 — Policy change (10-70 sec): the avatar speaks while key points appear as bullet-point overlays beside them. 'Starting April 1st, our remote work policy is expanding from three days to four days per week.' The avatar gestures naturally toward the overlay — 'The details are on screen, but here's what matters most: your core collaboration day remains Wednesday, and the additional remote day is flexible.' Show the policy summary as a graphic while the avatar pauses. 'Your managers will reach out this week to discuss how this applies to your specific team.' Update 2 — New tool rollout (70-130 sec): the avatar continues with a screen share appearing beside them — a split layout with the avatar on the left and the software demo on the right. 'We're rolling out a new project management tool starting next Monday.' The avatar narrates while the screen recording plays. 'Training sessions are scheduled for Thursday and Friday — the links are in your inbox. If you attended the pilot program, you're already ahead.' Update 3 — Upcoming event (130-170 sec): the avatar shifts tone — slightly more enthusiastic. 'Finally, the annual company retreat is confirmed for June 14-16. This year's theme is [theme].' Show the event graphic beside the avatar. 'Registration opens Friday. Space is limited for the workshop tracks, so sign up early.' Closing (170-180 sec): the avatar returns to center frame. 'Three updates: remote policy expansion, new tool rollout Monday, retreat registration Friday. Details are in the email that accompanied this video. If you have questions, your managers have the answers — and if they don't, HR does. Have a great week.'"

### 2. Multi-Language Product Video — Same Avatar, 5 Languages
"Build a 2-minute product introduction video in 5 languages using the same AI avatar. The script: identical content, professionally translated into English, Spanish, French, German, and Japanese. English version (master): the avatar introduces the product — what it does, who it's for, how to get started. 'Our product helps [audience] achieve [outcome] in [timeframe].' Clean, simple language — chosen for translatability. Product screenshots appear beside the avatar at key moments. The avatar gestures toward the screenshots naturally. Call to action: 'Start your free trial at [URL].' Language versions: the same avatar, same gestures, same visual layout — but the voice changes to match each language. Spanish: natural Latin American Spanish, not Castilian unless specified. French: metropolitan French. German: standard Hochdeutsch. Japanese: polite-formal register. 'Each language version feels native, not dubbed. The lip sync adjusts to the new audio. The gestures remain natural.' Delivery: 5 separate video files, each with language-appropriate captions. 'One script. One production process. Five markets reached. The alternative — filming a native speaker for each language — costs 5x and takes 5x longer.'"

### 3. Personalized Outreach — Scaled Video Messages
"Produce a personalized 45-second sales outreach video template. The avatar addresses the recipient by name: 'Hi [Name], I noticed [personalized detail] and wanted to share how [product] could help with [specific pain point].' The personalization points: recipient name (inserted dynamically), company name, specific challenge (from a variable field). 'The video feels personally recorded. It's actually a template with dynamic insertion points.' The pitch: 15 seconds of value proposition, tailored to the recipient's industry. 'For [industry], our clients typically see [specific metric improvement].' Social proof: 'Companies like [similar company] achieved [result] within [timeframe].' Call to action: 'I'd love to show you a quick demo. There's a booking link below — pick a time that works.' The avatar smiles genuinely. 'Personalized video outreach gets 3x the response rate of text email. Personalized AI avatar video gets that response rate at scale.' Template variables highlighted: [Name], [Company], [Industry], [Pain Point], [Similar Company], [Result]. Each generates a unique video.'"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the script, avatar appearance, tone, and visual layout |
| `duration` | string | | Target video length (e.g. "45 sec", "2 min", "3 min") |
| `style` | string | | Video style: "corporate-announcement", "product-intro", "personalized-outreach", "training-presenter", "news-anchor" |
| `music` | string | | Background audio: "corporate-subtle", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `avatar_style` | string | | Avatar appearance: "professional", "casual", "creative" |
| `language` | string | | Output language for voice and captions (default: "en") |

## Workflow

1. **Describe** — Write the script, specify avatar appearance, and define the visual layout
2. **Upload** — Add brand assets, product screenshots, and background graphics (optional)
3. **Generate** — AI produces the video with avatar presentation, lip sync, and overlays
4. **Review** — Verify script delivery, lip-sync accuracy, and visual timing
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-avatar-video-maker",
    "prompt": "Create a 3-minute corporate announcement: professional avatar with company-branded background, 3 updates with bullet-point overlays (remote policy expansion, tool rollout with screen recording split, retreat announcement with event graphic), clear closing with action items summary",
    "duration": "3 min",
    "style": "corporate-announcement",
    "avatar_style": "professional",
    "language": "en",
    "music": "corporate-subtle",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Write scripts for speaking, not reading** — Short sentences, conversational tone, natural pauses. The AI avatar delivers conversational scripts more naturally than formal prose.
2. **Use split-screen layouts for demonstrations** — Avatar on the left, product demo on the right. The AI positions visual aids beside the avatar.
3. **Keep videos under 3 minutes for announcements** — Attention drops sharply after 3 minutes for talking-head content. Break longer scripts into chaptered segments.
4. **Match avatar formality to content** — Professional for corporate announcements, casual for product tours. The AI adjusts gesture frequency and expression range by style.
5. **Test multi-language versions with native speakers** — AI translation is good but not perfect. Have a native speaker review before publishing.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Corporate announcement / training video |
| MP4 9:16 | 1080p | TikTok / Instagram Reels avatar clip |
| MP4 1:1 | 1080p | LinkedIn post / email embed |
| GIF | 720p | Avatar greeting loop / teaser |

## Related Skills

- [ai-voice-video-maker](/skills/ai-voice-video-maker) — AI voiceover and narration videos
- [text-to-video-maker](/skills/text-to-video-maker) — Text-to-video generation
- [virtual-youtuber-video](/skills/virtual-youtuber-video) — Virtual YouTuber and VTuber videos
