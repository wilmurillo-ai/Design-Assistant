---
name: strider-wholefoods
description: Shop Whole Foods via Strider Labs MCP connector. Search organic products, check store inventory, order groceries for pickup or delivery via Amazon Prime.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "grocery"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Whole Foods Connector

MCP connector for Whole Foods Market shopping. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-wholefoods
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "wholefoods": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-wholefoods"]
    }
  }
}
```

## Available Tools

### wholefoods.search_products
Search Whole Foods product catalog.

**Input Schema:**
```json
{
  "query": "string",
  "category": "produce | meat | seafood | bakery | deli | dairy | frozen (optional)",
  "dietary": ["organic", "vegan", "gluten-free", "non-gmo"],
  "store_id": "string (optional)"
}
```

**Output:**
```json
{
  "products": [{
    "sku": "wf789012",
    "name": "Organic Baby Spinach",
    "price": 5.99,
    "unit": "5 oz",
    "prime_price": 4.99,
    "organic": true,
    "local": false,
    "in_stock": true
  }]
}
```

### wholefoods.find_stores
Find nearby Whole Foods locations.

**Input Schema:**
```json
{
  "address": "string",
  "radius_miles": "number (optional)"
}
```

### wholefoods.add_to_cart
Add item to cart for pickup or delivery.

**Input Schema:**
```json
{
  "sku": "string",
  "quantity": "number",
  "store_id": "string"
}
```

### wholefoods.place_order
Complete order for pickup or delivery.

**Input Schema:**
```json
{
  "order_type": "pickup | delivery",
  "store_id": "string",
  "delivery_address": "object (for delivery)",
  "time_slot": "string"
}
```

### wholefoods.get_prime_deals
List current Amazon Prime member deals.

### wholefoods.get_weekly_sales
Get weekly sales and specials.

## Authentication

First use triggers OAuth authorization:
1. User logs in with Amazon account
2. Prime membership detected for discounts
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Search products:**
```
Find organic eggs at Whole Foods
```

**Order groceries:**
```
Order salmon and vegetables from Whole Foods for delivery tomorrow
```

**Prime deals:**
```
What Prime member deals does Whole Foods have this week?
```

**Check availability:**
```
Is the grass-fed beef in stock at my local Whole Foods?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_SLOTS | No delivery/pickup times | Try different day |
| OUT_OF_STOCK | Item unavailable | Check alternatives |
| PRIME_REQUIRED | Need Prime for deal | Sign up or pay regular price |

## Use Cases

- Organic shopping: find organic and natural products
- Prime discounts: get exclusive member pricing
- Grocery delivery: order for same-day delivery
- Meal planning: shop by category and dietary needs
- Local products: find locally sourced items

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-wholefoods
- Strider Labs: https://striderlabs.ai
