---
name: strider-expedia
description: Book travel via Expedia using Strider Labs MCP connector. Search flights, hotels, car rentals, vacation packages. Complete autonomous travel booking for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Expedia Connector

MCP connector for booking travel through Expedia — search and book flights, hotels, car rentals, and vacation packages. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-expedia
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "expedia": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-expedia"]
    }
  }
}
```

## Available Tools

### expedia.search_flights
Search for flights by route, date, and preferences.

**Input Schema:**
```json
{
  "origin": "string (airport code or city)",
  "destination": "string (airport code or city)",
  "departure_date": "string (YYYY-MM-DD)",
  "return_date": "string (optional: YYYY-MM-DD for round trip)",
  "passengers": "number",
  "cabin_class": "string (optional: economy, business, first)",
  "nonstop_only": "boolean (optional)"
}
```

**Output:**
```json
{
  "flights": [{
    "id": "string",
    "airline": "string",
    "departure": "string (datetime)",
    "arrival": "string (datetime)",
    "duration": "string",
    "stops": "number",
    "price": "number",
    "cabin": "string"
  }]
}
```

### expedia.search_hotels
Search for hotels by location, dates, and filters.

**Input Schema:**
```json
{
  "location": "string (city or address)",
  "check_in": "string (YYYY-MM-DD)",
  "check_out": "string (YYYY-MM-DD)",
  "guests": "number",
  "rooms": "number",
  "star_rating": "number (optional: minimum stars)",
  "amenities": ["string (optional: pool, wifi, gym)"]
}
```

### expedia.search_cars
Search for rental cars at a location.

### expedia.search_packages
Search for bundled flight + hotel packages.

### expedia.get_details
Get full details for a flight, hotel, or car rental.

### expedia.add_to_trip
Add an item to your trip cart.

### expedia.checkout
Complete booking with traveler details and payment.

**Input Schema:**
```json
{
  "travelers": [{
    "first_name": "string",
    "last_name": "string",
    "date_of_birth": "string",
    "passport_number": "string (for international)"
  }],
  "payment_method_id": "string",
  "loyalty_number": "string (optional)"
}
```

### expedia.get_itinerary
Get booked itinerary details and confirmation numbers.

## Authentication

First use triggers OAuth authorization flow. Expedia Rewards points earned automatically. Tokens stored encrypted per-user.

## Usage Examples

**Flight search:**
```
Find flights from SFO to JFK next Friday, returning Sunday
```

**Hotel booking:**
```
Book a 4-star hotel in downtown Seattle for March 15-18
```

**Package deal:**
```
Search for flight and hotel packages to Cancun for spring break
```

**Complete trip:**
```
Book the cheapest nonstop flight to Miami and a hotel near South Beach
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| SOLD_OUT | No availability | Suggest alternatives |
| PRICE_CHANGED | Price increased | Confirm new price |
| PAYMENT_FAILED | Card declined | Update payment |

## Use Cases

- Vacation planning: flights, hotels, and packages
- Business travel: quick bookings with loyalty integration
- Group trips: coordinate multi-traveler bookings
- Last-minute deals: find availability and discounts

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-expedia
- Strider Labs: https://striderlabs.ai
