---
name: strider-safeway
description: Shop Safeway via Strider Labs MCP connector. Search groceries, clip Just for U deals, order delivery or DriveUp & Go pickup. Complete autonomous grocery shopping for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "commerce"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Safeway Connector

MCP connector for shopping at Safeway — search products, clip Just for U personalized deals, and order for delivery or DriveUp & Go curbside pickup. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-safeway
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "safeway": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-safeway"]
    }
  }
}
```

## Available Tools

### safeway.search_products
Search Safeway's grocery catalog.

**Input Schema:**
```json
{
  "query": "string",
  "category": "string (optional: produce, dairy, meat, etc.)",
  "store_id": "string (optional)",
  "on_sale": "boolean (optional)"
}
```

**Output:**
```json
{
  "products": [{
    "id": "string",
    "name": "string",
    "price": "number",
    "sale_price": "number",
    "just_for_u": "boolean",
    "in_stock": "boolean",
    "aisle": "string"
  }]
}
```

### safeway.add_to_cart
Add products to shopping cart.

### safeway.get_just_for_u
Get personalized Just for U offers.

**Output:**
```json
{
  "offers": [{
    "description": "string",
    "discount": "string",
    "product": "string",
    "expires": "string"
  }]
}
```

### safeway.clip_offer
Clip a Just for U offer.

### safeway.checkout
Complete order for delivery or pickup.

**Input Schema:**
```json
{
  "fulfillment": "string (delivery, driveup)",
  "store_id": "string (for driveup)",
  "time_slot": "string (ISO datetime)"
}
```

### safeway.get_rewards
Check Safeway for U rewards balance.

### safeway.find_stores
Find nearby Safeway stores.

## Authentication

First use triggers OAuth. Just for U linked automatically. Tokens stored encrypted per-user.

## Usage Examples

**Weekly shopping:**
```
Order my weekly groceries from Safeway with DriveUp & Go pickup tomorrow
```

**Find deals:**
```
What Just for U offers do I have at Safeway? Clip the good ones.
```

**Search sales:**
```
Search Safeway for chicken that's on sale this week
```

**Schedule pickup:**
```
Schedule Safeway DriveUp & Go for Saturday at 10am
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| OUT_OF_STOCK | Item unavailable | Suggest alternatives |
| SLOT_UNAVAILABLE | Time not available | Offer other times |
| OFFER_EXPIRED | Deal no longer valid | Remove from cart |

## Use Cases

- Weekly grocery shopping: full cart orders
- Deal hunting: maximize Just for U savings
- Curbside pickup: convenient DriveUp & Go
- Delivery: same-day grocery delivery

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-safeway
- Strider Labs: https://striderlabs.ai
