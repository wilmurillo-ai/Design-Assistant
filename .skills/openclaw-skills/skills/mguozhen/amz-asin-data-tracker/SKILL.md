---
name: amz-asin-data-tracker
description: "Amazon ASIN visual data collection and monitoring agent. Zero-code collection of Amazon ASIN and competitor data, supports scheduled tasks, real-time alerts, and multi-format export. Triggers: asin data tracker, amazon data collection, asin monitor, competitor data, amazon scraper, asin tracking, real-time alert, amazon export, asin collector, product monitoring, amazon surveillance, data export"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amz-asin-data-tracker
---

# Amazon ASIN Data Tracker

Zero-code Amazon ASIN and competitor data collection with scheduled monitoring, real-time alerts, and multi-format export — the essential tool for Amazon sellers.

Paste an ASIN or product URL. The agent collects key metrics, sets up monitoring schedules, and alerts you to significant changes.

## Commands

```
track add <asin>              # add ASIN to monitoring list
track snapshot                # capture current data for all tracked ASINs
track alert <threshold>       # set alert conditions (price drop %, BSR change)
track schedule <interval>     # configure monitoring schedule (daily/weekly)
track export <format>         # export data as CSV/JSON/Markdown table
track compare <asin1> <asin2> # side-by-side ASIN comparison
track history <asin>          # show full history for an ASIN
track report                  # generate comprehensive monitoring report
track save                    # save all tracking data to workspace
```

## What Data to Provide

- **ASIN** — Amazon Standard Identification Number (e.g., B08XYZ1234)
- **Product page data** — paste title, price, BSR, review count, rating
- **Historical data** — any prior snapshots you have
- **Alert preferences** — what changes matter most to you
- **Category context** — niche, main keywords, target market

## Data Collection Framework

### Core Metrics Tracked Per ASIN

| Metric | Collection Method | Alert Threshold |
|--------|------------------|-----------------|
| Price | Page data / paste | ±10% change |
| BSR | Page data / paste | ±500 ranks |
| Review count | Page data / paste | +20 new reviews |
| Star rating | Page data / paste | Drop below 4.0 |
| Seller count | Page data / paste | New sellers entering |
| Image count | Manual observation | New images added |
| Variation count | Manual observation | New variations |

### Scheduled Monitoring Cadences

**Daily monitoring** (high-priority ASINs):
- Price and BSR check
- New review detection
- Buy Box status

**Weekly monitoring** (standard watchlist):
- Full metric snapshot
- Listing change detection
- Competitor movement summary

**Monthly monitoring** (market overview):
- Trend analysis report
- Market share estimation
- Seasonal pattern identification

### Alert Conditions

```
PRICE DROP ALERT:     Price falls >10% from baseline
BSR SPIKE ALERT:      BSR improves >500 ranks in 7 days
REVIEW BOMB ALERT:    >10 new 1-star reviews in 48 hours
REVIEW SURGE ALERT:   >30 new reviews in 7 days (possible manipulation)
LISTING CHANGE ALERT: Title or main image changed
SELLER ALERT:         New seller with <100 feedback enters Buy Box
STOCK ALERT:          "Only X left in stock" message appears
```

## Export Formats

### CSV Export
```
ASIN, Title, Price, BSR, Reviews, Rating, Date, Category
B08XYZ123, "Product Name", $29.99, 1234, 456, 4.3, 2024-01-15, Kitchen
```

### Markdown Table
```
| ASIN | Price | BSR | Reviews | Rating | Updated |
|------|-------|-----|---------|--------|---------|
| B08X | $29.99 | 1,234 | 456 | ⭐4.3 | Jan 15 |
```

### JSON Export
```json
{
  "asin": "B08XYZ123",
  "snapshots": [
    {"date": "2024-01-15", "price": 29.99, "bsr": 1234, "reviews": 456}
  ]
}
```

## Workspace Structure

Creates `~/asin-tracker/` containing:
- `watchlist.md` — all tracked ASINs with settings
- `snapshots/` — date-stamped metric files per ASIN
- `alerts/` — triggered alert log
- `exports/` — generated export files
- `reports/` — monitoring summary reports

## Analysis Rules

1. Require at least 2 data points before declaring a trend
2. Distinguish between organic and promotional BSR movements
3. Flag BSR improvements during Prime Day, Black Friday, holiday seasons as potentially seasonal
4. Never declare a price drop permanent until it holds for 7+ days
5. Cross-reference review velocity with known promotion dates before flagging manipulation
6. Always timestamp every data point — tracking is only useful with temporal context

## Output Format

Every report outputs:
1. **Current Snapshot Table** — all tracked ASINs with latest metrics
2. **Changes Since Last Check** — delta table showing what moved and by how much
3. **Active Alerts** — list of triggered conditions with severity (High/Medium/Low)
4. **Trend Summary** — 30-day direction for each key metric
5. **Recommended Actions** — prioritized response list based on detected changes
