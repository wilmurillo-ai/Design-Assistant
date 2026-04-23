# Skincare Video Maker — Build AM/PM Routine Content for SkinTok and Beauty Creators

Describe your skincare routine and NemoVideo creates the video. From CeraVe cleanser to retinol serum to hyaluronic acid — narrate your AM routine, PM routine, or ingredient deep-dive and get a #SkinTok-ready short that educates and converts.

## When to Use This Skill

Use this skill to create skincare content:
- Document your morning (AM) routine with hydration and SPF focus
- Film your evening (PM) routine featuring retinol, acids, and overnight treatments
- Explain ingredient science (hyaluronic acid, ceramides, niacinamide) in short-form video
- Show skin barrier repair journey with before-after skin texture comparison
- Create "What I use for [skin concern]" style content
- Build a CeraVe/drugstore routine that demystifies skincare for beginners

## How to Describe Your Routine

Be specific about products, ingredients, and the skin concern you're targeting.

**Examples of good prompts:**
- "AM skincare routine: CeraVe cleanser, The Ordinary niacinamide, hyaluronic acid serum, CeraVe AM moisturizer with SPF — focus on skin barrier protection, #SkinTok style"
- "PM retinol routine — explain why you wait 20 min after cleansing before applying retinol, how to buffer with moisturizer, skin barrier rebuilding, 45-second educational video"
- "Beginner skincare routine using only drugstore products under $15: cleanser, hyaluronic acid, ceramide moisturizer, SPF — step-by-step with ingredient callouts"

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `routine_type` | Routine focus | `"am_routine"`, `"pm_routine"`, `"ingredient_education"`, `"before_after"` |
| `products` | Product list with steps | `[{"name": "CeraVe Cleanser", "step": 1}]` |
| `key_ingredients` | Ingredients to highlight | `["retinol", "hyaluronic_acid", "ceramides"]` |
| `skin_concern` | Target issue | `"dryness"`, `"acne"`, `"aging"`, `"skin_barrier"` |
| `show_wait_timers` | Display wait times between steps | `true` |
| `duration` | Length in seconds | `30`, `45`, `60`, `90` |
| `platform` | Target platform | `"tiktok"`, `"reels"`, `"shorts"` |

## Workflow

1. Describe your routine steps, products, and skin concern
2. NemoVideo sequences the product shots with step callouts
3. Ingredient highlights and timing cues added automatically
4. Export vertical video with educational overlays

## API Usage

### AM Skincare Routine Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "skincare-video-maker",
    "input": {
      "prompt": "Morning skincare routine for dry skin: CeraVe hydrating cleanser, The Ordinary hyaluronic acid 2%, CeraVe AM moisturizer SPF 30 — skin barrier focus, simple and affordable",
      "routine_type": "am_routine",
      "key_ingredients": ["hyaluronic_acid", "ceramides", "niacinamide"],
      "skin_concern": "dryness",
      "show_wait_timers": true,
      "duration": 45,
      "platform": "tiktok",
      "hashtags": ["SkinTok", "SkincareRoutine", "AMRoutine", "CeraVe", "SkinBarrier"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "skincare_def456",
  "status": "processing",
  "estimated_seconds": 120,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/skincare_def456"
}
```

### PM Retinol Routine with Ingredient Education

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "skincare-video-maker",
    "input": {
      "prompt": "Evening skincare routine featuring retinol — explain the 20-minute wait rule, how to buffer retinol with moisturizer, why it repairs skin barrier overnight. Products: gentle cleanser, hyaluronic acid, retinol 0.5%, ceramide night cream",
      "routine_type": "pm_routine",
      "key_ingredients": ["retinol", "hyaluronic_acid", "ceramides"],
      "skin_concern": "aging",
      "show_wait_timers": true,
      "duration": 60,
      "platform": "reels",
      "voiceover": true
    }
  }'
```

## Tips for Best Results

- **Name the ingredients**: "hyaluronic acid" not just "serum" — ingredient callouts drive #SkinTok engagement
- **Include the skin concern**: "dry skin" or "skin barrier repair" helps NemoVideo frame the narrative
- **Specify AM vs PM**: Routines have different logic (SPF in AM, actives in PM) — be explicit
- **Add timing context**: "wait 20 min after retinol" details make videos more educational
- **Use real product names**: CeraVe, The Ordinary, La Roche-Posay — brand names boost searchability

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| TikTok | 1080×1920 | 30–90s |
| Instagram Reels | 1080×1920 | 30–90s |
| YouTube Shorts | 1080×1920 | up to 60s |

## Related Skills

- `makeup-tutorial-video` — Beauty application step-by-step content
- `hairstyle-video-maker` — Hair routine and styling content
- `product-photography-enhance` — Improve product flatlay photos
- `tiktok-content-maker` — General TikTok video creation

## Common Questions

**Can I upload my actual product photos?**
Yes — pass image URLs in the `images` array. NemoVideo incorporates your flatlay and application shots.

**Does it explain ingredients automatically?**
Specify `key_ingredients` and the video will include educational text callouts for each one.

**What if my routine has 7+ steps?**
List all steps in the prompt. NemoVideo groups them logically for pacing — cleanser/toner/serum/moisturizer/SPF for AM; cleanse/treat/moisturize for PM.

**Does it add wait timers?**
Set `show_wait_timers: true` to display "wait 20 min" cues between actives and moisturizers.
