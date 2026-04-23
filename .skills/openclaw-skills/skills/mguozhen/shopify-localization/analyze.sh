#!/usr/bin/env bash
# shopify-localization — Store localization strategy for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: localize store for: <target market or country>"
  exit 1
fi

SESSION_ID="shopify-local-$(date +%s)"

PROMPT="You are a Shopify localization expert specializing in cultural adaptation, multilingual store setup, local payment integration, and market-specific marketing for international ecommerce. Build a complete localization strategy for: ${INPUT}

Produce a complete store localization report with these sections:

## 1. Translation Strategy & Workflow
- Translation scope: product pages, collections, checkout, emails, legal pages
- Machine translation tools: DeepL, Google Translate — accuracy and limitations
- Professional translation: when to invest, cost per word benchmarks
- Shopify translation apps: Weglot, Langify, Transcy — comparison and recommendation
- Translation management workflow and quality review process

## 2. Cultural Adaptation for Target Market
- Color psychology differences: colors to avoid or embrace in target market
- Imagery and lifestyle photography: representation and cultural relevance
- Tone of voice differences: formal vs casual communication norms
- Social proof format: how testimonials and reviews are consumed in this market
- Local holidays, events, and cultural moments for marketing calendar

## 3. Local Payment Method Integration
- Mandatory payment methods for this target market with adoption rates
- Shopify Payments availability and alternatives in target market
- BNPL options popular in this market (Klarna, Afterpay, local providers)
- Bank transfer and local wallet options setup

## 4. SEO Localization
- Hreflang tag implementation for international SEO
- Keyword research in local language: tools and process
- URL structure for localized content (subdirectory vs subdomain)
- Local backlink strategy: directories, media, and partner sites
- Google My Business setup if applicable for local presence

## 5. Pricing & Currency Strategy
- Psychological pricing in target market (odd pricing norms, price points)
- Currency display: automatic conversion vs fixed local pricing
- Tax-inclusive vs tax-exclusive pricing convention in this market
- Promotional discount norms: what percentage off resonates

## 6. Localized Customer Service
- Primary customer service channel preference in this market
- Language support options: hire local, use translation AI, or partner
- Local business hours and response time expectations
- Return and refund norms and legal requirements in target market

## 7. Market-Specific Marketing Plan
- Immediate actions (week 1): translation scope, payment setup, SEO hreflang
- Short-term (month 1): first localized campaigns, local influencer outreach
- Long-term (month 3+): market-specific ad campaigns, local PR, community building

Include localization ROI data: conversion rate lift from localized stores vs English-only for non-English markets, and cost benchmarks for full store localization."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
