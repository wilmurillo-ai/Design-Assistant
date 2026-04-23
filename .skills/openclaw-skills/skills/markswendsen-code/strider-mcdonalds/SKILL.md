---
name: strider-mcdonalds
description: Order from McDonald's via Strider Labs MCP connector. Build custom orders, earn MyMcDonald's Rewards, mobile order ahead for pickup or delivery. Complete autonomous fast food ordering for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider McDonald's Connector

MCP connector for ordering from McDonald's — browse the menu, customize orders, earn MyMcDonald's Rewards points, and mobile order for pickup or McDelivery. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-mcdonalds
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "mcdonalds": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-mcdonalds"]
    }
  }
}
```

## Available Tools

### mcdonalds.get_menu
Get menu with prices and customization options.

**Input Schema:**
```json
{
  "store_id": "string (optional: for local pricing)",
  "category": "string (optional: breakfast, burgers, chicken, etc.)"
}
```

**Output:**
```json
{
  "items": [{
    "id": "string",
    "name": "string",
    "price": "number",
    "calories": "number",
    "customizations": ["string"],
    "available": "boolean"
  }]
}
```

### mcdonalds.add_to_cart
Add items with customizations.

**Input Schema:**
```json
{
  "item_id": "string",
  "quantity": "number",
  "customizations": {
    "size": "string (small, medium, large)",
    "add_ons": ["string"],
    "remove": ["string (no pickles, etc.)"]
  }
}
```

### mcdonalds.get_deals
Get current deals and offers.

### mcdonalds.apply_deal
Apply a deal or coupon to order.

### mcdonalds.submit_order
Submit order for pickup or delivery.

**Input Schema:**
```json
{
  "store_id": "string",
  "fulfillment": "string (pickup, drive_through, curbside, mcdelivery)",
  "payment_method_id": "string"
}
```

### mcdonalds.get_rewards
Check MyMcDonald's Rewards points.

### mcdonalds.redeem_reward
Redeem points for free items.

### mcdonalds.find_locations
Find nearby McDonald's restaurants.

## Authentication

First use triggers OAuth with McDonald's app account. Rewards earned automatically. Tokens stored encrypted per-user.

## Usage Examples

**Quick order:**
```
Order a Big Mac meal with medium fries and a Coke from McDonald's
```

**Breakfast:**
```
Order an Egg McMuffin and large coffee from McDonald's for pickup
```

**Use deals:**
```
What McDonald's deals are available? Apply the best one to my order.
```

**Rewards:**
```
How many McDonald's Rewards points do I have? Can I get free fries?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| STORE_CLOSED | Location not open | Find open location |
| ITEM_UNAVAILABLE | Out of item | Suggest alternatives |
| BREAKFAST_ENDED | No longer serving | Show regular menu |

## Use Cases

- Quick meals: fast ordering for pickup
- Breakfast runs: morning orders before work
- Deal hunting: maximize savings with app offers
- Family orders: large customized orders

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-mcdonalds
- Strider Labs: https://striderlabs.ai
