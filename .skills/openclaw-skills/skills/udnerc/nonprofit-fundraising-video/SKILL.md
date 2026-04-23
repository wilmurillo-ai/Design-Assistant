---
name: nonprofit-fundraising-video
version: "1.0.0"
displayName: "Nonprofit Fundraising Video Maker — Create Donation and Campaign Videos"
description: >
  Nonprofit Fundraising Video Maker — Create Donation and Campaign Videos.
metadata: {"openclaw": {"emoji": "💝", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Nonprofit Fundraising Video Maker — Donation and Campaign Videos

Create compelling fundraising videos that turn viewers into donors. This tool produces impact stories, year-end campaigns, emergency appeals, and donor-appreciation videos for nonprofits, charities, and social enterprises. It handles the full production pipeline — from beneficiary narrative scripting through data-visualization overlays to donation-CTA rendering — so organizations can communicate their mission in a format that generates measurable giving.

## Use Cases

1. **Annual Campaign Launch** — Produce a 2-minute video combining beneficiary stories with organizational impact data for email, social media, and gala presentation. Include matching-gift callouts and a December 31 tax-deadline reminder.
2. **Emergency Appeal** — Rapidly generate a 60-second crisis-response video when a natural disaster, funding shortfall, or urgent need requires immediate donor mobilization. Emphasize urgency, specific dollar-to-impact ratios, and a one-tap donation mechanism.
3. **Peer-to-Peer Fundraiser Kit** — Create shareable 30-second clips that individual fundraisers can post on their personal social media during walkathons, birthday fundraisers, or giving days. Each clip includes the fundraiser's name, their personal goal, and a link to their campaign page.
4. **Major-Donor Cultivation** — Build a 3-minute deep-dive video for prospect meetings showing program methodology, financial transparency (cost per outcome), and a personalized message from the executive director addressing the prospect by name.
5. **Donor Thank-You Loop** — Produce quarterly thank-you videos showing what previous donations accomplished: meals served, students graduated, houses built. Close the loop so donors see their dollars at work and give again.

## Core API Workflow

### Step 1 — Prepare Assets
Gather beneficiary footage or photos, impact metrics (served/graduated/housed), logo, brand colors, and chosen background music.

### Step 2 — Submit Generation Request
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "nonprofit-fundraising-video",
    "prompt": "Create a 2-minute annual campaign video. Open with Maria, a bakery owner who graduated from our culinary program — her first-person narrative about sleeping in her car, joining the 12-week program, and opening her bakery 14 months later. Overlay impact metrics: 2400 families served, 340 graduates, 89% employment rate. Close with specific ask: $50 funds one week of training, $500 funds a full micro-loan. Include QR code and text-to-donate number. Year-end deadline December 31.",
    "duration": "2 min",
    "style": "impact-story",
    "impact_metrics": true,
    "donation_cta": true,
    "music": "warm-emotional",
    "format": "16:9"
  }'
```

### Step 3 — Poll for Completion
```bash
curl -s https://mega-api-prod.nemovideo.ai/api/v1/status/{job_id} \
  -H "Authorization: Bearer $NEMO_TOKEN"
```
Returns `{ "status": "completed", "output_url": "https://..." }` when ready.

### Step 4 — Download and Distribute
Download the rendered MP4. Upload to email platform, social channels, and event presentation deck. Track donation conversions per distribution channel.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the campaign, beneficiary story, and donation goal |
| `duration` | string | | Target length: "30 sec", "60 sec", "2 min", "4 min" |
| `style` | string | | "impact-story", "year-end-campaign", "emergency-appeal", "donor-appreciation", "peer-fundraiser" |
| `music` | string | | "warm-emotional", "hopeful-uplifting", "urgent-dramatic", "quiet-intimate" |
| `format` | string | | "16:9", "9:16", "1:1" |
| `impact_metrics` | boolean | | Overlay animated data cards showing organizational results (default: true) |
| `donation_cta` | boolean | | Render QR code / URL / text-to-donate at video end (default: true) |

## Output Example

```json
{
  "job_id": "nfr-20260328-001",
  "status": "completed",
  "duration_seconds": 124,
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 38.2,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/nfr-20260328-001.mp4",
  "thumbnail_url": "https://mega-api-prod.nemovideo.ai/output/nfr-20260328-001-thumb.jpg",
  "sections": [
    {"label": "Beneficiary Story — Maria", "start": 0, "end": 72},
    {"label": "Impact Metrics Overlay", "start": 72, "end": 96},
    {"label": "Donation Ask + CTA", "start": 96, "end": 124}
  ]
}
```

## Tips

1. **Film the present, reference the past** — Show Maria's bakery, not her car. Dignity-first visuals generate more donations than pity-based imagery.
2. **Specific dollar-to-impact ratios** — "$50 = one week of training" outperforms "please donate generously" by 3-4x in conversion testing.
3. **Send thank-you videos within 48 hours** — Speed signals that the gift was noticed. Donor retention jumps from 43% to 60%+ with timely acknowledgment.
4. **Year-end videos need a deadline** — "Donate by December 31 for tax deduction" creates urgency that open-ended asks lack.
5. **Include the uncomfortable honesty** — Acknowledging what the organization hasn't yet achieved builds more trust than a highlights-only reel.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Website / gala / email campaign |
| MP4 9:16 | 1080p | Instagram / TikTok / Reels |
| MP4 1:1 | 1080p | Facebook / Twitter fundraising post |
| GIF | 720p | Impact metric animation / social teaser |

## Related Skills

- [csr-video-maker](/skills/csr-video-maker) — Corporate social responsibility content
- [social-impact-video](/skills/social-impact-video) — Social impact storytelling
- [awareness-campaign-video](/skills/awareness-campaign-video) — Cause awareness and advocacy
