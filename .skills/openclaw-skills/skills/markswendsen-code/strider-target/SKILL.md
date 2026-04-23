---
name: strider-target
description: Shop Target via Strider Labs MCP connector. Search products, check Circle offers, manage cart, order for same-day delivery or pickup. Complete autonomous shopping for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "commerce"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Target Connector

MCP connector for shopping at Target — search products, apply Circle offers, manage cart, and order for same-day delivery via Shipt or store pickup. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-target
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "target": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-target"]
    }
  }
}
```

## Available Tools

### target.search_products
Search Target's catalog by keyword, category, or brand.

**Input Schema:**
```json
{
  "query": "string (search terms)",
  "category": "string (optional: grocery, home, clothing, etc.)",
  "sort": "string (optional: price_low, price_high, rating, featured)",
  "store_id": "string (optional: for local inventory)"
}
```

**Output:**
```json
{
  "products": [{
    "id": "string",
    "name": "string",
    "price": "number",
    "sale_price": "number (if on sale)",
    "rating": "number",
    "circle_offer": "boolean",
    "in_stock": "boolean",
    "same_day_available": "boolean"
  }]
}
```

### target.add_to_cart
Add products to shopping cart with specified quantity.

### target.get_circle_offers
Get available Target Circle offers and deals.

**Output:**
```json
{
  "offers": [{
    "id": "string",
    "title": "string",
    "discount": "string",
    "category": "string",
    "expires": "string (ISO date)"
  }]
}
```

### target.apply_circle_offer
Apply a Circle offer to your account for automatic savings.

### target.checkout
Complete purchase with saved payment and RedCard if available.

**Input Schema:**
```json
{
  "fulfillment_type": "string (pickup, drive_up, same_day_delivery)",
  "store_id": "string (for pickup/drive-up)",
  "delivery_address": "object (for delivery)",
  "use_redcard": "boolean"
}
```

### target.find_stores
Find nearby Target stores by location.

## Authentication

First use triggers OAuth authorization flow with Target account. Tokens stored encrypted per-user with automatic refresh.

## Usage Examples

**Weekly essentials:**
```
Order my Target essentials: paper towels, laundry detergent, and dishwasher pods with same-day delivery
```

**Deal hunting:**
```
Show me Target Circle offers for baby products and add any good deals to my cart
```

**Drive-up order:**
```
Order these items from Target for drive-up pickup at my usual store: diapers size 4, baby wipes, formula
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| OUT_OF_STOCK | Item unavailable | Suggest alternatives |
| SHIPT_UNAVAILABLE | Same-day not available | Offer pickup instead |
| REDCARD_DECLINED | Payment issue | Try alternate payment |

## Use Cases

- Household essentials: automate restocking orders
- Same-day needs: urgent items via Shipt delivery
- Deal stacking: combine Circle offers with RedCard savings
- Drive-up convenience: quick pickups without leaving car

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-target
- Strider Labs: https://striderlabs.ai
