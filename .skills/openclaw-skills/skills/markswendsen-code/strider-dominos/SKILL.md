---
name: strider-dominos
description: Order pizza from Domino's, customize toppings, track delivery, and save favorite orders via Strider Labs MCP connector. Browse menu, apply coupons, and get real-time delivery updates.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Domino's Connector

MCP connector for ordering pizza from Domino's with full menu access and delivery tracking. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-dominos
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "dominos": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-dominos"]
    }
  }
}
```

## Available Tools

### dominos.find_stores
Find nearby Domino's locations.

**Input Schema:**
```json
{
  "address": "string",
  "delivery": "boolean (true for delivery, false for carryout)"
}
```

### dominos.get_menu
Get full menu for a store including prices and available items.

**Input Schema:**
```json
{
  "store_id": "string"
}
```

### dominos.build_pizza
Build a custom pizza with toppings.

**Input Schema:**
```json
{
  "size": "small | medium | large | xlarge",
  "crust": "hand_tossed | thin | pan | brooklyn",
  "toppings": ["pepperoni", "mushrooms", "extra_cheese"],
  "sauce": "tomato | alfredo | bbq | garlic_parmesan"
}
```

### dominos.place_order
Place an order for delivery or carryout.

**Input Schema:**
```json
{
  "store_id": "string",
  "items": [{"product_code": "string", "quantity": "number"}],
  "delivery_address": "string (optional for carryout)",
  "payment_method": "card | cash",
  "tip_amount": "number"
}
```

### dominos.track_order
Track an active order with real-time updates.

**Input Schema:**
```json
{
  "order_id": "string"
}
```

**Output:**
```json
{
  "status": "prep | oven | quality_check | out_for_delivery",
  "estimated_delivery": "2024-03-22T19:30:00",
  "driver_name": "string"
}
```

### dominos.get_coupons
Get available coupons and deals.

### dominos.reorder_favorite
Reorder a saved favorite order.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Domino's to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

No API key required — connector manages OAuth flow.

## Usage Examples

**Order a pizza:**
```
Order a large pepperoni pizza from Domino's for delivery to 123 Main St
```

**Track delivery:**
```
Where's my Domino's order?
```

**Custom pizza:**
```
Build a medium thin crust pizza with mushrooms, olives, and extra cheese from Domino's
```

**Find deals:**
```
What coupons are available at my local Domino's?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| STORE_CLOSED | Store not accepting orders | Try different store or time |
| DELIVERY_UNAVAILABLE | Address out of range | Try carryout instead |
| ITEM_UNAVAILABLE | Menu item not available | Check current menu |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Pizza ordering: browse menu and place orders
- Delivery tracking: real-time order status updates
- Deal hunting: find and apply coupons
- Repeat orders: quickly reorder favorites
- Group orders: build complex multi-item orders

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-dominos
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
