---
name: strider-chewy
description: Order pet supplies via Chewy using Strider Labs MCP connector. Shop food, treats, meds, set up Autoship for recurring deliveries. Complete autonomous pet care shopping for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "pets"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Chewy Connector

MCP connector for shopping at Chewy — order pet food, treats, medications, toys, and set up Autoship for automatic recurring deliveries. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-chewy
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "chewy": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-chewy"]
    }
  }
}
```

## Available Tools

### chewy.search_products
Search Chewy's catalog.

**Input Schema:**
```json
{
  "query": "string",
  "pet_type": "string (optional: dog, cat, fish, bird, etc.)",
  "category": "string (optional: food, treats, toys, pharmacy)",
  "brand": "string (optional)"
}
```

**Output:**
```json
{
  "products": [{
    "id": "string",
    "name": "string",
    "price": "number",
    "autoship_price": "number",
    "rating": "number",
    "review_count": "number",
    "in_stock": "boolean"
  }]
}
```

### chewy.add_to_cart
Add products to cart.

### chewy.checkout
Complete order.

**Input Schema:**
```json
{
  "fulfillment": "string (standard, express)",
  "add_to_autoship": "boolean (optional)"
}
```

### chewy.setup_autoship
Set up automatic recurring deliveries.

**Input Schema:**
```json
{
  "product_id": "string",
  "quantity": "number",
  "frequency_weeks": "number (1, 2, 4, 8, etc.)"
}
```

### chewy.get_autoship
Get current Autoship subscriptions.

### chewy.modify_autoship
Change frequency or skip next delivery.

### chewy.get_pet_profiles
Get saved pet profiles for personalized recommendations.

### chewy.request_vet_prescription
Request prescription approval for pharmacy items.

## Authentication

First use triggers OAuth. Pet profiles and Autoship managed per-account. Tokens stored encrypted per-user.

## Usage Examples

**Order food:**
```
Order a 30lb bag of Blue Buffalo dog food from Chewy
```

**Set up Autoship:**
```
Set up Chewy Autoship for cat litter every 4 weeks
```

**Pharmacy:**
```
Order my dog's flea medication from Chewy pharmacy
```

**Find treats:**
```
Search Chewy for grain-free dog treats under $20
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| OUT_OF_STOCK | Item unavailable | Suggest alternatives |
| RX_REQUIRED | Prescription needed | Contact vet |
| AUTOSHIP_EXISTS | Already subscribed | Offer to modify |

## Use Cases

- Pet food delivery: recurring food orders
- Pharmacy: prescription medications
- Supplies: litter, toys, accessories
- Autoship: never run out of essentials

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-chewy
- Strider Labs: https://striderlabs.ai
