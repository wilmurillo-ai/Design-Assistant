---
name: strider-vrbo
description: Book vacation rentals via Vrbo using Strider Labs MCP connector. Search homes, cabins, condos, beach houses. Compare with full kitchen and space for families. Complete autonomous vacation rental booking for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Vrbo Connector

MCP connector for booking vacation rentals through Vrbo — search entire homes, cabins, condos, and beach houses perfect for families and groups. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-vrbo
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "vrbo": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-vrbo"]
    }
  }
}
```

## Available Tools

### vrbo.search_properties
Search for vacation rental properties.

**Input Schema:**
```json
{
  "location": "string (city, region, or landmark)",
  "check_in": "string (YYYY-MM-DD)",
  "check_out": "string (YYYY-MM-DD)",
  "guests": "number",
  "bedrooms": "number (optional: minimum)",
  "amenities": ["string (optional: pool, hot_tub, pet_friendly, etc.)"],
  "property_type": "string (optional: house, condo, cabin, etc.)"
}
```

**Output:**
```json
{
  "properties": [{
    "id": "string",
    "title": "string",
    "type": "string",
    "bedrooms": "number",
    "bathrooms": "number",
    "sleeps": "number",
    "rating": "number",
    "review_count": "number",
    "price_per_night": "number",
    "total_price": "number",
    "amenities": ["string"]
  }]
}
```

### vrbo.get_property_details
Get full details including photos, rules, and availability.

### vrbo.check_availability
Check if property is available for dates.

### vrbo.book_property
Book a property with guest details.

**Input Schema:**
```json
{
  "property_id": "string",
  "check_in": "string",
  "check_out": "string",
  "guests": "number",
  "guest_info": {
    "name": "string",
    "email": "string",
    "phone": "string"
  },
  "message_to_host": "string (optional)",
  "payment_method_id": "string"
}
```

### vrbo.get_reservations
Get upcoming and past reservations.

### vrbo.message_host
Send message to property host.

### vrbo.cancel_reservation
Cancel a booking (per cancellation policy).

## Authentication

First use triggers OAuth. Vrbo accounts required for booking. Tokens stored encrypted per-user.

## Usage Examples

**Find a beach house:**
```
Search Vrbo for a 3-bedroom beach house in Outer Banks for a week in July
```

**Family reunion:**
```
Find a large house on Vrbo that sleeps 12 with a pool for Thanksgiving weekend
```

**Ski trip:**
```
Search Vrbo for a cabin near Breckenridge with a hot tub for 6 people
```

**Contact host:**
```
Message the Vrbo host to ask about early check-in
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NOT_AVAILABLE | Dates taken | Try different dates |
| MIN_STAY | Below minimum nights | Extend stay |
| INSTANT_BOOK_DISABLED | Host approval required | Submit request |

## Use Cases

- Family vacations: houses with kitchens and space
- Group trips: large properties for reunions
- Beach trips: oceanfront condos and houses
- Mountain getaways: cabins and chalets

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-vrbo
- Strider Labs: https://striderlabs.ai
