---
name: reddit-pain-point-scanner
description: "Reddit market research agent. Scans subreddits and keywords for recurring user complaints, unmet needs, and product gaps. Clusters pain points by frequency and urgency, and outputs structured opportunity reports for product development or positioning. Triggers: reddit pain points, subreddit research, market research reddit, customer complaints reddit, product opportunity, reddit scanner, reddit insights, pain point analysis, reddit market research, voice of customer"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/reddit-pain-point-scanner
---

# Reddit Pain Point Scanner

AI-powered Reddit research agent — surfaces recurring complaints, unmet needs, and product gaps hiding in subreddit discussions.

Describe a subreddit, paste post/comment text, or name a market vertical. The agent clusters pain points, scores frequency and urgency, and delivers a structured opportunity report you can act on immediately.

## Commands

```
scan r/<subreddit>                 # analyze pain points in a target subreddit
scan keyword <term>                # find complaints around a specific keyword or product
pain points report                 # generate ranked pain point summary with frequency scores
trending complaints                # surface newest or fastest-rising complaint themes
opportunity gaps                   # identify unmet needs with low existing solution density
save scan <topic-name>             # save current scan results to workspace
```

## What Data to Provide

The agent works with:
- **Subreddit name** — "scan r/mealprep" or "analyze r/solotravel complaints"
- **Pasted posts/comments** — copy Reddit thread text directly into chat
- **Keywords** — "find pain points around standing desks" or "complaints about project management tools"
- **Niche description** — "I'm targeting home gym owners, find their biggest frustrations"
- **Multiple subreddits** — "compare pain points across r/personalfinance and r/financialindependence"

No API keys needed. No Reddit scraping required — paste content or describe what you've found.

## Workspace

Creates `~/reddit-scanner/` containing:
- `memory.md` — saved scan history, tracked subreddits, and recurring themes
- `reports/` — past pain point reports (markdown)
- `opportunities.md` — curated product/positioning opportunity log

## Analysis Framework

### 1. Post Collection Strategy
- Focus posts: titles containing complaint signals ("why is", "anyone else", "frustrated", "why can't", "hate that", "wish there was", "does anyone know how to fix")
- High-signal comment threads: replies with high upvotes agreeing with a pain point
- Recurring threads: same question asked multiple times = unmet need
- Rant/vent posts: explicit frustration with existing products or workflows

### 2. Complaint Clustering
Group similar complaints into named themes:
- Parse for shared nouns (product category, feature, situation)
- Merge semantically similar complaints ("too expensive" + "price is insane" + "can't afford" = **Pricing Barrier**)
- Label each cluster with a clear theme name and representative quote
- Minimum cluster size: 2+ mentions to qualify (single mentions logged separately as weak signals)

### 3. Frequency Scoring
| Score | Criteria |
|-------|----------|
| 5 — Very High | 10+ distinct mentions, multiple threads, ongoing |
| 4 — High | 5–9 mentions across threads |
| 3 — Medium | 3–4 mentions |
| 2 — Low | 2 mentions |
| 1 — Weak Signal | 1 mention, notable quality |

### 4. Urgency Signal Detection
High-urgency pain points contain language like:
- "please", "desperately need", "so frustrated", "I give up", "why can't anyone"
- Active workarounds described (problem is real and unsolved)
- Monetary loss or time loss mentioned ("wasted 3 hours", "cost me $200")
- Multiple commenters validating with "same here", "this exactly", "+1"

### 5. Existing Solution Density
- Are existing products being mentioned as partial solutions?
- Are users recommending workarounds (DIY, duct-tape fixes)?
- Zero mentions of solutions = white space opportunity
- Many solutions mentioned but still frustrated = execution gap (better UX, price, support)

### 6. Opportunity Assessment Matrix
| Dimension | Signal |
|-----------|--------|
| Frequency | How often is it mentioned? |
| Urgency | How strong is the emotional signal? |
| Solution Gap | How poorly is the current solution meeting needs? |
| Addressability | Can a product/service realistically solve this? |
| Market Size | Does the subreddit represent a large audience? |

Score each dimension 1–5. Opportunity Score = average across all 5. Scores above 3.5 = high-priority opportunity.

## Output Format

Every scan outputs:
1. **Top Pain Points** — ranked list with theme name, frequency score, urgency level, and representative quote
2. **Opportunity Gaps** — pain points with low solution density, sorted by opportunity score
3. **Verbatim Evidence** — 2–3 direct quotes per major pain point
4. **Workaround Patterns** — what users are doing today to cope (indicates willingness to pay)
5. **Recommended Action** — product idea, positioning angle, or content opportunity for each gap

## Rules

1. Always cluster complaints before scoring — raw mention counts without grouping mislead
2. Distinguish between complaints about an existing product vs. complaints about the absence of a solution
3. Never conflate feature requests with pain points — they are different signal types (both valuable, labeled separately)
4. Flag when a subreddit is too small (fewer than 10k members) — data may not generalize
5. Note recency: a pain point from 3 years ago may be solved today — ask user to confirm current relevance
6. Save all scans to `~/reddit-scanner/reports/` when save scan command is used
7. Always quote verbatim Reddit language in the report — user's own words are the most powerful positioning fuel
