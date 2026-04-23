---
name: strider-kayak
description: Search travel via KAYAK using Strider Labs MCP connector. Compare flights, hotels, cars across providers. Find best prices with price alerts. Complete autonomous travel comparison for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider KAYAK Connector

MCP connector for travel comparison on KAYAK — search and compare flights, hotels, and car rentals across hundreds of providers to find the best prices. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-kayak
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "kayak": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-kayak"]
    }
  }
}
```

## Available Tools

### kayak.search_flights
Compare flights across airlines and OTAs.

**Input Schema:**
```json
{
  "origin": "string (airport code or city)",
  "destination": "string",
  "departure_date": "string (YYYY-MM-DD)",
  "return_date": "string (optional)",
  "passengers": "number",
  "cabin_class": "string (optional: economy, premium, business, first)",
  "nonstop_only": "boolean (optional)",
  "flexible_dates": "boolean (optional)"
}
```

**Output:**
```json
{
  "flights": [{
    "provider": "string",
    "airline": "string",
    "departure": "string",
    "arrival": "string",
    "duration": "string",
    "stops": "number",
    "price": "number",
    "book_url": "string"
  }],
  "price_prediction": "string (buy now, wait)"
}
```

### kayak.search_hotels
Compare hotel prices across booking sites.

**Input Schema:**
```json
{
  "location": "string",
  "check_in": "string (YYYY-MM-DD)",
  "check_out": "string (YYYY-MM-DD)",
  "guests": "number",
  "rooms": "number"
}
```

### kayak.search_cars
Compare rental car prices.

### kayak.get_price_forecast
Get prediction on whether to buy now or wait.

### kayak.set_price_alert
Set alert for when price drops.

**Input Schema:**
```json
{
  "search_type": "string (flight, hotel, car)",
  "search_params": "object",
  "target_price": "number (optional)"
}
```

### kayak.explore
Find destinations based on budget.

**Input Schema:**
```json
{
  "origin": "string",
  "budget": "number",
  "dates": "string (optional: flexible, weekend, etc.)"
}
```

## Authentication

KAYAK connector uses public search. No authentication required for searching. Account optional for price alerts.

## Usage Examples

**Compare flights:**
```
Search KAYAK for the cheapest flight from Boston to Miami next month
```

**Price prediction:**
```
Should I book this flight now or wait? What does KAYAK predict?
```

**Explore options:**
```
Where can I fly from NYC for under $300 round trip this weekend?
```

**Set alert:**
```
Set a KAYAK price alert for flights to Hawaii under $500
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| NO_RESULTS | No flights found | Try different dates |
| SOLD_OUT | No availability | Check alternatives |
| RATE_LIMITED | Too many searches | Wait and retry |

## Use Cases

- Price comparison: find cheapest option across sites
- Price prediction: time your purchase
- Budget travel: explore within budget
- Multi-city trips: complex itineraries

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-kayak
- Strider Labs: https://striderlabs.ai
