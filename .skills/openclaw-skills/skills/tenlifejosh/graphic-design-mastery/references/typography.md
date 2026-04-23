# Typography & Lettering Reference

Use this reference for: type selection, font pairing, typographic hierarchy, lettering compositions,
type-as-art, kinetic typography, variable fonts, typographic systems, and any task where type is the
primary design element.

---

## TABLE OF CONTENTS
1. Advanced Font Pairing
2. Typographic Hierarchy Systems
3. Type-as-Art Compositions
4. Kinetic Typography (CSS)
5. OpenType Features
6. Responsive Typography
7. Typographic Color & Texture
8. Specialty Type Treatments

---

## 1. ADVANCED FONT PAIRING

### The Pairing Matrix

For any project, select fonts to fill these roles:

| Role | Character | Weight Range | Size Range |
|------|-----------|-------------|------------|
| Display | High personality, distinctive | Bold-Black | 40px+ |
| Heading | Readable, authoritative | Semibold-Bold | 20-40px |
| Body | Excellent readability, neutral | Regular-Medium | 16-18px |
| Caption/UI | Compact, clear at small sizes | Regular-Medium | 11-14px |
| Accent | Distinctive, used sparingly | Any | Varies |

### Proven Pairing Recipes

**Corporate/Professional**
```css
--font-display: 'Sora', sans-serif;           /* Geometric, modern authority */
--font-body: 'Source Serif 4', serif;          /* Readable, trustworthy */
```

**Editorial/Magazine**
```css
--font-display: 'Instrument Serif', serif;     /* Elegant, editorial */
--font-body: 'DM Sans', sans-serif;            /* Clean, contemporary */
```

**Tech/Startup**
```css
--font-display: 'Space Grotesk', sans-serif;   /* Technical, distinctive */
--font-body: 'Manrope', sans-serif;            /* Geometric, modern */
--font-mono: 'JetBrains Mono', monospace;      /* Code-ready */
```

**Luxury/Premium**
```css
--font-display: 'Cormorant Garamond', serif;   /* Refined, luxurious */
--font-body: 'Lato', sans-serif;               /* Elegant, minimal */
```

**Creative/Expressive**
```css
--font-display: 'Bricolage Grotesque', sans-serif; /* Characterful, warm */
--font-body: 'Crimson Text', serif;                 /* Classic readability */
```

**Brutalist/Raw**
```css
--font-display: 'Archivo Black', sans-serif;   /* Heavy, impactful */
--font-body: 'IBM Plex Mono', monospace;        /* Technical, raw */
```

**Warm/Friendly**
```css
--font-display: 'Fraunces', serif;             /* Quirky, warm */
--font-body: 'Figtree', sans-serif;            /* Friendly, open */
```

### Contrast Testing
After selecting a pair, verify contrast by comparing:
- Stroke width difference (thick display + thin body = good contrast)
- x-height relationship (similar x-heights improve harmony)
- Structural difference (geometric + humanist = clear contrast)

---

## 2. TYPOGRAPHIC HIERARCHY SYSTEMS

### System A: Classic Editorial
```css
.display    { font: 700 3.5rem/1.1 var(--font-display); letter-spacing: -0.03em; }
.h1         { font: 700 2.5rem/1.15 var(--font-display); letter-spacing: -0.02em; }
.h2         { font: 600 1.875rem/1.2 var(--font-display); letter-spacing: -0.01em; }
.h3         { font: 600 1.5rem/1.25 var(--font-body); }
.body-lg    { font: 400 1.125rem/1.7 var(--font-body); }
.body       { font: 400 1rem/1.65 var(--font-body); }
.caption    { font: 400 0.875rem/1.5 var(--font-body); color: var(--color-text-secondary); }
.overline   { font: 500 0.75rem/1.4 var(--font-body); letter-spacing: 0.1em; text-transform: uppercase; }
```

### System B: Modern Minimal
```css
.display    { font: 300 4rem/1.05 var(--font-display); letter-spacing: -0.04em; }
.h1         { font: 300 2.75rem/1.1 var(--font-display); letter-spacing: -0.03em; }
.h2         { font: 400 2rem/1.2 var(--font-display); letter-spacing: -0.02em; }
.h3         { font: 500 1.25rem/1.3 var(--font-body); letter-spacing: 0.01em; }
.body       { font: 400 1rem/1.7 var(--font-body); }
.small      { font: 400 0.875rem/1.6 var(--font-body); }
.label      { font: 500 0.6875rem/1.4 var(--font-body); letter-spacing: 0.08em; text-transform: uppercase; }
```

### System C: Bold & Expressive
```css
.hero       { font: 900 5rem/0.95 var(--font-display); letter-spacing: -0.05em; text-transform: uppercase; }
.display    { font: 800 3rem/1.05 var(--font-display); letter-spacing: -0.03em; }
.h1         { font: 700 2.25rem/1.15 var(--font-display); }
.h2         { font: 700 1.5rem/1.2 var(--font-display); }
.body       { font: 400 1.0625rem/1.65 var(--font-body); }
.accent     { font: 600 0.8125rem/1.5 var(--font-mono); letter-spacing: 0.06em; text-transform: uppercase; }
```

---

## 3. TYPE-AS-ART COMPOSITIONS

When type IS the primary visual element (posters, hero sections, editorial spreads):

### Techniques

**Scale Contrast**: Pair extremely large type (100px+) with very small type (10-12px) for dramatic tension.

**Weight Contrast**: Use hairline weight next to ultra-bold. The weight difference creates visual energy.

**Overlapping Type**: Layer text elements with reduced opacity or blend modes for depth:
```css
.background-text {
  font-size: 15vw;
  font-weight: 900;
  opacity: 0.04;
  position: absolute;
  user-select: none;
}
```

**Vertical Text**: Rotate 90° for strong vertical rhythm:
```css
.vertical-text {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  /* Or for rotated text: */
  transform: rotate(-90deg);
  transform-origin: left bottom;
}
```

**Text Clipping**: Use text as a mask for images/gradients:
```css
.clipped-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**Outlined Text**: Stroke without fill for elegant display:
```css
.outlined {
  -webkit-text-stroke: 2px #1a1a2e;
  -webkit-text-fill-color: transparent;
  /* SVG fallback for cross-browser */
}
```

### SVG Type Art
```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@900&display=swap');
    </style>
    <!-- Text on a path -->
    <path id="curve" d="M 50 300 Q 400 50 750 300" fill="none"/>
    <!-- Gradient for text -->
    <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#667eea"/>
      <stop offset="100%" stop-color="#764ba2"/>
    </linearGradient>
  </defs>

  <!-- Large background text -->
  <text font-family="'Playfair Display'" font-weight="900" font-size="200"
        fill="rgba(0,0,0,0.03)" x="50%" y="60%" text-anchor="middle">TYPE</text>

  <!-- Text on path -->
  <text font-family="'Playfair Display'" font-size="32" fill="url(#textGrad)">
    <textPath href="#curve" startOffset="50%" text-anchor="middle">
      Typography is the art of arranging type
    </textPath>
  </text>
</svg>
```

---

## 4. KINETIC TYPOGRAPHY (CSS ANIMATIONS)

### Letter-by-Letter Reveal
```css
.reveal-text span {
  display: inline-block;
  opacity: 0;
  transform: translateY(20px);
  animation: revealLetter 0.4s ease forwards;
}
.reveal-text span:nth-child(1) { animation-delay: 0.05s; }
.reveal-text span:nth-child(2) { animation-delay: 0.1s; }
/* ... etc, or use JS to set dynamically */

@keyframes revealLetter {
  to { opacity: 1; transform: translateY(0); }
}
```

### Typing Effect
```css
.typewriter {
  overflow: hidden;
  white-space: nowrap;
  border-right: 2px solid;
  width: 0;
  animation: typing 2s steps(20) forwards, blink 0.7s step-end infinite;
}
@keyframes typing { to { width: 100%; } }
@keyframes blink { 50% { border-color: transparent; } }
```

### Weight Animation (Variable Fonts)
```css
@keyframes breathe {
  0%, 100% { font-variation-settings: 'wght' 300; }
  50% { font-variation-settings: 'wght' 800; }
}
.breathing-text {
  font-family: 'Inter', sans-serif; /* Must be variable font */
  animation: breathe 3s ease-in-out infinite;
}
```

### Scroll-Driven Type Scale
```css
.scroll-scale {
  font-size: clamp(1rem, 5vw + 1rem, 8rem);
  /* Or with container queries for component-level responsive type */
}
```

---

## 5. OPENTYPE FEATURES

Unlock advanced typographic features when available:

```css
/* Ligatures */
font-variant-ligatures: common-ligatures discretionary-ligatures;

/* Small caps */
font-variant-caps: small-caps;
/* Or petite-caps, all-small-caps, titling-caps, unicase */

/* Numeric styles */
font-variant-numeric: oldstyle-nums tabular-nums; /* For data tables */
font-variant-numeric: lining-nums proportional-nums; /* For headings */

/* Stylistic alternates */
font-feature-settings: 'salt' 1; /* Stylistic alternates */
font-feature-settings: 'ss01' 1; /* Stylistic set 1 */

/* Fractions */
font-variant-numeric: diagonal-fractions;

/* All caps with proper spacing */
text-transform: uppercase;
font-variant-caps: all-petite-caps; /* or use letter-spacing */
```

---

## 6. RESPONSIVE TYPOGRAPHY

### Fluid Type Scale (clamp)

```css
/* Fluid type that scales between viewport widths */
--text-base: clamp(1rem, 0.5vw + 0.875rem, 1.125rem);
--text-lg: clamp(1.125rem, 0.75vw + 0.95rem, 1.375rem);
--text-xl: clamp(1.375rem, 1vw + 1rem, 1.75rem);
--text-2xl: clamp(1.75rem, 1.5vw + 1.25rem, 2.5rem);
--text-3xl: clamp(2rem, 2.5vw + 1.25rem, 3.5rem);
--text-4xl: clamp(2.5rem, 4vw + 1rem, 5rem);
--text-5xl: clamp(3rem, 6vw + 1rem, 8rem);
```

### Responsive Measure Control
```css
.text-container {
  max-width: clamp(30ch, 50vw, 70ch);
  margin-inline: auto;
  padding-inline: var(--space-6);
}
```

---

## 7. TYPOGRAPHIC COLOR & TEXTURE

"Typographic color" = the overall gray value of a text block. Controlled by:
- **Font weight**: Heavier = darker color
- **Line height**: Tighter = darker color
- **Letter spacing**: Tighter = darker color
- **Font size**: Larger relative to leading = darker color
- **x-height**: Taller x-height = darker color

For even typographic color:
- Avoid rivers (white vertical channels in justified text)
- Use consistent word spacing
- Hyphenate long words at line breaks (CSS: `hyphens: auto;`)
- Never justify text on the web (use `text-align: left`)

---

## 8. SPECIALTY TYPE TREATMENTS

### Drop Caps
```css
.drop-cap::first-letter {
  float: left;
  font-family: var(--font-display);
  font-size: 3.5em;
  line-height: 0.8;
  padding-right: 0.1em;
  margin-top: 0.05em;
  font-weight: 700;
  color: var(--color-brand-primary);
}
```

### Pull Quotes
```css
.pull-quote {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-style: italic;
  line-height: 1.3;
  border-left: 4px solid var(--color-brand-primary);
  padding-left: var(--space-6);
  margin: var(--space-12) 0;
  color: var(--color-text-primary);
}
```

### Numbered Lists with Typographic Flair
```css
.fancy-list {
  counter-reset: fancy;
  list-style: none;
  padding: 0;
}
.fancy-list li {
  counter-increment: fancy;
  padding-left: 3rem;
  position: relative;
  margin-bottom: var(--space-4);
}
.fancy-list li::before {
  content: counter(fancy, decimal-leading-zero);
  position: absolute;
  left: 0;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.25em;
  color: var(--color-brand-primary);
  line-height: inherit;
}
```

### Mixed-Weight Headlines
For dramatic impact, use inline weight variation:
```html
<h1 class="mixed-weight">
  <span style="font-weight: 300">The Art of</span>
  <span style="font-weight: 900">Typography</span>
</h1>
```

### Gradient Text
```css
.gradient-text {
  background: linear-gradient(135deg, var(--color-brand-primary), var(--color-brand-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```
