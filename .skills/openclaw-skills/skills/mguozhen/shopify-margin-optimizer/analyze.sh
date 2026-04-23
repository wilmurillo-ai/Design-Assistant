#!/usr/bin/env bash
# shopify-margin-optimizer — Margin and profitability optimizer for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: margin optimizer for: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-margin-$(date +%s)"

PROMPT="You are a Shopify profitability and financial optimization expert specializing in ecommerce P&L analysis, COGS reduction, and margin improvement strategies for DTC brands. Build a complete margin optimization plan for: ${INPUT}

Produce a complete profitability optimization report with these sections:

## 1. Ecommerce P&L Framework
- Revenue line items: gross sales, discounts, returns, net revenue
- COGS components: product cost, inbound freight, duties, packaging
- Gross margin calculation and industry benchmarks for this niche
- Contribution margin: gross profit minus variable marketing and fulfillment costs
- Net margin: after fixed operating expenses

## 2. COGS Component Analysis
- Product cost as % of revenue: target ranges by category
- Shipping cost optimization: carrier comparison, dimensional weight, zone skipping
- Packaging cost audit: opportunities to right-size and reduce material costs
- Fulfillment cost analysis: in-house vs 3PL comparison for this volume

## 3. Margin Leak Identification
- Top 5 margin leaks common in this product category
- Returns rate impact on gross margin (each 1% return rate = X% margin hit)
- Discount depth vs frequency analysis: are promotions killing margin?
- Payment processing fee optimization: Shopify Payments vs alternatives
- App subscription costs: audit against actual value delivered

## 4. COGS Reduction Tactics
- Supplier negotiation leverage: volume commitments, longer payment terms, exclusivity
- Material substitution: same quality, lower cost alternatives
- Manufacturing process improvements: where waste can be reduced
- Private label vs branded: margin comparison for resellers

## 5. Revenue-Side Margin Improvement
- Product mix optimization: shift sales toward higher-margin SKUs
- Price increase strategy: 5% increase with minimal demand impact tactics
- Bundle design for higher-margin combinations
- AOV increases: upsell and cross-sell impact on contribution margin

## 6. Operating Expense Reduction
- Marketing efficiency: CAC vs LTV ratio and paid media efficiency targets
- Team and contractor cost optimization
- Technology and app stack audit: 10 common unnecessary Shopify apps
- Shipping carrier rate negotiation thresholds and tactics

## 7. 90-Day Margin Improvement Roadmap
- Immediate actions (week 1): full P&L build, margin leak identification, app audit
- Short-term (month 1): top 3 COGS reduction initiatives, price increase on 20% of catalog
- Long-term (month 3+): supplier renegotiation, shipping optimization, 3-5 point margin improvement

Include specific margin benchmarks: healthy DTC gross margins (40-70% by category), contribution margin targets (20-30%), and what top quartile Shopify brands achieve for net margins."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
