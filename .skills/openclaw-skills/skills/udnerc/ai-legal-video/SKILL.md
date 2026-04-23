---
name: ai-legal-video
version: "1.0.0"
displayName: "AI Legal Video Maker — Create Law Firm Marketing and Legal Explainer Videos"
description: >
  Create professional legal videos for law firm marketing, client education, and courtroom presentation using AI-powered production. NemoVideo produces attorney profile videos, practice-area explainers, client testimonials with bar-compliant disclaimers, FAQ answer series, and case-result showcases — helping lawyers convert website visitors into consultations by showing expertise through video instead of walls of legalese nobody reads.
metadata: {"openclaw": {"emoji": "⚖️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Legal Video Maker — Law Firm Marketing and Legal Explainer Videos

The average law firm website bounces 65-75% of visitors because it presents the scared, confused person searching "do I need a lawyer after a car accident" with exactly what they don't want: dense paragraphs of legal terminology explaining practice areas in language the visitor doesn't understand, a team page of headshots communicating nothing about whether this attorney is competent or trustworthy, and a contact form demanding the visitor commit to a consultation before seeing any evidence this firm can help. Video fixes every one of these failures. A 60-second attorney introduction builds trust a headshot cannot. A 2-minute practice-area explainer demonstrates expertise in language the visitor actually understands. A client testimonial proves results. A FAQ video answers the exact question the visitor Googled before asking them to call. NemoVideo produces all of these at scale for law firms that understand the prospective client's hiring decision — choosing the attorney for the most stressful legal situation of their life — is fundamentally emotional, dressed in rational justification. Video is the only medium that communicates both competence and empathy simultaneously, and the firm that has video on every attorney profile page and every practice-area page converts at 2-3x the rate of the firm that relies on text alone.

## Use Cases

1. **Attorney Profile Video (60-90 sec)** — Filmed in the attorney's office — bookshelves, diplomas, natural light. NemoVideo structures: name and specialty title card (5 sec), personal story of why they became a lawyer (15 sec — the human connection, not the resume), approach to clients ("I return every call within 4 hours and explain everything in plain language" — 20 sec), a representative result without confidential details (15 sec), what a first visit looks like demystified (15 sec), and CTA: "Free consultation" with phone number large on screen (10 sec). Zero legal jargon. Warm, confident, approachable.
2. **Practice Area Explainer (2 min)** — "What is personal injury law and when do you need a lawyer?" NemoVideo produces an animated explainer: the situation (accident, injury, medical bills mounting), the legal concept (negligence, liability, damages — illustrated with simple diagrams, not Latin phrases), the typical process timeline (investigation → demand letter → negotiation → trial if needed, with realistic durations), what the firm handles vs what the client does, and CTA: "Free case evaluation." Designed for the practice-area page and YouTube SEO.
3. **Client Testimonial with Compliance (90 sec)** — A satisfied client describes their experience on camera. NemoVideo auto-applies the required state bar disclaimer ("Prior results do not guarantee a similar outcome") as both text overlay and audio disclosure. The testimonial: the client's problem, their fear before hiring, how the attorney handled the case, and the resolution. Filmed at the client's home or business for authenticity, not in the law office.
4. **Legal FAQ Series (60 sec each)** — The firm's 10 most-Googled questions, each answered in 60 seconds. NemoVideo structures: the question as a bold text hook (3 sec), the attorney answering in plain English (45 sec), a key-takeaway text overlay (7 sec), and CTA (5 sec). Optimized for YouTube search and Google featured snippets. Example: "How much does a DUI lawyer cost?" → "Most criminal defense attorneys charge a flat fee between $2,500 and $10,000 depending on the complexity. Here's what determines the price..."
5. **Case Result Showcase (90 sec)** — Without revealing client identity, the firm presents a notable outcome. NemoVideo structures: animated situation (car accident at intersection), the legal challenge (disputed liability — the other driver's insurance denied fault), the firm's strategy (attorney describing the investigation, accident reconstruction, witness depositions), the result ($1.8M settlement — animated counter rising), and the bar-required disclaimer. Professional, factual, compelling without being boastful.

## How It Works

### Step 1 — Film the Attorney
Record in the attorney's actual office with a smartphone on a tripod at eye level plus a clip-on lavalier mic ($15). The office environment — bookshelves, desk, diplomas — provides subconscious credibility signals that a studio cannot replicate.

### Step 2 — Provide Compliance Requirements
Specify the state bar's attorney advertising rules (varies by state). NemoVideo auto-applies required disclaimers, avoids prohibited claims (outcome guarantees), and formats testimonials with mandated disclosures.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-legal-video",
    "prompt": "Create a 90-second attorney profile video. Attorney: Michael Torres, Criminal Defense, Torres Law Group, 18 years experience. Filmed in his office, bookshelf and law-school diplomas behind him. Structure: (1) Title card — Michael Torres, JD, Criminal Defense Attorney, 5 sec. (2) Origin story — worked as a public defender for 6 years, saw how the system treats people who cant afford representation, started his own firm to bridge that gap, 15 sec. (3) His approach — every client gets his personal cell number, he answers calls on evenings and weekends because arrests dont happen during business hours, 20 sec. (4) What to expect — a free 30-minute consultation where Michael reviews the charges, explains the possible outcomes honestly, and outlines a defense strategy, 20 sec. (5) A representative result — DUI case dismissed after challenging the traffic stop legality, client kept their license and their job, 15 sec. (6) CTA — Call 555-0247 now or book online at torreslaw.com, phone number large on screen, 10 sec. Disclaimer text: Prior results do not guarantee similar outcomes, per Texas State Bar Rule 7.01-7.07. Tone: direct, confident, zero condescension. Music: professional subtle at -18dB.",
    "duration": "90 sec",
    "style": "attorney-profile",
    "compliance": "texas-bar",
    "lower_third": true,
    "cta_overlay": true,
    "disclaimer": true,
    "music": "professional-subtle",
    "format": "16:9"
  }'
```

### Step 4 — Compliance Review and Publish
Route through the firm's compliance reviewer or state bar advertising committee if required. Verify disclaimers, confirm no prohibited claims. Publish to: attorney profile page, Google Business Profile (highest-ROI placement — every patient who searches the attorney's name sees it), YouTube, and social media.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the attorney, video type, and key messages |
| `duration` | string | | Target length: "60 sec", "90 sec", "2 min" |
| `style` | string | | "attorney-profile", "practice-area-explainer", "client-testimonial", "legal-faq", "case-result" |
| `compliance` | string | | State bar rules: "texas-bar", "california-bar", "new-york-bar", "florida-bar", "aba-model-rules" |
| `lower_third` | boolean | | Show attorney name, title, and firm (default: true) |
| `cta_overlay` | boolean | | Render phone number, URL, or booking link (default: true) |
| `disclaimer` | boolean | | Auto-apply state-bar-required advertising disclaimers (default: true) |
| `music` | string | | "professional-subtle", "confident-corporate", "warm-trust", "none" |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "alv-20260328-001",
  "status": "completed",
  "title": "Michael Torres — Criminal Defense Attorney | Torres Law Group",
  "duration_seconds": 92,
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 27.8,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/alv-20260328-001.mp4",
  "sections": [
    {"label": "Title Card + Credentials", "start": 0, "end": 5},
    {"label": "Origin Story — Public Defender", "start": 5, "end": 20},
    {"label": "Approach — Personal Cell, Evenings", "start": 20, "end": 40},
    {"label": "First Visit — What to Expect", "start": 40, "end": 60},
    {"label": "Representative Result — DUI Dismissed", "start": 60, "end": 75},
    {"label": "CTA + Disclaimer", "start": 75, "end": 92}
  ],
  "compliance": {
    "standard": "Texas State Bar Rules 7.01-7.07",
    "disclaimers_applied": 1,
    "prohibited_claims_check": "passed — no outcome guarantees",
    "testimonial_disclosures": "not applicable (no client testimonial in this video)"
  }
}
```

## Tips

1. **The origin story builds trust faster than credentials** — "I was a public defender for 6 years" connects emotionally. "I graduated from Harvard Law" impresses peers but doesn't build trust with a scared client at 2 AM searching for a criminal defense attorney.
2. **Demystify the first visit** — The #1 barrier to hiring a lawyer is fear of the unknown: what happens, what it costs, whether the attorney will judge them. "A free 30-minute conversation where I explain your options honestly" reduces that fear in 15 seconds.
3. **No jargon — translate everything** — "Negligence per se" means nothing to the person who was rear-ended. "The law says the other driver was automatically at fault because they ran a red light" means everything.
4. **Google Business Profile is the highest-ROI video placement** — Every person who searches the attorney's name sees the Google listing first. A video there is the first impression before the website.
5. **State bar disclaimers are non-negotiable** — Rules vary by state. Omitting required disclaimers risks bar discipline. NemoVideo's compliance parameter auto-applies the correct format per jurisdiction.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Website / YouTube / Google Business Profile |
| MP4 9:16 | 1080p | Instagram Reels / TikTok / Stories |
| MP4 1:1 | 1080p | LinkedIn / Facebook / Twitter |
| GIF | 720p | Attorney intro loop / CTA animation |

## Related Skills

- [ai-mental-health-video](/skills/ai-mental-health-video) — Mental health education videos
- [ai-cooking-video](/skills/ai-cooking-video) — Recipe and food content
- [ai-wedding-video](/skills/ai-wedding-video) — Wedding film production
