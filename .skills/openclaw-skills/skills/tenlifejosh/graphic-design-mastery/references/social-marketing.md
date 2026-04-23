# Social Media & Marketing Design Reference

Use this reference for: social media templates, ad creatives, banner ads, email templates, OG images,
thumbnails, story templates, carousel posts, cover images, promotional graphics, campaign assets,
and any marketing-oriented visual design.

---

## TABLE OF CONTENTS
1. Platform Size Guide
2. Social Media Design Principles
3. Ad Creative Design
4. Email Template Design
5. OG Image & Thumbnail Design
6. Campaign Asset Systems
7. Templates & Patterns

---

## 1. PLATFORM SIZE GUIDE

### Instagram
| Format | Dimensions | Aspect Ratio |
|--------|-----------|-------------|
| Post (Square) | 1080 × 1080px | 1:1 |
| Post (Portrait) | 1080 × 1350px | 4:5 (best engagement) |
| Post (Landscape) | 1080 × 566px | 1.91:1 |
| Story / Reel | 1080 × 1920px | 9:16 |
| Carousel | 1080 × 1080px per slide | 1:1 |
| Profile Photo | 320 × 320px | 1:1 (circular crop) |

### Twitter/X
| Format | Dimensions | Aspect Ratio |
|--------|-----------|-------------|
| Post Image | 1200 × 675px | 16:9 |
| Header/Banner | 1500 × 500px | 3:1 |
| Profile Photo | 400 × 400px | 1:1 (circular) |
| Card Image | 800 × 418px | 1.91:1 |

### LinkedIn
| Format | Dimensions | Aspect Ratio |
|--------|-----------|-------------|
| Post Image | 1200 × 627px | 1.91:1 |
| Article Cover | 1200 × 644px | ~1.86:1 |
| Company Banner | 1128 × 191px | ~5.9:1 |
| Profile Photo | 400 × 400px | 1:1 |

### YouTube
| Format | Dimensions | Aspect Ratio |
|--------|-----------|-------------|
| Thumbnail | 1280 × 720px | 16:9 |
| Channel Banner | 2560 × 1440px | 16:9 (safe area: 1546 × 423) |
| Profile Photo | 800 × 800px | 1:1 |

### Facebook
| Format | Dimensions | Aspect Ratio |
|--------|-----------|-------------|
| Post Image | 1200 × 630px | 1.91:1 |
| Cover Photo | 820 × 312px | ~2.63:1 |
| Story | 1080 × 1920px | 9:16 |
| Event Cover | 1920 × 1005px | ~1.91:1 |

### Open Graph (OG) / Link Preview
| Platform | Dimensions |
|----------|-----------|
| Default OG | 1200 × 630px |
| Twitter Card | 1200 × 600px |
| WhatsApp Preview | 300 × 200px (min) |

### Web Banner Ads (IAB Standard)
| Format | Dimensions |
|--------|-----------|
| Leaderboard | 728 × 90px |
| Medium Rectangle | 300 × 250px |
| Wide Skyscraper | 160 × 600px |
| Large Rectangle | 336 × 280px |
| Billboard | 970 × 250px |
| Mobile Banner | 320 × 50px |
| Mobile Interstitial | 320 × 480px |

---

## 2. SOCIAL MEDIA DESIGN PRINCIPLES

### The 3-Second Rule
Users scroll past in ~3 seconds. Your design must:
1. **STOP the scroll**: Bold color, striking composition, or unexpected visual
2. **Communicate instantly**: Headline readable in 1 second
3. **Reward closer inspection**: Detail that makes them pause longer

### Text on Social Media
- **Maximum 6-8 words** on image (the shorter the better)
- **Large, bold type**: Minimum 60px on 1080×1080 for readability on mobile
- **High contrast**: Text must be readable on any background
- **Safe zones**: Keep text away from edges (platform UI overlaps)

### Instagram-Specific Safe Zones
```
Story (1080×1920):
┌──────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │  ← Top 250px: Username/icon overlay
│                  │
│   SAFE AREA      │  ← Middle 1200px: Main content
│   for content    │
│                  │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │  ← Bottom 270px: CTA/swipe up area
└──────────────────┘
```

### Brand Consistency Across Platforms
- Use consistent color palette, fonts, and visual style
- Adapt layout to each platform's dimensions, but maintain recognizable brand elements
- Create a template system: header treatment, text placement, logo position
- Logo: Small, corner-positioned (not centered unless it's the hero)

---

## 3. AD CREATIVE DESIGN

### Ad Hierarchy (AIDA)
1. **Attention**: Visual hook (image, bold color, or unexpected element)
2. **Interest**: Headline that addresses a need or desire
3. **Desire**: Supporting copy or visual that deepens engagement
4. **Action**: Clear CTA button or directive

### CTA Button Design
```css
.cta-button {
  display: inline-block;
  padding: 14px 32px;
  font-family: var(--font-body);
  font-size: 16px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--color-brand-primary);
  color: white;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}
```

### Banner Ad Best Practices
- **Logo**: Small, visible but not dominant. Top-left or bottom-right.
- **Headline**: 2-5 words max. The single most important message.
- **CTA**: "Learn More", "Shop Now", "Get Started" — action-oriented, specific
- **Visual**: One strong image, not a collage
- **Border**: 1px border around the ad for definition on white pages
- **File size**: Keep under 150KB for fast loading
- **Animation**: If animated, max 3 loops, 15-30 seconds total

---

## 4. EMAIL TEMPLATE DESIGN

### Email Layout Structure
```
Max width: 600px (standard for email clients)

┌─────────────────────────┐
│       HEADER             │  Logo + preheader
├─────────────────────────┤
│                         │
│    HERO IMAGE           │  Full-width, compelling
│    or HERO TEXT          │
│                         │
├─────────────────────────┤
│    BODY CONTENT         │  1-2 columns max
│    Short paragraphs      │  Large text (16px min)
│    Clear hierarchy       │
├─────────────────────────┤
│     [ CTA BUTTON ]      │  Prominent, centered
├─────────────────────────┤
│    SECONDARY CONTENT    │  Optional: features, links
├─────────────────────────┤
│       FOOTER            │  Unsubscribe, social, legal
└─────────────────────────┘
```

### Email Design Rules
- **Max width**: 600px (some modern templates go to 700px)
- **Single column**: Preferred for mobile compatibility
- **Font size**: 16px minimum body, 22px+ headlines
- **CTA button**: Minimum 44px tall, full-width on mobile
- **Images**: Include ALT text, many clients block images by default
- **Dark mode**: Test with inverted colors (many email clients auto-invert)
- **Inline CSS**: Many email clients strip `<style>` tags
- **No JavaScript**: Email clients don't execute JS
- **Tables for layout**: Flexbox/Grid not supported in most email clients

### Email-Safe Fonts
```
/* These render reliably across email clients */
font-family: Georgia, 'Times New Roman', serif;
font-family: Arial, Helvetica, sans-serif;
font-family: 'Trebuchet MS', sans-serif;
font-family: Verdana, Geneva, sans-serif;

/* Web fonts with fallback (supported in some clients) */
font-family: 'Google Font Name', Arial, sans-serif;
```

---

## 5. OG IMAGE & THUMBNAIL DESIGN

### OG Image Template (1200×630)
```svg
<svg viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&display=swap');
    </style>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="#0f172a"/>

  <!-- Decorative element -->
  <circle cx="1000" cy="200" r="300" fill="#1e3a5f" opacity="0.4"/>

  <!-- Title -->
  <text x="80" y="280" font-family="'Plus Jakarta Sans'" font-weight="800"
        font-size="56" fill="#f8fafc" width="800">
    <tspan x="80">Your Compelling</tspan>
    <tspan x="80" dy="68">Title Goes Here</tspan>
  </text>

  <!-- Subtitle -->
  <text x="80" y="420" font-family="'Plus Jakarta Sans'" font-weight="700"
        font-size="24" fill="#94a3b8">
    A supporting description or tagline
  </text>

  <!-- Logo area -->
  <g transform="translate(80, 520)">
    <!-- Logo + site name -->
    <text font-family="'Plus Jakarta Sans'" font-weight="700" font-size="18" fill="#64748b">
      yoursite.com
    </text>
  </g>
</svg>
```

### YouTube Thumbnail Best Practices
- **Face close-ups**: Thumbnails with expressive faces get 30%+ more clicks
- **3 elements max**: Face + text + one graphic element
- **Bold text**: 3-5 words, outlined or with drop shadow for readability
- **Bright colors**: Yellow, red, blue backgrounds outperform muted ones
- **Contrast with YouTube UI**: Avoid red (like buttons) and white (like page bg)
- **Test at small size**: Must be readable at 168×94px (smallest display size)

---

## 6. CAMPAIGN ASSET SYSTEMS

### Creating a Consistent Campaign

A campaign asset system starts with these shared elements:
1. **Color palette**: 1 primary, 1 secondary, neutrals
2. **Typography**: 1 display font, 1 body font (max)
3. **Layout grid**: Consistent margins, text placement zones
4. **Visual treatment**: Photo style, illustration style, or graphic device
5. **Logo lockup**: Consistent logo size and position

### Asset Checklist for a Typical Campaign
- Instagram post (1080×1080)
- Instagram story (1080×1920)
- Twitter/X post image (1200×675)
- LinkedIn post image (1200×627)
- Facebook post image (1200×630)
- Email header (600×200)
- Web banner: leaderboard (728×90)
- Web banner: medium rectangle (300×250)
- OG image (1200×630)

---

## 7. TEMPLATES & PATTERNS

### Quote Card Template
```svg
<svg viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif&family=DM+Sans:wght@400;500&display=swap');
    </style>
  </defs>
  <rect width="1080" height="1080" fill="#faf5ee"/>

  <!-- Large quotation mark -->
  <text x="80" y="280" font-family="'Instrument Serif'" font-size="300"
        fill="#e8ddd0" opacity="0.5">"</text>

  <!-- Quote text -->
  <text x="100" y="420" font-family="'Instrument Serif'" font-size="48"
        fill="#2d2a26" width="880">
    <tspan x="100">Design is not just what it</tspan>
    <tspan x="100" dy="64">looks like and feels like.</tspan>
    <tspan x="100" dy="64">Design is how it works.</tspan>
  </text>

  <!-- Attribution -->
  <text x="100" y="720" font-family="'DM Sans'" font-weight="500"
        font-size="20" fill="#8a8078" letter-spacing="0.1em">
    — STEVE JOBS
  </text>

  <!-- Divider -->
  <line x1="100" y1="780" x2="300" y2="780" stroke="#d4c9bc" stroke-width="1"/>

  <!-- Brand -->
  <text x="100" y="980" font-family="'DM Sans'" font-weight="400"
        font-size="16" fill="#b0a89e">@yourbrand</text>
</svg>
```

### Stat Highlight Template
```svg
<svg viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
  <rect width="1080" height="1080" fill="#0f172a"/>

  <!-- Large stat number -->
  <text x="540" y="480" text-anchor="middle"
        font-family="sans-serif" font-weight="900" font-size="240"
        fill="#3b82f6">73%</text>

  <!-- Description -->
  <text x="540" y="580" text-anchor="middle"
        font-family="sans-serif" font-weight="400" font-size="32"
        fill="#94a3b8">of developers prefer dark mode</text>

  <!-- Source -->
  <text x="540" y="950" text-anchor="middle"
        font-family="sans-serif" font-size="16" fill="#475569">
    Source: Developer Survey 2024
  </text>
</svg>
```
