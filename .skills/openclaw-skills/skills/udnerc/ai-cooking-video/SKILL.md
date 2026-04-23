---
name: ai-cooking-video
version: 1.2.1
displayName: "AI Cooking Video Maker — Create Recipe Videos and Food Content with AI"
description: >
  Create polished recipe videos, cooking tutorials, and food content using AI-powered editing. NemoVideo processes raw kitchen footage into shareable recipe clips with automatic ingredient labels, step-number overlays, speed-ramped prep sequences, recipe-card end screens, and platform-optimized exports — turning a messy 40-minute cooking session into a crisp 90-second overhead video that makes viewers hungry and hits save.
metadata: {"openclaw": {"emoji": "👨‍🍳", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Cooking Video Maker — Recipe Videos and Food Content

The overhead recipe video — hands, ingredients, cutting board, 60 seconds of cooking compressed into pure food satisfaction — looks effortless. Behind it is 40 minutes of raw footage, a camera rig that took 20 minutes to set up, lighting that required opening every blind in the kitchen and adding a ring light, a mise en place that was arranged three times before it looked casual enough, and an editing session where someone watched 40 minutes at 2x speed to find the 90 seconds of footage where the hands weren't blocking the action, the lighting was consistent, and the garlic actually sizzled on contact. NemoVideo eliminates the editing session: it identifies every ingredient addition, every technique moment (chop, pour, sizzle, flip, plate), and every dead-time segment (stirring, waiting, adjusting the stove) — then assembles the video by keeping the satisfying moments at real speed, speed-ramping the repetitive parts, labeling ingredients as they appear, numbering steps, and generating a recipe card that viewers screenshot and take to the grocery store. The creator films once and gets a 90-second Instagram clip, a 3-minute YouTube tutorial, and a 15-second TikTok teaser — all from the same raw footage.

## Use Cases

1. **Overhead Recipe — Tasty Format (60-90 sec)** — Hands-only, no face, no narration. NemoVideo processes 35 minutes of overhead footage: auto-detects ingredient additions (floating labels: "2 cloves garlic, minced"), speed-ramps boiling and simmering (10 min → 3 sec with timer overlay), preserves sizzle/pour/flip moments at real speed for sensory impact, adds step numbers ("Step 4: Deglaze with white wine"), and closes with a plating beauty shot plus full recipe card. Music: upbeat acoustic. Exported 1:1 for Instagram feed, 9:16 for Reels/TikTok.
2. **Talking-Head Recipe Tutorial (3-5 min)** — A food creator films with face cam above and overhead cam below. NemoVideo switches angles: face for personality ("This is where most people ruin their risotto"), overhead for technique (stirring in broth, showing the consistency). Ingredient callouts on overhead shots, chapter markers (Prep, Cook, Plate), and a personality-driven intro hook ("I made this dish 14 times before I got it right — here's what I learned").
3. **Meal Prep — 5 Lunches in 1 Hour (2-3 min)** — NemoVideo structures: grocery haul with price tags (12 sec), prep montage with running timer (60 sec, speed-ramped), five containers assembled with per-meal macro labels and cost ("$4.20 / 420 cal / 35g protein"), and a grocery-list end screen. The running timer creates urgency and proves the "1 hour" claim.
4. **Restaurant Chef Showcase (90 sec)** — A restaurant's social media signature-dish video. NemoVideo edits cinematically: flame close-up in slow motion, knife skills at 0.5x speed, sauce drizzle with shallow depth of field, final plating with a rack focus from dish to chef's face. No recipe card — this is brand atmosphere, not instruction. Music: moody jazz.
5. **Baking with Precision (4-6 min)** — Baking demands exact measurements and timing. NemoVideo adds: weight overlays as ingredients are added ("227g butter, room temperature"), oven-temperature display, timer countdowns for rest/proof/bake periods, visual texture indicators ("The dough should look like this" with close-up comparison), and a troubleshooting section ("Dense? You overworked the gluten. Flat? Your butter was too warm.").

## How It Works

### Step 1 — Film the Cook
Record the full process: overhead for technique, face cam for personality (optional). Film the ingredient lineup before starting — NemoVideo auto-generates labels from this shot. Film the final plated dish from multiple angles for at least 10 seconds.

### Step 2 — Provide the Recipe
Upload the recipe (ingredients + steps) as text or let NemoVideo extract it from the narration transcript. The recipe ensures labels and step numbers are accurate.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-cooking-video",
    "prompt": "Create a 90-second overhead recipe video for creamy garlic tuscan chicken. Source: 42 minutes overhead footage. Sequence: (1) Season chicken thighs — label: salt, pepper, paprika, garlic powder — real speed sear in cast iron, 10 sec. (2) Remove chicken, sauté garlic and sun-dried tomatoes — sizzle moment at real speed, label: 4 cloves garlic, 1/2 cup sun-dried tomatoes, 8 sec. (3) Add spinach — wilt montage speed-ramped 4x, label: 3 cups fresh spinach, 5 sec. (4) Pour cream and parmesan — real speed pour with steam, label: 1 cup heavy cream, 1/2 cup parmesan, 8 sec. (5) Nestle chicken back in, simmer — speed ramp 10 min to 4 sec with timer overlay, 4 sec. (6) Plating beauty shot — slow motion sauce drizzle over chicken, fresh basil garnish, rack focus, 12 sec. Recipe card end screen: full ingredients + 6 steps + serves 4 + 35 min total. Music: Italian cafe acoustic. Captions burned in. Export 1:1 + 9:16.",
    "duration": "90 sec",
    "style": "overhead-recipe",
    "ingredient_labels": true,
    "step_numbers": true,
    "speed_ramp": true,
    "recipe_card": true,
    "captions": true,
    "music": "cafe-acoustic",
    "format": "1:1"
  }'
```

### Step 4 — Review and Publish
Preview the edit. Verify ingredient labels match the recipe, step order is correct, and the recipe card includes all measurements. Export and post. The recipe card will be the most-screenshotted frame.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the dish, footage, and desired structure |
| `duration` | string | | Target length: "60 sec", "90 sec", "3 min", "5 min" |
| `style` | string | | "overhead-recipe", "talking-head-tutorial", "meal-prep", "chef-showcase", "baking-precision" |
| `ingredient_labels` | boolean | | Auto-label ingredients with names and measurements (default: true) |
| `step_numbers` | boolean | | Overlay numbered steps and cooking timers (default: true) |
| `speed_ramp` | boolean | | Accelerate prep/wait time, preserve action at real speed (default: true) |
| `recipe_card` | boolean | | Generate recipe card end screen (default: true) |
| `captions` | boolean | | Burn in captions (default: true) |
| `music` | string | | "cafe-acoustic", "upbeat-kitchen", "lo-fi-cooking", "cinematic-food", "moody-jazz" |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "acv-20260328-001",
  "status": "completed",
  "title": "Creamy Garlic Tuscan Chicken — 35-Minute Recipe",
  "duration_seconds": 92,
  "format": "mp4",
  "resolution": "1080x1080",
  "file_size_mb": 26.2,
  "output_files": {
    "square_instagram": "tuscan-chicken-1x1.mp4",
    "vertical_tiktok": "tuscan-chicken-9x16.mp4"
  },
  "sections": [
    {"label": "Season + Sear Chicken", "start": 0, "end": 15},
    {"label": "Sauté Garlic + Sun-Dried Tomatoes", "start": 15, "end": 28},
    {"label": "Wilt Spinach (speed ramp)", "start": 28, "end": 35},
    {"label": "Cream + Parmesan Pour", "start": 35, "end": 48},
    {"label": "Simmer (speed ramp)", "start": 48, "end": 55},
    {"label": "Plating Beauty Shot", "start": 55, "end": 75},
    {"label": "Recipe Card End Screen", "start": 75, "end": 92}
  ],
  "ingredient_labels_rendered": 8,
  "speed_ramps_applied": 2,
  "recipe_card": {
    "servings": 4,
    "total_time": "35 min",
    "ingredients_listed": 10,
    "steps_listed": 6
  }
}
```

## Tips

1. **Keep the sizzle at real speed** — Garlic in hot butter, chicken searing, wine deglazing — these are the sounds that make viewers hungry. Speed-ramping them kills the sensory appeal. NemoVideo identifies audio sizzle peaks and preserves them at 1x.
2. **Recipe card end screen is the most valuable frame** — 73% of cooking-video viewers screenshot the recipe. If it's not on screen, they don't save it. The recipe card converts viewers into cooks.
3. **Film the ingredient lineup first** — A 10-second pan across all ingredients enables auto-labeling and gives the viewer a visual shopping list in the opening frames.
4. **Speed-ramp waiting, not technique** — Boiling water: 10 min → 3 sec. Knife skills: full speed or slight slow-motion. Viewers watch cooking videos to see technique, not timers.
5. **Export 1:1 for Instagram grid, 9:16 for Reels/TikTok** — Square format dominates the Instagram feed; vertical dominates short-form. NemoVideo renders both from the same source with intelligent reframing.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube recipe tutorial / blog embed |
| MP4 9:16 | 1080p | TikTok / Reels / Shorts recipe clip |
| MP4 1:1 | 1080p | Instagram feed / Pinterest / Facebook |
| GIF | 720p | Sizzle moment loop / plating beauty shot |

## Related Skills

- [ai-mental-health-video](/skills/ai-mental-health-video) — Mental health education videos
- [ai-wedding-video](/skills/ai-wedding-video) — Wedding film production
- [ai-sports-video](/skills/ai-sports-video) — Sports highlight videos
