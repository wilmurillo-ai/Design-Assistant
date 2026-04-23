# Layout & Composition Reference

Use this reference for: print layout, editorial design, magazine/book layout, poster design, brochure/flyer
design, business cards, packaging, certificates, menus, signage, environmental graphics, and any design task
where spatial arrangement of elements on a surface is the primary challenge.

---

## TABLE OF CONTENTS
1. Poster Design
2. Editorial & Magazine Layout
3. Business Card Design
4. Brochure & Flyer Design
5. Certificate & Award Design
6. Menu Design
7. Packaging Design Concepts
8. Large Format & Environmental

---

## 1. POSTER DESIGN

### Poster Anatomy
Every effective poster has these layers:

1. **Attention Layer**: The single element that stops someone in their tracks (usually large image or bold type)
2. **Information Layer**: The essential details (what, when, where)
3. **Texture Layer**: The subtle details that reward closer inspection

### Poster Composition Approaches

**Full Bleed Image + Overlay Text**: Image covers entire poster. Text overlaid with contrast treatment.
- Use semi-transparent color block behind text
- Or place text in a naturally low-detail area of the image
- Or use `mix-blend-mode` to integrate text with image

**Typographic Poster**: Type IS the visual. No imagery needed.
- Use extreme scale contrast (one word at 200pt, details at 10pt)
- Play with weight, width, color within a single word
- Explore vertical/diagonal/curved text placement

**Grid-Based Information Poster**: Structured layout for content-rich posters.
- Strong column grid (3-4 columns)
- Clear typographic hierarchy
- Consistent spacing system
- Color blocks to separate sections

**Asymmetric Dynamic Poster**: Diagonal composition, overlapping elements, broken grids.
- Create movement through diagonal axes
- Overlap images and text deliberately
- Use scale contrast for dramatic tension

### Poster Size Standards
```
A3:     297 × 420mm (11.69 × 16.54")
A2:     420 × 594mm (16.54 × 23.39")
US Letter: 8.5 × 11"
Tabloid: 11 × 17"
24×36": Common US poster size
```

### SVG Poster Template (A3 proportions)
```svg
<svg viewBox="0 0 595 842" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="595" height="842" fill="#1a1a2e"/>

  <!-- Grid overlay (construction, remove in final) -->
  <!-- 3 columns with 24px gutter, 40px margins -->

  <!-- Headline zone: top 40% -->
  <!-- Information zone: middle 35% -->
  <!-- Details zone: bottom 25% -->
</svg>
```

---

## 2. EDITORIAL & MAGAZINE LAYOUT

### Spread Design Principles

**The Optical Center**: In a printed spread (two facing pages), the reader's eye enters at the top-left of the
right page — NOT the geometric center. Place focal elements here or at the top third.

**Cross-Gutter Flow**: Elements that span across the gutter (spine) of a spread create unity. But ensure
critical content (faces, text) doesn't fall in the gutter.

**Pacing**: A publication needs rhythm — dense pages alternating with sparse ones. Full-bleed images followed
by generous whitespace. This pacing keeps the reader engaged.

### Column Structures

**Single Column** (manuscript): Best for long-form reading. Max width 65ch.
```css
.manuscript {
  max-width: 40em;
  margin: 0 auto;
  padding: 2rem;
}
```

**Two Column**: Versatile. Main content + sidebar, or equal columns for comparison.
```css
.two-col {
  display: grid;
  grid-template-columns: 2fr 1fr; /* Main + sidebar */
  gap: 2rem;
}
```

**Three Column**: Editorial standard. Flexible for mixed content.
```css
.three-col {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
/* Span image across 2 columns */
.feature-image { grid-column: 1 / 3; }
```

### Pull Quotes & Breakout Elements
Break the grid deliberately to create visual interest:
```css
.pull-quote {
  grid-column: 1 / -1;
  max-width: 80%;
  margin: 3rem auto;
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-style: italic;
  border-left: 4px solid var(--color-brand);
  padding-left: 1.5rem;
}
```

### Running Headers & Folios
```css
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
  padding-bottom: 1rem;
  border-bottom: 0.5px solid var(--color-border-default);
  margin-bottom: 2rem;
}
```

---

## 3. BUSINESS CARD DESIGN

### Standard Dimensions
- **US**: 3.5 × 2" (89 × 51mm)
- **EU**: 85 × 55mm (3.35 × 2.17")
- **Japan**: 91 × 55mm
- **Square**: 2.5 × 2.5" (trending)

### Print Specifications
- **Bleed**: 3mm (0.125") on all sides
- **Safe zone**: Keep text 5mm (0.2") from trim edge
- **Resolution**: 300 DPI minimum
- **Color**: CMYK for print, RGB for digital mockup

### Layout Patterns

**Minimal Left-Aligned**:
```
┌─────────────────────────┐
│                         │
│  LOGO                   │
│                         │
│  Name Surname           │
│  Title                  │
│                         │
│  email@company.com      │
│  +1 555 123 4567        │
│  company.com            │
│                         │
└─────────────────────────┘
```

**Centered Elegant**:
```
┌─────────────────────────┐
│                         │
│         LOGO            │
│                         │
│     Name Surname        │
│       Title             │
│                         │
│    ──── ◆ ────          │
│                         │
│   email@company.com     │
│    +1 555 123 4567      │
│                         │
└─────────────────────────┘
```

**Two-Column Split**:
```
┌─────────────────────────┐
│             │           │
│  LOGO       │  Name     │
│             │  Title    │
│  Brand      │           │
│  Tagline    │  email    │
│             │  phone    │
│             │  web      │
│             │           │
└─────────────────────────┘
```

### SVG Business Card Template
```svg
<svg viewBox="0 0 890 510" xmlns="http://www.w3.org/2000/svg">
  <!-- 10x scale of 89×51mm for crisp rendering -->
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    </style>
  </defs>

  <!-- Card background -->
  <rect width="890" height="510" fill="#ffffff" rx="20"/>

  <!-- Logo area -->
  <g transform="translate(60, 60)">
    <!-- Logo here -->
  </g>

  <!-- Name & Title -->
  <text x="60" y="280" font-family="'DM Sans'" font-weight="700" font-size="32" fill="#1a1a2e">
    Jane Smith
  </text>
  <text x="60" y="315" font-family="'DM Sans'" font-weight="400" font-size="20" fill="#6b7280">
    Creative Director
  </text>

  <!-- Contact Details -->
  <text x="60" y="390" font-family="'DM Sans'" font-weight="400" font-size="16" fill="#9ca3af">
    jane@studio.com  ·  +1 555 123 4567  ·  studio.com
  </text>
</svg>
```

---

## 4. BROCHURE & FLYER DESIGN

### Common Formats
- **Single sheet flyer**: 8.5 × 11" or A4 (single or double-sided)
- **Bi-fold**: 8.5 × 11" folded to 4.25 × 11" (4 panels)
- **Tri-fold**: 8.5 × 11" folded to ~3.67 × 8.5" (6 panels)
- **Gate fold**: 8.5 × 11" with two panels folding inward (4 panels, dramatic reveal)
- **Z-fold**: Like tri-fold but panels fold in opposite directions

### Panel Flow for Tri-fold
```
OUTSIDE (face-up, folded):
┌──────────┬──────────┬──────────┐
│  BACK    │  FRONT   │  FLAP    │
│  Panel 5 │  Panel 6 │  Panel 4 │
│  (info)  │  (cover) │  (teaser)│
└──────────┴──────────┴──────────┘
Note: Panel 4 (flap) is slightly narrower (~3.625")

INSIDE:
┌──────────┬──────────┬──────────┐
│  Panel 1 │  Panel 2 │  Panel 3 │
│  (intro) │  (main)  │  (main)  │
└──────────┴──────────┴──────────┘
```

### Flyer Design Principles
1. **One hero image or headline** that dominates (50%+ of space)
2. **Clear CTA** — What should the reader DO? Make it obvious.
3. **Minimal text** — People glance at flyers for 2-3 seconds. Every word must earn its place.
4. **Contact/action info** at bottom — website, phone, QR code, date/location
5. **Brand consistency** — Logo, colors, fonts from the brand system

---

## 5. CERTIFICATE & AWARD DESIGN

### Certificate Layout Pattern
```
┌─────────────────────────────────────┐
│           ┌─ ornamental border ─┐   │
│           │                     │   │
│           │    ORGANIZATION     │   │
│           │      LOGO           │   │
│           │                     │   │
│           │  Certificate of     │   │
│           │  ACHIEVEMENT        │   │
│           │                     │   │
│           │  Presented to       │   │
│           │                     │   │
│           │  Recipient Name     │   │
│           │  ═══════════════    │   │
│           │                     │   │
│           │  For accomplishing  │   │
│           │  [description]      │   │
│           │                     │   │
│           │  Date    Signature  │   │
│           │                     │   │
│           └─────────────────────┘   │
└─────────────────────────────────────┘
```

### Certificate Typography
- Organization name: Display font, medium weight, uppercase, wide tracking
- "Certificate of": Script or light serif, elegant
- Award type: Display font, bold, largest text on page
- Recipient name: Display font, medium/semibold, prominent
- Description: Body font, regular, modest size
- Date/Signature: Small, caption weight

### Ornamental Borders (SVG)
```svg
<!-- Corner ornament -->
<g id="corner-ornament">
  <path d="M 0 30 Q 0 0 30 0" fill="none" stroke="#c8a96e" stroke-width="2"/>
  <circle cx="15" cy="15" r="3" fill="#c8a96e"/>
  <path d="M 5 25 Q 5 5 25 5" fill="none" stroke="#c8a96e" stroke-width="1"/>
</g>
<!-- Repeat and mirror for all four corners -->
```

---

## 6. MENU DESIGN

### Menu Layout Principles
1. **Eye scanning pattern**: Readers look at the center-right of a menu first, then top-right, then top-left
2. **Golden triangle**: Place highest-profit items in these high-attention zones
3. **No dollar signs**: "$12" feels more expensive than "12" (menu psychology)
4. **Descriptions matter**: 2-line descriptions increase orders
5. **Photography**: Use sparingly and only if very high quality. Bad food photos reduce sales.

### Menu Typography
- **Category headers**: Display font, bold/semibold, clear separation
- **Item names**: Body font, bold or semibold, 14-16pt
- **Descriptions**: Body font, regular or light, 10-12pt, secondary color
- **Prices**: Body font, regular, aligned right (or tucked after description with dots/space)
- **NEVER use ALL CAPS for item names** (reduces readability)

---

## 7. PACKAGING DESIGN CONCEPTS

### Die-Line Thinking
Packaging design starts with understanding the 3D form:
- **Box**: 6 faces + flaps + glue tabs
- **Bottle label**: Wrapped cylinder with viewing area
- **Bag/Pouch**: Front, back, sides, bottom gusset
- **Sleeve**: Continuous wrap around the product

### Primary Display Panel (PDP)
The face the consumer sees first. Must include:
- Brand name/logo
- Product name
- Key visual (product image/illustration)
- Variant identifier (flavor, size, type)
- Net weight/volume (regulatory)

### SVG Packaging Mockup (Flat Box)
```svg
<svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
  <!-- Front face -->
  <rect x="150" y="50" width="200" height="300" fill="#f0e8d8" stroke="#333" stroke-width="1"/>
  <!-- Side face (perspective) -->
  <polygon points="350,50 430,80 430,330 350,350" fill="#e8dcc8" stroke="#333" stroke-width="1"/>
  <!-- Top face (perspective) -->
  <polygon points="150,50 350,50 430,80 230,80" fill="#f8f0e0" stroke="#333" stroke-width="1"/>
</svg>
```

---

## 8. LARGE FORMAT & ENVIRONMENTAL

### Banner/Billboard Proportions
- **Horizontal banner**: 3:1 or 4:1 (web) / 14:48 (billboard)
- **Vertical banner/retractable**: 1:2.5 or 1:3
- **Square**: Social media, trade show panels

### Large Format Design Rules
1. **Simplify ruthlessly**: Viewed at distance, only big bold elements register
2. **Maximum 7 words**: For billboards and highway signs
3. **High contrast**: Must be readable from 50+ feet
4. **No fine details**: Thin lines and small text disappear
5. **Test at thumbnail size**: If it works tiny, it works big
6. **Bleed generously**: Production tolerances are larger at scale

### Wayfinding & Signage
- **Legibility distance**: 1" of letter height ≈ 25 feet of reading distance
- **Contrast**: Dark text on light background for daytime; light text on dark for night/interior
- **Pictograms**: Use universally recognized symbols (ISO 7001)
- **Arrow conventions**: Arrows point in the direction of travel, positioned on the side closest to the path
- **ADA compliance**: Tactile characters, Braille, non-glare surfaces, appropriate mounting height
