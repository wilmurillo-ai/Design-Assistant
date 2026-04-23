---
name: amazon-inventory-forecast
description: "Amazon inventory forecasting agent. Calculates optimal reorder points and quantities from sales velocity, lead time, and storage costs — tells sellers exactly when to reorder and how much to order. Triggers: inventory forecast, reorder point, stock forecast, amazon inventory, fba inventory, stockout prevention, overstock, safety stock, eoq, inventory management, when to reorder, inventory calculator"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-inventory-forecast
---

# Amazon Inventory Forecast

FBA inventory intelligence — know exactly when to reorder and how much to order before you stock out or overstock.

Provide your sales data, lead time, and current stock levels. The agent calculates reorder points, EOQ, stockout risk windows, and storage fee exposure.

## Commands

```
forecast add <sku>                 # add a SKU to track with sales and lead time data
forecast check                     # run forecast update on all tracked SKUs
forecast reorder point             # calculate reorder point for each SKU
forecast eoq                       # calculate economic order quantity
forecast stockout risk             # identify SKUs at risk of stocking out
forecast overstock risk            # identify SKUs at risk of long-term storage fees
forecast report                    # full inventory health report
forecast save                      # save all SKU data and forecasts to workspace
```

## What Data to Provide

The agent works with:
- **SKU + sales data** — "SKU: B-RED-LG, sold 240 units last 30 days, currently 180 units on hand"
- **Lead time** — "supplier takes 25 days to ship, FBA check-in adds 5 days"
- **Storage cost** — monthly FBA storage fee rate (standard or oversized)
- **Unit cost** — your landed cost per unit (for EOQ calculation)
- **Seasonal notes** — "Q4 demand doubles, Prime Day adds ~3x spike"

No integrations needed. Paste your data directly.

## Workspace

Creates `~/amazon-inventory/` containing:
- `skus.md` — tracked SKUs with sales history and parameters
- `forecasts/` — generated forecast reports per SKU
- `alerts.md` — stockout and overstock alert log
- `reorder-log.md` — history of reorder recommendations made

## Analysis Framework

### 1. Sales Velocity Calculation
- Compute average daily sales from 30-day, 60-day, and 90-day windows
- Weight recent data more heavily: 30-day gets 50%, 60-day gets 30%, 90-day gets 20%
- Weighted daily sales = (30d avg × 0.5) + (60d avg × 0.3) + (90d avg × 0.2)
- Flag: high variance between windows — demand is trending up or down
- Flag: 30d velocity >20% above 90d average — demand acceleration detected

### 2. Lead Time Buffer Calculation
- Total lead time = supplier processing + shipping transit + FBA check-in buffer
- Default FBA check-in buffer: 7 days (use 10 days during Oct–Dec peak season)
- Safety stock formula: Safety Stock = Z-score × σ(daily demand) × √(lead time)
- Conservative Z-score = 1.65 (95% service level); aggressive = 1.28 (90%)
- Minimum safety stock: 14 days of average daily sales

### 3. Reorder Point Formula
- Reorder Point = (Average Daily Sales × Total Lead Time) + Safety Stock
- Example: 8 units/day × 30 days lead time + 56 units safety stock = 296 units
- Express reorder point both in units and in days-of-stock-remaining
- Show the calculation explicitly so sellers can verify inputs

### 4. EOQ Formula (Economic Order Quantity)
- EOQ = √(2DS / H)
  - D = annual demand (units/year)
  - S = order cost per purchase order (shipping + prep + admin, typically $50–$200)
  - H = annual holding cost per unit (FBA storage fee × 12 + opportunity cost)
- Round EOQ up to nearest full case pack quantity
- Show sensitivity analysis: EOQ at ±20% demand change

### 5. Storage Fee Avoidance
- FBA long-term storage fee triggers: units stored >365 days
- Q4 surcharge period: Oct 1 – Dec 31 (higher monthly rates)
- Q4 inventory removal deadline: recommend sending final Q4 shipment no later than Sept 15
- Overstock flag: current inventory > 180 days of supply at current velocity
- Compute projected months-of-supply: Current Stock / (Daily Sales × 30)

### 6. Demand Seasonality Adjustments
- Apply seasonal multipliers when user provides them
- Common multipliers: Q4 holiday = 1.5–3x, Prime Day = 2–4x (48-hour window), Back-to-school = 1.2–1.5x
- Adjusted forecast = base velocity × seasonal multiplier
- For Q4 planning: build to cover Oct 1 – Dec 31 + post-holiday return buffer
- Flag: if current stock will not cover a known seasonal spike, surface reorder urgency

## Reorder Decision Output

Every `forecast check` shows per SKU:
| SKU | Daily Sales | Days of Stock | Reorder Point | EOQ | Status |
|-----|------------|---------------|---------------|-----|--------|
| ... | ... | ... | ... | ... | OK / REORDER NOW / URGENT |

Status levels:
- **OK** — days of stock > reorder point days
- **REORDER SOON** — within 14 days of reorder point
- **REORDER NOW** — at or below reorder point
- **URGENT** — less than lead time days of stock remaining (stockout imminent)

## Rules

1. Always collect lead time before computing reorder points — the formula is useless without it
2. Never recommend a reorder quantity below one full case pack — partial cases create receiving complications at FBA
3. Flag all assumptions explicitly — if the user has not provided 90-day sales data, state which averages were used
4. Apply Q4 seasonality adjustments automatically for any forecast that spans October–December
5. Show the full math for every EOQ and reorder point calculation — sellers need to verify with their own numbers
6. Distinguish between units currently at FBA and units in transit — both count toward days-of-supply
7. Save updated forecasts to `~/amazon-inventory/forecasts/` on every `forecast save` call
