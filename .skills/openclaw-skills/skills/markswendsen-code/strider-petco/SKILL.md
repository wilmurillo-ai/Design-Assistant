---
name: strider-petco
description: Shop Petco pet supplies via Strider Labs MCP connector. Search pet food, toys, and supplies. Schedule grooming, vet services, and order medications for dogs, cats, and other pets.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "retail"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Petco Connector

MCP connector for Petco pet supplies and services. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-petco
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "petco": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-petco"]
    }
  }
}
```

## Available Tools

### petco.search_products
Search Petco's product catalog.

**Input Schema:**
```json
{
  "query": "string",
  "pet_type": "dog | cat | fish | bird | reptile | small_pet",
  "category": "food | treats | toys | health | grooming",
  "brand": "string (optional)"
}
```

**Output:**
```json
{
  "products": [{
    "sku": "12345",
    "name": "Blue Buffalo Life Protection",
    "price": 54.99,
    "rating": 4.8,
    "weight": "30 lbs",
    "autoship_price": 49.49,
    "in_stock": true
  }]
}
```

### petco.schedule_grooming
Book a grooming appointment.

**Input Schema:**
```json
{
  "pet_name": "string",
  "pet_type": "dog | cat",
  "service": "bath | full_groom | nail_trim",
  "store_id": "string",
  "date": "string (YYYY-MM-DD)",
  "time_preference": "morning | afternoon"
}
```

### petco.schedule_vet
Book a Vetco clinic appointment.

**Input Schema:**
```json
{
  "pet_name": "string",
  "service": "vaccination | wellness | microchip",
  "store_id": "string",
  "date": "string"
}
```

### petco.refill_prescription
Refill pet medication.

**Input Schema:**
```json
{
  "prescription_id": "string",
  "quantity": "number"
}
```

### petco.add_to_cart
Add items to shopping cart.

### petco.setup_autoship
Set up recurring delivery.

**Input Schema:**
```json
{
  "sku": "string",
  "frequency_weeks": "number"
}
```

## Authentication

First use triggers OAuth authorization:
1. User redirected to Petco login
2. Pet profiles synced automatically
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Order pet food:**
```
Order 30 lbs of Blue Buffalo dog food from Petco
```

**Book grooming:**
```
Schedule a dog grooming appointment this Saturday
```

**Set up autoship:**
```
Set up monthly delivery of cat litter from Petco
```

**Find products:**
```
Find grain-free dog treats at Petco under $20
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_APPOINTMENTS | No slots available | Try different date |
| PRESCRIPTION_EXPIRED | Rx needs renewal | Contact vet |
| OUT_OF_STOCK | Item unavailable | Check alternatives |

## Use Cases

- Pet food orders: buy and autoship pet food
- Grooming: schedule baths, haircuts, nail trims
- Vet services: vaccinations and wellness visits
- Pharmacy: refill pet medications
- Supplies: order toys, beds, crates, and accessories

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-petco
- Strider Labs: https://striderlabs.ai
