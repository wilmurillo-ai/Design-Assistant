---
name: cat-video-creator
version: 1.0.5
displayName: "Cat Video Creator — Create Feline Behavior and Cat Life Showcase Videos"
description: >
  Cat Video Creator — Create Feline Behavior and Cat Life Showcase Videos.
metadata: {"openclaw": {"emoji": "🐱", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Cat Video Creator — Feline Behavior and Cat Life Showcase Videos

The cat did something genuinely hilarious at 3 AM — a full-body leap from the dresser to the ceiling fan chain, a mid-air recalculation, and a landing on the laundry pile that would've scored a 9.2 in Olympic gymnastics — and the only witness was a half-asleep human who didn't think to grab a phone until the cat was already sitting on the windowsill pretending nothing happened. Cat content dominates every platform because cats are inherently cinematic: they have dramatic lighting preferences (every sunbeam is a stage), impeccable comedic timing (the pause before the swat), and a complete indifference to being filmed that reads as effortless charisma. This tool transforms the hundreds of nearly-identical-looking cat clips in your camera roll into structured feline content — personality showcases that capture the specific weirdness of your cat, daily-routine compilations timed to the cat's actual schedule (not yours), multi-cat dynamics with relationship narratives, slow-motion hunting sequences that reveal the athlete inside the couch potato, and the adoption-anniversary montages that celebrate the journey from shelter cage to sun puddle. Built for cat Instagram accounts growing beyond 10K followers, shelter adoption coordinators producing meet-the-cat profiles, cat behaviorists documenting enrichment-protocol results, veterinary clinics creating patient-spotlight reels, cat-café owners showcasing resident personalities, and the 94 million cat owners who film their cat daily but never edit a single clip.

## Example Prompts

### 1. Cat Personality Profile — Instagram Series
"Create a 60-second personality-profile Reel for Mochi, a 5-year-old tuxedo cat. Opening: Mochi sitting in a cardboard box that's clearly too small — 'Mochi. 5 years old. Thinks she's a liquid.' Quick-cut personality showcase: the 6 AM face tap (her wake-up method), the sprint from nothing to nothing (zoomies clip), sitting IN the salad bowl on the counter (text: 'Personal chef. Unpaid.'), the slow blink at the camera (text: 'This is affection. Allegedly.'), chattering at a bird through the window (teeth-clacking audio boosted), kneading the blanket for 45 seconds straight (time-lapse: 'Biscuit count: 847'). The one serious moment: Mochi curled in a sunbeam, genuinely beautiful — hold for 3 seconds, no text, just the purring audio. Closing card: 'Mochi | Professional napper. Amateur bird hunter. Full-time weirdo.' Playful pizzicato strings soundtrack."

### 2. Multi-Cat Household — Relationship Documentary
"Build a 3-minute documentary-style video about the relationship between our two cats: Chairman Meow (orange tabby, 8, grumpy) and Beans (calico kitten, 6 months, chaotic). Narrator-style text cards: 'Day 1: Chairman Meow hissed for 4 hours straight. Beans was unbothered.' Show the introduction through a baby gate (Chairman's murder-eyes visible). 'Week 2: The first tolerance.' — sharing the couch with exactly 3 feet of buffer zone. 'Week 4: The accidental touch.' — tails brushing while sleeping, both startling awake. 'Month 2: The grooming.' — Chairman licking Beans' head, then immediately biting her ear (text: 'Love language: complicated'). 'Month 3: Found like this.' — both curled together in the cat tree, Chairman's paw draped over Beans. Closing: 'They're not friends. They're roommates who share custody of the sunny spot.' Gentle indie folk with a comedic tone shift for the biting scene."

### 3. Shelter Cat Adoption Profile — Senior Cat Feature
"Produce a 45-second adoption video for Whiskers, 12-year-old orange tabby, at the shelter for 6 months. Opening: 'Whiskers has been waiting 187 days. He'd like you to know he's worth it.' Show him doing his signature move: the slow approach, the headbutt against an offered hand, the immediate flop onto his back for belly rubs (text: 'Rare: a cat who actually wants belly rubs'). Lap-sitting segment: curled on a volunteer's lap, eyes closed, purr audible. Honest note: 'Whiskers has managed hyperthyroidism — one pill daily, hidden in a Churu treat. His vet says he's got years of napping left.' Closing: Whiskers looking through the cage bars, then the shot opens to the volunteer holding him — 'Adopt Whiskers | Age: 12 (distinguished) | Fee: $50 | Includes: one pill-hiding trick, unlimited headbutts.' Shelter logo. Warm, golden grade — nothing clinical. Hopeful piano, not sad piano."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the cat(s), personality traits, key moments, and emotional tone |
| `duration` | string | | Target video length (e.g. "45 sec", "60 sec", "3 min") |
| `style` | string | | Visual style: "personality-profile", "documentary", "shelter-adoption", "aesthetic", "comedy" |
| `music` | string | | Music mood: "pizzicato", "indie-folk", "piano", "playful", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `text_cards` | boolean | | Show narrator-style text cards between clips (default: true) |
| `purr_audio` | boolean | | Boost and preserve purring audio in quiet moments (default: true) |

## Workflow

1. **Describe** — Write the cat's personality with specific behaviors, quirks, and the story arc
2. **Upload** — Add clips of key behaviors, funny moments, sleeping positions, and interaction footage
3. **Generate** — AI selects the most character-revealing clips, adds text cards, and paces for comedy or sentiment
4. **Review** — Preview the video, adjust the comedic timing, verify the emotional arc lands
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "cat-video-creator",
    "prompt": "Create a 60-second personality Reel for Mochi, 5yo tuxedo: too-small box, 6AM face tap, salad bowl sitting, slow blink, bird chattering with teeth audio, blanket kneading timelapse, sunbeam purring moment held 3 seconds. Closing card with bio. Pizzicato strings",
    "duration": "60 sec",
    "style": "personality-profile",
    "format": "9:16"
  }'
```

## Tips for Best Results

1. **Describe the specific weird behavior, not the category** — "Sits IN the salad bowl" is content; "funny cat moments" is nothing. The AI selects clips matching your specific descriptions, so the weirder and more precise, the better the result.
2. **Include the comedic pause** — Cat humor lives in timing. "Slow blink at the camera — hold 2 seconds before the text appears" gives the AI the beat that makes the joke land. Rushing text overlays over cat moments kills the natural comedy.
3. **Boost the purring for emotional moments** — Enable `purr_audio` and describe the quiet scene ("sunbeam, curled up, eyes closed"). The AI isolates and amplifies the purr frequency while reducing background noise. Purring is the most emotionally resonant sound in pet content.
4. **Use narrator-style text for multi-cat dynamics** — "Day 1: hissing. Week 4: accidental touch. Month 3: found like this." Text-card narration gives multi-cat stories a documentary structure that viewers follow like a plot. Direct captions ("our cats are friends now") don't build narrative tension.
5. **Show the honest health note for shelter cats** — "Managed hyperthyroidism, one pill daily" attracts the right adopter and prevents returns. The AI formats medical disclosures as dignified info cards, not scary warnings.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube cat personality documentary |
| MP4 9:16 | 1080p | TikTok / Instagram Reels |
| MP4 1:1 | 1080p | Instagram feed cat post |
| MP4 45-sec | 1080p | Shelter adoption profile card |

## Related Skills

- [pet-video-maker](/skills/pet-video-maker) — General pet highlight reels and montage videos
- [funny-pet-video](/skills/funny-pet-video) — Pet comedy compilations and blooper reels
- [pet-care-video](/skills/pet-care-video) — Pet health, grooming, and care tutorials
