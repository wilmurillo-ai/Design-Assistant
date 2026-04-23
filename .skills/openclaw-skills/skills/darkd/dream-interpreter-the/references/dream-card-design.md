# Dream Card Image Design — v5.3

Specifications for rendering the Dream Analysis Card as a visual image. The JSON schema (`output-schema.md`) provides the data; this document defines how that data becomes a beautiful image.

---

## Card Dimensions

- **Width**: 800px
- **Height**: Dynamic (scales with content, typically 2000–3200px)
- **Format**: PNG
- **Background**: Mood-based gradient (see `visual-mapping.md`)

---

## Layout Structure

```
┌──────────────────────────────────────────────┐
│  HEADER                                      │
│  Dream summary · Mood badge · Keywords       │
├──────────────────────────────────────────────┤
│  SECTION: The Six Permanent Voices            │
│  ┌────────────────────────────────────────┐  │
│  │  🔮 Chinese Mystic                     │  │
│  │  Interpretation text                   │  │
│  │  Fortune badge    │    Advice          │  │
│  └────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────┐  │
│  │  🏛️ Greek Oracle                       │  │
│  │  ...                                   │  │
│  └────────────────────────────────────────┘  │
│  [... 4 more]                                │
├──────────────────────────────────────────────┤
│  SECTION: Guests Called by the Dream          │
│  ┌────────────────────────────────────────┐  │
│  │  𓂀 Egyptian Priest                     │  │
│  │  ...                                   │  │
│  └────────────────────────────────────────┘  │
│  [... 2 more]                                │
├──────────────────────────────────────────────┤
│  FOOTER                                      │
│  Overall Advice · Shareable text             │
└──────────────────────────────────────────────┘
```

---

## Color System

### Background Gradient

The entire card background uses the mood-based gradient from `visual-mapping.md`:

| Mood | Background Gradient |
|------|-------------------|
| anxious | Dark purple → dark blue (#2D1B69 → #1A1A2E) |
| peaceful | Warm yellow → soft green (#F4D35E → #83C5BE) |
| sad | Grey-blue → dark grey (#4A6FA5 → #2D3142) |
| surreal | Dark with neon pink/purple accents (#1A1A2E → #2D1B69 with #FF006E accents) |
| exciting | Orange-red → gold (#FF6B35 → #FFD700) |
| nostalgic | Amber → warm brown (#DDA15E → #BC6C25) |
| mystical | Deep forest green → violet (#1B4332 → #7B2D8E) |

### Text Colors

| Element | Light Backgrounds | Dark Backgrounds |
|---------|------------------|-----------------|
| Primary text | #1A1A2E (near black) | #F0E6D3 (warm cream) |
| Secondary text | #4A4A5A (dark grey) | #B8A99A (warm grey) |
| Accent/highlight | Mood primary color | Mood primary color |
| Advice label | Slightly muted | Slightly muted |

**Rule**: Use light text on dark backgrounds, dark text on light backgrounds. Determine based on mood.

### Perspective Card Colors

Each perspective mini-card has a subtle tinted background:

| Perspective | Tint color | Opacity |
|------------|-----------|---------|
| Chinese Mystic | Red-gold (#C41E3A at 8%) | Subtle |
| Greek Oracle | Marble white (#E8E0D0 at 10%) | Subtle |
| Slavic Vedunya | Forest green (#2D5A27 at 8%) | Subtle |
| European Prophet | Parchment (#D4C5A9 at 10%) | Subtle |
| Northern Shaman | Ice blue (#4A8BAA at 8%) | Subtle |
| Indian Brahman | Saffron (#E67E22 at 8%) | Subtle |
| Egyptian Priest | Gold (#DAA520 at 8%) | Subtle |
| Japanese Miko | Sakura pink (#FFB7C5 at 8%) | Subtle |
| Mesoamerican Daykeeper | Jade (#00A86B at 8%) | Subtle |
| Polynesian Navigator | Ocean blue (#006994 at 8%) | Subtle |
| Yoruba Babalawo | Earth red (#8B4513 at 8%) | Subtle |
| Arabian Sufist | Desert gold (#C2B280 at 8%) | Subtle |
| Scandinavian Volva | Frost grey (#778899 at 8%) | Subtle |

---

## Typography

### Font Stack

- **Headers**: Serif font (Noto Serif SC for CJK, Tinos for Latin, or system serif fallback)
- **Body text**: Sans-serif (Noto Sans SC for CJK, Carlito for Latin, or system sans-serif fallback)
- **Perspective names**: Bold sans-serif
- **Verdict badges**: Small caps or uppercase, bold

### Sizes

| Element | Size | Weight |
|---------|------|--------|
| Card title "DREAM ANALYSIS" | 24px | Bold |
| Dream summary | 18px | Medium |
| Section headings (⬡ The Six...) | 16px | Bold, uppercase |
| Perspective name | 15px | Bold |
| Interpretation text | 13px | Regular |
| Verdict/unique field | 12px | Italic |
| Advice text | 13px | Medium |
| Keywords / footer | 11px | Regular |

---

## Header Section

- Center-aligned
- "🌙 DREAM ANALYSIS CARD 🌙" as card title
- Dream summary in italic below
- Mood emoji + label as a badge (rounded rectangle, mood-tinted background)
- Keywords as small tags in a row

---

## Perspective Mini-Card

Each perspective is rendered as a rounded rectangle (border-radius: 12px) containing:

1. **Icon + Name**: Left-aligned, bold. Icon from the JSON schema.
2. **Interpretation text**: Left-aligned, regular weight. 100-200 chars.
3. **Verdict row**: The perspective's unique field (fortune / lesson / omen / prophecy / journey / dreamType / verdict / wyrd / dreamClass / daySign / voyage / dreamType) displayed as a styled badge with the perspective's tint color.
4. **Advice**: Label "Advice:" in bold, followed by the advice text.

Spacing: 16px padding inside each card, 12px gap between cards.

---

## Section Dividers

- Between the permanent section and guest section: a thin decorative line with a centered ornament (✦ or ⬡)
- Between individual perspective cards: subtle gap (no line needed)
- Between the guest section and overall advice: a slightly thicker divider

---

## Footer Section

- Overall advice in slightly larger text (14px), centered
- Shareable text in small italic text below, with a subtle "share" icon

---

## Decorative Elements

- A faint ornamental border around the entire card (1px, semi-transparent, mood primary color)
- Subtle vignette effect (darker edges) on dark mood backgrounds
- Optional: faint background texture pattern appropriate to the dominant tradition (see `visual-mapping.md` atmosphere modifiers)

---

## Supplemental Card

Same design as the main card, but:
- Title: "✦ SUPPLEMENTAL VOICES ✦" instead of "DREAM ANALYSIS CARD"
- No dream summary / keywords header (those were in the main card)
- Only the invited guest perspectives
- Shorter height
- Same mood-based color scheme

---

## Rendering Method

Use HTML + CSS rendered via Playwright browser automation for the best typography and layout control:

1. Build an HTML string with all card content styled inline
2. Use Playwright to open a headless browser, set viewport to 800px width
3. Screenshot the page
4. Save as PNG to `/home/z/my-project/download/dream-card-[timestamp].png`

Alternative: Python PIL/Pillow for simpler cards, but HTML+CSS gives much better typography and layout control.

---

## File Naming

- Main card: `dream-card-[YYYYMMDD-HHMMSS].png`
- Supplemental card: `dream-card-supplemental-[YYYYMMDD-HHMMSS].png`

All saved to `/home/z/my-project/download/`.
