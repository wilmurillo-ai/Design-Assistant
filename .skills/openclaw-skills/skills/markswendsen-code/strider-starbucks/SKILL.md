---
name: strider-starbucks
description: Order from Starbucks via Strider Labs MCP connector. Customize drinks, earn Stars, mobile order ahead, check store wait times. Complete autonomous coffee ordering for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Starbucks Connector

MCP connector for ordering from Starbucks — customize drinks, manage favorites, earn Rewards Stars, and mobile order ahead. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-starbucks
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "starbucks": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-starbucks"]
    }
  }
}
```

## Available Tools

### starbucks.get_menu
Get full menu with customization options for a store.

**Input Schema:**
```json
{
  "store_id": "string (optional: for local menu)",
  "category": "string (optional: hot_drinks, cold_drinks, food, etc.)"
}
```

**Output:**
```json
{
  "items": [{
    "id": "string",
    "name": "string",
    "price": "number",
    "category": "string",
    "customizations": [{
      "name": "string",
      "options": ["string"],
      "price_modifier": "number"
    }]
  }]
}
```

### starbucks.create_order
Create an order with customized items.

**Input Schema:**
```json
{
  "store_id": "string",
  "items": [{
    "item_id": "string",
    "quantity": "number",
    "customizations": {
      "size": "string (tall, grande, venti)",
      "milk": "string (whole, oat, almond, etc.)",
      "shots": "number",
      "syrup": "string",
      "temperature": "string (hot, iced)"
    }
  }]
}
```

### starbucks.submit_order
Submit order for mobile order ahead.

**Input Schema:**
```json
{
  "order_id": "string",
  "pickup_type": "string (instore, drive_through, curbside)",
  "payment_method": "string (card, rewards_balance)"
}
```

### starbucks.get_rewards
Get current Stars balance and available rewards.

### starbucks.redeem_reward
Redeem Stars for a free item.

### starbucks.find_stores
Find nearby Starbucks with wait times.

**Output:**
```json
{
  "stores": [{
    "id": "string",
    "name": "string",
    "address": "string",
    "distance": "number (miles)",
    "wait_time_minutes": "number",
    "features": ["drive_through", "mobile_order", "wifi"]
  }]
}
```

### starbucks.get_favorites
Get saved favorite orders for quick reordering.

## Authentication

First use triggers OAuth with Starbucks Rewards account. Stars earned automatically on all orders. Tokens stored encrypted per-user.

## Usage Examples

**Morning order:**
```
Order my usual from Starbucks: a venti iced oat milk latte with an extra shot
```

**Custom drink:**
```
Order a grande caramel macchiato with almond milk, extra caramel drizzle, and light ice from the nearest Starbucks
```

**Quick reorder:**
```
Reorder my favorite Starbucks drink at the store with the shortest wait time
```

**Check rewards:**
```
How many Starbucks Stars do I have? Can I get a free drink?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| STORE_CLOSED | Store not open | Suggest nearby open store |
| ITEM_UNAVAILABLE | Item out of stock | Suggest alternatives |
| INSUFFICIENT_STARS | Not enough rewards | Pay with card |

## Use Cases

- Daily coffee routine: automate morning orders
- Custom drinks: save complex customizations
- Rewards optimization: track Stars and redeem rewards
- Meeting prep: order for a group ahead of time

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-starbucks
- Strider Labs: https://striderlabs.ai
