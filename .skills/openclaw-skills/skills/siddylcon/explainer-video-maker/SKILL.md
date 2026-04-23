---
name: explainer-video-maker
version: "5.0.1"
displayName: "Explainer Video Maker — Create Animated Explainer and How-It-Works Videos"
description: >
    Explainer Video Maker — Create Animated Explainer and How-It-Works Videos. Works by connecting to the NemoVideo AI backend. Supports MP4, MOV, AVI, WebM, and MKV output formats. Automatic credential setup on first use — no manual configuration needed.
metadata: {"openclaw": {"emoji": "💡", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

# Explainer Video Maker — Animated Explainer and How-It-Works Videos

The product is brilliant, the pitch deck explains it in 47 slides, and every investor meeting ends with the same question: "So what does it actually do?" Explainer videos exist because complex products need a 90-second narrative that takes a confused stranger to an informed buyer without requiring a PhD in the problem space. The format — animated characters encountering a problem, discovering the solution, and experiencing the outcome — has become the standard top-of-funnel conversion tool for SaaS, fintech, healthtech, and any industry where the product's value isn't obvious from a screenshot. This tool transforms product descriptions, pitch decks, and value propositions into animated explainer videos — problem-agitation-solution narrative structures, character animations that represent the target user, process-flow visualizations showing how the product works step by step, data-point animations that make statistics feel tangible, and the clear CTA ending that tells the viewer exactly what to do next. Built for startup founders producing landing-page hero videos, marketing teams creating campaign-launch explainers, sales enablement managers building prospect-education libraries, course creators explaining complex methodologies, nonprofit organizations communicating mission impact, and any company whose homepage visitors bounce because they can't figure out what the product does in the first ten seconds.

## Example Prompts

### 1. SaaS Startup — Problem-Solution-CTA Structure
"Create a 90-second animated explainer for our expense-management SaaS. Problem (0-20 sec): animated office worker drowning in paper receipts, spreadsheet chaos on screen, boss asking 'Where's the Q3 report?' — text: 'Finance teams spend 15 hours/month chasing expense reports.' Agitation (20-35 sec): the consequences — 'Late reimbursements. Lost receipts. Audit nightmares. Your finance team deserves better.' Solution (35-70 sec): introduce the product — character opens the app, snaps a receipt photo (OCR extracts the data instantly), expense auto-categorizes, approval workflow sends to the manager with one tap, report generates automatically. Process flow: 'Snap → Categorize → Approve → Report → Done.' Three key benefits with icons: '90% faster processing | Zero lost receipts | Audit-ready always.' Social proof (70-80 sec): '2,400 companies trust us. $1.2B expenses processed.' CTA (80-90 sec): 'Start your free 14-day trial. No credit card required.' Logo + URL. Clean, modern 2D animation — flat design, brand colors (teal #0EA5E9 + coral #F97316), friendly character style. Upbeat corporate-but-not-boring music."

### 2. Healthcare — Patient Portal Explainer
"Build a 2-minute explainer for a patient portal app. Audience: patients over 50 who are skeptical of health technology. Tone: reassuring, not patronizing. Problem: 'You called the office to reschedule. You were on hold for 22 minutes. Then they asked you to fax — fax! — your insurance card.' Solution: animated character (warm, age-appropriate — glasses, friendly face) opening the app on a tablet (not phone — larger screen reads as more accessible). Feature walkthrough: book appointments (calendar view, tap a slot), message your doctor (texting interface, response within 24 hours — 'No more phone tag'), view test results (simple cards with green/yellow/red indicators — 'Your cholesterol: 185 — in the healthy range ✓'), refill prescriptions (tap the refill button, pharmacy confirmation). Security callout: 'Your data is encrypted — the same technology your bank uses.' Closing: 'Your health information. Your schedule. Your control. Download the app or ask at your next visit.' Warm, accessible design — larger text, soft rounded shapes, muted palette (sage green, cream, soft blue). Gentle, confident narration voice. No jargon."

### 3. Nonprofit — Impact Explainer for Donors
"Produce a 75-second nonprofit impact explainer for a clean-water organization. Opening: '785 million people don't have clean water. That number is impossible to feel. Let's make it real.' Zoom into one animated village: 'This is Kibo Village. 340 people. The nearest water source is 4 km away. The walk takes 3 hours. The water makes children sick.' Solution animation: a well being drilled (construction time-lapse), clean water flowing, children drinking. Impact chain: '$1 provides clean water for 1 person for 1 year. $340 serves an entire village. $12,000 builds the well that lasts 20 years.' Visual: a dollar bill transforms into a water droplet, which multiplies into a flowing stream, which feeds the village. Before/after split screen: dusty path with jerry cans → children playing at a clean water point. Social proof: '847 wells built. 288,000 people served. 0 wells failed.' CTA: 'Fund a well. Change a village. $1 starts today.' QR code + URL. Emotional but not manipulative — warm earth tones, hopeful music building to the reveal, real impact data. No sad-piano poverty imagery."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the product/concept, narrative structure, characters, and CTA |
| `duration` | string | | Target video length (e.g. "75 sec", "90 sec", "2 min") |
| `style` | string | | Animation style: "2d-flat", "whiteboard", "isometric", "character", "motion-graphics" |
| `music` | string | | Music mood: "corporate-upbeat", "warm-hopeful", "tech-minimal", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `brand_colors` | string | | Primary and accent hex colors (e.g. "#0EA5E9, #F97316") |
| `narration` | string | | Narration voice: "professional-male", "warm-female", "friendly-neutral", "none" |

## Workflow

1. **Describe** — Write the narrative with problem, solution, benefits, social proof, and CTA
2. **Upload (optional)** — Add brand assets, logo, character references, or data visualizations
3. **Generate** — AI produces the animated explainer with characters, process flows, and data animations
4. **Review** — Preview the video, adjust the narrative pacing, verify data-point accuracy
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "explainer-video-maker",
    "prompt": "Create a 90-second expense management SaaS explainer: problem (15hrs/month chasing receipts), agitation (late reimbursements, audit nightmares), solution (snap receipt, auto-categorize, one-tap approval, auto-report), 3 benefit icons, social proof 2400 companies, CTA free 14-day trial. 2D flat animation, teal #0EA5E9 + coral #F97316",
    "duration": "90 sec",
    "style": "2d-flat",
    "brand_colors": "#0EA5E9, #F97316",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Follow Problem → Agitation → Solution → Proof → CTA** — This is the proven explainer structure. The AI uses your section labels to time each segment. Skipping the agitation step weakens the urgency; skipping social proof weakens the credibility.
2. **Describe the character as the target user** — "Office worker drowning in receipts" or "patient over 50 with glasses" helps the AI create a character the viewer identifies with. Generic characters don't create the "that's me" moment that drives conversion.
3. **Include one concrete data point per section** — "15 hours/month," "$1.2B processed," "22 minutes on hold." Numbers make abstract problems tangible. The AI animates statistics as counting-up numbers or transforming icons that are more memorable than narration alone.
4. **Specify brand colors as hex codes** — "#0EA5E9, #F97316" produces exact brand-matched visuals. "Blue and orange" produces the AI's interpretation of blue and orange, which won't match your brand guidelines.
5. **Keep the CTA to one action** — "Start your free trial" converts; "Visit our website, follow us on social, and download our whitepaper" confuses. The AI renders a single CTA as a prominent end card with animation emphasis.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Website hero / YouTube explainer |
| MP4 9:16 | 1080p | TikTok / Instagram Reels / LinkedIn vertical |
| MP4 1:1 | 1080p | LinkedIn feed / Facebook ad |
| MP4 15-sec | 1080p | Pre-roll ad cut-down |

## Related Skills

- [product-demo-video](/skills/product-demo-video) — Product walkthrough and feature demo videos
- [brand-video-maker](/skills/brand-video-maker) — Brand story and company identity videos
- [corporate-video-maker](/skills/corporate-video-maker) — Internal communications and corporate content
