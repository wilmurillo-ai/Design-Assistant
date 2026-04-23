---
name: strider-homedepot
description: Shop Home Depot via Strider Labs MCP connector. Search products, check inventory, order for pickup or delivery, schedule installations. Complete autonomous home improvement shopping for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "commerce"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Home Depot Connector

MCP connector for shopping at Home Depot — search products, check store inventory, order for pickup or delivery, and schedule professional installations. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-homedepot
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "homedepot": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-homedepot"]
    }
  }
}
```

## Available Tools

### homedepot.search_products
Search Home Depot's catalog.

**Input Schema:**
```json
{
  "query": "string",
  "category": "string (optional: lumber, plumbing, electrical, etc.)",
  "brand": "string (optional)",
  "store_id": "string (optional: for local inventory)"
}
```

**Output:**
```json
{
  "products": [{
    "sku": "string",
    "name": "string",
    "price": "number",
    "rating": "number",
    "in_stock": "boolean",
    "aisle_location": "string",
    "store_quantity": "number"
  }]
}
```

### homedepot.check_inventory
Check real-time inventory at specific store.

### homedepot.add_to_cart
Add products to cart.

### homedepot.checkout
Complete order.

**Input Schema:**
```json
{
  "fulfillment": "string (pickup, delivery, ship_to_store)",
  "store_id": "string (for pickup)",
  "delivery_address": "object (for delivery)"
}
```

### homedepot.rent_tools
Rent tools and equipment.

**Input Schema:**
```json
{
  "tool_id": "string",
  "duration": "string (4_hour, day, week)",
  "store_id": "string"
}
```

### homedepot.schedule_installation
Schedule professional installation service.

### homedepot.find_stores
Find nearby Home Depot stores.

### homedepot.get_pro_rewards
Check Pro Xtra rewards for contractors.

## Authentication

First use triggers OAuth. Pro Xtra benefits apply for registered pros. Tokens stored encrypted per-user.

## Usage Examples

**Find products:**
```
Search Home Depot for 2x4 lumber and check if it's in stock at my local store
```

**Project supplies:**
```
Order everything I need to install a ceiling fan from Home Depot
```

**Tool rental:**
```
Rent a power washer from Home Depot for this weekend
```

**Installation:**
```
Schedule Home Depot installation for the new dishwasher I bought
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| OUT_OF_STOCK | Not available | Check nearby stores |
| RENTAL_UNAVAILABLE | Tool not available | Suggest alternatives |
| DELIVERY_UNAVAILABLE | Can't deliver | Offer pickup |

## Use Cases

- DIY projects: lumber, tools, supplies
- Home repair: plumbing, electrical, hardware
- Tool rental: occasional-use equipment
- Pro purchasing: bulk ordering for contractors

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-homedepot
- Strider Labs: https://striderlabs.ai
