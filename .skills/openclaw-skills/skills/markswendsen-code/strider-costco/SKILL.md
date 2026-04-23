---
name: strider-costco
description: Shop Costco via Strider Labs MCP connector. Search bulk products, check warehouse inventory, manage cart, order delivery or same-day via Instacart. Complete autonomous wholesale shopping for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "commerce"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Costco Connector

MCP connector for shopping at Costco — search bulk products, check warehouse inventory, manage cart, and order for delivery or same-day via Instacart. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-costco
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "costco": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-costco"]
    }
  }
}
```

## Available Tools

### costco.search_products
Search Costco's catalog by keyword, category, or brand.

**Input Schema:**
```json
{
  "query": "string (search terms)",
  "category": "string (optional: grocery, electronics, furniture, etc.)",
  "warehouse_id": "string (optional: for local inventory)",
  "online_only": "boolean (optional: filter to costco.com items)"
}
```

**Output:**
```json
{
  "products": [{
    "id": "string",
    "name": "string",
    "price": "number",
    "unit_price": "string (price per unit/oz)",
    "member_only": "boolean",
    "warehouse_available": "boolean",
    "delivery_available": "boolean",
    "same_day_available": "boolean"
  }]
}
```

### costco.add_to_cart
Add products to shopping cart with specified quantity.

### costco.get_cart
Retrieve current cart contents and totals.

### costco.checkout
Complete purchase with membership and payment method.

**Input Schema:**
```json
{
  "fulfillment_type": "string (delivery, same_day)",
  "delivery_address": "object",
  "payment_method_id": "string"
}
```

### costco.check_warehouse_inventory
Check real-time inventory at a specific warehouse.

### costco.find_warehouses
Find nearby Costco warehouses by location.

### costco.get_deals
Get current Costco deals and member-only pricing.

## Authentication

Requires Costco membership. First use triggers OAuth authorization flow:
1. User is redirected to Costco to authorize
2. Membership verified and tokens stored
3. Automatic refresh handles token expiration

## Usage Examples

**Bulk pantry restock:**
```
Order from Costco: 2 cases of sparkling water, olive oil, and a bag of organic quinoa
```

**Check warehouse stock:**
```
Is the Kirkland organic peanut butter in stock at my local Costco warehouse?
```

**Same-day delivery:**
```
Order Costco groceries for same-day delivery: rotisserie chicken, croissants, berries, and a case of eggs
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| MEMBERSHIP_REQUIRED | Need valid membership | Prompt to verify |
| OUT_OF_STOCK | Item unavailable | Suggest alternatives |
| MIN_ORDER | Below minimum | Add more items |

## Use Cases

- Bulk household supplies: toilet paper, paper towels, cleaning supplies
- Pantry staples: rice, beans, oils, snacks in bulk quantities
- Office supplies: bulk ordering for home office
- Party supplies: large-format food and beverages

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-costco
- Strider Labs: https://striderlabs.ai
