---
name: strider-traderjoes
description: Shop Trader Joe's via Strider Labs MCP connector. Search products, check store inventory, find seasonal items, and get product nutrition information.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "grocery"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Trader Joe's Connector

MCP connector for Trader Joe's product search and store info. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-traderjoes
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "traderjoes": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-traderjoes"]
    }
  }
}
```

## Available Tools

### traderjoes.search_products
Search Trader Joe's product catalog.

**Input Schema:**
```json
{
  "query": "string",
  "category": "frozen | fresh | snacks | beverages | wine | dairy (optional)",
  "dietary": ["vegan", "gluten-free", "organic"]
}
```

**Output:**
```json
{
  "products": [{
    "sku": "tj123456",
    "name": "Everything But the Bagel Seasoning",
    "price": 2.49,
    "category": "pantry",
    "seasonal": false,
    "rating": 4.9,
    "description": "Sesame, poppy, and garlic seasoning blend"
  }]
}
```

### traderjoes.find_stores
Find nearby Trader Joe's locations.

**Input Schema:**
```json
{
  "address": "string",
  "radius_miles": "number (optional)"
}
```

### traderjoes.get_product_details
Get detailed product info.

**Input Schema:**
```json
{
  "sku": "string"
}
```

### traderjoes.get_seasonal_items
List current seasonal and limited items.

### traderjoes.check_store_inventory
Check if product is in stock at a store.

**Input Schema:**
```json
{
  "sku": "string",
  "store_id": "string"
}
```

## Authentication

First use triggers OAuth authorization:
1. User logs in with Trader Joe's account
2. Tokens stored encrypted per-user
3. Favorites synced automatically

No API key required — connector manages OAuth flow.

## Usage Examples

**Search products:**
```
Find vegan snacks at Trader Joe's
```

**Seasonal items:**
```
What seasonal items does Trader Joe's have right now?
```

**Check inventory:**
```
Is the Everything Bagel Seasoning in stock at my local TJ's?
```

**Find stores:**
```
Where's the nearest Trader Joe's?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| PRODUCT_NOT_FOUND | Item doesn't exist | Search again |
| STORE_NOT_FOUND | Invalid store ID | Find stores first |
| SEASONAL_ENDED | Item no longer available | Check next season |

## Use Cases

- Product search: find TJ's specialty items
- Seasonal hunting: track limited-time products
- Shopping planning: check inventory before visiting
- Store locator: find nearby locations and hours
- Dietary filtering: find vegan, GF, or organic options

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-traderjoes
- Strider Labs: https://striderlabs.ai
