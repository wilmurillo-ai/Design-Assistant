---
name: fundraising-video
version: 1.0.5
displayName: "Fundraising Video Maker — Create Donation Campaign and Appeal Videos"
description: >
  Fundraising Video Maker — Create Donation Campaign and Appeal Videos.
metadata: {"openclaw": {"emoji": "🎗️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Fundraising Video Maker — Donation Campaign and Appeal Videos

The fundraising email has a 2.3% open rate, the direct-mail letter costs $1.40 per piece and generates $0.80 in average return, and the "Donate Now" button on the website sits at the bottom of a page that 94% of visitors never scroll to — a collection of underperforming channels that collectively represent how most nonprofits ask for money: through text-based media in a world that has moved to video, using rational arguments to trigger what is fundamentally an emotional decision, and placing the ask after a wall of information when the donor's willingness to give peaks in the first 30 seconds of engagement and declines with every additional paragraph. Fundraising video content outperforms every other donation-solicitation format because giving is an emotional act rationalized after the fact — the donor feels moved by a story, decides to give, and then reads the tax-deductibility information, a sequence that video triggers faster and more reliably than text because seeing a face, hearing a voice, and watching an outcome creates empathetic connection in seconds that paragraphs of compelling copy cannot replicate in pages. This tool transforms fundraising campaigns into polished appeal videos — emotional-story appeals connecting donors to specific beneficiaries, campaign-progress updates showing momentum and creating urgency, matching-gift announcements amplifying perceived impact, year-end giving videos capitalizing on the December donation surge, emergency appeals mobilizing rapid response to crises, and the peer-to-peer fundraising tools that enable supporters to share personalized ask videos within their own networks. Built for nonprofit development teams creating campaign content, individual fundraisers running personal campaigns on GoFundMe or similar platforms, school PTAs producing annual-fund appeals, faith-based organizations funding capital campaigns, alumni associations driving reunion giving, and anyone whose cause needs money and whose current ask isn't generating enough of it.

## Example Prompts

### 1. Emotional Appeal — Story-Driven Donation Ask
"Create a 2-minute emotional fundraising appeal for a children's hospital. Opening (0-10 sec): a hospital hallway. Not sterile and cold — warm, with murals on the walls, a playroom visible through a window. 'This hallway looks like a school. It's a hospital. The murals, the colors, the playroom — they exist because a child who is scared deserves to walk through a hallway that doesn't make the fear worse.' The story (10-70 sec): a family. The parents — tired, strong, holding it together. 'When the Johnsons brought their 4-year-old daughter Emma here, they were terrified.' Show the hospital room — personalized, a stuffed animal on the bed, drawings taped to the wall. 'Emma was diagnosed with leukemia. The word alone is devastating. The treatment takes 2 years.' The care: a nurse talking to Emma at eye level, not standing over her. A doctor explaining the treatment plan to the parents with the patience that only practice at delivering hard news can produce. 'The medical team treats the disease. The support team treats the family. Social workers, child-life specialists, psychologists — they're the people who make sure a 4-year-old doesn't lose her childhood to a diagnosis.' The progress: Emma, a few months later — hair shorter, smile unchanged. Playing in the playroom with another child. 'Emma is 8 months into treatment. She's responding well. She thinks the playroom is the best part of the hospital. She's right.' The impact (70-110 sec): pull back to the broader picture. 'This hospital treats 3,200 children per year. Twelve hundred of them have cancer.' 'Insurance covers the medicine. It doesn't cover the murals, the playroom, the child-life specialists, the family housing, or the support groups for siblings who don't understand why their brother or sister lives at the hospital now.' 'That's what your donation funds: the humanity around the medicine.' The ask (110-120 sec): '$50 provides art supplies for the playroom for a month.' '$100 funds a family counseling session.' '$500 covers a week of family housing so parents can sleep near their child.' 'Emma's hallway has murals because someone donated. The next child's hallway needs them too.' Donate URL. Logo. 'Give them a hallway that doesn't make the fear worse.'"

### 2. Campaign Progress Update — Building Momentum
"Build a 60-second campaign-progress video creating urgency. Opening (0-5 sec): the fundraising thermometer — animated, filling to the current level. '$127,000 of our $200,000 goal.' 'We're 63% there. Here's what's happened and what's left.' What's been funded (5-25 sec): rapid-fire impact updates. '$127,000 has already funded: 14 wells drilled — each serving 250 people. 3,500 people now have clean water who didn't 3 months ago.' Show: three photos of completed wells — the community celebrations, the first water flowing. 'Each well took 4 weeks from funding to flowing water. The communities named two of them after the donors who funded them.' What's left (25-45 sec): the gap visualized. '$73,000 remaining = 9 more wells = 2,250 more people.' 'We have 21 days to close the gap.' Show the communities waiting — the sites surveyed, the drilling teams ready. 'The teams are ready. The sites are identified. The communities are waiting. The only missing piece is funding.' The accelerator (45-55 sec): 'A donor has offered a $25,000 match.' The thermometer updates: every dollar donated counts as two. 'Until we hit $150,000, every dollar you give is doubled. $25 becomes $50. $100 becomes $200. One well costs $8,000 — with the match, that's $4,000 from you and $4,000 from the matching donor.' CTA (55-60 sec): the thermometer pulsing. 'Twenty-one days. Nine wells. Two thousand two hundred fifty people.' Donate URL. '$73,000 to go. Let's close it.'"

### 3. Year-End Giving — December Donation Appeal
"Produce a 90-second year-end giving video. Opening (0-8 sec): calendar pages flipping — January through November. Landing on December. 'The year is almost over. There's still time to make it matter.' The reflection (8-35 sec): a year in review — 3-second clips of the nonprofit's work throughout the year. January: volunteers sorting supplies. March: a program launch. June: summer camp for underserved kids. September: back-to-school supplies delivered. November: Thanksgiving meals distributed. 'This year, your support reached 2,400 families. Each moment you just saw was made possible by someone who gave.' The deadline (35-55 sec): 'December 31 is more than New Year's Eve.' 'It's the tax-deduction deadline for charitable giving.' 'Gifts made before midnight December 31 are deductible on your 2026 taxes.' 'For many of our donors, the year-end gift is their largest. It's the gift that funds our January, our March, and our September.' The need (55-75 sec): 'Next year, we're expanding.' 'From 2,400 families to 3,200.' 'From one location to three.' 'From a summer camp of 80 kids to 200.' 'The demand is there. The families are waiting. The expansion depends on what happens between now and December 31.' The ask (75-85 sec): 'Your year-end gift — any amount — directly funds next year's expansion.' '$100 sends a child to summer camp.' '$250 provides a family with a month of support services.' '$1,000 sponsors a classroom for a semester.' CTA (85-90 sec): 'Give before December 31. The year ends. The impact doesn't.' Donate URL. Tax-ID number on screen. Logo."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the cause, campaign, goal, and donor audience |
| `duration` | string | | Target length (e.g. "60 sec", "90 sec", "2 min") |
| `style` | string | | Video style: "emotional-appeal", "progress-update", "year-end", "matching-gift", "emergency-appeal" |
| `music` | string | | Background audio: "emotional-build", "urgent-momentum", "hopeful-close" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `donation_tiers` | boolean | | Show concrete donation amounts with impact equivalencies (default: true) |
| `progress_thermometer` | boolean | | Display animated fundraising progress toward goal (default: false) |

## Workflow

1. **Describe** — Outline the campaign, goal, beneficiary story, and urgency
2. **Upload** — Add beneficiary footage, progress data, and campaign assets
3. **Generate** — AI produces the video with donation tiers, progress tracking, and emotional pacing
4. **Review** — Verify amounts, impact claims, and beneficiary consent
5. **Export** — Download in your chosen format

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "fundraising-video",
    "prompt": "Create 2-minute children hospital appeal: warm hallway with murals opening, Emma 4yo leukemia diagnosis family story, nurse at eye-level and playroom detail, insurance-covers-medicine but not humanity framing, 3200 children per year scale, $50/$100/$500 tiered donation with specific impact, hallway-that-doesnt-make-fear-worse closing line",
    "duration": "2 min",
    "style": "emotional-appeal",
    "donation_tiers": true,
    "music": "emotional-build",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Open with a person, close with a number** — The story creates emotion; the scale creates urgency. The AI structures person-first, data-second narratives.
2. **Make donation amounts concrete** — "$50 = art supplies for a month" is actionable. The AI renders tier cards when donation_tiers is enabled.
3. **Show the progress thermometer for campaigns** — Momentum motivates. The AI displays animated progress when progress_thermometer is enabled.
4. **Create urgency with deadlines** — "21 days" and "December 31" are time-bounded. The AI structures countdown framing.
5. **Include matching-gift amplifiers** — "Your $25 becomes $50" doubles perceived impact. The AI highlights matching opportunities.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Email campaign / website / gala presentation |
| MP4 9:16 | 1080p | Instagram Reels / TikTok fundraising clip |
| MP4 1:1 | 1080p | Facebook / LinkedIn campaign post |
| GIF | 720p | Progress thermometer / donation tier card |

## Related Skills

- [charity-video-maker](/skills/charity-video-maker) — Charity and cause awareness videos
- [community-event-video](/skills/community-event-video) — Community event videos
- [volunteer-video-maker](/skills/volunteer-video-maker) — Volunteer recruitment and appreciation
