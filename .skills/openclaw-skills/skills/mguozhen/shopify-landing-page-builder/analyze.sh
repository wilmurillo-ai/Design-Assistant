#!/usr/bin/env bash
# shopify-landing-page-builder — High-converting landing page strategy for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: landing page strategy: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-landing-$(date +%s)"

PROMPT="You are a Shopify conversion rate optimization expert specializing in high-converting landing page design, copywriting, and A/B testing for ecommerce stores. Build a complete landing page strategy and copy framework for: ${INPUT}

Produce a complete landing page optimization report with these sections:

## 1. Page Architecture & Layout
- Above-the-fold requirements: hero image, headline, subhead, CTA, trust signals
- Recommended section order for maximum conversion flow
- Visual hierarchy principles for this product category
- Exit intent and sticky elements placement

## 2. Headline & Copy Framework
- 5 headline formulas with specific examples for this niche
- Value proposition statement formula (for whom, what outcome, how different)
- Bullet point copy structure: feature → benefit → emotional payoff
- Objection handling section placement and copy

## 3. Social Proof & Trust Architecture
- Review placement strategy: stars near CTA, detailed reviews below fold
- Trust badge types and placement (secure checkout, guarantee, certifications)
- Number proof: customers served, units sold, satisfaction rate
- Press mentions and media logo bar setup

## 4. CTA Optimization Strategy
- Primary CTA button copy variations to test (5 options with psychology)
- Button size, color contrast, and whitespace guidelines
- Multi-CTA strategy: primary, secondary, and micro-conversions
- Urgency and scarcity elements: countdown timers, stock indicators

## 5. Mobile-First Design Requirements
- Mobile layout differences from desktop
- Thumb zone optimization for CTA placement
- Mobile image sizing and load optimization
- Tap target sizing and form field best practices

## 6. Page Speed & Technical Foundations
- Target load time and Core Web Vitals scores
- Image optimization checklist (WebP, lazy loading, sizing)
- App and script audit: what to remove for speed
- Shopify theme vs page builder comparison (GemPages, Shogun, Pagefly)

## 7. A/B Testing & Optimization Roadmap
- Immediate actions (week 1): launch page, baseline metrics, heatmap setup
- Short-term (month 1): first A/B test (headline), second test (CTA copy)
- Long-term (month 3+): multivariate testing, personalization, segment-specific pages

Include conversion rate benchmarks by industry, average order value impact from page improvements, and specific tools for heatmaps, session recording, and A/B testing on Shopify."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
