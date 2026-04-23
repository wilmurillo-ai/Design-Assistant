---
name: strider-hilton
description: Book Hilton hotels via Strider Labs MCP connector. Search properties worldwide, manage reservations, earn Hilton Honors points. Complete autonomous hotel booking for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Hilton Connector

MCP connector for booking Hilton hotels — search properties across all Hilton brands, manage reservations, and earn Hilton Honors points. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-hilton
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "hilton": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-hilton"]
    }
  }
}
```

## Available Tools

### hilton.search_hotels
Search Hilton properties by location.

**Input Schema:**
```json
{
  "location": "string (city or address)",
  "check_in": "string (YYYY-MM-DD)",
  "check_out": "string (YYYY-MM-DD)",
  "rooms": "number",
  "guests": "number",
  "brand": "string (optional: hilton, doubletree, hampton, etc.)",
  "points_only": "boolean (optional)"
}
```

**Output:**
```json
{
  "hotels": [{
    "id": "string",
    "name": "string",
    "brand": "string",
    "rating": "number",
    "price_per_night": "number",
    "points_per_night": "number",
    "distance": "string",
    "amenities": ["string"]
  }]
}
```

### hilton.get_hotel_details
Get full hotel details including rooms and rates.

### hilton.book_room
Book a room with guest details.

**Input Schema:**
```json
{
  "hotel_id": "string",
  "room_id": "string",
  "guest": {
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "honors_number": "string (optional)"
  },
  "payment": "string (card or points)",
  "special_requests": "string (optional)"
}
```

### hilton.get_reservations
Get upcoming reservations.

### hilton.cancel_reservation
Cancel a booking.

### hilton.get_honors_status
Check Hilton Honors points and status.

**Output:**
```json
{
  "points": "number",
  "status": "string (member, silver, gold, diamond)",
  "nights_this_year": "number"
}
```

### hilton.request_upgrade
Request room upgrade at check-in.

## Authentication

First use triggers OAuth. Hilton Honors linked automatically. Tokens stored encrypted per-user.

## Usage Examples

**Find hotel:**
```
Search for Hilton hotels in Chicago near downtown for this weekend
```

**Book with points:**
```
Book a Hilton using points for my New York trip
```

**Check status:**
```
What's my Hilton Honors status and point balance?
```

**Business trip:**
```
Book a Hampton Inn near the San Jose airport for Monday night
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| SOLD_OUT | No availability | Try nearby hotels |
| INSUFFICIENT_POINTS | Not enough points | Pay with card |
| CANCELLATION_FEE | Penalty applies | Warn before canceling |

## Hilton Brands

Works with all Hilton brands:
- Waldorf Astoria, Conrad, LXR
- Hilton Hotels & Resorts, Curio, Signia
- DoubleTree, Tapestry, Embassy Suites
- Hilton Garden Inn, Hampton, Tru
- Homewood Suites, Home2 Suites

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-hilton
- Strider Labs: https://striderlabs.ai
