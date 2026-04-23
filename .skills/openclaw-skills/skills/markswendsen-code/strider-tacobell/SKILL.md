---
name: strider-tacobell
description: Order from Taco Bell via Strider Labs MCP connector. Browse menu, customize items, use rewards, and schedule pickup or delivery for tacos, burritos, and more.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Taco Bell Connector

MCP connector for Taco Bell ordering. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-tacobell
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "tacobell": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-tacobell"]
    }
  }
}
```

## Available Tools

### tacobell.get_menu
Get menu for a location.

**Input Schema:**
```json
{
  "location_id": "string (optional)",
  "category": "tacos | burritos | quesadillas | bowls | nachos | combos | breakfast (optional)"
}
```

**Output:**
```json
{
  "items": [{
    "item_id": "crunchy-taco",
    "name": "Crunchy Taco",
    "price": 1.99,
    "calories": 170,
    "customizations": ["no lettuce", "add sour cream", "fresco style"]
  }]
}
```

### tacobell.find_nearby
Find Taco Bell locations.

**Input Schema:**
```json
{
  "address": "string",
  "radius_miles": "number (optional)"
}
```

### tacobell.add_to_order
Add item to order.

**Input Schema:**
```json
{
  "item_id": "string",
  "quantity": "number",
  "customizations": ["add nacho cheese", "grilled"]
}
```

### tacobell.apply_reward
Redeem Taco Bell Rewards.

**Input Schema:**
```json
{
  "reward_id": "string"
}
```

### tacobell.place_order
Submit order.

**Input Schema:**
```json
{
  "order_type": "pickup | delivery | drive_thru",
  "location_id": "string",
  "scheduled_time": "string (optional)"
}
```

### tacobell.get_rewards
Check Taco Bell Rewards balance.

## Authentication

First use triggers OAuth authorization:
1. User redirected to Taco Bell app login
2. Rewards linked automatically
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Order tacos:**
```
Order 3 crunchy tacos and a Baja Blast from Taco Bell
```

**Use rewards:**
```
What Taco Bell rewards can I redeem?
```

**Late night:**
```
Find a Taco Bell open now for drive-thru
```

**Customize order:**
```
Order a Crunchwrap Supreme with no tomatoes and extra sour cream
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| LOCATION_CLOSED | Store not open | Find 24-hour location |
| ITEM_UNAVAILABLE | Menu item out | Choose alternative |
| REWARD_UNAVAILABLE | Can't apply reward | Check eligibility |

## Use Cases

- Quick meals: fast food orders
- Late night food: 24-hour location ordering
- Customization: build custom items
- Rewards: earn and redeem points
- Group orders: large orders for multiple people

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-tacobell
- Strider Labs: https://striderlabs.ai
