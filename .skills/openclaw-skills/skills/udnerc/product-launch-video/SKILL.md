---
name: product-launch-video
version: 1.0.3
displayName: "Product Launch Video Maker"
description: >
  Describe your product launch and NemoVideo creates the video. Software releases, hardware reveals, new feature drops, rebrands — narrate what you're launching, who it's for, and why it matters, and get a launch video that drives sign-ups and press coverage.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: ["NEMO_TOKEN"]
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎨 Welcome! I can product launch video for you. Share a video file or tell me your idea!

**Try saying:**
- "edit my video"
- "help me create a short video"
- "add effects to this clip"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Product Launch Video Maker — Create Launch Announcements and New Product Reveal Videos

Describe your product launch and NemoVideo creates the video. Software releases, hardware reveals, new feature drops, rebrands — narrate what you're launching, who it's for, and why it matters, and get a launch video that drives sign-ups and press coverage.

## When to Use This Skill

Use this skill for product and feature launch content:
- Create product reveal videos for public launch announcements
- Film feature release videos for SaaS product updates
- Build "we're live on Product Hunt" launch day content
- Document hardware product unveil and unboxing reveal videos
- Create rebrand announcement videos explaining the new direction
- Produce launch week content series across multiple platforms

## How to Describe Your Product Launch

Be specific about what's launching, who it's for, and the key benefit that makes it worth paying attention to.

**Examples of good prompts:**
- "SaaS feature launch: we're releasing async video messaging inside our project management tool. Teams can now record 90-second video updates instead of writing long status updates nobody reads. Launching on Product Hunt Tuesday. Target: remote engineering teams who have too many meetings. Show the record button, the team feed, the reaction feature. The hook: kill the weekly all-hands."
- "Hardware launch: wireless earbuds with bone conduction sensor that detects jaw movement — tap your teeth twice to pause, three times to skip. Launching at CES. Primary audience: athletes and cyclists who can't use their hands. Show the product, the jaw sensor close-up, a cyclist actually using it."
- "B2B SaaS v2.0 rebrand: we were 'DataSync Pro', now we're 'Relay'. Completely rebuilt interface, new positioning from 'data integration tool' to 'the operating layer for your business data'. Same great underlying tech, completely different UX. Existing customers get free upgrade. Show the old vs new interface side-by-side."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `launch_type` | What's launching | `"new_product"`, `"feature_release"`, `"hardware_reveal"`, `"rebrand"`, `"product_hunt"` |
| `product_name` | Product being launched | `"Relay"`, `"AthleteOS v2"` |
| `target_audience` | Who it's for | `"remote engineering teams"`, `"cyclists and athletes"` |
| `key_benefit` | Core value proposition | `"kill the weekly all-hands"` |
| `launch_platform` | Where it launches | `"product_hunt"`, `"ces"`, `"app_store"`, `"website"` |
| `show_demo` | In-product footage | `true` |
| `tone` | Launch energy | `"excited_reveal"`, `"confident_brand"`, `"problem_solution"` |
| `duration_seconds` | Video length | `60`, `90`, `120`, `180` |
| `platform` | Distribution | `"twitter"`, `"linkedin"`, `"product_hunt"`, `"youtube"` |

## Workflow

1. Describe the product, target audience, key benefit, and launch context
2. NemoVideo structures the launch narrative (hook → problem → reveal → CTA)
3. Product name, launch date, and call-to-action overlaid automatically
4. Export in the formats needed for launch day distribution

## API Usage

### SaaS Product Hunt Launch Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "product-launch-video",
    "input": {
      "prompt": "Product Hunt launch video for Relay — async video messaging for teams: We are launching Tuesday. The problem is that most team updates are either too long (nobody reads) or too short (lost context). Relay lets you record 60-second video updates that replace written status updates and most standup meetings. Show: the record button in the dashboard, the video appearing in the team feed, someone reacting with a quick emoji response, then the 'skip the meeting' moment where someone watches the update instead of joining a Zoom. 60 seconds, punchy, CTA: upvote on Product Hunt.",
      "launch_type": "product_hunt",
      "product_name": "Relay",
      "target_audience": "remote engineering and design teams",
      "key_benefit": "async video updates that replace standups",
      "launch_platform": "product_hunt",
      "show_demo": true,
      "tone": "excited_reveal",
      "duration_seconds": 60,
      "platform": "product_hunt",
      "hashtags": ["ProductHunt", "RemoteWork", "AsyncWork", "SaaS", "TeamCommunication"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "launch_def456",
  "status": "processing",
  "estimated_seconds": 85,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/launch_def456"
}
```

### Hardware Product Reveal Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "product-launch-video",
    "input": {
      "prompt": "CES hardware launch for Gnaw earbuds: bone conduction jaw sensor, control music by tapping teeth. Target: cyclists, runners, anyone who needs hands-free control. Show the product design (clean, minimal, athletic), the close-up of the jaw sensor technology, a cyclist using it one-handed on a mountain bike, then the gesture demo: two taps to pause, three to skip. End with the spec card: 8hr battery, IPX7 waterproof, available Q2 2026.",
      "launch_type": "hardware_reveal",
      "product_name": "Gnaw",
      "target_audience": "cyclists and athletes",
      "key_benefit": "hands-free music control via jaw movement",
      "launch_platform": "ces",
      "show_demo": true,
      "tone": "confident_brand",
      "duration_seconds": 90,
      "platform": "twitter"
    }
  }'
```

## Tips for Best Results

- **The hook in the first 3 seconds**: "Kill the weekly all-hands" or "Control music with your jaw" — the opening hook determines whether anyone watches the rest
- **Show the product, don't just describe it**: Set `show_demo: true` and describe what the product looks like in action — UI screenshots, product close-ups, real usage context
- **Target audience in the launch video**: "For remote engineering teams" or "For cyclists" — specific audience calling makes the right people stop scrolling
- **Launch context matters**: Product Hunt requires a specific energy (community-facing, authentic, CTA to upvote); CES is polished brand reveal; Twitter/X is punchy and fast
- **The CTA is the most important part**: "Upvote on Product Hunt", "Pre-order now", "Sign up free" — make the next step obvious and immediate

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| Product Hunt | 1920×1080 | 60–90s |
| Twitter/X | 1920×1080 | 60–140s |
| LinkedIn | 1920×1080 | 60–180s |
| YouTube | 1920×1080 | 90s–5 min |

## Related Skills

- `startup-pitch-video` — Investor-facing fundraising content
- `explainer-video-business` — How-the-product-works explainer
- `linkedin-video-maker` — Thought leadership around the launch
- `testimonial-video-maker` — Early customer proof for launch week

## Common Questions

**How many videos should I create for a launch?**
Launch day typically needs: 1 main 90-second launch video, 1 short 15-second teaser (pre-launch), and 1 feature explainer. Create them in sequence with consistent visual style.

**Can I create a launch video before the product is ready?**
Yes — describe the product as it will be. Include "launching [date]" in the prompt and set `tone: "excited_reveal"` to build anticipation rather than showing the live product.

**What's the ideal launch video length for Product Hunt?**
60-90 seconds. Product Hunt viewers are technical early adopters who will watch the full video if the first 5 seconds hook them — but not longer than 90 seconds.
