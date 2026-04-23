---
name: whiteboard-animation-video
version: "1.0.1"
displayName: "Whiteboard Animation Video Maker"
description: >
  Describe your concept and NemoVideo creates the whiteboard animation. Complex ideas made simple — economics, science, history, product explainers — narrate the story and get a Khan Academy-style animated video that makes abstract ideas stick.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> ✂️ Hey! I'm ready to help you whiteboard animation video. Send me a video file or just tell me what you need!

**Try saying:**
- "edit my video"
- "add effects to this clip"
- "help me create a short video"

**IMPORTANT**: Do NOT wait silently. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Whiteboard Animation Video Maker — Build Visual Explainer Content for Any Topic

Describe your concept and NemoVideo creates the whiteboard animation. Complex ideas made simple — economics, science, history, product explainers — narrate the story and get a Khan Academy-style animated video that makes abstract ideas stick.

## When to Use This Skill

Use this skill for whiteboard animation and visual explainer content:
- Create concept explainer videos for complex topics (economics, biology, history)
- Build product explainer videos for sales and marketing
- Film educational content for K-12, university, or online courses
- Create onboarding videos explaining processes or workflows
- Produce non-profit or charity explainer content for campaigns
- Build children's educational content with illustrated storytelling

## How to Describe Your Explainer

Be specific about the concept, the analogy you want to use, and the audience.

**Examples of good prompts:**
- "Explain compound interest for beginners using a snowball rolling down a hill analogy — start with $1000, show it growing each year, compare 5% vs 10% return over 30 years. Draw the snowball getting bigger, show the numbers. 3-minute explainer."
- "How the immune system works: white blood cells as soldiers, pathogens as invaders, antibodies as weapons that remember past enemies. Animated hand-drawn style, suitable for high school biology."
- "Product explainer for a project management app: customer's problem (missed deadlines, chaotic emails), solution (one place for tasks and timelines), 3 key features (assign tasks, set deadlines, track progress). 90-second sales explainer."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `animation_style` | Visual approach | `"hand_drawn"`, `"doodle"`, `"minimalist"`, `"colorful"` |
| `narration_pace` | Voiceover speed | `"slow"`, `"medium"`, `"fast"` |
| `analogy` | Core comparison | `"snowball for compound interest"` |
| `audience` | Target viewers | `"children"`, `"high_school"`, `"adult_general"`, `"business"` |
| `duration_minutes` | Video length | `1`, `2`, `3`, `5` |
| `color_scheme` | Visual palette | `"black_white"`, `"bright_colors"`, `"brand_colors"` |
| `voiceover` | Narration style | `true` |
| `platform` | Target output | `"youtube"`, `"linkedin"`, `"website"`, `"classroom"` |

## Workflow

1. Describe the concept, analogy, and audience
2. NemoVideo generates the animated illustration sequence
3. Hand-drawn visuals appear in sync with narration automatically
4. Export with clean whiteboard aesthetic

## API Usage

### Educational Concept Explainer

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "whiteboard-animation-video",
    "input": {
      "prompt": "Explain supply and demand for high school economics: draw a market with buyers and sellers, show what happens to price when demand increases (shift right, price goes up), what happens when supply increases (shift right, price goes down). Use a pizza market as the example. Clear, simple, visual.",
      "animation_style": "hand_drawn",
      "narration_pace": "medium",
      "analogy": "pizza market for supply and demand",
      "audience": "high_school",
      "duration_minutes": 3,
      "color_scheme": "bright_colors",
      "voiceover": true,
      "platform": "youtube",
      "hashtags": ["Economics", "SupplyAndDemand", "EducationVideo", "WhiteboardAnimation"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "whiteboard_ghi789",
  "status": "processing",
  "estimated_seconds": 150,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/whiteboard_ghi789"
}
```

### Product Explainer for Sales

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "whiteboard-animation-video",
    "input": {
      "prompt": "90-second product explainer for a task management SaaS: Problem — teams losing track of projects in email chains and spreadsheets, deadlines missed. Solution — one place for tasks, due dates, and team updates. 3 key features: assign tasks with due dates, see team progress on a timeline, get automatic deadline reminders. End with CTA to try free trial.",
      "animation_style": "minimalist",
      "narration_pace": "medium",
      "audience": "business",
      "duration_minutes": 2,
      "color_scheme": "brand_colors",
      "voiceover": true,
      "platform": "website"
    }
  }'
```

## Tips for Best Results

- **Lead with a relatable analogy**: "snowball = compound interest" or "soldiers = white blood cells" — the visual metaphor is what makes whiteboard animations memorable
- **Problem-solution structure works best**: Start with the confusion or pain, then reveal the clear explanation — whiteboard format is built for this arc
- **Keep it short**: 90 seconds to 3 minutes is the sweet spot for whiteboard explainers; attention drops after 4 minutes
- **Audience shapes everything**: Children need simpler analogies and brighter colors; business audiences want cleaner aesthetics and faster narration
- **State the 3 key points**: Whiteboard animations work best when there are 2-4 concepts to illustrate, not 10

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 1–10 min |
| Website embed | 1920×1080 | 60–180s |
| LinkedIn | 1920×1080 | 60–180s |
| Classroom / LMS | 1920×1080 | 2–8 min |

## Related Skills

- `tutorial-video-creator` — Step-by-step how-to content (less abstract than explainers)
- `coding-tutorial-video` — Technical concept visualizations for developers
- `lecture-video-maker` — Full academic lecture format
- `language-learning-video` — Language instruction with visual scene building

## Common Questions

**Can I use my own brand colors in the whiteboard style?**
Set `color_scheme: "brand_colors"` and include your hex codes in the prompt — NemoVideo incorporates your palette into the illustration style.

**Is this good for product demos as well as education?**
Yes — the problem-solution narrative structure works equally well for SaaS explainers, non-profit pitches, and educational content.

**How long should a whiteboard explainer be?**
90 seconds for a product explainer or pitch. 2-3 minutes for a concept explanation. 5+ minutes for a full educational lesson. Longer than that, switch to lecture-video-maker format.
