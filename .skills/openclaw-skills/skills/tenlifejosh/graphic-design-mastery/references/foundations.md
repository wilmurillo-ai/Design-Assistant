# Design Foundations — Universal Knowledge Base

Read this file FIRST before any design task. It contains the bedrock knowledge that informs every design decision.

---

## TABLE OF CONTENTS
1. Color Theory & Systems
2. Typography Fundamentals
3. Composition & Grid Systems
4. Visual Hierarchy & Gestalt Principles
5. Spacing & Rhythm
6. Accessibility Standards
7. Design Tokens & Variables
8. Font Resources & Loading
9. Color Palette Construction

---

## 1. COLOR THEORY & SYSTEMS

### Color Models & When to Use Them

**HSL (Hue, Saturation, Lightness)** — Your primary working model for screen design.
- Hue: 0-360° on the color wheel (0=red, 120=green, 240=blue)
- Saturation: 0-100% (0=gray, 100=vivid)
- Lightness: 0-100% (0=black, 50=pure color, 100=white)
- WHY HSL: Intuitive to manipulate. To darken a color, reduce lightness. To mute it, reduce saturation.
  To create harmonies, shift hue. HSL makes design thinking natural.

**RGB/Hex** — For final output and CSS values.
- Use hex for static colors: `#1a1a2e`, `#e94560`
- Use `rgba()` when you need transparency
- Convert from HSL to hex for implementation

**CMYK** — For print production only (see print-production.md).

### Color Relationship Systems

**Monochromatic**: Single hue, varied saturation and lightness. Safest, most cohesive.
```
Base:    hsl(220, 70%, 50%)
Light:   hsl(220, 60%, 75%)
Dark:    hsl(220, 80%, 30%)
Muted:   hsl(220, 30%, 60%)
```

**Analogous**: Adjacent hues (within 30° of each other). Harmonious, natural.
```
Primary:   hsl(220, 70%, 50%)   /* Blue */
Adjacent1: hsl(195, 65%, 48%)   /* Cyan-blue */
Adjacent2: hsl(245, 60%, 55%)   /* Blue-violet */
```

**Complementary**: Opposite hues (180° apart). High contrast, energetic.
```
Primary:     hsl(220, 70%, 50%)   /* Blue */
Complement:  hsl(40, 70%, 50%)    /* Orange */
```

**Split-Complementary**: One hue + two hues adjacent to its complement. Vibrant but balanced.
```
Primary: hsl(220, 70%, 50%)   /* Blue */
Split1:  hsl(25, 65%, 50%)    /* Red-orange */
Split2:  hsl(55, 65%, 50%)    /* Yellow-green */
```

**Triadic**: Three hues equidistant (120° apart). Dynamic, requires careful balance.
```
Primary:  hsl(220, 70%, 50%)   /* Blue */
Second:   hsl(340, 65%, 50%)   /* Red-pink */
Third:    hsl(100, 60%, 45%)   /* Green */
```

### The 60-30-10 Rule
- **60%**: Dominant color (backgrounds, large surfaces)
- **30%**: Secondary color (supporting elements, cards, sections)
- **10%**: Accent color (CTAs, highlights, key interactive elements)

### Color Temperature & Emotion

| Temperature | Colors | Emotions |
|-------------|--------|----------|
| Warm | Reds, oranges, yellows | Energy, passion, urgency, warmth, appetite |
| Cool | Blues, greens, purples | Calm, trust, professionalism, technology |
| Neutral | Grays, beiges, whites | Sophistication, balance, timelessness |

### Building a Production Color Palette

Every project needs these color roles defined:

```css
:root {
  /* Surface colors (backgrounds) */
  --color-surface-primary: #ffffff;
  --color-surface-secondary: #f8f9fa;
  --color-surface-tertiary: #e9ecef;
  --color-surface-inverse: #1a1a2e;

  /* Text colors */
  --color-text-primary: #1a1a2e;
  --color-text-secondary: #4a4a5a;
  --color-text-tertiary: #8a8a9a;
  --color-text-inverse: #ffffff;
  --color-text-link: #2563eb;

  /* Brand / Accent */
  --color-brand-primary: #2563eb;
  --color-brand-primary-hover: #1d4ed8;
  --color-brand-primary-light: #dbeafe;
  --color-brand-secondary: #7c3aed;

  /* Semantic */
  --color-success: #059669;
  --color-warning: #d97706;
  --color-error: #dc2626;
  --color-info: #2563eb;

  /* Border & Divider */
  --color-border-default: #e5e7eb;
  --color-border-strong: #d1d5db;
}
```

### Contrast Requirements (WCAG 2.1)
- **Normal text**: Minimum 4.5:1 contrast ratio (AA), 7:1 (AAA)
- **Large text (18px+ bold or 24px+ regular)**: Minimum 3:1 (AA), 4.5:1 (AAA)
- **UI components and graphics**: Minimum 3:1 against adjacent colors
- **ALWAYS verify**: Use the formula or check programmatically. Never eyeball contrast.

### Perceptual Uniformity
- Saturated yellows and greens appear lighter than saturated blues and purples at the same HSL lightness
- When creating a multi-hue palette, adjust lightness per-hue to achieve visual uniformity
- Dark backgrounds: Keep accent text lightness above 65%. Light backgrounds: Keep accent text lightness below 40%.

---

## 2. TYPOGRAPHY FUNDAMENTALS

### The Type Scale

Use a modular scale for consistent typographic hierarchy. The most common ratio is **1.25** (Major Third):

```
xs:   0.75rem  (12px)  — Captions, footnotes
sm:   0.875rem (14px)  — Secondary text, metadata
base: 1rem     (16px)  — Body text (NEVER go below this for body)
lg:   1.25rem  (20px)  — Lead paragraphs, emphasized text
xl:   1.563rem (25px)  — H4 / Subheadings
2xl:  1.953rem (31px)  — H3
3xl:  2.441rem (39px)  — H2
4xl:  3.052rem (49px)  — H1
5xl:  3.815rem (61px)  — Display / Hero text
```

For more dramatic hierarchy, use **1.333** (Perfect Fourth) or **1.5** (Perfect Fifth) ratios.

### Font Classification & Selection

**Serif** — Authority, tradition, editorial, luxury
- Use for: Long-form reading, editorial, luxury brands, legal, academic
- Key families: Georgia, Garamond, Playfair Display, Lora, Merriweather, Source Serif Pro, Crimson Text, Libre Baskerville

**Sans-Serif** — Modernity, clarity, technology, efficiency
- Use for: UI/UX, technology brands, clean modern aesthetics, data-heavy contexts
- Geometric: Futura, Poppins, Montserrat, DM Sans — Structured, technical feel
- Humanist: Lato, Open Sans, Source Sans Pro, Nunito — Warm, approachable
- Grotesque: Helvetica, Archivo, IBM Plex Sans — Neutral, professional
- Neo-grotesque: Söhne, Suisse, Aktiv Grotesk — Contemporary editorial

**Monospace** — Code, technical, typewriter aesthetic, retro-tech
- Use for: Code display, technical interfaces, brutalist aesthetics, tabular data
- Key families: JetBrains Mono, Fira Code, IBM Plex Mono, Source Code Pro, Space Mono

**Display** — Headlines, posters, impact moments
- Use for: Hero text, poster headlines, brand statements — NEVER for body text
- Variable weight fonts are excellent for display use

### Font Pairing Principles

**The Contrast Principle**: Pair fonts that are clearly different from each other, not slightly different. A serif heading + sans-serif body works because the contrast is obvious. Two similar sans-serifs creates tension.

**Reliable Pairing Strategies**:
1. **Serif heading + Sans-serif body**: Classic, professional (Playfair Display + Source Sans Pro)
2. **Geometric display + Humanist body**: Modern, approachable (Poppins + Lato)
3. **Bold grotesque + Light serif**: Editorial, luxe (Archivo Black + Libre Baskerville)
4. **Monospace heading + Sans-serif body**: Technical, modern (Space Mono + DM Sans)
5. **Same superfamily, different weights**: Safe, cohesive (IBM Plex Sans + IBM Plex Serif)

**What NOT to pair**:
- Two serifs from the same era (Garamond + Times = confusion)
- Two geometrics (Futura + Poppins = bland)
- Decorative + decorative (chaos)

### Line Height (Leading)
- **Body text**: 1.5–1.75 (more generous = more readable)
- **Headings**: 1.1–1.3 (tighter = more impactful)
- **Display/Hero**: 0.9–1.1 (very tight = dramatic)
- **Captions/UI**: 1.3–1.5

### Letter Spacing (Tracking)
- **Body text**: 0 to +0.01em (default is usually fine)
- **Headings (large)**: -0.01 to -0.03em (tighten slightly)
- **All-caps text**: +0.05 to +0.15em (ALWAYS add tracking to uppercase)
- **Small text/captions**: +0.02 to +0.05em (open up for legibility)

### Measure (Line Length)
- **Optimal**: 45–75 characters per line (including spaces)
- **Ideal**: 66 characters (the typographic "canon")
- **Minimum**: 30 characters (for narrow columns)
- **Maximum**: 90 characters (beyond this, reading fatigue increases)
- Use `max-width: 65ch` for body text containers

### Web Font Loading

**Google Fonts** (available in HTML artifacts):
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=FONT_NAME:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**Popular high-quality Google Fonts for design work**:
- Display: Playfair Display, Sora, Space Grotesk, Outfit, Bricolage Grotesque, Fraunces, Instrument Serif
- Body: DM Sans, Plus Jakarta Sans, Figtree, Geist (via CDN), Manrope, Karla, Rubik
- Monospace: JetBrains Mono, Fira Code, Space Mono, IBM Plex Mono
- Serif: Lora, Merriweather, Crimson Text, Source Serif 4, Libre Baskerville, Cormorant

**CRITICAL**: Avoid defaulting to the same fonts. Every project should have a unique typographic identity. Rotate through options. Surprise yourself.

---

## 3. COMPOSITION & GRID SYSTEMS

### Grid Types

**Column Grid**: The workhorse of layout. Divide the canvas into vertical columns with consistent gutters.
- **12-column grid**: Most flexible (divisible by 2, 3, 4, 6). Standard for web.
- **8-column grid**: Clean, slightly less flexible. Good for focused layouts.
- **Asymmetric grids**: Unequal column widths. Creates dynamic tension. Use for editorial/artistic layouts.

**Modular Grid**: Columns AND rows, creating a matrix of modules. Best for complex layouts with many elements
(newspapers, dashboards, catalogs).

**Manuscript Grid**: Single column. Best for long-form text (articles, books, letters).

**Hierarchical Grid**: No uniform columns — elements placed based on visual importance. Best for landing pages,
posters, and creative layouts where each section needs unique treatment.

### Grid Implementation (CSS)

```css
/* 12-column grid with responsive gutters */
.grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Span utilities */
.col-full    { grid-column: 1 / -1; }
.col-half    { grid-column: span 6; }
.col-third   { grid-column: span 4; }
.col-quarter { grid-column: span 3; }
.col-two-thirds { grid-column: span 8; }

/* Asymmetric layout example */
.layout-sidebar {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 32px;
}
```

### Composition Techniques

**Rule of Thirds**: Divide the canvas into a 3×3 grid. Place key elements at intersection points or along grid lines.
The most universally applicable composition technique.

**Golden Ratio (1:1.618)**: Creates naturally pleasing proportions. Use for:
- Width-to-height ratios
- Content area to sidebar ratios
- Heading-to-body size ratios
- Spacing relationships

**Focal Point**: Every composition needs one. The element with the greatest visual weight (largest, brightest,
most saturated, most detailed, or most isolated) becomes the focal point. Everything else supports it.

**Visual Flow Patterns**:
- **F-pattern**: How people scan content-heavy pages (left to right, top to bottom). Align key content to the F.
- **Z-pattern**: How people scan minimal pages (top-left → top-right → bottom-left → bottom-right). Place CTA at end.
- **Diagonal**: Creates dynamic energy. Use for posters, editorial, dramatic layouts.
- **Circular**: Guides the eye in a loop. Good for contained compositions, logos, cyclical narratives.

**Negative Space (White Space)**: Not empty — it's an active design element. It:
- Creates breathing room and reduces cognitive load
- Draws attention to the elements that ARE present
- Communicates luxury, sophistication, confidence
- Establishes visual groups (proximity principle)

### The Rule of Tension

Static, perfectly balanced compositions are forgettable. Create **controlled tension** by:
- Offsetting elements slightly from center
- Using asymmetric weight distribution
- Creating unequal spacing relationships
- Breaking the grid intentionally (and sparingly)
- Contrasting large elements with very small ones

---

## 4. VISUAL HIERARCHY & GESTALT PRINCIPLES

### Hierarchy Levers (ranked by impact)

1. **Size**: Bigger = more important. The simplest, most powerful lever.
2. **Contrast**: Higher contrast against background = more attention. Pure black on white pops.
3. **Color**: Saturated/warm colors advance, desaturated/cool colors recede.
4. **Weight**: Bold text, thick strokes, filled shapes demand attention.
5. **Position**: Top-left gets attention first (in LTR cultures). Above the fold matters.
6. **Isolation**: An element surrounded by space draws the eye.
7. **Detail**: More detailed elements attract more attention than simple ones.

### Gestalt Principles (How humans perceive visual groups)

**Proximity**: Elements close together are perceived as a group. This is the most important grouping principle.
Use generous spacing BETWEEN groups and tight spacing WITHIN groups.

**Similarity**: Elements that look alike (same color, shape, size) are perceived as related.
Use this for consistent treatment of same-function elements (all buttons look alike, all links are the same color).

**Continuity**: The eye follows lines, curves, and implied directions. Align elements along invisible axes.
Use this for navigation flows, process steps, and creating visual momentum.

**Closure**: The mind completes incomplete shapes. Powerful for logo design and clever illustrations.
Use this to create sophisticated logos that imply more than they show.

**Figure-Ground**: The brain separates foreground from background. Create clear distinction between content
(figure) and its container (ground). Ambiguity here creates confusion — unless intentionally exploited for artistic effect.

**Common Region**: Elements within a shared boundary are grouped. Cards, panels, and containers leverage this.

**Symmetry**: The brain prefers balanced compositions. Use symmetry for stability and trust; break it for dynamism.

---

## 5. SPACING & RHYTHM

### The Spacing Scale

Use a consistent mathematical scale for ALL spacing decisions. Base-8 is the most versatile:

```
4px   — Hairline (icon padding, tight element gaps)
8px   — Compact (inline spacing, small gaps)
12px  — Snug (form element padding, tight stacks)
16px  — Default (paragraph spacing, card padding)
24px  — Comfortable (section padding, component gaps)
32px  — Roomy (card margins, group separation)
48px  — Spacious (section separation)
64px  — Generous (major section breaks)
96px  — Dramatic (hero padding, page margins)
128px — Monumental (full-bleed section spacing)
```

### Rhythm Types

**Vertical Rhythm**: All vertical spacing should be multiples of your baseline grid (typically the body line-height).
This creates an invisible but perceivable order.

**Horizontal Rhythm**: Column gutters, padding, and margins should share a consistent relationship.
If your gutter is 24px, your padding might be 24px or 48px — not 30px.

**Progressive Spacing**: Increase spacing as elements become more conceptually distant.
- Within a component: 8-16px
- Between related components: 24-32px
- Between sections: 48-64px
- Between major page areas: 96-128px

---

## 6. ACCESSIBILITY STANDARDS

### Color Accessibility
- Never convey information through color alone (use labels, icons, patterns too)
- Ensure 4.5:1 contrast for normal text, 3:1 for large text
- Test with color blindness simulators (protanopia, deuteranopia, tritanopia)
- Provide sufficient contrast for interactive states (hover, focus, active)

### Typography Accessibility
- Body text: minimum 16px
- Line height: minimum 1.5 for body text
- Paragraph spacing: minimum 1.5× the font size
- Letter spacing: minimum 0.12× the font size
- Word spacing: minimum 0.16× the font size
- Never use `text-align: justify` (creates uneven word spacing)

### Interactive Accessibility
- Touch targets: minimum 44×44px (iOS) or 48×48dp (Android/WCAG)
- Focus indicators: visible, 2px+ width, 3:1 contrast
- Never rely solely on hover states (they don't exist on touch devices)
- Keyboard navigation must be logical and complete

### Semantic Structure
- Use heading levels correctly (h1 > h2 > h3, no skipping)
- Use ARIA labels for icons and non-text interactive elements
- Provide alt text concepts for images in design specifications
- Mark decorative elements as `aria-hidden="true"`

---

## 7. DESIGN TOKENS & CSS VARIABLES

### Standard Token Architecture

```css
:root {
  /* ===== SPACING ===== */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
  --space-24: 96px;
  --space-32: 128px;

  /* ===== TYPOGRAPHY ===== */
  --font-display: 'Your Display Font', serif;
  --font-body: 'Your Body Font', sans-serif;
  --font-mono: 'Your Mono Font', monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.5rem;
  --text-2xl: 1.875rem;
  --text-3xl: 2.25rem;
  --text-4xl: 3rem;
  --text-5xl: 3.75rem;

  --leading-tight: 1.15;
  --leading-snug: 1.3;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.05em;
  --tracking-wider: 0.1em;

  /* ===== BORDERS ===== */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* ===== SHADOWS ===== */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
  --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04);

  /* ===== TRANSITIONS ===== */
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
}
```

---

## 8. FONT RESOURCES

### Loading Google Fonts in HTML

Always preconnect, always use `display=swap`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Font+Name:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
```

### Font Stacks for Fallback

```css
/* Sans-serif stacks */
font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Serif stacks */
font-family: 'Lora', 'Georgia', 'Cambria', 'Times New Roman', serif;

/* Monospace stacks */
font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace;

/* Display stacks */
font-family: 'Playfair Display', 'Georgia', serif;
```

---

## 9. COLOR PALETTE CONSTRUCTION RECIPES

### Professional Neutral Palette (for any project)
```
Ink:     hsl(220, 15%, 10%)  — Darkest text
Charcoal: hsl(220, 10%, 25%) — Secondary text
Slate:   hsl(220, 8%, 45%)   — Tertiary text
Silver:  hsl(220, 8%, 65%)   — Disabled/placeholder
Mist:    hsl(220, 8%, 85%)   — Borders
Cloud:   hsl(220, 8%, 94%)   — Subtle backgrounds
Snow:    hsl(220, 8%, 98%)   — Page background
White:   hsl(0, 0%, 100%)    — Cards, surfaces
```

### Dark Mode Neutral Palette
```
Paper:   hsl(220, 8%, 90%)   — Primary text
Smoke:   hsl(220, 8%, 70%)   — Secondary text
Ash:     hsl(220, 8%, 50%)   — Tertiary text
Steel:   hsl(220, 10%, 30%)  — Borders
Carbon:  hsl(220, 12%, 18%)  — Elevated surfaces
Void:    hsl(220, 15%, 12%)  — Base background
Abyss:   hsl(220, 18%, 8%)   — Deepest background
```

### Generating Accent Color Scales
For any accent/brand color, generate a 10-step scale:

```
50:  Very light tint (background highlights)
100: Light tint (hover backgrounds)
200: Soft tint (selected backgrounds)
300: Medium light (borders, decorative)
400: Medium (secondary buttons)
500: Base color (primary brand)
600: Medium dark (hover on primary)
700: Dark (active/pressed states)
800: Very dark (high-contrast text on light)
900: Darkest (headings on light backgrounds)
```

Technique: Start with your base (500), then shift lightness up for tints and down for shades while slightly
adjusting saturation (increase for darks, decrease for lights) to maintain vibrancy.
