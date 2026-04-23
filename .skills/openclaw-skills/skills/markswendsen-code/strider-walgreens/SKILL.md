---
name: strider-walgreens
description: Order from Walgreens via Strider Labs MCP connector. Refill prescriptions, shop health products, earn myWalgreens rewards, schedule vaccinations. Complete autonomous pharmacy management for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "health"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Walgreens Connector

MCP connector for Walgreens — refill prescriptions, shop health and beauty products, earn myWalgreens rewards, and schedule vaccinations. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-walgreens
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "walgreens": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-walgreens"]
    }
  }
}
```

## Available Tools

### walgreens.get_prescriptions
Get list of prescriptions and refill status.

**Output:**
```json
{
  "prescriptions": [{
    "rx_number": "string",
    "medication": "string",
    "dosage": "string",
    "quantity": "number",
    "refills_remaining": "number",
    "last_filled": "string (ISO date)",
    "ready_for_refill": "boolean",
    "auto_refill": "boolean"
  }]
}
```

### walgreens.refill_prescription
Request prescription refill.

**Input Schema:**
```json
{
  "rx_number": "string",
  "store_id": "string (optional)",
  "delivery_option": "string (pickup, mail, same_day)"
}
```

### walgreens.check_refill_status
Check if prescription is ready.

### walgreens.search_products
Search Walgreens products.

**Input Schema:**
```json
{
  "query": "string",
  "category": "string (optional)",
  "brand": "string (optional)"
}
```

### walgreens.add_to_cart
Add products to cart.

### walgreens.checkout
Complete order.

**Input Schema:**
```json
{
  "fulfillment": "string (pickup, delivery, same_day)",
  "store_id": "string (for pickup)",
  "use_rewards": "boolean"
}
```

### walgreens.get_rewards
Check myWalgreens Cash rewards balance.

**Output:**
```json
{
  "cash_balance": "number",
  "points_earned_ytd": "number",
  "available_offers": "number"
}
```

### walgreens.clip_coupons
Clip digital coupons to myWalgreens account.

### walgreens.schedule_vaccination
Schedule immunizations.

### walgreens.find_stores
Find nearby Walgreens locations.

## Authentication

First use triggers OAuth with Walgreens.com account. myWalgreens linked automatically. Tokens stored encrypted per-user.

## Usage Examples

**Refill medication:**
```
Refill my prescription at Walgreens with same-day delivery
```

**Check status:**
```
Is my Walgreens prescription ready?
```

**Shop products:**
```
Order sunscreen and allergy medicine from Walgreens
```

**Use rewards:**
```
What's my Walgreens Cash balance? Apply it to my order.
```

**Schedule vaccination:**
```
Schedule a COVID booster at Walgreens for tomorrow afternoon
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_REFILLS | No refills remaining | Contact doctor |
| SAME_DAY_UNAVAILABLE | No same-day slots | Offer standard delivery |
| INSURANCE_ISSUE | Needs attention | Visit pharmacy |

## Use Cases

- Prescription management: refill and track medications
- Health shopping: OTC medicines, vitamins, personal care
- Same-day delivery: urgent health items
- Vaccination scheduling: flu, COVID, shingles, etc.

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-walgreens
- Strider Labs: https://striderlabs.ai
