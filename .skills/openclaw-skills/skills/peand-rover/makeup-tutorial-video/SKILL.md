---
name: makeup-tutorial-video
version: 1.0.5
displayName: "Makeup Tutorial Video Maker — Create Beauty Tutorials and Makeup Look Videos"
description: >
    Makeup Tutorial Video Maker — Create Beauty Tutorials and Makeup Look Videos. Works by connecting to the NemoVideo AI backend. Supports MP4, MOV, AVI, WebM, and MKV output formats. Automatic credential setup on first use — no manual configuration needed.
metadata: {"openclaw": {"emoji": "💄", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

# Makeup Tutorial Video Maker — Beauty Tutorials and Makeup Look Videos

The foundation shade looked perfect on the back of the hand, completely different on the face, and somehow became a third color entirely under the bathroom light — because skin undertones exist, fluorescent lighting is a war crime against cosmetics, and the beauty counter associate who said "this is your shade" was working on commission under lights calibrated to sell, not to match. Makeup tutorials are the original YouTube category — beauty content predates every other niche on the platform — and they remain the most replayed format because viewers follow along in real time, pausing to blend each section before moving to the next step. The tutorials that build loyal audiences are the ones that explain why a technique works, not just how — why tapping concealer sets differently than swiping, why setting powder under the eyes before eyeshadow prevents fallout cleanup, and why the $8 drugstore mascara outperforms the $32 prestige one in a side-by-side test that the prestige brand would prefer you not see. This tool transforms raw beauty footage into polished makeup tutorials — split-face comparisons showing technique differences, product-swatch close-ups with shade names and prices, step-numbered application sequences with brush-identification callouts, before-and-after reveals with matched lighting, eye-look breakdowns with labeled lid-placement diagrams, and the natural-light final look that shows the makeup as it actually appears outside the ring-light bubble. Built for beauty YouTubers producing daily tutorial content, makeup artists showcasing editorial and bridal work, cosmetics brands creating product-education videos, beauty-school instructors building curriculum content, skincare-to-makeup hybrid creators documenting full routines, and anyone who has ever said "I just followed the tutorial" while looking nothing like the tutorial.

## Example Prompts

### 1. Full Glam — Evening Makeup Tutorial
"Create a 12-minute full glam makeup tutorial for a night out. Opening (0-15 sec): bare face, good lighting, no filter — 'This face is going to a dinner at 8. Right now it's going to the grocery store. Let's fix that.' Skin prep (15-60 sec): moisturizer application — 'Wait 2 minutes before foundation. Wet moisturizer under foundation is how you get pilling — those little balls of product that make you look like your face is shedding.' Show the wait with a time-lapse. Primer on the T-zone only — 'Primer everywhere = too slippery for foundation to grip. T-zone only, where oil breaks through first.' Base (60-180 sec): foundation application — show the shade selection process (swatch three shades on the jaw, blend into the neck, the one that disappears is correct). Apply with a damp beauty sponge — bouncing technique in macro close-up. 'Bounce, don't swipe. Swiping moves product around. Bouncing pushes it into the skin for a second-skin finish.' Concealer: under-eye triangle technique — 'The triangle brightens the under-eye and lifts the midface visually. A line following the crease just highlights the crease.' Set with translucent powder — press, don't sweep, with a velour puff. Eyes (180-400 sec): the hero section. Eye diagram overlay showing lid zones: lid, crease, outer V, inner corner, brow bone. Transition shade in the crease — 'Windshield-wiper motion with a fluffy brush. Start from the outer corner and blend inward.' Deepen the outer V with a darker shade — show the placement (small pencil brush, packed into the corner). Lid shade: pat (don't sweep) a shimmer onto the center lid with a flat shader brush. 'Patting keeps the shimmer intact. Sweeping scatters it and you lose the foil effect.' Inner corner highlight — tiny dab with a pinky finger. Lower lash line: smudge the crease shade along the outer third. Eyeliner: show the wing technique — 'Start from the outer corner angled toward the tail of your brow. Connect back to the lash line. Fill the triangle.' Show the correction technique with concealer on an angled brush for a sharp wing. Mascara: wiggle at the base, pull through — 'The wiggle separates the lashes at the root where they're densest.' Contour and highlight (400-480 sec): contour shade in the hollows of cheeks (suck in to find the hollow — 'follow the line from the ear to the corner of the mouth'), blend upward. Jaw contour for definition. Highlight on cheekbone tops, nose bridge, and cupid's bow — show the light catching each point. Blush: smile, apply to the apple, blend upward toward the temple. Lips (480-530 sec): lip liner slightly outside the natural lip line — 'This is overlining, not lying. 1mm max. More than that and it's visible in person.' Fill with lip liner as a base. Lipstick: press together, blot with tissue, second layer. Final reveal (530-720 sec): the full look — turn in natural window light. Before-and-after split: same angle, same lighting. 'Twenty-two products. Forty-five minutes. Worth it.' Product list on screen with prices."

### 2. Drugstore vs High-End — Side-by-Side Comparison
"Build a 8-minute drugstore vs prestige makeup comparison. The test: identical looks on each half of the face. Opening: bare face, line drawn down the center with an eyeliner pencil. 'Left side: $47 in drugstore products. Right side: $186 in prestige. Same technique, same brushes. Let's see if you can tell the difference at the end.' Foundation (0-100 sec): apply both simultaneously — drugstore on left (show the product: $12.99), prestige on right ($44). Blend each with identical technique. Close-up comparison: 'Coverage is comparable. The prestige formula is slightly more luminous. At 3x zoom you can see it. At conversation distance? No.' Concealer (100-160 sec): drugstore $7.99 vs prestige $32. Under-eye application. 'The prestige creases less after 4 hours. But the drugstore with a setting powder is indistinguishable.' Eyeshadow (160-300 sec): drugstore palette $14 vs prestige palette $54. Swatch the comparable shades side by side on the arm — 'The prestige mattes blend more easily. The drugstore shimmers are actually better — more metallic, less fallout.' Apply identical looks on each eye. Show the close-up: 'Can you tell which eye cost $14 and which cost $54? If you can, your screen is better than mine.' Mascara (300-350 sec): drugstore $8.99 vs prestige $28. Apply to each eye. Close-up of lash separation, volume, and clumping. 'This is where drugstore wins consistently. The $8.99 mascara lifts, separates, and holds the curl better. I will die on this hill.' Four-hour wear test (350-420 sec): time-lapse of the day — eating, working, the oil-breakthrough test at hour 4. Close-up comparison: 'The prestige foundation held slightly better in the T-zone. The drugstore eye look is identical.' Reveal (420-480 sec): full-face comparison — left vs right. 'The total difference is about 15% in performance for a 300% price increase.' Verdict: 'Save on mascara, concealer, and eyeshadow. Spend on foundation if your skin is oily. Everything else is marketing.'"

### 3. Quick Look — 5-Minute Everyday Makeup
"Produce a 5-minute everyday makeup tutorial for people who want to look polished in the time it takes to make coffee. Opening: timer on screen — 'Five minutes. Not five YouTube minutes where time mysteriously expands. Five actual clock minutes. Starting now.' Minute 1 — Base (0-60 sec): tinted moisturizer (not foundation — 'If you only have 5 minutes, you don't have time for full coverage or the commitment it requires'). Dot on forehead, cheeks, chin, blend with fingers — 'Fingers are warm. Warmth sheers out tinted moisturizer better than a sponge.' Concealer under eyes and on any spots — tap to blend. Minute 2 — Brows and eyes (60-120 sec): brow pencil — quick hair-like strokes to fill sparse areas. 'Don't draw a brow. Fill the gaps that exist.' Spoolie to blend. One eyeshadow: a neutral shimmer (finger application) pressed onto the lid. 'One shade, one finger, five seconds. It catches light and makes you look awake.' Minute 3 — Mascara and cheeks (120-180 sec): mascara on upper lashes only — 'Lower lashes take 30 seconds you don't have and smudge by noon.' Cream blush: two dots on each cheek, blend with fingers upward. 'Cream over powder for a 5-minute face. It melts into skin; powder sits on top.' Minute 4 — Lips and set (180-240 sec): tinted lip balm — 'Lipstick requires liner and precision. Tinted balm is one swipe and it looks intentional.' Setting spray: two spritzes in an X pattern over the face. 'This is the step that makes everything stay until 6 PM.' Minute 5 — Final check (240-300 sec): timer hits 5:00. Mirror check. The look: polished, natural, effortless. Before-and-after side-by-side. 'Seven products. Five minutes. You look like someone who takes care of themselves without looking like you tried. That's the goal.' Product list with prices: total under $60."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the makeup look, products, techniques, and audience skill level |
| `duration` | string | | Target video length (e.g. "5 min", "8 min", "12 min") |
| `style` | string | | Tutorial style: "full-glam", "everyday-natural", "drugstore-dupe", "editorial", "bridal" |
| `music` | string | | Background audio: "beauty-pop", "lofi-chill", "ambient-soft", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `product_labels` | boolean | | Show product names, shades, and prices on screen (default: true) |
| `face_diagram` | boolean | | Overlay placement diagrams for eye zones and contour maps (default: true) |

## Workflow

1. **Describe** — Outline the makeup look, products, application order, and target audience
2. **Upload** — Add raw tutorial footage, product close-ups, swatch shots, and before-after clips
3. **Generate** — AI produces the tutorial with step numbers, product labels, and placement diagrams
4. **Review** — Preview the edit, verify product names and technique accuracy
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "makeup-tutorial-video",
    "prompt": "Create a 12-minute full glam tutorial: skin prep with moisturizer wait tip, foundation shade matching on jaw, damp sponge bouncing technique macro, eye look with lid-zone diagram overlay, crease windshield-wiper blending, eyeliner wing technique with concealer cleanup, contour hollow placement, natural-light final reveal with before-after split, full product list with prices",
    "duration": "12 min",
    "style": "full-glam",
    "product_labels": true,
    "face_diagram": true,
    "music": "beauty-pop",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Show the technique in macro before full-face** — "Bouncing the sponge" close-up on one cheek, then pull back to show the full-face result. The AI sequences macro technique demonstrations before wide-angle results when you describe application methods.
2. **Include product swatches with shade names** — A forearm swatch of three foundations with names and prices lets viewers match their shade remotely. The AI generates labeled swatch overlays when product_labels is enabled and you name the products.
3. **Use face diagrams for placement guidance** — "Transition shade in the crease" is clearer with a labeled eye-zone diagram overlay. The AI renders anatomical placement maps when face_diagram is enabled and you describe application zones.
4. **Film the final look in natural light** — Ring lights flatter everything; window light shows the truth. The AI places natural-light footage after ring-lit application segments, giving viewers the realistic final result.
5. **End with the complete product list and total cost** — Every viewer wants to know "What did you use?" and "How much?" The AI generates an end-card product list with prices from the products mentioned in your prompt.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube beauty tutorial / course content |
| MP4 9:16 | 1080p | TikTok / Instagram Reels GRWM |
| MP4 1:1 | 1080p | Instagram post / Pinterest beauty look |
| GIF | 720p | Before-after beauty loop / technique demo |

## Related Skills

- [skincare-routine-video](/skills/skincare-routine-video) — Skincare routine and product review videos
- [hair-tutorial-video](/skills/hair-tutorial-video) — Hairstyling tutorial and hair care videos
- [nail-art-video](/skills/nail-art-video) — Nail art design and manicure tutorial videos
