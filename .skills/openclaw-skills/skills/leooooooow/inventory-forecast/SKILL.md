---
name: inventory-forecast
description: Project inventory needs based on historical order velocity, seasonality, and planned promotions so you reorder before stockouts hurt rankings.
---

# Inventory Forecast

Running out of stock is one of the most costly mistakes in ecommerce — it tanks your search rankings, hands sales to competitors, and can take weeks to recover from. This skill projects your inventory needs by analyzing historical order velocity, seasonal demand patterns, supplier lead times, and upcoming promotional events so you can place reorders with confidence before stockouts damage your momentum.

## Use when

- You notice a fast-moving SKU is dropping below safety stock levels and need to calculate exactly when to place the next purchase order to avoid a gap in availability
- You are planning a major promotional event like a TikTok Shop Flash Sale, Shopee 9.9 campaign, or Amazon Prime Day and need to estimate how much extra inventory to pre-position based on expected demand lift
- Your supplier has long lead times of 30 to 90 days and you need to build a rolling reorder calendar that accounts for production, shipping, and customs clearance delays
- You want to compare sell-through rates across multiple SKUs or product categories to identify which items need urgent restocking versus which ones are overstocked and tying up cash
- You are expanding to a new warehouse or fulfillment center and need to decide initial stock allocation quantities based on regional demand forecasts

## What this skill does

This skill takes your historical sales data, current inventory levels, supplier lead times, and any planned promotions or seasonal events as inputs, then builds a forward-looking demand projection for each SKU or product group. It applies velocity-based forecasting adjusted for weekly and monthly seasonality curves, calculates safety stock buffers based on demand variability and lead time uncertainty, and generates specific reorder dates with recommended quantities. The output helps you maintain optimal stock levels without over-ordering, which is especially critical for cash-constrained sellers managing dozens or hundreds of SKUs across multiple channels.

## Inputs required

- **Historical sales data** (required): Daily or weekly unit sales for each SKU over the past 3 to 12 months. Provide as a CSV, spreadsheet export, or paste raw numbers. Example: "SKU-A sold 142 units in January, 198 in February, 310 in March."
- **Current inventory levels** (required): How many units of each SKU you currently have on hand and in transit. Example: "SKU-A: 450 on hand, 200 in transit arriving April 5."
- **Supplier lead time** (required): The number of days from placing a purchase order to receiving goods at your warehouse. Example: "45 days from order to delivery for our Shenzhen supplier."
- **Planned promotions or events** (optional): Any upcoming campaigns, flash sales, influencer pushes, or seasonal peaks that could spike demand. Including these dramatically improves forecast accuracy. Example: "Running a 30% off flash sale on May 5, expecting 3x normal daily volume."
- **Target days of supply** (optional): How many days of inventory buffer you want to maintain. Defaults to 30 days if not specified. Helps calibrate reorder aggressiveness to your risk tolerance and cash position.

## Output format

The output is structured in four sections. First, a **Demand Forecast Table** showing projected daily and weekly unit sales for each SKU over the next 30, 60, and 90 days with seasonality adjustments applied. Second, a **Reorder Schedule** listing the specific date each SKU should be reordered, the recommended order quantity, and the expected arrival date based on lead time. Third, a **Risk Assessment** highlighting SKUs at high risk of stockout within the next 14 days, SKUs that are overstocked by more than 60 days of supply, and the estimated revenue impact of potential stockouts. Fourth, a **Cash Flow Impact** summary estimating the total purchase order cost for the forecast period so you can plan working capital needs alongside inventory decisions.

## Scope

- Designed for: ecommerce operators, inventory planners, and supply chain managers running DTC or marketplace businesses
- Platform context: platform-agnostic — works for TikTok Shop, Amazon FBA, Shopee, Lazada, Shopify, and multi-channel sellers
- Language: English

## Limitations

- Does not connect to live inventory management systems or ERPs; you must provide current stock data manually or via export
- Forecasts are based on historical patterns and stated assumptions — unexpected viral moments, supply chain disruptions, or competitor actions may cause actual demand to deviate significantly
- Does not account for supplier-side constraints like minimum order quantities or tiered pricing unless you specify them in the inputs