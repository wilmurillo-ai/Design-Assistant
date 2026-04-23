---
name: strider-doordash
description: Order food delivery via DoorDash using Strider Labs MCP connector. Search restaurants, browse menus, place orders, and track deliveries.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider DoorDash Connector

MCP connector for ordering food delivery through DoorDash. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-doordash
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "doordash": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-doordash"]
    }
  }
}
```

## Available Tools

### doordash.search_restaurants
Search nearby restaurants by cuisine, rating, or delivery time.

**Input Schema:**
```json
{
  "address": "string (delivery address)",
  "cuisine": "string (optional, e.g., 'pizza', 'thai')",
  "sort_by": "rating | delivery_time | price (optional)"
}
```

**Output:**
```json
{
  "restaurants": [{
    "id": "string",
    "name": "string",
    "rating": "number",
    "delivery_fee": "number",
    "delivery_time_min": "number"
  }]
}
```

### doordash.get_menu
Retrieve a restaurant's full menu with prices and options.

### doordash.place_order
Submit an order for delivery.

**Input:**
```json
{
  "restaurant_id": "string",
  "items": [{"item_id": "string", "quantity": "number", "customizations": []}],
  "delivery_address": "string",
  "tip": "number (optional)"
}
```

### doordash.track_order
Get real-time status and driver location for an active order.

### doordash.get_order_history
Retrieve past orders for easy reordering.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to DoorDash to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

No API key required — connector manages OAuth flow.

## Usage Examples

**Find dinner options:**
```
Search DoorDash for Thai restaurants near 456 Oak Ave that deliver in under 30 minutes
```

**Reorder favorites:**
```
Order my usual from that Thai place I got last week on DoorDash
```

**Group ordering:**
```
What restaurants on DoorDash near the office can handle an order for 8 people?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| RATE_LIMITED | Too many requests | Retry after delay |
| SERVICE_UNAVAILABLE | DoorDash unavailable | Retry with backoff |
| INVALID_INPUT | Bad order data | Check item availability |

## Use Cases

- Lunch orders: quick delivery to home or office
- Group meals: coordinate orders for teams or parties
- Late night food: find what's open and delivering
- Meal planning: browse menus and save favorites

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-doordash
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
