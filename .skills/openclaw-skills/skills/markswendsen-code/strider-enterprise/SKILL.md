---
name: strider-enterprise
description: Rent cars from Enterprise, check availability, manage reservations, and access Enterprise Plus rewards via Strider Labs MCP connector. Search vehicles by location, dates, and class.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Enterprise Connector

MCP connector for Enterprise Rent-A-Car reservations, vehicle selection, and rewards management. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-enterprise
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "enterprise": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-enterprise"]
    }
  }
}
```

## Available Tools

### enterprise.search_vehicles
Search available rental vehicles at a location.

**Input Schema:**
```json
{
  "pickup_location": "string (airport code, address, or city)",
  "pickup_date": "string (YYYY-MM-DD)",
  "pickup_time": "string (HH:MM)",
  "return_date": "string (YYYY-MM-DD)",
  "return_time": "string (HH:MM)",
  "vehicle_class": "economy | compact | midsize | fullsize | suv | luxury | truck"
}
```

**Output:**
```json
{
  "vehicles": [{
    "class": "midsize",
    "make_model": "Toyota Camry or similar",
    "daily_rate": 45.99,
    "total_price": 137.97,
    "features": ["automatic", "ac", "bluetooth"],
    "available": true
  }]
}
```

### enterprise.find_locations
Find nearby Enterprise locations.

**Input Schema:**
```json
{
  "address": "string",
  "radius_miles": "number"
}
```

### enterprise.make_reservation
Book a rental vehicle.

**Input Schema:**
```json
{
  "location_id": "string",
  "vehicle_class": "string",
  "pickup_datetime": "string (ISO 8601)",
  "return_datetime": "string (ISO 8601)",
  "driver_age": "number",
  "add_ons": ["gps", "child_seat", "additional_driver"]
}
```

### enterprise.get_reservations
List upcoming and past reservations.

### enterprise.modify_reservation
Change dates, location, or vehicle class for existing reservation.

### enterprise.cancel_reservation
Cancel a reservation.

### enterprise.get_rewards_balance
Check Enterprise Plus points balance and tier status.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Enterprise to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

No API key required — connector manages OAuth flow.

## Usage Examples

**Search for rentals:**
```
Find available cars at LAX airport from March 22-25
```

**Book a specific vehicle:**
```
Book a midsize car from Enterprise at SFO for this weekend
```

**Modify reservation:**
```
Change my Enterprise reservation to return one day later
```

**Check rewards:**
```
How many Enterprise Plus points do I have?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_AVAILABILITY | Vehicle class unavailable | Try different class or dates |
| LOCATION_CLOSED | Pickup location closed at time | Adjust pickup time |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Travel planning: search and compare rental options
- Business travel: quick reservations with corporate rates
- Weekend trips: short-term rentals with flexible pickup
- Moving/hauling: truck and cargo van rentals
- Loyalty rewards: track and redeem Enterprise Plus points

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-enterprise
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
