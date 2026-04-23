#!/usr/bin/env bash
# shopify-ab-testing — A/B testing framework for Shopify stores
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: AB testing plan: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-ab-testing-$(date +%s)"

PROMPT="You are a Shopify CRO (conversion rate optimization) expert specializing in A/B testing methodology, statistical analysis, and systematic experimentation for ecommerce stores. Build a complete A/B testing framework for: ${INPUT}

Produce a complete A/B testing strategy report with these sections:

## 1. Test Prioritization Framework
- ICE scoring model (Impact, Confidence, Ease) for ranking test ideas
- Top 20 highest-impact A/B test ideas for this store type
- Quick wins vs long-term structural tests
- Revenue impact calculator: how 1% CR improvement affects annual revenue

## 2. Hypothesis Writing Templates
- Hypothesis structure: We believe [change] will [outcome] because [reasoning]
- 10 specific hypothesis examples for this niche
- Success metric definition for each test type
- Secondary metric tracking to detect unintended consequences

## 3. Element Testing Roadmap (Priority Order)
- Homepage: hero image, headline, featured products, navigation
- Product page: title, images, description, price display, CTA button
- Cart page: upsell placement, trust signals, checkout button
- Checkout: form fields, payment icons, progress indicators

## 4. Sample Size & Statistical Requirements
- Minimum traffic threshold for valid test results
- Sample size calculator inputs: baseline CR, MDE, confidence level
- How long to run tests: minimum 2 weeks, statistical significance at 95%
- How to handle seasonal traffic fluctuations during tests

## 5. A/B Testing Tool Stack for Shopify
- Native: Shopify built-in theme editor variants
- Third-party: Google Optimize alternatives, Shogun, Neat A/B Testing
- Heatmap and session recording: Hotjar, Microsoft Clarity (free)
- Analytics integration: GA4, Shopify Analytics, Triple Whale

## 6. Results Analysis & Decision Framework
- Statistical significance explained: p-value, confidence interval interpretation
- Common mistakes: peeking at results early, stopping tests too soon
- When to declare a winner vs when to run follow-up tests
- How to document and share learnings across the team

## 7. 12-Week Testing Calendar & Scaling Plan
- Immediate actions (week 1): baseline metrics, heatmaps, first hypothesis
- Short-term (month 1): run 2 simultaneous tests, analyze first results
- Long-term (month 3+): 10+ completed tests, compound conversion gains, personalization

Include realistic conversion rate improvement expectations (e.g., 5-15% lift per winning test), compounding effect math, and testing velocity benchmarks for stores at different traffic levels."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
