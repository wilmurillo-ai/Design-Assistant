#!/usr/bin/env bash
# shopify-content-marketing — Content marketing and SEO blog strategy for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: content marketing strategy: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-content-mkt-$(date +%s)"

PROMPT="You are a Shopify content marketing and SEO expert specializing in blog strategy, keyword-driven content creation, and organic traffic growth for ecommerce stores. Build a complete content marketing strategy for: ${INPUT}

Produce a complete content marketing and SEO strategy report with these sections:

## 1. Keyword Research & Content Pillar Strategy
- Content pillar identification: 5 broad topic pillars for this niche
- Pillar page (10x content) topics: comprehensive guides that anchor each pillar
- Cluster content: 10 supporting articles per pillar
- Keyword difficulty balance: mix of quick wins (low KD) and long-term plays (high KD)
- Featured snippet opportunities: question-based keywords to target

## 2. Top 30 Blog Post Ideas
- 10 informational posts: how-to, guides, educational content
- 10 commercial investigation posts: best X, reviews, comparisons
- 10 transactional posts: product-linked content close to purchase
- Priority ranking: which to write first for fastest organic traffic impact

## 3. Content Calendar Structure
- Publishing frequency recommendation: 2-4 posts/month minimum for this niche
- Editorial calendar template with monthly themes
- Seasonal content: which months need specific topics
- Evergreen vs trending content ratio recommendation

## 4. Blog Post SEO Optimization Framework
- Title formula: primary keyword + power word + number/year
- Meta description template: hook + keyword + CTA (under 155 characters)
- Header structure: H1, H2, H3 hierarchy guidelines
- Image optimization: alt text formula, file names, compression targets
- Word count targets by content type: guide (2000+), comparison (1500+), how-to (1000+)

## 5. Content Distribution & Amplification
- Email newsletter integration: promoting each post to subscriber list
- Social media repurposing: turning one blog post into 10 social assets
- Pinterest strategy: creating pins for every blog post
- Link building: outreach strategy to earn backlinks to pillar pages
- Internal linking: connecting blog posts to product and collection pages

## 6. Conversion Architecture in Content
- Product recommendation placement within articles
- Email opt-in placement: inline, pop-up, and end-of-post CTAs
- Social proof integration: reviews and photos within relevant posts
- Bottom-of-funnel content: buying guides linked directly to product pages

## 7. Content Performance Measurement Plan
- Immediate actions (week 1): keyword research, first 4 blog posts outlined
- Short-term (month 1): first 4 posts published, Google Search Console setup
- Long-term (month 3+): 12+ posts live, organic traffic growing, revenue attribution tracking

Include content marketing benchmarks: average time to rank in top 10 for low-difficulty keywords (3-6 months), organic traffic value calculations, and content ROI examples from successful Shopify content programs."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
