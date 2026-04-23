#!/usr/bin/env bash
# shopify-ai-product-description — AI product description generator for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: write product descriptions: <product name and details>"
  exit 1
fi

SESSION_ID="shopify-ai-desc-$(date +%s)"

PROMPT="You are a Shopify product copywriting expert specializing in AI-assisted product description generation, SEO optimization, and conversion-focused copy for ecommerce stores. Generate a complete product description framework for: ${INPUT}

Produce a complete product description strategy and samples with these sections:

## 1. Copy Framework Selection
- AIDA formula (Attention, Interest, Desire, Action) — when to use it
- PAS formula (Problem, Agitation, Solution) — best for problem-solving products
- FAB formula (Features, Advantages, Benefits) — best for technical products
- Hybrid formula for this specific product type with example

## 2. SEO Keyword Integration Strategy
- Primary keyword placement: title, first sentence, H2 headers
- Secondary keywords: bullet points and body copy
- Long-tail keyword opportunities for this product category
- Schema markup recommendation for product rich snippets

## 3. 3 Complete Product Description Samples
- Version A: AIDA-style narrative description (150-200 words)
- Version B: Benefit-led bullet point format (10 bullets)
- Version C: Short punchy version for mobile/ads (50-75 words)
- All three versions written specifically for the input product/niche

## 4. Bullet Point Optimization Framework
- Feature-to-benefit transformation formula: [Feature] so you can [Benefit]
- Sensory language for physical products: how it feels, sounds, smells
- Specificity rule: numbers and dimensions over vague claims
- 10 bullet point templates for common product attributes in this niche

## 5. Brand Voice & Tone Guidelines
- Casual vs professional tone selection by customer avatar
- Power words for this niche: 30 conversion-driving adjectives and verbs
- Words to avoid: clichés, overused phrases, and weak filler words
- Consistency checklist for maintaining voice across all products

## 6. AI Prompt Templates for Catalog Scale
- Master prompt template for generating descriptions at scale
- Input variables: product name, key features, target customer, brand voice
- Quality control checklist after AI generation
- Edit time estimate: 5-10 minutes per description for human polish

## 7. Implementation & Testing Plan
- Immediate actions (week 1): audit current descriptions, prioritize top products
- Short-term (month 1): rewrite top 50 products, track conversion impact
- Long-term (month 3+): full catalog updated, A/B test winners identified

Include conversion rate lift data from optimized product descriptions (typically 10-30% improvement) and SEO traffic impact from keyword-optimized copy."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
