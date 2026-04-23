---
name: social-impact-video
version: "1.0.0"
displayName: "Social Impact Video Maker — Create Advocacy and Change-Making Videos"
description: >
  Social Impact Video Maker — Create Advocacy and Change-Making Videos.
metadata: {"openclaw": {"emoji": "✊", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Social Impact Video Maker — Advocacy and Change-Making Videos

Produce videos that document, measure, and communicate social impact for NGOs, social enterprises, impact investors, and community organizations. This tool handles the full range of impact storytelling — from program-outcome documentaries and theory-of-change explainers through community-voice narratives to impact-investor pitch videos. It bridges the gap between raw impact data (lives changed, communities served, systems improved) and the human stories that make those numbers meaningful to funders, policymakers, volunteers, and the public.

## Use Cases

1. **Program Outcome Documentary** — Produce a 3-minute mini-documentary following a single community through a year-long intervention: baseline conditions, program activities, and measurable outcomes. Intercut beneficiary interviews with data overlays showing literacy rates, income growth, or health improvements.
2. **Theory of Change Explainer** — Create a 90-second animated explainer that maps the logical pathway from inputs (funding, volunteers) through activities (training, distribution) to outputs (graduates, meals) and long-term outcomes (reduced poverty, improved health). Make the logic chain visible so funders understand exactly how their money creates change.
3. **Impact Investor Pitch** — Build a 2-minute pitch video for social enterprise fundraising rounds. Combine market-opportunity data, social-impact metrics (SROI, IRIS+ indicators), founder story, and a clear ask for investment size and terms.
4. **Community Voice Campaign** — Equip community members with simple filming guides and compile their self-recorded footage into a 2-minute advocacy video. The community speaks for itself — no external narrator, no NGO branding dominating the frame.
5. **Policy Advocacy Brief** — Convert a policy paper into a 60-second video targeting legislators: the problem in one sentence, the data in one chart, the affected community in one face, and the policy ask in one slide. Designed for social media sharing before a legislative vote.

## Core API Workflow

### Step 1 — Define Impact Framework
Identify the impact metrics (IRIS+, SDG alignment, custom KPIs), gather baseline and endline data, collect beneficiary footage or self-recorded community clips, and prepare the theory-of-change diagram.

### Step 2 — Submit Generation Request
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "social-impact-video",
    "prompt": "Create a 3-minute program outcome documentary for a rural literacy initiative. Open with baseline: 34% adult literacy rate in the target district, filmed interviews with community members describing barriers to education. Middle section: show the program in action — mobile library visits, adult evening classes, volunteer tutors working with families. Data overlay: 2400 participants, 18-month program. Close with endline results: literacy rate now 61%, three participants describing how reading changed their daily lives — one reads medicine labels for the first time, one helps children with homework, one reads a bus schedule independently. Include SDG 4 alignment badge.",
    "duration": "3 min",
    "style": "program-documentary",
    "impact_data": true,
    "community_voice": true,
    "music": "documentary-warm",
    "format": "16:9"
  }'
```

### Step 3 — Poll for Completion
```bash
curl -s https://mega-api-prod.nemovideo.ai/api/v1/status/{job_id} \
  -H "Authorization: Bearer $NEMO_TOKEN"
```

### Step 4 — Review, Verify, and Distribute
Download the MP4. Cross-check all data points against evaluation reports. Distribute to grant funders (full version), social media (60-second cut), and partner organizations (co-branded version).

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the social issue, program, community, and impact data |
| `duration` | string | | Target length: "60 sec", "90 sec", "3 min", "5 min" |
| `style` | string | | "program-documentary", "theory-of-change", "investor-pitch", "community-voice", "policy-advocacy" |
| `music` | string | | "documentary-warm", "hopeful-ambient", "urgent-advocacy", "quiet-intimate" |
| `format` | string | | "16:9", "9:16", "1:1" |
| `impact_data` | boolean | | Overlay impact metrics, baseline/endline comparisons, and SDG badges (default: true) |
| `community_voice` | boolean | | Prioritize first-person beneficiary narratives over narrator voiceover (default: true) |

## Output Example

```json
{
  "job_id": "siv-20260328-001",
  "status": "completed",
  "duration_seconds": 186,
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 52.3,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/siv-20260328-001.mp4",
  "thumbnail_url": "https://mega-api-prod.nemovideo.ai/output/siv-20260328-001-thumb.jpg",
  "sections": [
    {"label": "Baseline — Community Context", "start": 0, "end": 42},
    {"label": "Program in Action", "start": 42, "end": 108},
    {"label": "Endline Results + Personal Stories", "start": 108, "end": 168},
    {"label": "SDG Alignment + CTA", "start": 168, "end": 186}
  ],
  "impact_summary": {
    "sdg_alignment": ["SDG 4 — Quality Education"],
    "participants": 2400,
    "baseline_literacy": "34%",
    "endline_literacy": "61%",
    "program_duration_months": 18
  }
}
```

## Tips

1. **Let the community tell the story** — First-person narrative from beneficiaries generates deeper engagement than third-party voiceover. Enable `community_voice` for authentic perspectives.
2. **Show baseline AND endline** — "34% → 61% literacy" is a story. "61% literacy" alone is a statistic without context. Always include the starting point.
3. **Make the theory of change visible** — A simple animated chain (input → activity → output → outcome) demystifies how funding creates results. Funders fund what they understand.
4. **Include SDG alignment badges** — Institutional funders and impact investors look for SDG mapping. The badge is a credibility signal that takes 2 seconds to display.
5. **Keep policy advocacy under 60 seconds** — Legislators and their staff won't watch 3 minutes. One problem, one chart, one face, one ask.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Grant report / funder presentation / website |
| MP4 9:16 | 1080p | Instagram / TikTok advocacy campaign |
| MP4 1:1 | 1080p | Twitter / Facebook impact post |
| GIF | 720p | Impact metric before/after animation |

## Related Skills

- [nonprofit-fundraising-video](/skills/nonprofit-fundraising-video) — Nonprofit fundraising and campaigns
- [csr-video-maker](/skills/csr-video-maker) — Corporate social responsibility content
- [awareness-campaign-video](/skills/awareness-campaign-video) — Cause awareness and advocacy
