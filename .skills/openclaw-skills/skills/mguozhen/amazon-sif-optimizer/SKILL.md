---
name: amazon-sif-optimizer
description: "Amazon Listing, keyword, and advertising deep optimization agent. Comprehensive SIF (Search-Index-Funnel) optimization — audit and improve listings for search indexing, keyword relevance, and conversion funnel performance. Triggers: amazon listing optimizer, sif optimizer, listing optimization, keyword optimization, ad optimization, search indexing, listing audit, listing score, conversion optimization, ppc optimization, listing quality, amazon seo optimization"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-sif-optimizer
---

# Amazon SIF Optimizer

Search-Index-Funnel (SIF) — the complete framework for Amazon listing optimization. Audit your listing's search discoverability, keyword indexing, and conversion funnel, then get specific improvements to climb rankings and boost sales.

## Commands

```
sif audit <listing>               # full SIF audit of a listing
sif search <listing>              # search discovery audit (S)
sif index <listing> <keywords>    # keyword indexing check (I)
sif funnel <listing>              # conversion funnel audit (F)
sif title <product> <keywords>    # optimize product title
sif bullets <product>             # rewrite bullet points
sif backend <listing>             # optimize backend search terms
sif ads <campaign-data>           # optimize PPC campaign structure
sif score <listing>               # compute SIF score (0-100)
sif compare <listing1> <listing2> # SIF comparison with competitor
sif improve <listing>             # generate full improved listing draft
sif report <listing>              # comprehensive SIF optimization report
```

## What Data to Provide

- **Current listing** — full title, 5 bullets, description, current price
- **Backend search terms** — what you currently have in backend
- **Target keywords** — keywords you want to rank for
- **Competitor ASINs** — top competitors to benchmark against
- **Ad campaign data** — current PPC campaigns and performance
- **Metrics** — click-through rate, conversion rate, sales/day

## SIF Framework

### S — Search Discovery

How easily can buyers find your listing?

**Search discovery factors:**
1. **Primary keyword in title** — must appear in first 60 characters
2. **Keyword indexing** — is Amazon actually indexing your keywords?
3. **Search rank position** — where do you appear for key terms?
4. **Ad coverage** — are you bidding on all critical terms?

**Search audit checklist:**
```
[ ] Primary keyword in title (first 60 chars)?
[ ] Top 3 keywords appear in title?
[ ] All bullet points contain at least 1 target keyword?
[ ] Description is keyword-rich?
[ ] Backend search terms filled (249 chars)?
[ ] Backend has no word repetition from title/bullets?
[ ] Backend includes misspellings, synonyms, long-tails?
[ ] Running Sponsored Products on exact match for top 10 keywords?
[ ] Auto campaign running to discover new keywords?
```

**Search score (0-25):**
- Title keyword presence: 0-8 pts
- Backend completeness: 0-7 pts
- Ad coverage: 0-5 pts
- Search rank on key terms: 0-5 pts

### I — Index Verification

Is Amazon indexing your keywords?

**Indexing check method:**
- Search: `site:amazon.com/dp/[ASIN] keyword`
- Or search the keyword on Amazon and check if your ASIN appears
- Note: Amazon drops keywords that don't drive conversions

**Common indexing failures:**
```
Reason                          Fix
Too many keywords in title      Prioritize top 5 only
Duplicate keywords              Remove repeats from backend
Restricted/prohibited terms     Replace with compliant alternatives
Non-English characters          Use ASCII equivalents
Keyword not in any field        Add to backend search terms
```

**Index score (0-25):**
- Primary keyword indexed: 0-10 pts
- All Tier 1-2 keywords indexed: 0-10 pts
- No prohibited terms detected: 0-5 pts

### F — Conversion Funnel

Once a buyer lands on your listing, does it convert?

**Conversion funnel stages:**
```
Search results → Click (driven by main image + title + price)
                    ↓
Product page → Add to Cart (driven by images, bullets, price, reviews)
                    ↓
Cart → Purchase (driven by trust signals, price, delivery)
```

**Conversion funnel audit:**

**Stage 1 — Click-through (CTR):**
```
[ ] Main image: white background, product fills 85%, no text overlays
[ ] Title: keyword-rich AND human-readable, not stuffed
[ ] Price: competitive within ±10% of top 3 competitors
[ ] Review count: minimum 15+ reviews to compete
[ ] Prime badge: FBA/FBM with Prime eligibility
[ ] CTR benchmark: >0.5% for search results
```

**Stage 2 — Page conversion (CVR):**
```
[ ] 7+ high-quality images (main + lifestyle + infographic + detail)
[ ] Video present (boosts CVR by 20-30%)
[ ] All 5 bullet points used, benefit-led format
[ ] A+ content present (Brand Registry required)
[ ] Price anchored appropriately (MSRP shown if discounted)
[ ] Review rating ≥4.0 stars
[ ] FAQ section answered (reduces purchase hesitation)
[ ] CVR benchmark: >10% for category (varies widely)
```

**Stage 3 — Cart to purchase:**
```
[ ] Fast delivery promise (2-day Prime preferred)
[ ] Return policy visible (30-day free returns = trust signal)
[ ] Secure transaction badge
[ ] No negative red flags in Q&A section
[ ] Seller feedback rating >95%
```

**Funnel score (0-50):**
- CTR optimization: 0-15 pts
- Page CVR optimization: 0-25 pts
- Trust signals: 0-10 pts

### SIF Score Interpretation

```
Total SIF Score (0-100):
90-100: Elite listing — maximize ad spend, listing is a machine
75-89:  Strong listing — minor improvements for incremental gains
60-74:  Good listing — targeted improvements will boost performance significantly
45-59:  Average listing — significant work needed on multiple fronts
<45:    Poor listing — comprehensive rewrite required before scaling ads
```

## Title Optimization Framework

**Title formula:**
`[Brand] + [Primary Keyword] + [Top Feature] + [Secondary Keyword] + [Benefit/Use Case]`

**Title scoring:**
- Character count: 150-200 chars (not <80, not >200)
- Primary keyword in first 40 chars: essential
- 2-3 key selling features: yes
- Mobile truncation (first 80 chars): must be compelling on mobile
- Readability: must make sense as a sentence

**Example:**
```
Before: "Water Bottle Stainless Steel Insulated 32oz BPA Free Lid Straw Sport School Office"
After: "HydroMax Insulated Water Bottle 32oz | Stainless Steel, Leak-Proof Lid, Stays Cold 24hrs | BPA-Free Flask for Gym, Hiking, School"
```

## Bullet Point Framework

**5-bullet structure:**
```
Bullet 1: [Primary benefit + primary keyword] — your biggest selling point
Bullet 2: [Key feature + secondary keyword] — technical proof of benefit 1
Bullet 3: [Use case/versatility + long-tail keyword] — broadens appeal
Bullet 4: [Trust signal + quality claim] — certifications, compatibility, warranty
Bullet 5: [Customer promise + brand keyword] — satisfaction guarantee, service
```

**Format rules:**
- Start with ALL CAPS benefit statement: "LEAK-PROOF LID GUARANTEED —"
- Follow with specific evidence: "triple-seal technology prevents spills..."
- End with use case or emotional benefit

## PPC Campaign Optimization

**3-campaign structure:**
```
Campaign 1: Exact Match — top 20 keywords, aggressive bids
Campaign 2: Phrase Match — broad keyword variations
Campaign 3: Auto — discovery, harvest new keywords weekly

Weekly tasks:
1. Harvest converting keywords from auto → add to exact/phrase
2. Negate non-converting terms from all campaigns
3. Adjust bids: raise for ACOS <target, lower for ACOS >target
4. Check new keyword opportunities from search term reports
```

**Bid optimization matrix:**
```
ACOS < 15%:    Raise bid 20% — underinvesting in a winner
ACOS 15-25%:   Maintain — at target range
ACOS 25-40%:   Lower bid 15% — marginal profitability
ACOS > 40%:    Lower bid 30% or pause — burning cash
0 impressions: Raise bid significantly or check keyword match
0 conversions >50 clicks: Negative match + listing review
```

## Workspace

Creates `~/sif-optimizer/` containing:
- `audits/` — SIF audit reports per ASIN
- `listings/` — optimized listing drafts
- `keywords/` — keyword tracking and indexing status
- `campaigns/` — PPC campaign structures and notes
- `scores/` — historical SIF scores to track improvement

## Output Format

Every SIF audit outputs:
1. **SIF Score Summary** — S/I/F scores and total with grade (A/B/C/D/F)
2. **Search Audit** — keyword presence check with specific gaps
3. **Index Report** — confirmed indexed keywords vs. missing
4. **Funnel Diagnosis** — stage-by-stage conversion blockers
5. **Improved Title Draft** — optimized title ready to use
6. **Bullet Rewrites** — all 5 bullets rewritten with improvements
7. **Backend Optimization** — updated 249-char backend search terms
8. **PPC Recommendation** — campaign structure changes needed
9. **Priority Fix List** — top 5 changes ranked by expected impact
