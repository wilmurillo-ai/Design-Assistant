---
name: talking-avatar-video
version: 1.0.1
displayName: "Talking Avatar Video — Create AI Presenter Videos with Realistic Digital Avatars"
description: >
  Create talking avatar videos using AI — generate realistic digital presenters that speak your script with natural lip sync, facial expressions, and body language. NemoVideo produces broadcast-quality presenter videos from text alone: choose from diverse AI avatars, customize appearance and background, deliver scripts in 30+ languages with native pronunciation, add branded overlays and CTA elements, and export professional talking-head videos without filming, studios, or on-camera talent.
metadata: {"openclaw": {"emoji": "🧑‍💼", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Talking Avatar Video — AI Presenters That Look and Sound Real

Every business communication would benefit from a human face delivering the message — a presenter looking at the camera, speaking clearly, creating the personal connection that slides and text emails cannot. But putting a human on camera requires: scheduling the person, preparing them (script memorization, wardrobe, makeup), booking a space (studio or clean room), setting up equipment (camera, lighting, microphone), recording multiple takes (most people need 3-10 takes per section), editing out mistakes, and re-filming when content changes. A 3-minute internal update takes a full production day. NemoVideo eliminates filming entirely. Write a script, choose an AI avatar, and receive a broadcast-quality talking-head video with natural lip synchronization, appropriate facial expressions, professional lighting, branded background, and lower-third titles — in minutes instead of days. When content changes (product updates, quarterly numbers, policy changes), update the script and regenerate. No re-scheduling, no re-filming. The avatar is available 24/7, delivers flawlessly on the first take, speaks 30+ languages without accent training, and costs nothing beyond the API call.

## Use Cases

1. **Corporate Training — Consistent Presenter (3-8 min per module)** — An L&D team needs a presenter for 15 compliance modules. NemoVideo produces: professional avatar in business attire against a clean office background, each module's script delivered with natural pacing, section titles animated between topics, key terms highlighted as on-screen text, and quiz prompts between sections. All 15 modules feature the same avatar for learner familiarity — produced in hours, not weeks.
2. **Product Update — Monthly Announcement (60-90s)** — A SaaS company releases monthly feature updates. NemoVideo creates: avatar with company-branded background, new features presented as animated bullet points beside the presenter, brief demo clips inserted between speaking segments, and a CTA: "Try the new features today." Same presenter every month builds brand recognition. Script change = instant regeneration.
3. **Customer Onboarding — Personalized Welcome (2-3 min)** — New customers receive a welcome video: "Welcome to [Company], [Customer Name]." NemoVideo dynamically inserts the customer's name into voiceover and on-screen text, walks through 3 getting-started steps with animated screen mockups, and closes with support contact details. Personalized at scale — thousands of unique welcome videos from one template.
4. **Multilingual Communication — One Script, 8 Languages (any length)** — A global company's safety training needs to reach teams in English, Spanish, German, French, Japanese, Portuguese, Chinese, and Arabic. NemoVideo produces the same avatar delivering the script in all 8 languages: lip sync adjusted for each language's phoneme patterns, cultural presentation style adapted (formal for Japanese, expressive for Brazilian Portuguese), and localized on-screen text. Eight language versions from one script, one production session.
5. **Social Media — Faceless Creator with a Face (30-60s)** — A content creator wants consistent talking-head videos without appearing on camera themselves. NemoVideo creates: a custom avatar that becomes the channel's face, delivering daily scripts about finance, health, or tech topics. The avatar provides the human connection that faceless videos lack, while the creator maintains privacy. Consistent character across hundreds of videos.

## How It Works

### Step 1 — Write the Script
Provide the spoken text. Mark emphasis with *asterisks*, pauses with [pause], and tone shifts with [tone: excited]. NemoVideo calculates duration (150 words ≈ 1 minute).

### Step 2 — Choose Avatar and Setting
Select: avatar appearance (gender, age, ethnicity, attire), demeanor (professional, friendly, authoritative), and background (office, studio, branded, custom image).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "talking-avatar-video",
    "prompt": "Create a 2-minute product update video. Avatar: professional male, early 40s, business casual, approachable demeanor. Background: modern office with subtle company logo. Script: Welcome to the April product update. This month we shipped two features you have been asking for. First, real-time collaboration. Multiple team members can now edit the same project simultaneously with zero lag. Second, smart templates. AI analyzes your past projects and suggests layouts that match your style. Both features are live in your account right now. Try them today. Lower-third: David Kim, Head of Product. End CTA: See all updates at app.example.com/changelog.",
    "avatar": "professional-male-40s",
    "attire": "business-casual",
    "demeanor": "approachable",
    "background": "modern-office-branded",
    "language": "en",
    "lower_third": "David Kim, Head of Product",
    "cta": "app.example.com/changelog",
    "format": "16:9"
  }'
```

### Step 4 — Review and Distribute
Preview the video. Adjust: avatar expression, speech pacing, background elements. Export and distribute via email, LMS, website, or social channels.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Script and production requirements |
| `avatar` | string | | Avatar selection: demographics and style |
| `attire` | string | | "business-formal", "business-casual", "casual", "medical", "custom" |
| `demeanor` | string | | "professional", "friendly", "authoritative", "energetic", "calm" |
| `background` | string | | "modern-office", "studio-white", "branded", "custom-image" |
| `language` | string | | "en", "es", "de", "fr", "ja", "pt", "zh", "ko", "ar" |
| `lower_third` | string | | Name and title overlay |
| `cta` | string | | Call-to-action text/URL |
| `music` | string | | "corporate-subtle", "none" |
| `format` | string | | "16:9", "9:16", "1:1" |
| `batch_scripts` | array | | Multiple scripts for series production |

## Output Example

```json
{
  "job_id": "tav-20260328-001",
  "status": "completed",
  "duration_seconds": 124,
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 32.4,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/tav-20260328-001.mp4",
  "avatar": {
    "type": "ai-digital-presenter",
    "appearance": "professional-male-40s",
    "lip_sync": "natural",
    "language": "en",
    "demeanor": "approachable"
  },
  "overlays": {
    "lower_third": "David Kim, Head of Product (0:02-0:08)",
    "cta": "app.example.com/changelog (1:56-2:04)"
  }
}
```

## Tips

1. **Same avatar across a series builds trust** — Viewers develop familiarity with a consistent presenter. Changing avatars between episodes breaks the relationship. Lock in one avatar for the entire series, course, or update cycle.
2. **150 words per minute is natural pacing** — Faster sounds rushed and reduces comprehension. Slower sounds patronizing. 150 wpm is the conversational pace that works for 80% of business content.
3. **Lower-thirds in the first 8 seconds** — The viewer needs to know who's speaking immediately. Display name and title early, then remove to keep the frame clean.
4. **Branded background with subtle logo** — The logo should be recognizable but not dominant. A clean office with the logo at 20% opacity on the wall communicates brand without competing for attention.
5. **Multilingual from one script saves weeks** — Traditional multilingual video requires separate filming sessions per language. NemoVideo produces all languages from one translated script set — identical quality, fraction of the time.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Website / LMS / email |
| MP4 9:16 | 1080x1920 | LinkedIn / TikTok / social |
| MP4 1:1 | 1080x1080 | Instagram / internal comms |
| MP4 (transparent bg) | 1080p | Custom compositing |

## Related Skills

- [ai-video-script-generator](/skills/ai-video-script-generator) — Script writing
- [video-hook-maker](/skills/video-hook-maker) — Hook generation
- [video-color-correction-ai](/skills/video-color-correction-ai) — Color correction
