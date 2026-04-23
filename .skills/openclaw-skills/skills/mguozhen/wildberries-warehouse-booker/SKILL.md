---
name: wildberries-warehouse-booker
description: "Wildberries smart warehouse booking and logistics management agent. Solve WB warehouse appointment scarcity with intelligent monitoring, auto-submit strategies, and fulfillment efficiency optimization for Wildberries sellers. Triggers: wildberries warehouse, wb booking, wildberries fulfillment, wb склад, wildberries logistics, wb поставка, warehouse appointment, wb fbo, wildberries supply, wildberries inventory, wb supplier, russian marketplace logistics"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/wildberries-warehouse-booker
---

# Wildberries Warehouse Booker

Solve the WB warehouse appointment challenge — intelligent monitoring strategies, auto-booking tactics, fulfillment timing optimization, and logistics management for Wildberries sellers.

## Commands

```
wb book <warehouse> <date>        # warehouse booking strategy guide
wb monitor                        # set up booking monitoring plan
wb supply plan <inventory>        # create supply delivery plan
wb warehouse choose               # compare WB warehouses by strategy
wb timing                         # optimal booking time windows
wb inventory check                # inventory level analysis and restock planning
wb coefficient <warehouse>        # analyze acceptance coefficient strategy
wb logistics plan <product>       # end-to-end logistics plan
wb emergency <situation>          # emergency restock strategy
wb report <period>                # fulfillment performance report
```

## What Data to Provide

- **Your warehouse preference** — which WB warehouse(s) you ship to
- **Inventory data** — current stock levels at each warehouse
- **Sales velocity** — daily sales per SKU
- **Supply lead time** — how long from order to WB warehouse delivery
- **Coefficient status** — current acceptance coefficients for target warehouses

## WB Warehouse Framework

### Wildberries Warehouse Network

Major WB warehouses:
```
Warehouse       Location        Characteristics
Коледино        Moscow region   Largest, most competitive to book
Подольск        Moscow region   Alternative to Коледино
Казань          Kazan           Regional, less competition
Екатеринбург    Yekaterinburg   Ural region coverage
Краснодар       Krasnodar       South Russia
Новосибирск     Novosibirsk     Siberia region
Электросталь    Moscow region   Growing capacity
```

### The Warehouse Booking Challenge

**Why booking is difficult:**
- WB warehouse capacity released in limited daily slots
- Popular warehouses (Коледино) open slots at unpredictable times
- Sellers must compete for available slots
- "Acceptance coefficient" system limits which products can be delivered
- Slot availability often announced with 1-3 days notice

**Acceptance coefficient system:**
- Coefficient 1: Normal acceptance fee
- Coefficient 2-5: Premium fee required (WB charges extra)
- Coefficient 0: Free acceptance — grab immediately!
- High coefficient: Consider alternative warehouse

### Booking Strategy

**Monitoring approach:**
```
1. Check WB Seller Dashboard: "Поставки" → "Принять поставку"
2. Best checking times: 07:00-09:00, 12:00-14:00, 20:00-22:00 Moscow time
3. New slots often released: Monday and Wednesday mornings
4. Set up Telegram notifications if WB bot available
5. Check multiple warehouses simultaneously (not just your preferred)
```

**Booking decision tree:**
```
Available slot detected?
├── Coefficient = 0: BOOK IMMEDIATELY regardless of timing
├── Coefficient 1: Book if inventory needed within 3 weeks
├── Coefficient 2-3: Book if critically low (< 7 days stock)
└── Coefficient 4-5: Decline unless emergency (cost prohibitive)
```

**Multi-warehouse diversification:**
```
Instead of: 100% to Коледино
Consider:   60% Коледино + 40% Подольск or Казань

Benefits:
- Reduces dependency on single warehouse
- Faster slots available at regional warehouses
- Geographic distribution improves delivery speed to buyers
- Regional warehouses have lower coefficient fees
```

### Supply Planning

**Reorder timeline calculation:**
```
Safety stock = Daily sales × Delivery lead time × Safety factor
Safety factor = 1.5 (recommended for WB booking uncertainty)

Example:
Daily sales: 50 units
Lead time: 21 days (production 14 + transit 7)
Safety factor: 1.5
Safety stock = 50 × 21 × 1.5 = 1,575 units

Reorder when: Inventory at WB = Safety stock + Units in transit
= 1,575 + 0 = 1,575 units trigger point
```

**Booking frequency strategy:**
```
Volume scenario       Recommended booking frequency
High volume (>200/day): Every 2 weeks — maintain 30-day supply
Medium (50-200/day):    Every 3-4 weeks — maintain 45-day supply
Low (<50/day):          Monthly — maintain 60-day supply
```

### Shipment Preparation Checklist

```
BEFORE BOOKING
[ ] Check coefficient for target warehouse (aim ≤2)
[ ] Confirm inventory ready for delivery date
[ ] Barcode all items (WB barcode requirements)
[ ] Package per WB standards (box sizes, weight limits)
[ ] Prepare shipment list in WB system

DURING BOOKING PROCESS
[ ] Book slot with buffer (at least 3 days before needed)
[ ] Complete supply order in WB system
[ ] Print supply stickers and route sheet
[ ] Schedule logistics carrier for pickup

ON DELIVERY DAY
[ ] Confirm carrier booked and confirmed
[ ] Have all documents ready (supply order, route sheet)
[ ] Arrive at warehouse at appointed time (penalties for no-show)
[ ] Get acceptance confirmation and slip number
```

### Emergency Restock Strategy

When facing stockout risk:
```
Priority 1: Check coefficient 0 warehouses immediately — book any available
Priority 2: Use FBS (seller ships to buyer) temporarily while waiting for FBO slot
Priority 3: Split shipment — send available inventory now, rest when slot opens
Priority 4: Express delivery service to WB (more expensive but fast)
Priority 5: Reduce ad spend to slow sales velocity while restocking
```

**FBS backup plan:**
- Activate FBS (seller-fulfilled) for affected SKUs
- Set processing time to 1-2 days
- Maintain small FBS stock at your location as buffer
- Deactivate FBS once FBO stock replenished

### Inventory Level Optimization

**Target inventory levels:**
```
Green zone: 30-45 days of stock at warehouse
Yellow zone: 15-30 days of stock (initiate restock)
Red zone: 7-15 days (emergency booking needed)
Critical: <7 days (out-of-stock risk, ranking damage)
```

**Out-of-stock impact on WB:**
- Ranking drops significantly after 24-48 hours out of stock
- Recovery time: 2-4 weeks to return to previous position
- Financial impact: Lost sales + ranking recovery cost in ads

### Logistics Carrier Options

For delivering to WB warehouses:
```
Carrier         Notes
ТК Деловые Линии    Reliable, major carrier
СДЭК            Good network, tracking
ПЭК             Large freight specialist
Boxberry        Good for smaller shipments
Direct delivery Own car — cheapest but limited
```

**Carrier selection by volume:**
- <500 kg per delivery: СДЭК or Boxberry
- 500-3000 kg: Деловые Линии or ПЭК
- >3000 kg: Direct negotiation with major carriers

## Workspace

Creates `~/wb-logistics/` containing:
- `bookings/` — booking history and tracking
- `inventory/` — stock level monitoring
- `supply-plans/` — delivery schedule
- `warehouses/` — warehouse comparison data
- `reports/` — fulfillment performance reports

## Output Format

Every logistics plan outputs:
1. **Inventory Status** — current days of stock by warehouse
2. **Booking Recommendation** — when and where to book next supply
3. **Coefficient Analysis** — current fees at each warehouse
4. **Supply Schedule** — next 3 delivery dates with quantities
5. **Emergency Plan** — what to do if out-of-stock imminent
6. **Checklist** — pre-delivery preparation steps
7. **Cost Estimate** — logistics cost for planned supply
