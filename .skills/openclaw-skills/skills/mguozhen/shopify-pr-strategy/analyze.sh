#!/usr/bin/env bash
# shopify-pr-strategy — PR and press coverage strategy for Shopify stores
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: PR strategy for: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-pr-$(date +%s)"

PROMPT="You are a Shopify brand PR and media relations expert specializing in earning press coverage, building brand authority, and securing high-quality backlinks for ecommerce stores. Build a complete PR strategy for: ${INPUT}

Produce a complete PR and press strategy report with these sections:

## 1. Story Angle Development
- 10 specific pitchable story angles for this brand (beyond product announcement)
- Data story: original research or survey that journalists will want to cover
- Founder story: personal narrative hooks that resonate with business media
- Trend jacking: how to attach to existing media trends in this niche
- Impact story: community, sustainability, or social mission angles

## 2. Media Target List & Prioritization
- Tier 1 targets: major publications (Forbes, Business Insider, Vogue, etc. for niche)
- Tier 2 targets: niche-specific blogs, trade publications, and industry sites
- Tier 3 targets: local media, podcasts, and micro-publications
- 20 specific publication names with their audience focus for this niche

## 3. Journalist Outreach & Pitch Templates
- Subject line formulas that journalists actually open (5 options)
- Cold pitch email template: 150 words max, story-first structure
- Follow-up sequence: 2-touch, 1-week apart
- How to find the right journalist's email (tools: Hunter.io, LinkedIn)

## 4. Press Release Writing Framework
- Standard press release format with all required elements
- Headline formula: newsworthy and SEO-optimized
- Boilerplate company description template
- Distribution strategy: PR Newswire vs free wire services vs direct outreach

## 5. HARO & Reactive PR Tactics
- HARO (Help a Reporter Out) setup: categories to subscribe to
- How to write a compelling HARO response in under 200 words
- Response template for journalist queries
- Alternative platforms: Qwoted, SourceBottle, ProfNet

## 6. Long-Term Media Relationship Building
- How to become a go-to source for journalists in your niche
- Building a media kit: what to include (brand assets, stats, founder bio)
- Gifting product to journalists: strategy and follow-up
- Social media engagement with target journalists before pitching

## 7. PR Measurement & ROI Plan
- Immediate actions (week 1): media list building, story angle finalization, pitch drafting
- Short-term (month 1): first 10 pitches sent, HARO responses daily, 1 press release
- Long-term (month 3+): 5+ media placements, SEO backlink impact, brand mention tracking

Include expected results: backlink quality from press mentions, referral traffic from Tier 1 vs Tier 2 coverage, and brand search lift from earned media."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
