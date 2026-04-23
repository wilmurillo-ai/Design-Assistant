---
name: ai-voc-review-insights
description: "AI-powered Voice of Customer (VoC) review intelligence agent using DeepSeek-style analysis. Deep semantic analysis of customer reviews to extract pain points, purchase motivations, unmet needs, and product improvement signals across any e-commerce platform. Triggers: voc analysis, voice of customer, review intelligence, customer sentiment, pain points, purchase motivation, review deep dive, customer insights, product feedback, ai review analysis, deepseek voc, customer voice"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/ai-voc-review-insights
---

# AI VoC Review Intelligence

Deep AI-powered Voice of Customer analysis — go beyond basic sentiment to extract purchase motivations, hidden pain points, unmet needs, and product-market fit signals from customer reviews across any platform.

## Commands

```
voc analyze <reviews>             # full VoC analysis of review set
voc pain-points <reviews>         # extract and rank customer pain points
voc motivations <reviews>         # identify purchase motivations
voc unmet-needs <reviews>         # find unserved customer needs
voc personas <reviews>            # build customer persona from reviews
voc jobs-to-be-done <reviews>     # JTBD analysis from review language
voc compare <reviews1> <reviews2> # compare VoC between two products
voc opportunity <reviews>         # identify product development opportunities
voc marketing <reviews>           # extract marketing messages from reviews
voc report <product>              # full VoC intelligence report
```

## What Data to Provide

- **Reviews** — paste 20-200 customer reviews (more = better analysis)
- **Star distribution** — 1-5 star count breakdown
- **Product category** — context for benchmarking
- **Competitor reviews** — for comparative VoC analysis
- **Your marketing copy** — to align with customer language

## VoC Analysis Framework

### Level 1: Surface Analysis (Standard Review Analysis)

**What customers say explicitly:**
```
"The product is great quality"
"Arrived quickly"
"Easy to assemble"
"A bit expensive but worth it"
```

Basic sentiment: positive/negative/neutral classification

### Level 2: Semantic Analysis (What They Really Mean)

**Reading between the lines:**
```
Review: "Exactly what I needed" → Unmet need was real, product solves it
Review: "Better than I expected" → Category has history of disappointing products
Review: "I was skeptical but..." → High purchase anxiety in this category
Review: "Bought this as a gift" → Gifting is a significant use case
Review: "Replaced my old [brand]" → Competitor switching signal
Review: "My husband/wife loves it" → Multi-person household use
Review: "Works in my [specific context]" → Niche use case validation
```

### Level 3: Jobs-to-be-Done (JTBD) Analysis

**Functional jobs** (what they hire the product to do):
- "I need to [task]"
- Extract the core functional use from review language

**Emotional jobs** (how they want to feel):
- "I feel confident/safe/proud/excited when..."
- Extract emotional outcomes from positive reviews

**Social jobs** (how they want to be perceived):
- "My [guests/family/colleagues] noticed..."
- Extract social signaling from reviews

```
JTBD template from reviews:
When I [situation], I want to [motivation], so I can [outcome].

Example from reviews of a standing desk converter:
When I work from home all day, I want to avoid back pain,
so I can stay productive without discomfort.

→ Marketing message: "Work pain-free all day. Designed for the modern home office."
```

### Pain Point Extraction Matrix

Extract all pain points and classify:

**Dimension 1: Frequency**
- Mentioned in >20% of reviews: Critical issue
- Mentioned in 10-20%: Significant issue
- Mentioned in 5-10%: Notable issue
- Mentioned in <5%: Edge case

**Dimension 2: Intensity**
- "Terrible", "awful", "destroyed", "complete waste": Severity 5
- "Disappointed", "frustrated", "annoyed": Severity 4
- "Could be better", "wished it had": Severity 3
- "Minor issue", "small complaint": Severity 2
- Implied, not stated directly: Severity 1

**Dimension 3: Resolution Potential**
- Product redesign needed: Hard (3-6 months)
- Listing/instruction update: Easy (<1 week)
- Packaging/insert improvement: Medium (2-4 weeks)
- Customer service response: Immediate

```
Pain Point Matrix:
Pain Point           Freq   Intensity  Resolution  Priority
Instructions unclear 18%    3          Easy        HIGH
Strap breaks easily  12%    5          Hard        HIGH
Bag smaller than shown 9%   4          Listing fix MEDIUM
Color slightly off    6%    2          Listing fix LOW
```

### Customer Persona Building

From review language patterns, identify buyer segments:

**Segment 1: Core buyers (most reviews)**
```
Demographics: [infer from review context]
Trigger: [what prompted purchase]
Use case: [primary use]
Success metric: [what makes them happy]
Quote: "[representative review excerpt]"
```

**Segment 2: Edge case buyers (cause most problems)**
```
Demographics: [who writes the negative reviews]
Mismatch: [how product doesn't meet their expectations]
Fix: [listing change to filter them out or meet their needs]
```

**Segment 3: Surprise buyers (unexpected use cases)**
```
Discovery: [how they found your product]
Use case: [unexpected application]
Opportunity: [new marketing angle or product variation]
```

### Purchase Motivation Analysis

Extract why people buy, beyond the obvious:

**Rational motivators** (stated reasons):
- Quality, price, functionality, specifications

**Emotional motivators** (unstated reasons):
- Status, identity, relationships, fear/risk reduction
- Safety ("my child will be safe")
- Belonging ("everyone in our community uses this")
- Achievement ("I finally solved this problem")

**Trigger events** (what caused the purchase NOW):
- "After moving to a new home"
- "Since working from home"
- "After my old one broke"
- "Doctor recommended"
- "Saw on TikTok"

### Unmet Needs Identification

Find gaps in the market from review language:

**Explicit unmet needs:**
- "I wish it came in [X]"
- "Would be perfect if it also [function]"
- "Need something like this but for [use case]"

**Implicit unmet needs** (inferred from workarounds):
- "I had to [work around]" → product doesn't do X natively
- "It would help if..." → feature request pattern
- Comparisons to competitors: what competitor does better

### Competitive Switching Signals

From reviews mentioning competitors:
```
"Switched from [Brand X]" → X is your direct competitor
"Better than [Brand X]" → X is in buyer's consideration set
"[Brand X] stopped working, got this" → X has quality issues
"Half the price of [Brand X]" → X is premium alternative
```

### Marketing Message Extraction

The best marketing copy comes directly from customer words:

```
Reviews say:                 → Marketing copy:
"Finally found one that..."  → "The [product] you've been searching for"
"Works exactly as advertised" → "What you see is what you get"
"Gift for my husband, he loves it" → "The gift he'll actually use"
"Solved my [problem]"        → "[Problem]? Problem solved."
"Worth every penny"          → "Invest in quality. Feel the difference."
```

### Sentiment Evolution Analysis

Compare early reviews vs. recent reviews:
```
Early reviews (product launch): Focus on unboxing, first impressions
Recent reviews (mature product): Focus on durability, long-term value

Declining sentiment pattern:
Early avg: 4.5 stars → Recent avg: 3.9 stars
Signal: Quality or supplier change, investigate manufacturing
```

## Workspace

Creates `~/voc-intelligence/` containing:
- `analyses/` — full VoC reports per product
- `personas/` — customer persona profiles
- `pain-points/` — pain point matrices
- `marketing/` — extracted marketing messages
- `jtbd/` — jobs-to-be-done frameworks

## Output Format

Every VoC analysis outputs:
1. **VoC Executive Summary** — 5 key findings in plain language
2. **Pain Point Matrix** — all pain points scored by frequency × intensity
3. **JTBD Framework** — functional, emotional, and social jobs identified
4. **Customer Personas** — 2-3 buyer segments with profiles
5. **Unmet Needs List** — product/feature gaps discovered
6. **Marketing Messages** — 5 ready-to-use copy lines from customer language
7. **Competitor Switching Map** — which competitors appear and in what context
8. **Product Roadmap Signals** — prioritized improvements by business impact
