---
name: strider-panera
description: Order from Panera Bread via Strider Labs MCP connector. Browse menu, customize orders, schedule pickup or delivery, and manage Panera Rewards.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Panera Bread Connector

MCP connector for Panera Bread ordering. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-panera
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "panera": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-panera"]
    }
  }
}
```

## Available Tools

### panera.get_menu
Get menu for a location.

**Input Schema:**
```json
{
  "location_id": "string (optional, uses default)",
  "category": "breakfast | lunch | soups | salads | sandwiches | bakery (optional)"
}
```

**Output:**
```json
{
  "items": [{
    "item_id": "broccoli-cheddar-soup",
    "name": "Broccoli Cheddar Soup",
    "price": 7.99,
    "calories": 360,
    "description": "Creamy broccoli soup with cheddar cheese",
    "customizations": ["bread bowl", "cup", "bowl"]
  }]
}
```

### panera.search_menu
Search menu by keyword or dietary needs.

**Input Schema:**
```json
{
  "query": "string",
  "dietary": ["vegetarian", "low-sodium", "gluten-free"]
}
```

### panera.add_to_order
Add item to current order.

**Input Schema:**
```json
{
  "item_id": "string",
  "quantity": "number",
  "customizations": ["no onions", "extra cheese"]
}
```

### panera.place_order
Submit the order.

**Input Schema:**
```json
{
  "order_type": "pickup | delivery | rapid_pickup",
  "location_id": "string (for pickup)",
  "address": "object (for delivery)",
  "scheduled_time": "string (optional)"
}
```

### panera.get_rewards
Check Panera Rewards status.

### panera.get_order_status
Track current order.

## Authentication

First use triggers OAuth authorization:
1. User redirected to Panera login
2. Rewards account linked automatically
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Order soup:**
```
Order a bowl of broccoli cheddar soup from Panera for pickup
```

**Lunch order:**
```
Get me a Mediterranean veggie sandwich and a coffee for 12:30 pickup
```

**Check rewards:**
```
How many Panera rewards do I have?
```

**Find low-cal options:**
```
What's on the Panera menu under 500 calories?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| LOCATION_CLOSED | Store not open | Try different time/location |
| ITEM_UNAVAILABLE | Menu item out | Choose alternative |
| DELIVERY_UNAVAILABLE | Can't deliver | Try pickup |

## Use Cases

- Lunch ordering: quick meals for work
- Breakfast pickup: coffee and bakery items
- Catering: large orders for meetings
- Rewards tracking: monitor and redeem points
- Rapid Pickup: skip the line with mobile orders

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-panera
- Strider Labs: https://striderlabs.ai
