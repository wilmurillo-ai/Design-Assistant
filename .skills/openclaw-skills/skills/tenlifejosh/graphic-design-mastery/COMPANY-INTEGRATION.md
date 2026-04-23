# COMPANY-INTEGRATION.md
## Graphic Design Mastery — Ten Life Creatives Integration Guide
### Connecting the Designer Role Charter to the Technical Skill System
#### Last Updated: 2026-03-21 | Skill Version: 1.0.0

---

## Purpose

This document bridges two things:
1. **What** Designer does — defined in `company/roles/DESIGNER-CHARTER.md`
2. **How** Designer does it — defined in `SKILL.md` and all 14 domain references

Read this before starting any design task at Ten Life Creatives.

---

## 1. Charter-to-Skill Domain Mapping

The Designer Charter defines output types. The graphic-design-mastery skill provides the technical knowledge to produce them. Here's the full mapping:

| Charter Output Type | Primary Skill Domain | Secondary Reference |
|---------------------|---------------------|---------------------|
| Brand graphics, visual identity | `references/brand-identity.md` | `references/foundations.md` |
| Cover images (Gumroad, editorial) | `references/layout.md` | `references/typography.md` |
| Thumbnails (video, content) | `references/social-marketing.md` | `references/photo-image.md` |
| Social media graphics (all platforms) | `references/social-marketing.md` | `references/foundations.md` |
| PDF visual formatting & layout | `references/layout.md` | `references/print-production.md` |
| Visual templates (reusable frames) | `references/design-systems.md` | `references/layout.md` |
| Ad creative concepts & variants | `references/social-marketing.md` | `references/brand-identity.md` |
| Brand-consistent design systems | `references/design-systems.md` | `references/foundations.md` |
| Mockups and concept visuals | `references/illustration.md` | `references/3d-webgl.md` |
| Icon system guidance | `references/illustration.md` | `references/design-systems.md` |
| Infographic layout and structure | `references/data-viz.md` | `references/layout.md` |
| Slide deck design direction | `references/layout.md` | `references/typography.md` |
| Image prompt specifications | `references/generative.md` | `references/photo-image.md` |
| Motion & animation assets | `references/motion.md` | `references/ui-ux.md` |
| UI/UX for web or Prayful | `references/ui-ux.md` | `references/design-systems.md` |
| Generative / algorithmic visuals | `references/generative.md` | `references/3d-webgl.md` |

**Skill routing logic:** When receiving a brief, identify the primary output type, then load the corresponding reference file FIRST. Load secondary reference only if the task requires it.

---

## 2. Standard Design Brief Format

The Designer Charter requires a complete brief before starting work. This is the canonical format for Ten Life Creatives, derived from `company/HANDOFF-TEMPLATES.md`:

```
---
DESIGN BRIEF — TEN LIFE CREATIVES
---

Task Title:
[Short label — e.g., "Gumroad Cover: AI COO Framework v1"]

Goal:
[What should this graphic accomplish? Be specific about the outcome.]

Audience:
[Who will see this? Demographics, platform context, buyer stage]

Platform / Use Case:
[Gumroad listing | Instagram post | Facebook ad | Email header | PDF cover | etc.]

Required Dimensions:
[Exact pixels — e.g., 1280×1080px for Gumroad, 1080×1080 for IG square]
[Use references/social-marketing.md § Platform Size Guide for standard sizes]

Tone / Visual Style:
[Premium / Clean / Bold / Editorial / Warm / Tech / Minimal / Playful]
[Reference brand personality axes from references/brand-identity.md § Brand Strategy]

Brand References:
[Color palette: Deep Navy #1B3358, Gold #C9A84C, Warm Cream #F7F3EC, Charcoal #2C2C2C]
[Always apply TLC brand colors unless brief specifies a product-specific palette]

Copy to Include:
[Exact text — verified final copy from Scribe. No approximate copy.]

CTA (if any):
[Exact CTA text — e.g., "Get Instant Access", "Download Free"]

Approval Tier:
[1 = auto-approved by Designer | 2 = Sentinel review | 3 = Founder approval]

Deadline / Priority:
[Urgent / High / Normal / Low — or specific date]

Variations Needed:
[Primary only | Primary + 2 variants | etc.]

Archive Destination:
[e.g., /company/library/design/social-graphics/ or /products/[product-name]/assets/]

Notes:
[Any other context — competitor references, existing related assets, technical constraints]
---
```

**Brief completeness gate:** If any required field above is missing, return the brief to Hutch before starting. Do not begin polished layout on an incomplete brief.

---

## 3. Brand Color Standards

Ten Life Creatives brand palette. Use these exact values on every asset unless a product-specific palette is specified in the brief.

### Primary Palette

| Role | Name | Hex | HSL | Usage |
|------|------|-----|-----|-------|
| Primary | Deep Navy | `#1B3358` | hsl(217, 52%, 23%) | Headlines, primary CTAs, key brand elements, dark backgrounds |
| Accent | Gold | `#C9A84C` | hsl(41, 52%, 55%) | Highlights, premium accents, dividers, icon accents, CTA borders |
| Background | Warm Cream | `#F7F3EC` | hsl(40, 41%, 95%) | Light backgrounds, card surfaces, page background |
| Text | Charcoal | `#2C2C2C` | hsl(0, 0%, 17%) | Body text, secondary headlines, supporting copy |

### Extended Palette (Derived from Primary)

```css
/* Use these when you need intermediate values */
--navy-dark:    #0F2040;  /* Deeper navy for shadows, hover states */
--navy-mid:     #1B3358;  /* Primary navy */
--navy-light:   #2E5490;  /* Lighter navy for secondary elements */
--gold-dark:    #A07830;  /* Darker gold for pressed states */
--gold-mid:     #C9A84C;  /* Primary gold */
--gold-light:   #E8D090;  /* Tinted gold for backgrounds */
--cream-dark:   #EDE8DE;  /* Slightly darker cream for borders */
--cream-mid:    #F7F3EC;  /* Primary cream */
--cream-light:  #FDFBF8;  /* Near-white cream for elevated surfaces */
--charcoal:     #2C2C2C;  /* Body text */
--charcoal-mid: #5A5A5A;  /* Secondary text */
--charcoal-light: #9A9A9A; /* Tertiary text, captions */
```

### Color Application Rules (60-30-10)
- **60% Warm Cream** — dominant surfaces, backgrounds
- **30% Deep Navy** — primary structure, headlines, containers
- **10% Gold** — accent, CTA, highlights, premium details

### Dark / Inverted Compositions
For dark-background designs (social covers, hero graphics):
- Swap: Navy becomes dominant background, Cream becomes text
- Gold remains the accent — it pops on both
- Always verify WCAG AA contrast (4.5:1 for body text, 3:1 for large text)

### Semantic Colors (Status Indicators)
```
Success:  #2E7D4F  (muted green — harmonizes with navy)
Warning:  #C9A84C  (reuse gold — natural for brand)
Error:    #A03030  (muted red — not garish)
Info:     #1B3358  (primary navy)
```

---

## 4. Standard Deliverable Types & Specs

### Cover Images

| Platform | Dimensions | Format | Notes |
|----------|-----------|--------|-------|
| Gumroad listing | 1280×1080px | PNG | Product-style cover, full-bleed optional |
| KDP/print front | 1600×2560px (varies) | JPG 300dpi | Full bleed at trim + 0.125" |
| Social share | 1200×630px | PNG | OG image format, link preview |
| Etsy listing | 2000×2000px | JPG | Square, lifestyle context preferred |

### Social Media Graphics

| Platform | Format | Dimensions |
|----------|--------|-----------|
| Instagram post (square) | PNG | 1080×1080px |
| Instagram post (portrait — best engagement) | PNG | 1080×1350px |
| Instagram story / Reel | PNG | 1080×1920px |
| Twitter/X post | PNG | 1200×675px |
| LinkedIn post | PNG | 1200×627px |
| Facebook post | PNG | 1200×630px |
| Pinterest pin | PNG | 1000×1500px |
| YouTube thumbnail | JPG | 1280×720px |

Reference: `references/social-marketing.md` § Platform Size Guide for complete list.

### PDF Layouts

| Type | Page Size | Bleed | Safe Zone |
|------|-----------|-------|-----------|
| Standard US document | 8.5×11" (letter) | 0.125" all sides | 0.25" inside trim |
| A4 document | 210×297mm | 3mm all sides | 5mm inside trim |
| PDF cover (KDP interior) | Varies by page count | Per KDP calculator | Per KDP specs |

Reference: `references/print-production.md` § File Setup & Specifications.

### Ad Creatives

| Type | Dimensions |
|------|-----------|
| Facebook/Instagram feed | 1200×628px horizontal, 1080×1080px square |
| Google Display (Medium Rectangle) | 300×250px |
| Google Display (Leaderboard) | 728×90px |
| Google Display (Large Rectangle) | 336×280px |
| Stories ad | 1080×1920px |

### Internal / Operational Assets

| Type | Dimensions / Format |
|------|---------------------|
| Slide deck | 1920×1080px (16:9), PPT or Google Slides |
| Infographic | 800×2000px (standard vertical) or 1200×900px (horizontal) |
| Email header | 600×200px (standard email-safe width) |
| Email template | 600px max width, table-based layout |

Reference: `references/social-marketing.md` § Email Template Design.

---

## 5. Designer → Publisher & Social Handoff Protocol

### To Publisher

Publisher deploys products to KDP, Gumroad, Etsy. Designer's delivery to Publisher must be:

**Required:**
- [ ] Files named per convention: `[ASSET-TYPE]-[PRODUCT]-[PLATFORM]-[VERSION].[ext]`
- [ ] Final exports only (no source files in export folder)
- [ ] Correct dimensions and format for destination platform
- [ ] Images at correct DPI (72dpi for web, 300dpi for print)
- [ ] All copy verified correct (no typos — print is permanent)
- [ ] Explicit message: "This bundle is Publisher-ready"

**Folder structure:**
```
/products/[product-name]/assets/
  /final/       ← Publisher gets this folder
    COVER-[name]-GUMROAD-v1.png
    COVER-[name]-SOCIAL-v1.png
    THUMB-[name]-YOUTUBE-v1.jpg
  /source/      ← Designer keeps this, not for Publisher
    COVER-[name]-GUMROAD-v1-SOURCE.fig
```

### To Social

Social needs platform-ready files, batched where possible.

**Required:**
- [ ] Files sized correctly per platform (Social should not be resizing)
- [ ] Named to indicate platform: `POST-[campaign]-INSTAGRAM-v1.png`
- [ ] Copy in the design is exact (verified against approved copy)
- [ ] Delivered as a batch when creating multi-platform campaign assets
- [ ] Include a delivery note listing all files and their destinations

**Delivery note format:**
```
DESIGN DELIVERY — [Campaign/Product Name]
Date: YYYY-MM-DD

Files:
- POST-[name]-INSTAGRAM-v1.png → Instagram feed post
- POST-[name]-STORY-v1.png → Instagram Story
- POST-[name]-TWITTER-v1.png → Twitter/X post
- POST-[name]-LINKEDIN-v1.png → LinkedIn post

Copy verified: [Yes/No]
Brand reviewed: [Yes/No]
Sentinel cleared: [Yes/No — required before Social posts]
```

---

## 6. Sentinel QA Checkpoints for Design Work

All significant design work routes through Sentinel before use. These are the checkpoints Sentinel applies to Designer's work.

### Brand Consistency Check
- [ ] Colors match TLC palette (`#1B3358`, `#C9A84C`, `#F7F3EC`, `#2C2C2C`)
- [ ] No improvised colors outside the approved palette
- [ ] Font choices align with brand typography standards
- [ ] Spacing is consistent — not arbitrary
- [ ] Visual style matches the rest of the product/campaign family

### Hierarchy & Readability Check
- [ ] Most important element is visually dominant
- [ ] Reading order is intuitive (eye flows logically)
- [ ] Text is readable at intended display size (minimum 60px at 1080px for social)
- [ ] CTA is clear and actionable
- [ ] Contrast meets WCAG AA: 4.5:1 for body text, 3:1 for large text and UI elements

### Completeness Check
- [ ] All required copy is included and correct
- [ ] No placeholder text (no "Lorem ipsum")
- [ ] Dimensions match the brief specification
- [ ] Format is correct for destination (PNG for web, PDF for print, etc.)
- [ ] File is named per TLC naming convention
- [ ] Source file is saved separately from final export

### Founder Taste Alignment Check
- [ ] Layout is clean — no cluttered or overly busy compositions
- [ ] Typography is controlled — no more than 2-3 fonts
- [ ] No clashing colors or low-contrast text
- [ ] Whitespace is intentional — not just empty
- [ ] Design reflects "what Josh would approve without revision"

### QA Result Format
```
SENTINEL QA — Design Review
Asset: [filename]
Date: YYYY-MM-DD

Brand Consistency: PASS / FAIL / FLAG
Hierarchy & Readability: PASS / FAIL / FLAG
Completeness: PASS / FAIL / FLAG
Founder Taste Alignment: PASS / FAIL / FLAG

Overall: APPROVED / REVISION REQUIRED / REJECTED

Issues (if any):
1. [Specific issue with location and recommended fix]
2. [...]

Notes:
[Any additional context]
```

---

## 7. Scripts Available

Two Python scripts are included in `scripts/`:

### `scripts/recommend_fonts.py`
Recommends font pairings based on project type, audience, and brand personality.

**When to use:** When starting a new product, campaign, or brand extension and need typographic guidance aligned with the brand.

```bash
cd /path/to/skill/scripts
python recommend_fonts.py
```

### `scripts/generate_palette.py`
Generates complete color palettes from a base color, including 10-step scales, semantic colors, and dark mode variants.

**When to use:** When a product or sub-brand needs a derived palette that harmonizes with the TLC brand while having its own identity.

```bash
cd /path/to/skill/scripts
python generate_palette.py
```

---

## 8. Quick Reference Card

```
TASK STARTS → Check brief completeness → Identify output type
→ Load primary domain reference → Apply TLC brand colors
→ Create primary design → Self-review against brief
→ Package files (named, source separated) → Deliver to Sentinel
→ Sentinel QA → Revise if needed → Deliver to Publisher or Social
```

**Brand colors always:**
- Deep Navy `#1B3358` — authority, structure
- Gold `#C9A84C` — premium, accent
- Warm Cream `#F7F3EC` — background, warmth
- Charcoal `#2C2C2C` — readable text

**When in doubt:** Go cleaner. More whitespace. Stronger hierarchy. Less is more.

---

*This document is part of the graphic-design-mastery skill package. Update this file when brand standards change or new output types are established.*
