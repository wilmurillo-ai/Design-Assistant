---
name: aliexpress-shipping-optimizer
description: "AliExpress shipping template optimizer and pricing calculator agent. Batch configure shipping templates, calculate regional pricing, set up overseas warehouse templates, and optimize freight strategies for AliExpress sellers. Triggers: aliexpress shipping, freight template, aliexpress pricing, shipping cost calculator, overseas warehouse, aliexpress logistics, freight optimization, shipping template, regional pricing, aliexpress freight, cross-border logistics"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/aliexpress-shipping-optimizer
---

# AliExpress Shipping Template Optimizer

One-click batch shipping template configuration, regional pricing calculator, overseas warehouse setup, and freight strategy optimization for AliExpress cross-border sellers.

## Commands

```
shipping template <product>       # create optimal shipping template
shipping batch <products>         # batch configure templates for multiple products
shipping price <product> <region> # calculate shipping cost for region
shipping warehouse <product>      # overseas warehouse strategy
shipping zone <country>           # shipping options and costs for a country
shipping compare <carriers>       # compare carrier options
shipping calculator <weight> <dims> <dest> # freight cost estimate
shipping optimize <current>       # optimize existing shipping template
shipping seasonal <period>        # peak season shipping adjustments
shipping report <product>         # full logistics strategy report
```

## What Data to Provide

- **Product specs** — weight, dimensions, category
- **Origin country** — where you ship from (China, typically)
- **Target markets** — which countries/regions to sell to
- **Current carriers** — what shipping methods you're using
- **Cost targets** — maximum logistics cost you can afford

## Shipping Strategy Framework

### AliExpress Shipping Template Types

**Standard Template** (most common):
- Fixed shipping cost by region
- Customer pays shipping fee
- Use when: product price <$20, margins tight

**Free Shipping Template**:
- Shipping cost built into product price
- Removes buyer hesitation → higher conversion
- Use when: product price >$20, margins allow

**Dynamic Pricing Template**:
- Different prices per country/region
- Optimize based on actual shipping costs
- Use when: selling globally with varied logistics costs

### Major Shipping Carriers for AliExpress

**ePacket** (China → US/EU):
```
Delivery time: 12-20 days
Tracking: Full end-to-end tracking
Cost: $3-8 for 0-2kg packages
Best for: Small items <2kg to US/EU/AU markets
```

**AliExpress Standard Shipping**:
```
Delivery time: 15-35 days
Tracking: Yes
Cost: $2-6 competitive pricing
Best for: General goods, most destinations
```

**AliExpress Premium Shipping**:
```
Delivery time: 7-15 days
Cost: $8-20
Best for: Buyers wanting faster delivery, higher-value items
```

**China Post Ordinary Small Packet**:
```
Delivery time: 20-45 days
Cost: $1-3 (cheapest option)
Best for: Very low-cost items where speed isn't priority
```

**DHL Express / FedEx / UPS**:
```
Delivery time: 3-7 days
Cost: $15-60+ depending on weight
Best for: High-value items, time-sensitive orders
```

**SF Express / Yanwen / 4PX**:
```
Delivery time: 10-20 days
Cost: $4-12
Best for: Alternative to ePacket for some routes
```

### Regional Shipping Pricing Guide

**North America (US, CA):**
```
0-100g:  $2-4   (AliExpress Standard)
100-500g: $4-8  (ePacket preferred)
500g-2kg: $8-15 (AliExpress Premium or AliExpress Standard)
2kg+:     $20+  (DHL or sea freight for FBA)
```

**Western Europe (DE, FR, UK, ES, IT):**
```
0-100g:  $3-5
100-500g: $5-10
500g-2kg: $10-18
UK-specific: Add customs declaration since Brexit
```

**Southeast Asia (TH, VN, MY, PH, ID):**
```
0-100g:  $1-3   (very competitive rates)
100-500g: $3-6
500g-2kg: $6-12
Best carriers: AliExpress Standard, Yanwen
```

**Australia & NZ:**
```
0-500g:  $4-8
500g-2kg: $8-15
Alternative: ePacket if available
```

**Brazil (complex):**
```
All weights: Add 20-40% for customs clearance
ePacket NOT available → use AliExpress Standard
Expect 30-60 day delivery due to customs
```

### Overseas Warehouse Strategy

**When to use overseas warehouse:**
- Selling in US/EU with high volume (>100 units/month per SKU)
- Customers complain about long delivery times
- Category where 1-2 week delivery is competitive expectation
- Products with high repeat purchase rate

**Overseas warehouse options:**
```
US warehouse (dropshipping warehouse):
- Pre-ship inventory to US warehouse
- Ship to buyer in 3-7 days from US
- Cost: $50-150/pallet/month storage + pick & pack
- Break-even: typically >200 units/month/SKU

EU warehouse (Germany most common):
- Covers most EU with 3-7 day shipping
- VAT registration may be required
- Cost: similar to US, €50-120/pallet/month

AliExpress Local Warehouse:
- AliExpress-managed overseas fulfillment
- Apply through Seller Center
- Simplest setup, less control over costs
```

### Shipping Template Configuration

**Standard US-focused template:**
```
Region          Method                  Cost        Processing Time
United States   ePacket                 Free        2-3 days
Canada          AliExpress Standard     $2.99       2-3 days
UK              AliExpress Standard     $1.99       2-3 days
Germany         AliExpress Standard     $1.99       2-3 days
France          AliExpress Standard     $1.99       2-3 days
Australia       AliExpress Standard     $3.99       2-3 days
Brazil          AliExpress Standard     $4.99       2-3 days
Rest of World   China Post              $3.99       3-5 days
```

**Premium global template (higher margin products):**
```
US/CA/AU:       AliExpress Premium      Free        1-2 days
EU (Top 5):     AliExpress Premium      Free        1-2 days
Rest of EU:     AliExpress Standard     Free        2-3 days
Asia:           AliExpress Standard     Free        2-3 days
LATAM:          AliExpress Standard     $2.99       3-5 days
Rest of World:  AliExpress Standard     $4.99       3-5 days
```

### Product Pricing Calculator

```
Selling price calculation:
1. Product cost (from supplier): $X
2. AliExpress commission (5-10%): $Y
3. Shipping cost (if free shipping): $Z
4. Target profit margin: $M

Formula: Price = (X + Z + M) / (1 - Commission%)
Example: ($5 + $4 + $3) / (1 - 0.08) = $13 / 0.92 = $14.13
Recommended list price: $14.99 (round up for psychological pricing)
```

### Seasonal Shipping Adjustments

**Chinese New Year (Jan-Feb):**
- Factories close 2-4 weeks → pre-stock 4-6 weeks of inventory
- Announce extended processing time (5-7 days)
- Consider overseas warehouse for continuity

**Peak season (Oct-Dec)**:
- Shipping times increase by 30-50%
- Add 7-10 days to estimated delivery in templates
- Use premium carriers to differentiate
- Raise prices 10-15% to cover logistics surge

**Covid-like disruptions / force majeure:**
- Keep buyers updated on delays proactively
- Offer partial refund for extreme delays
- Document all shipping exceptions

## Workspace

Creates `~/aliexpress-logistics/` containing:
- `templates/` — shipping templates per product category
- `pricing/` — price calculations by region
- `warehouses/` — overseas warehouse research
- `carriers/` — carrier comparison data
- `reports/` — logistics strategy reports

## Output Format

Every shipping optimization outputs:
1. **Recommended Shipping Template** — region-by-region carrier and cost table
2. **Pricing Recommendation** — product price by market with margin calculation
3. **Carrier Comparison** — top 3 carrier options for your main markets
4. **Overseas Warehouse Assessment** — ROI analysis for warehousing decision
5. **Delivery Time Estimate** — realistic delivery ranges by region
6. **Seasonal Calendar** — upcoming peaks requiring template adjustments
7. **Cost Savings Opportunities** — specific ways to reduce logistics costs
