---
name: shopify-ad-attribution
description: "Shopify ad attribution agent. Calculates true ROAS per channel by correlating Shopify order UTM data with ad spend — reveals which channels actually drive profit vs. which ones just get credit. Triggers: ad attribution, shopify attribution, roas by channel, true roas, marketing attribution, utm analysis, ad spend analysis, channel performance, meta attribution, google attribution, shopify ads"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/shopify-ad-attribution
---

# Shopify Ad Attribution

Cut through attribution lies — find out which channels actually drive profit, not just which ones take credit.

Paste your Shopify order UTM data and ad spend by channel. The agent calculates true ROAS, profit-adjusted ROAS, and surfaces channels that over- or under-claim credit.

## Commands

```
attribution setup                  # configure store, COGS%, channels, and spend data
attribution report                 # full attribution analysis across all channels
attribution by channel             # per-channel revenue, spend, and ROAS breakdown
attribution roas                   # ROAS and profit-adjusted ROAS per channel
attribution ltv                    # LTV-adjusted attribution (repeat purchase value)
attribution last click vs multi touch  # compare last-click vs. linear vs. time-decay models
attribution anomaly                # flag channels with unusual credit patterns
attribution save                   # save setup and latest report to workspace
```

## What Data to Provide

The agent works with:
- **Shopify orders export** — paste UTM source/medium/campaign columns from order export CSV
- **Ad spend by channel** — "Meta: $3,200 | Google: $1,800 | TikTok: $900 this month"
- **COGS and margin** — "product cost is 30% of revenue, Shopify fees ~3%"
- **Channel setup** — list of active ad channels and their primary UTM source values
- **LTV data** — if available: average repeat purchase rate and second-order value

No integrations needed. Paste exported data directly.

## Workspace

Creates `~/shopify-attribution/` containing:
- `setup.md` — store configuration, COGS%, channel mapping, UTM conventions
- `reports/` — monthly attribution reports
- `spend-log.md` — historical ad spend by channel
- `anomalies.md` — flagged attribution anomalies

## Analysis Framework

### 1. UTM Parameter Mapping
- Map UTM source to channel: facebook/instagram → Meta, google/cpc → Google, tiktok → TikTok, email → Email, organic → Organic, (none)/(direct) → Direct
- Clean UTM data: normalize case, strip typos, consolidate variants (e.g., "FB" and "facebook" → Meta)
- Flag orders with missing UTM data — these are attribution dark zones (often direct/email/organic)
- Compute UTM coverage rate: % of orders with valid UTM source attribution
- Group by: source, medium, campaign for granular analysis

### 2. Last-Click Attribution Model
- Assign 100% of order revenue to the last UTM source before purchase
- Compute per-channel: total revenue, order count, average order value
- Match against ad spend to get last-click ROAS: Revenue / Spend
- Flag: channels with very high last-click ROAS — may be capturing credit from upper-funnel channels
- Flag: direct/(none) volume — if >30% of revenue is unattributed, attribution picture is incomplete

### 3. Linear Attribution Model
- Distribute revenue equally across all touchpoints in a customer journey
- Requires multi-session UTM data — if not available, estimate using channel mix ratios
- Compare linear attribution revenue vs. last-click revenue per channel
- Channels that gain credit under linear: typically top-of-funnel (Meta, TikTok, YouTube)
- Channels that lose credit under linear: typically bottom-of-funnel (Google Brand, Email)

### 4. Time-Decay Attribution Model
- Weight touchpoints more heavily the closer they are to the purchase
- Decay formula: weight = e^(−λ × days_before_purchase), λ = 0.1 for 7-day half-life
- Useful for longer purchase cycles (furniture, high-ticket items)
- Compare time-decay vs. last-click — large differences indicate assisted conversion patterns

### 5. ROAS Calculation
- **Reported ROAS** = Total Revenue Attributed / Ad Spend
- **Gross Profit ROAS** = (Revenue × Gross Margin%) / Ad Spend
- **Net Profit ROAS** = (Revenue × Net Margin% after fees) / Ad Spend
- Profitability threshold: Net Profit ROAS must exceed 1.0 to be contribution-positive
- True break-even ROAS = 1 / (Gross Margin% − Platform Fee%)
- Example: 60% margin, 3% Shopify fee → Break-even ROAS = 1 / 0.57 = 1.75

### 6. Channel Overlap and LTV Adjustment
- Identify customers who converted via multiple channels in a 30-day window
- Flag: Meta + Google overlap — common pattern where Meta drives discovery, Google captures conversion
- LTV adjustment: multiply first-order ROAS by repeat purchase multiplier
  - If avg customer makes 1.4 purchases in first year, LTV ROAS = Reported ROAS × 1.4
- Cohort LTV by acquisition channel — some channels acquire better long-term customers

### 7. Attribution Anomaly Detection
- Flag: channel spend increased but attributed revenue flat → ad performance degrading or UTM broken
- Flag: direct/(none) revenue spike without organic traffic explanation → UTM tags broken in campaign
- Flag: single campaign taking disproportionate credit (>40% of revenue) → potential tracking issue
- Flag: ROAS dramatically higher than industry benchmark → verify UTM data quality

## Output Format

`attribution report` delivers:

### Channel Summary Table
| Channel | Spend | Revenue (LC) | ROAS (LC) | Profit ROAS | Orders |
|---------|-------|-------------|-----------|-------------|--------|
| Meta | $X | $X | X.Xx | X.Xx | N |
| Google | ... | ... | ... | ... | ... |

### Attribution Model Comparison
| Channel | Last-Click | Linear | Time-Decay | Difference |
|---------|-----------|--------|------------|------------|

### Key Findings
1. Best true-ROAS channel (profit-adjusted)
2. Most over-credited channel (last-click vs. linear gap)
3. Attribution coverage rate and dark zone estimate
4. Recommended budget reallocation

## Rules

1. Always establish COGS and margin before computing profit-adjusted ROAS — reported ROAS without margin context is misleading
2. Never declare a channel unprofitable based on last-click attribution alone — always show multi-touch comparison
3. Flag UTM coverage rate prominently — if >25% of orders lack UTM data, all channel numbers are understated
4. Apply the correct break-even ROAS threshold for the store's margin — not a generic benchmark
5. Distinguish between revenue attribution and profit attribution — high-AOV channels may look great on revenue but poor on profit
6. Identify the Meta vs. Google credit-stealing dynamic by default — it is the most common misattribution pattern in Shopify stores
7. Save reports to `~/shopify-attribution/reports/` with month-year filename on every `attribution save` call
