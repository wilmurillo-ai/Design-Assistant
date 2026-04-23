# Brand & Identity Design Reference

Use this reference for: logo design, brand systems, visual identity, style guides, brand guidelines, brand strategy,
brand refresh, rebrand, brand architecture, sub-brands, brand collateral, monograms, wordmarks, lettermarks,
brand marks, emblems, mascots, and any identity-related design work.

---

## TABLE OF CONTENTS
1. Brand Strategy Foundation
2. Logo Design System
3. Logo Construction Techniques
4. Brand Color Systems
5. Brand Typography
6. Brand Asset Creation
7. Style Guide / Brand Book Structure
8. Implementation Patterns (SVG)

---

## 1. BRAND STRATEGY FOUNDATION

Before designing anything, answer these questions (ask the user if needed):

### Brand Positioning
- **What does this brand do?** (1-sentence description)
- **Who is the audience?** (Demographics, psychographics, sophistication level)
- **What makes it different?** (Unique value proposition)
- **What personality should it project?** (Choose 3-5 adjectives)
- **What brands is it NOT?** (Competitive differentiation)

### Brand Personality Spectrum
Position the brand on each axis:

```
Formal ←————————————→ Casual
Traditional ←————————→ Innovative
Serious ←————————————→ Playful
Corporate ←——————————→ Personal
Luxury ←—————————————→ Accessible
Minimal ←————————————→ Expressive
Masculine ←——————————→ Feminine
Loud ←———————————————→ Quiet
```

These positions directly inform every visual choice — color temperature, type weight, spacing, illustration style.

---

## 2. LOGO DESIGN SYSTEM

### Logo Types

**Wordmark (Logotype)**: The name in custom typography. Best for: unique names, established brands, text-friendly names.
- Examples: Google, Coca-Cola, FedEx
- When to use: Name is short (1-3 words), distinctive, or the primary identifier

**Lettermark (Monogram)**: Initials as a symbol. Best for: long names, technical brands, premium positioning.
- Examples: IBM, HBO, NASA
- When to use: Full name is long, initials are memorable, need a compact mark

**Brandmark (Symbol/Icon)**: A standalone symbol. Best for: global brands, app icons, physical products.
- Examples: Apple, Nike, Target
- When to use: Brand is established enough to be recognized by symbol alone, or creating a strong icon-first identity

**Combination Mark**: Symbol + wordmark together. The most versatile and common for new brands.
- Examples: Adidas, Burger King, Doritos
- When to use: New brands that need both recognition and name reinforcement

**Emblem**: Text enclosed within a symbol or badge shape. Conveys tradition, heritage, authority.
- Examples: Starbucks, Harley-Davidson, NFL
- When to use: Heritage brands, institutions, luxury, craft/artisanal

**Abstract Mark**: A geometric or abstract form representing the brand conceptually.
- Examples: Pepsi, Airbnb, Spotify
- When to use: Brand wants to own a unique visual territory not tied to literal meaning

### Logo Quality Standards

A professional logo MUST:
1. **Work at any size**: From 16px favicon to 100ft billboard
2. **Work in one color**: Must be effective in pure black on white
3. **Work in reverse**: White on dark backgrounds
4. **Be geometrically clean**: No wobbly lines, inconsistent curves, or sloppy spacing
5. **Have optical balance**: Visual center may differ from mathematical center
6. **Be memorable**: Recognizable after brief exposure
7. **Be timeless**: Avoid trendy effects that will date quickly (bevels, extreme gradients, 3D chrome)
8. **Be unique**: Not reminiscent of existing well-known logos

---

## 3. LOGO CONSTRUCTION TECHNIQUES (SVG)

### Geometric Construction

Build logos from primitive shapes on a construction grid:

```svg
<!-- Logo construction grid -->
<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
  <!-- Construction grid (invisible in final) -->
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#eee" stroke-width="0.5"/>
    </pattern>
  </defs>

  <!-- Build from circles, rectangles, triangles -->
  <!-- Use boolean operations: union, subtraction, intersection -->
  <!-- Golden ratio circles for organic precision -->
</svg>
```

### Wordmark Construction

```svg
<svg viewBox="0 0 600 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=YOUR+FONT:wght@700&display=swap');
    </style>
  </defs>
  <text
    x="0" y="90"
    font-family="'Your Font', sans-serif"
    font-weight="700"
    font-size="80"
    letter-spacing="0.02em"
    fill="#1a1a2e"
  >BRANDNAME</text>
</svg>
```

For custom wordmarks, convert text to paths for precise control:
- Adjust kerning between specific letter pairs
- Modify individual letterforms (cut, extend, connect)
- Add unique ligatures or custom flourishes
- Ensure perfect optical spacing (not just metric spacing)

### Monogram Construction

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Container shape -->
  <circle cx="100" cy="100" r="90" fill="#1a1a2e"/>

  <!-- Letterforms -->
  <text
    x="100" y="120"
    text-anchor="middle"
    font-family="'Your Display Font', serif"
    font-weight="600"
    font-size="72"
    fill="#ffffff"
    letter-spacing="0.08em"
  >AB</text>
</svg>
```

### Icon/Brandmark Construction

Use a consistent grid and stroke weight system:
```svg
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <!-- 64x64 grid with 4px padding = 56x56 active area -->
  <!-- 2px stroke weight for consistency -->
  <!-- Rounded corners: 2px for small, 4px for medium elements -->

  <!-- Build from geometric primitives -->
  <!-- Use clip-path and mask for complex shapes -->
  <!-- Test at 16x16, 32x32, 64x64, 128x128 -->
</svg>
```

### Logo Responsive Variants

Every logo system needs multiple versions:
1. **Full logo**: Complete combination mark with wordmark
2. **Compact logo**: Simplified for smaller spaces
3. **Icon only**: Brandmark/monogram for app icons, favicons
4. **Wordmark only**: Just the text for inline use
5. **Monochrome**: Single-color version (black and white)
6. **Reversed**: For dark backgrounds

---

## 4. BRAND COLOR SYSTEMS

### Primary Palette
- **1 primary color**: The brand's signature color. Should be ownable and distinctive.
- **1-2 secondary colors**: Supporting colors that complement the primary.
- **Neutral palette**: 6-8 shades from near-white to near-black.

### Extended Palette
- Generate 10-step scales for each brand color (50-900)
- Define semantic colors (success, warning, error, info)
- Create dark mode variants for all colors

### Color Usage Rules
- Primary color: CTAs, key interactive elements, brand accents (10-15% of visual surface)
- Secondary color: Supporting elements, illustrations, backgrounds (20-30%)
- Neutrals: Text, borders, backgrounds (60-70%)
- Never use brand colors for semantic meanings (don't use brand-blue for info AND links)

---

## 5. BRAND TYPOGRAPHY

### Type System Structure
```
Brand Typeface Family:
├── Display: Used for hero headlines, emotional impact
│   └── Weight: Bold/Black, Size: 40-80px+
├── Heading: Section headings, card titles
│   └── Weight: Semibold/Bold, Size: 20-40px
├── Body: Paragraphs, descriptions, content
│   └── Weight: Regular, Size: 16-18px
├── Caption: Metadata, labels, footnotes
│   └── Weight: Regular/Medium, Size: 12-14px
└── Mono: Code, data, technical content
    └── Weight: Regular, Size: 14-16px
```

### Brand-Specific Type Rules
- Define specific letter-spacing per size tier
- Define specific line-height per usage context
- Specify all-caps usage (headings only? labels? never?)
- Define color usage for each type tier
- Specify max line length per context

---

## 6. BRAND ASSET CREATION

### Business Card (Standard: 3.5" × 2" / 89mm × 51mm)
Key elements: Logo, name, title, contact info. Minimal design. Generous whitespace.
Print consideration: Add 3mm bleed, keep text 5mm from trim edge.

### Letterhead (8.5" × 11" / A4)
Logo placement, contact info in header/footer, generous margins for content area.

### Email Signature
HTML-compatible. Max width 600px. Logo + name + title + links. Simple, no images that might be blocked.

### Social Media Templates
- Profile picture: Square crop of logo/icon (min 400×400px)
- Cover images: Platform-specific sizes (see social-marketing.md)
- Post templates: Consistent brand treatment with flexible content areas

### Favicon
- 32×32px and 16×16px versions
- Simplified brandmark that reads at tiny sizes
- High contrast, minimal detail

---

## 7. STYLE GUIDE / BRAND BOOK STRUCTURE

A complete brand guide includes:

1. **Brand Story**: Mission, vision, values, personality
2. **Logo**: All variants, minimum sizes, clear space rules, misuse examples
3. **Color**: Full palette with hex/RGB/CMYK values, usage rules, dos and don'ts
4. **Typography**: Typefaces, scale, pairing rules, usage examples
5. **Photography/Imagery**: Style, mood, do's and don'ts, treatments
6. **Iconography**: Style, grid, stroke weight, corner radius
7. **Layout**: Grid system, spacing rules, composition principles
8. **Voice & Tone**: Writing style guidelines (if applicable)
9. **Applications**: Examples of the system applied to real materials

---

## 8. IMPLEMENTATION: SVG LOGO TEMPLATE

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Display+Font:wght@700&amp;family=Body+Font:wght@400;600&amp;display=swap');
    </style>
  </defs>

  <!-- Brandmark -->
  <g id="brandmark" transform="translate(10, 10)">
    <!-- Your symbol here, built from geometric primitives -->
  </g>

  <!-- Wordmark -->
  <g id="wordmark" transform="translate(100, 0)">
    <text y="65" font-family="'Display Font', sans-serif" font-weight="700"
          font-size="42" fill="#1a1a2e" letter-spacing="0.02em">
      BrandName
    </text>
    <!-- Optional tagline -->
    <text y="88" font-family="'Body Font', sans-serif" font-weight="400"
          font-size="14" fill="#6b7280" letter-spacing="0.08em"
          text-transform="uppercase">
      Tagline Here
    </text>
  </g>
</svg>
```

### Key SVG Logo Principles
- Use `viewBox` for scalability — never fixed width/height
- Use `currentColor` for fill when you want the logo to inherit text color
- Group logical parts (`<g>`) for easy variant creation
- Include `<title>` and `<desc>` for accessibility
- Keep file size minimal — remove unnecessary precision in path data
- Test rendering across browsers
