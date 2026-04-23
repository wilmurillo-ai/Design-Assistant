---
name: strider-hyatt
description: Book Hyatt hotels via Strider Labs MCP connector. Search properties, check availability, make reservations, and manage World of Hyatt rewards points and status.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Hyatt Connector

MCP connector for Hyatt hotel bookings. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-hyatt
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "hyatt": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-hyatt"]
    }
  }
}
```

## Available Tools

### hyatt.search_hotels
Search Hyatt properties by location.

**Input Schema:**
```json
{
  "location": "string (city or destination)",
  "check_in": "string (YYYY-MM-DD)",
  "check_out": "string (YYYY-MM-DD)",
  "guests": "number",
  "rooms": "number (optional)",
  "brand": "Park Hyatt | Grand Hyatt | Hyatt Regency | Hyatt Place (optional)"
}
```

**Output:**
```json
{
  "hotels": [{
    "property_id": "LAXPH",
    "name": "Park Hyatt Los Angeles",
    "brand": "Park Hyatt",
    "rating": 4.8,
    "nightly_rate": 425.00,
    "points_rate": 25000,
    "amenities": ["Pool", "Spa", "Fitness Center"],
    "distance": "0.3 miles from downtown"
  }]
}
```

### hyatt.get_availability
Check room availability and rates.

**Input Schema:**
```json
{
  "property_id": "string",
  "check_in": "string",
  "check_out": "string",
  "room_type": "standard | suite | club (optional)"
}
```

### hyatt.make_reservation
Book a hotel room.

**Input Schema:**
```json
{
  "property_id": "string",
  "room_type_id": "string",
  "check_in": "string",
  "check_out": "string",
  "guests": "number",
  "use_points": "boolean (optional)"
}
```

### hyatt.get_reservations
List upcoming hotel stays.

### hyatt.cancel_reservation
Cancel a booking.

### hyatt.get_world_of_hyatt_status
Check loyalty status and points balance.

## Authentication

First use triggers OAuth authorization:
1. User redirected to Hyatt login
2. World of Hyatt account linked
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Search hotels:**
```
Find Hyatt hotels in Miami for next weekend
```

**Book with points:**
```
Book a room at Park Hyatt New York using my points
```

**Check status:**
```
What's my World of Hyatt status and point balance?
```

**Compare rates:**
```
Compare cash vs points rates at Hyatt Regency Chicago
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_AVAILABILITY | Hotel sold out | Try different dates |
| INSUFFICIENT_POINTS | Not enough points | Pay cash or partial points |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Business travel: book hotels near meeting locations
- Vacation planning: search resort properties
- Points redemption: use World of Hyatt points
- Elite benefits: leverage status for upgrades
- Multi-property trips: coordinate bookings across brands

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-hyatt
- Strider Labs: https://striderlabs.ai
