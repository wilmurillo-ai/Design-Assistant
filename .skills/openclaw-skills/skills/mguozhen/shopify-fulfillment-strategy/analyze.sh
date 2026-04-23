#!/usr/bin/env bash
# shopify-fulfillment-strategy — 3PL vs in-house fulfillment strategy for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: fulfillment strategy for: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-fulfillment-$(date +%s)"

PROMPT="You are a Shopify fulfillment strategy expert specializing in 3PL selection, in-house operations, and fulfillment model optimization for ecommerce businesses at various growth stages. Build a complete fulfillment strategy for: ${INPUT}

Produce a complete fulfillment strategy report with these sections:

## 1. Fulfillment Model Comparison
- In-house fulfillment: cost structure, labor, space, control advantages
- 3PL (third-party logistics): cost structure, scalability, technology advantages
- Hybrid model: which operations to keep in-house vs outsource
- Decision matrix: when each model wins based on volume, SKU count, and growth rate

## 2. In-House Fulfillment Optimization
- Space requirements: typical sq ft needed per daily order volume
- Labor requirements: staff-to-order ratio benchmarks
- Technology stack: WMS, barcode scanning, packing station setup
- When to outgrow in-house: the inflection point signals to watch for

## 3. 3PL Market Overview & Selection Criteria
- Major 3PL options for Shopify: ShipBob, ShipHero, Deliverr, Whiplash, Red Stag
- Selection criteria: minimum order volumes, SKU limits, integration quality
- Specialty 3PLs: temperature-controlled, hazmat, apparel-specialized, DTC-focused
- RFQ process: what to send and what to compare

## 4. 3PL Cost Structure Breakdown
- Receiving fees: per pallet, per item, labor rates
- Storage fees: per bin, per pallet per month
- Pick and pack fees: per order, per item, packing materials
- Outbound shipping: carrier rates, dimensional weight practices
- Setup and integration fees: one-time costs

## 5. 3PL Contract Key Terms
- SLA requirements: order processing time, accuracy rate (99%+), damage rate
- Inventory accuracy: cycle count frequency and liability for losses
- Exit clauses: minimum contract length, termination notice, inventory return
- Liability and insurance: coverage for lost or damaged inventory

## 6. Migration & Integration Process
- 90-day transition plan: overlap period, inventory transfer, parallel testing
- Shopify integration: API connections, inventory sync, order routing
- Team communication: customer service alignment on new processes
- Peak season timing: when NOT to switch fulfillment providers

## 7. Performance Monitoring & Scaling Plan
- Immediate actions (week 1): fulfillment cost audit, 3PL shortlist, RFQ preparation
- Short-term (month 1): 3PL evaluation, contract negotiation, integration testing
- Long-term (month 3+): go-live, performance monitoring, quarterly business reviews

Include specific volume thresholds: when 3PL becomes cost-competitive with in-house (typically 50-100 orders/day), and average cost per order comparison across fulfillment models."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
