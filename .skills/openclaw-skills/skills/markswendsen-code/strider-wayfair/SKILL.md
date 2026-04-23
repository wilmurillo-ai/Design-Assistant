---
name: strider-wayfair
description: Shop Wayfair furniture and home goods via Strider Labs MCP connector. Search products, compare prices, check delivery estimates, and track orders.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "retail"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Wayfair Connector

MCP connector for Wayfair home goods shopping. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-wayfair
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "wayfair": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-wayfair"]
    }
  }
}
```

## Available Tools

### wayfair.search_products
Search Wayfair's catalog.

**Input Schema:**
```json
{
  "query": "string",
  "category": "furniture | bedding | rugs | lighting | decor | outdoor",
  "price_min": "number (optional)",
  "price_max": "number (optional)",
  "style": "modern | traditional | farmhouse | industrial (optional)"
}
```

**Output:**
```json
{
  "products": [{
    "sku": "W001234567",
    "name": "Mid-Century Modern Sofa",
    "price": 899.99,
    "original_price": 1199.99,
    "rating": 4.6,
    "reviews_count": 1247,
    "delivery_estimate": "Mar 25-28",
    "free_shipping": true,
    "image_url": "https://..."
  }]
}
```

### wayfair.get_product_details
Get full product information.

**Input Schema:**
```json
{
  "sku": "string"
}
```

### wayfair.check_delivery
Get delivery estimate for your address.

**Input Schema:**
```json
{
  "sku": "string",
  "zip_code": "string"
}
```

### wayfair.add_to_cart
Add product to shopping cart.

### wayfair.apply_coupon
Apply promotional code.

### wayfair.track_order
Check order delivery status.

## Authentication

First use triggers OAuth authorization:
1. User redirected to Wayfair login
2. Tokens stored encrypted per-user
3. Order history synced automatically

No API key required — connector manages OAuth flow.

## Usage Examples

**Search furniture:**
```
Find modern sofas under $1000 on Wayfair
```

**Check delivery:**
```
When can Wayfair deliver this dining table to 90210?
```

**Compare products:**
```
Compare the top-rated queen beds on Wayfair
```

**Track order:**
```
Where is my Wayfair order?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| OUT_OF_STOCK | Item unavailable | Check similar items |
| DELIVERY_UNAVAILABLE | Can't ship to address | Try different product |
| COUPON_INVALID | Code doesn't work | Check terms |

## Use Cases

- Furniture shopping: sofas, beds, tables, chairs
- Home renovation: lighting, rugs, decor
- Room design: search by style and color
- Delivery tracking: monitor large item shipments
- Sales hunting: find discounts and clearance

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-wayfair
- Strider Labs: https://striderlabs.ai
