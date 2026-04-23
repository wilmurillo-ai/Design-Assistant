---
name: amazon-logistics-calculator
description: "Amazon FBA logistics cost calculator and shipping optimizer. Compare sea freight, air freight, and express courier costs. Calculate total landed cost including duties, VAT, and customs fees. Choose the optimal shipping method for your product and timeline. Triggers: logistics calculator, shipping cost, sea freight, air freight, fba shipping, landed cost, freight cost, amazon logistics, import duty, customs fee, shipping method, inbound shipping, freight forwarder, fba inbound, shipping optimizer, amazon shipping cost"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-logistics-calculator
---

# Amazon FBA Logistics Cost Calculator

Calculate the true landed cost for your FBA shipments. Compare sea, air, and express — pick the right method based on your margin, volume, and urgency.

## Commands

```
logistics calc                  # interactive shipping cost calculator
logistics compare [details]     # compare sea vs air vs express
logistics landed [product]      # full landed cost breakdown
logistics duty [product] [country]  # import duty & VAT calculator
logistics route [origin] [dest] # common shipping route details
logistics timeline              # shipping timeline comparison
logistics forwarder             # freight forwarder selection guide
logistics carton [dimensions]   # carton CBM and chargeable weight
logistics save [shipment]       # save shipment profile
```

## What Data to Provide

- **Product details** — dimensions (cm), weight (kg) per unit and per carton
- **Quantity** — total units to ship
- **Origin** — factory location (city/country)
- **Destination** — Amazon FBA warehouse country/region
- **Timeline** — how urgently do you need stock?
- **Product value** — for duty calculation

## Shipping Method Comparison

### Sea Freight (FCL / LCL)
| Type | When to Use | Transit Time | Cost Estimate |
|------|------------|-------------|--------------|
| FCL 20ft | >15 CBM, frequent shipper | 25–35 days | $1,500–$3,000/container |
| FCL 40ft | >28 CBM | 25–35 days | $2,500–$5,000/container |
| LCL | <15 CBM, small shipments | 35–45 days | $80–$150/CBM |

**Best for:** Large shipments, low-margin products, planned inventory restocks
**Avoid when:** Urgent, small shipment, or product is high value/low volume

### Air Freight
| Service | Transit Time | Cost Estimate |
|---------|-------------|--------------|
| Standard Air | 7–14 days | $4–$8/kg |
| Economy Air | 14–21 days | $2.5–$5/kg |

**Chargeable weight** = max(actual weight, volumetric weight)
Volumetric weight = L × W × H (cm) / 6,000

**Best for:** New product launches, seasonal restocks, high-value low-weight products
**Avoid when:** Heavy/bulky products, cost is main concern

### Express Courier (DHL/FedEx/UPS)
| Service | Transit Time | Cost Estimate |
|---------|-------------|--------------|
| DHL Express | 3–5 days | $8–$15/kg |
| FedEx International | 3–5 days | $8–$15/kg |
| UPS Worldwide | 3–5 days | $8–$15/kg |

**Best for:** Urgent stock-outs, samples, <50kg shipments
**Avoid when:** >100kg (air freight becomes cheaper)

## Landed Cost Formula

```
Product Cost (COGS)             = Unit cost × Quantity
+ Inbound Freight               = Shipping method cost
+ Customs Duty                  = Product value × Duty rate %
+ VAT / Import Tax              = (Product + Freight + Duty) × VAT rate %
+ Customs Broker Fee            = $150–$300 flat
+ Port/Handling Charges         = $50–$200
+ Inland Delivery (to FBA)      = $0.50–$2.00/carton
+ Amazon FBA Inbound Placement  = $0.27–$1.58/unit (2024 fee)
─────────────────────────────────────────────────────
Total Landed Cost               = Sum of all above
Landed Cost Per Unit            = Total ÷ Quantity
```

## Import Duty Rates (US HTS Common Categories)

| Product Category | HS Code Range | US Duty Rate |
|-----------------|---------------|-------------|
| Electronics | 8471–8529 | 0–3.7% |
| Clothing/Apparel | 6101–6217 | 12–32% |
| Footwear | 6401–6403 | 20–37.5% |
| Kitchen tools | 7323–7326 | 0–3.9% |
| Toys/Games | 9501–9508 | 0% |
| Sports equipment | 9506 | 4–5.1% |
| Furniture | 9401–9403 | 0–7% |
| Yoga mats/Fitness | 3926/9506 | 4–5.3% |

**Note:** Section 301 China tariffs add 7.5–25% on many Chinese-origin products. Always verify current rates at USITC.gov.

## Shipping Timeline Planner

Work backwards from your target in-stock date:

```
Target in-stock date:           [Date]
- FBA receiving buffer:         -7 days
- Port to FBA transit:          -3 days
- Customs clearance:            -5 days (sea) / -2 days (air)
- Transit time:                 -30 days (sea) / -10 days (air)
- Export customs/loading:       -5 days
- Production lead time:         -[X] days
────────────────────────────────────────
Order placement date:           [Calculated]
```

## Decision Framework: Which Method to Choose?

| Scenario | Recommended Method |
|----------|-------------------|
| First shipment, <200kg | Air freight or Express |
| Regular restock, >500kg, >30 days lead time | Sea LCL |
| Large seller, >15 CBM per shipment | Sea FCL |
| Running out of stock, <2 weeks | Express (DHL/FedEx) |
| High-value, low-weight product | Air freight |
| Low-margin, heavy product | Sea freight only |
| Seasonal launch (e.g., Christmas stock) | Sea: ship by Oct 1 |

## Carton Optimization Tips

- Keep carton weight under 23kg (FBA requirement, safety)
- Standard carton size for FBA: 60×40×40cm (1 CBM = 25 cartons)
- Maximize carton fill to minimize LCL costs
- Match master carton quantity to FBA box limits (no more than 150 units/box for standard)

## Freight Forwarder Selection Criteria

| Factor | What to Look For |
|--------|-----------------|
| Amazon FBA experience | Must know FBA label requirements |
| US customs broker | In-house or established partner |
| Tracking system | Real-time shipment visibility |
| Communication | English-speaking, responsive |
| Price | Get 3+ quotes, compare apples-to-apples |
| Insurance | Cargo insurance included or available |

**Recommended: Always get quotes from at least 3 forwarders**

## Output Format

1. **Cost Comparison Table** — sea vs. air vs. express for your shipment
2. **Recommended Method** — best option with reasoning
3. **Full Landed Cost Breakdown** — every line item to final unit cost
4. **Timeline** — ship-by date based on your target in-stock date
5. **Red Flags** — duty risks, seasonal surcharges, FBA restrictions
