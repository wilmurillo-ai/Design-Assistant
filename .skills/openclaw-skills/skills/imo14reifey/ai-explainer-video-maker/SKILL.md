---
name: ai-explainer-video-maker
version: "1.0.0"
displayName: "AI Explainer Video Maker — Create Animated Explainer and Product Overview Videos"
description: >
  Create animated explainer videos that make complex ideas simple in 60-120 seconds. NemoVideo produces whiteboard animations, motion-graphics explainers, and character-driven narrative videos for startups explaining their product, enterprises simplifying internal processes, and educators making abstract concepts concrete — because if you can't explain it simply, you can't sell it, teach it, or get budget for it.
metadata: {"openclaw": {"emoji": "💡", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Explainer Video Maker — Animated Explainer and Product Overview Videos

The explainer video exists because of a universal human limitation: attention span divided by complexity equals comprehension, and when the denominator gets too large (your SaaS platform does 47 things), comprehension approaches zero regardless of how much attention the viewer pays — which is why the most effective sales tool in the history of B2B SaaS is not a demo, not a case study, and not a whitepaper, but a 90-second animated video that says "you have this problem, here's how we solve it, here's proof it works, try it free" in a format so compressed that the viewer understands the value proposition before their attention expires. The explainer format works because it imposes a discipline that founders, product managers, and marketers resist: radical simplification. You cannot explain 47 features in 90 seconds, so you must choose the ONE problem and the ONE solution that matters most, animate it in a way that makes the abstract concrete (showing data flowing through a pipeline is more comprehensible than describing a "data integration platform"), and close with a specific call to action before the viewer clicks away. NemoVideo handles the production — animation styles from whiteboard to motion graphics to character-driven narrative, voiceover sync, music bed, and CTA rendering — so the creator can focus on the hard part: deciding what to say in 90 seconds when they have 900 seconds of things they want to say.

## Use Cases

1. **Startup Pitch Explainer (60-90 sec)** — A B2B SaaS startup needs a homepage video. NemoVideo produces: the problem (animated frustrated user drowning in spreadsheets — 15 sec), the solution (the product dashboard appearing, data organizing itself — 20 sec), how it works (3-step animated workflow — 20 sec), proof (customer logos + one stat: "Teams save 12 hours/week" — 10 sec), CTA ("Start free trial" with animated button — 10 sec). Voiceover: professional, conversational, 150 words/minute. Style: flat motion graphics with brand colors.
2. **Internal Process Explainer (2 min)** — An enterprise HR department explains the new expense-reporting workflow to 5,000 employees. NemoVideo creates: character animation of an employee submitting an expense (step 1: photo the receipt, step 2: categorize in the app, step 3: submit — auto-routed to manager, step 4: reimbursed in 5 business days). Each step: animated screen mockup + character interaction. Closing: FAQ with the 3 most common questions answered in text cards.
3. **Product Feature Explanation (60 sec)** — A product team announces a new AI feature. NemoVideo structures: the user pain ("You spend 30 minutes writing report summaries" — 10 sec), the feature demo (animated: user clicks "Generate Summary," AI writes the report in 3 seconds — 20 sec), how it works behind the scenes (simplified: your data → AI model → formatted summary — 15 sec), and CTA ("Available now in Settings → AI Features" — 10 sec). Distributed via in-app notification and email.
4. **Investor Pitch Deck Video (2-3 min)** — A startup converts their pitch deck into a narrated video for async investor outreach. NemoVideo animates each slide: market size (animated TAM/SAM/SOM circles), problem (customer-pain scenario), solution (product demo animation), traction (animated growth chart), team (headshot transitions), and ask ($5M Series A, use of funds pie chart). The video replaces the cold email attachment that investors never open.
5. **Educational Concept Explainer (2 min)** — "How Does Blockchain Work?" for a financial literacy platform. NemoVideo produces: the analogy (imagine a notebook that everyone can read but nobody can erase — 15 sec), the mechanics (animated blocks linking together, each containing transaction data — 30 sec), why it matters (trust without intermediaries — animated bank disappearing, replaced by the chain — 20 sec), real-world examples (Bitcoin, supply chain, voting — 20 sec), limitations honestly stated (energy use, speed — 15 sec), and summary (20 sec). No jargon. The viewer's grandmother should understand it.

## How It Works

### Step 1 — Write or Provide the Script
The script is the video. A 90-second explainer = 225 words. Every word must earn its place. Provide a final script, or give NemoVideo a detailed prompt and it generates a script for review.

### Step 2 — Choose Animation Style
Select from: flat motion graphics (clean, modern — the SaaS default), whiteboard animation (hand-drawn feel — educational), character animation (people doing things — process and scenario), isometric illustration (3D-ish depth — tech and architecture), or kinetic typography (text-driven — manifesto and brand statement).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-explainer-video-maker",
    "prompt": "Create a 90-second startup explainer for DataPipe, a data integration platform. Problem (15 sec): animated scene — a data analyst surrounded by 7 different spreadsheets, databases, and dashboards, pulling hair out. Text: Your data lives in 7 places. You need it in 1. Solution (20 sec): DataPipe dashboard appears, animated data streams flowing from icons of Salesforce, HubSpot, Stripe, PostgreSQL into a single unified view. The chaos organizes itself. How it works (20 sec): 3 animated steps — Step 1: Connect your tools (animated plug icons), Step 2: DataPipe syncs automatically every 15 minutes (animated clock), Step 3: Query everything from one dashboard (animated search bar returning results). Proof (15 sec): Customer logos (Figma, Linear, Vercel), stat: Teams save 12 hours/week on data wrangling. CTA (10 sec): Start free — no credit card. Animated button with datapipe.io URL. Voiceover: professional female, warm, 150 wpm. Style: flat motion graphics. Brand colors: #4F46E5 indigo, #F9FAFB light.",
    "duration": "90 sec",
    "style": "flat-motion-graphics",
    "voiceover": "professional-female",
    "cta_overlay": true,
    "brand_colors": ["#4F46E5", "#F9FAFB"],
    "music": "tech-upbeat-subtle",
    "format": "16:9"
  }'
```

### Step 4 — Review, Iterate, Deploy
Preview the video. Adjust script timing, animation pacing, or voiceover tone. Export: 16:9 for homepage hero embed, 1:1 for LinkedIn/Twitter ads, 9:16 for paid social (Meta, TikTok). Track play-through rate and CTA conversion.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the concept, product, or process to explain |
| `duration` | string | | Target length: "60 sec", "90 sec", "2 min", "3 min" |
| `style` | string | | "flat-motion-graphics", "whiteboard", "character-animation", "isometric", "kinetic-typography" |
| `voiceover` | string | | "professional-male", "professional-female", "conversational", "energetic", "none" |
| `cta_overlay` | boolean | | Render CTA button/URL at video end (default: true) |
| `brand_colors` | array | | Hex color codes for brand palette |
| `music` | string | | "tech-upbeat-subtle", "corporate-warm", "minimal-clean", "none" |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "aevm-20260328-001",
  "status": "completed",
  "title": "DataPipe — Your Data, One Place",
  "duration_seconds": 88,
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 22.4,
  "output_files": {
    "hero_16x9": "datapipe-explainer-16x9.mp4",
    "social_1x1": "datapipe-explainer-1x1.mp4",
    "ad_9x16": "datapipe-explainer-9x16.mp4"
  },
  "sections": [
    {"label": "Problem — 7 Data Sources", "start": 0, "end": 15},
    {"label": "Solution — Unified Dashboard", "start": 15, "end": 35},
    {"label": "How It Works — 3 Steps", "start": 35, "end": 58},
    {"label": "Proof — Logos + Stat", "start": 58, "end": 75},
    {"label": "CTA — Free Trial", "start": 75, "end": 88}
  ],
  "voiceover": {"voice": "professional-female", "words": 218, "wpm": 149},
  "brand_compliance": {"colors_used": ["#4F46E5", "#F9FAFB"], "logo_placements": 2}
}
```

## Tips

1. **90 seconds = 225 words — every word must earn its place** — The most common explainer failure is trying to say too much. One problem, one solution, one proof point, one CTA. That's the entire video.
2. **Show, don't describe** — "Our platform integrates your data sources" is a description. An animated visualization of data streams flowing from 7 icons into one dashboard is comprehension. The animation IS the explanation.
3. **The problem must come before the solution** — The viewer needs to feel the pain (10-15 sec) before they care about the fix. Starting with the solution ("We built a data integration platform...") loses every viewer who doesn't already know they need one.
4. **Professional voiceover at 150 wpm** — Faster loses comprehension. Slower loses attention. 150 words per minute is the tested sweet spot for explainer narration.
5. **Deploy multiple aspect ratios from day one** — The same explainer needs 16:9 for the website, 1:1 for LinkedIn feed ads, and 9:16 for Instagram/TikTok ads. NemoVideo renders all three with intelligent reframing.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Website hero / investor deck / sales email |
| MP4 9:16 | 1080p | TikTok / Reels / Shorts paid ad |
| MP4 1:1 | 1080p | LinkedIn / Twitter / Facebook feed ad |
| GIF | 720p | Product animation loop / email embed |

## Related Skills

- [ai-elearning-video](/skills/ai-elearning-video) — eLearning course production
- [ai-presentation-video](/skills/ai-presentation-video) — Presentation video creation
- [ai-vlog-maker](/skills/ai-vlog-maker) — Vlog production and editing
