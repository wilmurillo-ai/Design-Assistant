---
name: amazon-listing-writer
description: "Write high-converting, SEO-optimized Amazon listings including title, bullets, description, A+ content, and backend search terms. Triggers: listing write, listing title, listing bullets, listing description, listing a+, listing backend, listing rewrite, listing score, listing translate"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-listing-writer
---

# Amazon Listing Copywriter

Write high-converting, SEO-optimized Amazon listings. Input your product details and target keywords — get a complete, ready-to-publish listing: title, 5 bullets, description, A+ content outline, and backend search terms.

## Commands

```
listing write                   # write complete listing (interactive)
listing title [product]         # write optimized title only
listing bullets [product]       # write 5 bullet points
listing description [product]   # write product description
listing a+ [product]            # outline A+ content modules
listing backend [product]       # generate backend search terms
listing rewrite [paste text]    # rewrite existing weak listing
listing score [paste text]      # score existing listing (1–100)
listing translate [lang]        # adapt listing for UK/DE/JP market
```

## What Data to Provide

- **Product name & category** — what it is
- **Key features** — materials, dimensions, what makes it special
- **Target customer** — who buys it and why
- **Top keywords** — your primary and secondary keywords
- **Competitor listings** — paste 1–2 competitor titles/bullets to differentiate
- **Use cases** — how/when customers use it

## Listing Structure Guide

### Title Formula (200 bytes max)
```
[Brand] + [Primary Keyword] + [Key Feature] + [Size/Color/Qty] + [Use Case/Benefit]

Example:
"BrandX Yoga Mat Non-Slip — Extra Thick 6mm, 72" × 24" — Eco-Friendly TPE,
Alignment Lines — For Hot Yoga, Pilates, Home Gym"
```

**Title Rules:**
- Lead with primary keyword (highest search volume)
- Include 2–3 secondary keywords naturally
- No promotional phrases (Best, #1, Amazing)
- No subjective claims without proof
- Capitalize each major word

### Bullet Point Formula (5 bullets, 200 chars each)
Structure each bullet:
```
🔑 [FEATURE IN CAPS] — [Benefit explanation] [Social proof/spec if available]
```

**Bullet 1:** Primary differentiator (why choose this over competitors)
**Bullet 2:** Key material/quality feature
**Bullet 3:** Dimensions/compatibility/what's included
**Bullet 4:** Use case / who it's for
**Bullet 5:** Warranty / customer satisfaction guarantee

### Backend Search Terms (250 bytes)
- Synonyms not in title/bullets
- Common misspellings
- Spanish terms (for US market)
- Long-tail phrases
- Competitor brand names (careful — no trademark infringement)

## Copywriting Principles

### Conversion-First Language
| Weak | Strong |
|------|--------|
| "Good quality" | "Aircraft-grade aluminum, tested to 500 lb load" |
| "Easy to use" | "Set up in 3 minutes — no tools required" |
| "Great for families" | "Safe for kids 3+ — BPA-free, no sharp edges" |
| "Long lasting" | "18-month warranty, 50,000+ units sold" |

### Emotional Triggers by Category
- **Health/Fitness**: Transformation, confidence, results
- **Home/Kitchen**: Simplicity, time-saving, pride of home
- **Baby/Kids**: Safety, development, peace of mind
- **Electronics**: Performance, reliability, seamless experience
- **Outdoor**: Adventure, freedom, durability

## Listing Score Rubric (100 points)

| Element | Max Points | Criteria |
|---------|-----------|---------|
| Title keyword placement | 20 | Primary keyword in first 80 chars |
| Title completeness | 10 | Brand + feature + benefit present |
| Bullet differentiation | 20 | Each bullet = unique selling point |
| Bullet readability | 10 | Scannable, no walls of text |
| Keyword coverage | 15 | Top 10 keywords placed naturally |
| Social proof signals | 10 | Specs, certifications, stats |
| Mobile optimization | 10 | First 2 bullets visible without scroll |
| Backend terms | 5 | 250 bytes used efficiently |

**Score 85+** = Publish ready
**Score 65–84** = Minor revisions needed
**Score <65** = Major rewrite required

## Output Format

1. **Complete Listing** — title + 5 bullets + description ready to paste
2. **Keyword Placement Map** — which keywords appear where
3. **Listing Score** — 100-point breakdown with specific improvements
4. **A+ Content Outline** — module suggestions with copy direction
5. **Split Test Suggestions** — 2 title variants to A/B test

## Rules

1. Never use restricted phrases: "FDA approved" (unless true), "#1 Best Seller", "guaranteed cure"
2. All claims must be supportable — no invented statistics
3. Front-load benefits in each bullet (customer scans first 50 chars)
4. Match reading level to target audience
5. Always include primary keyword in title within first 5 words
6. Check competitor listings before writing — differentiate, don't copy
