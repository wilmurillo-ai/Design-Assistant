---
name: profit-calculator
description: Calculate true per-unit profit margins across channels by factoring in COGS, platform fees, shipping costs, ad spend allocation, returns, and overhead to identify which SKUs and channels actually make money.
---

# Profit Calculator

Many ecommerce brands think they are profitable because revenue is growing, only to discover at year-end that certain SKUs or channels have been losing money on every order. Profit Calculator walks you through a full per-unit profit teardown so you can see exactly which products and channels deserve more budget and which should be repriced, rebundled, or killed.

## Use when

- The operator says "my TikTok Shop sales look great but the bank account isn't growing — can we figure out what's actually making money?"
- A Shopify seller asks "if I raise the price by $2, will that offset my new 3PL rate and higher Meta CPMs, or am I still underwater?"
- An Amazon FBA brand wants to compare a single SKU's contribution margin between FBA, FBM, and their own DTC store side by side before reallocating inventory.
- A founder is preparing a board update and needs a clean per-SKU contribution margin waterfall that rolls up to a blended gross margin with and without advertising.

## What this skill does

Takes a list of SKUs plus channel-level fee structures and produces a per-unit profit waterfall for each SKU on each channel. The calculation starts from the landed product cost (COGS including freight and duty), subtracts platform commissions and payment processing, then outbound shipping and pick-and-pack fees, then amortized ad spend using either blended MER or channel-specific ROAS, then refund and return cost reserves, and finally a per-unit allocation of fixed overhead. The output flags channels where a SKU is margin-dilutive and recommends a minimum retail price to hit a target contribution margin.

## Inputs required

- **SKU list with unit COGS** (required): landed cost per unit including inbound freight, duty, and any inspection fees. Example: "SKU-001, $4.20 landed."
- **Retail price per channel** (required): the current listed or promoted price on each channel including typical on-platform discount.
- **Channel fee schedule** (required): commission %, referral fees, payment processing %, and any monthly storage or subscription costs that should be amortized per unit.
- **Shipping and fulfillment cost per unit** (required): weight- or zone-based shipping plus 3PL pick-pack rates, or FBA fulfillment fees.
- **Ad spend allocation** (optional): either a blended MER target (e.g., 4.0) or channel-specific ROAS so advertising can be subtracted from contribution margin.
- **Return rate and refund cost** (optional): average return % per category and the fully loaded cost of a return (product loss + reverse logistics + restocking labor).
- **Monthly overhead** (optional): fixed costs like software, salaries, and rent to allocate per unit at expected volume.

## Output format

A structured per-SKU, per-channel table showing gross revenue, all deductions line by line, contribution margin in dollars and percent, and a channel ranking for each SKU. Below the table, a prioritized action list calls out: SKUs that lose money on at least one channel, SKUs where raising price by a small amount would unlock a target margin, channels that should get more inventory, and channels where you should pause promotion. A short written summary translates the math into a one-paragraph recommendation suitable for a partner or investor update.

## Scope

- Designed for: ecommerce operators, DTC founders, and marketplace sellers managing multiple channels.
- Platform context: platform-agnostic with specific fee templates for Amazon, TikTok Shop, Shopee, Lazada, and Shopify.
- Language: English.

## Limitations

- Does not pull real-time fee data from platform APIs; you must provide current fee rates as inputs.
- Does not replace bookkeeping, tax filing, or audited financial statements — it is a decision-support tool, not accounting.
- Ad allocation assumes a steady-state MER or ROAS; it does not model attribution decay or long multi-touch customer journeys.
