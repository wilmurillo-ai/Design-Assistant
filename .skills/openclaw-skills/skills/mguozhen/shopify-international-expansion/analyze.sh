#!/usr/bin/env bash
# shopify-international-expansion — International market expansion for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: international expansion plan: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-international-$(date +%s)"

PROMPT="You are a Shopify international expansion expert specializing in global ecommerce market entry, cross-border logistics, localization, and multi-market marketing strategy. Build a complete international expansion plan for: ${INPUT}

Produce a complete international expansion report with these sections:

## 1. Market Selection Framework
- Criteria for evaluating international markets: market size, competition, logistics, regulation
- Top 5 recommended markets for this product category with data rationale
- Quick wins: markets with lowest barrier to entry for this niche
- Markets to avoid or defer: high complexity or low opportunity

## 2. Top 3 Market Deep-Dives
For each of the top 3 markets:
- Market size and ecommerce penetration data
- Top competitors and their positioning
- Consumer behavior and purchasing preferences
- Cultural considerations that affect marketing and product presentation
- Estimated market entry cost and timeline

## 3. Shopify Markets & Technical Configuration
- Shopify Markets setup: enabling international markets, currency, and language
- Domain strategy: subdomain (.com/en-gb) vs country-code TLD (.co.uk)
- Geolocation redirect configuration and selector widget
- Automatic currency conversion vs fixed local pricing strategy

## 4. Localization Requirements Checklist
- Language translation: machine translation vs professional translator
- Currency display and pricing psychology per market
- Product images and lifestyle photography cultural adaptation
- Date formats, measurement units, and address format adjustments

## 5. International Payments & Tax Compliance
- Preferred payment methods by market (iDEAL in Netherlands, PayNow in Singapore, etc.)
- VAT/GST registration thresholds by country
- Duties and import tax handling: DDP vs DDU shipping
- International fraud prevention considerations

## 6. Cross-Border Logistics Strategy
- Shipping carriers by region: DHL, FedEx, local carriers comparison
- Fulfillment options: ship from home country vs 3PL in target market
- Delivery time benchmarks by market and customer expectations
- Returns strategy for international orders

## 7. Go-to-Market Launch Plan
- Immediate actions (week 1): market selection, Shopify Markets setup, first translations
- Short-term (month 1): first international orders, logistics tested, localized ads
- Long-term (month 3+): full localization, local marketing investment, market-specific influencers

Include specific market entry cost estimates, expected CAC in new markets vs home market, and revenue ramp timelines for Shopify international expansion."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
