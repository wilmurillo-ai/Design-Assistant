---
name: strider-marriott
description: Book Marriott hotels via Strider Labs MCP connector. Search properties worldwide, manage reservations, earn Bonvoy points. Complete autonomous hotel booking for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Marriott Connector

MCP connector for booking Marriott hotels — search properties across all Marriott Bonvoy brands, manage reservations, and earn Bonvoy points. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-marriott
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "marriott": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-marriott"]
    }
  }
}
```

## Available Tools

### marriott.search_hotels
Search Marriott properties by location.

**Input Schema:**
```json
{
  "location": "string (city or address)",
  "check_in": "string (YYYY-MM-DD)",
  "check_out": "string (YYYY-MM-DD)",
  "rooms": "number",
  "guests": "number",
  "brand": "string (optional: ritz, westin, sheraton, etc.)",
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
    "category": "number (1-8)",
    "price_per_night": "number",
    "points_per_night": "number",
    "distance": "string"
  }]
}
```

### marriott.get_hotel_details
Get full hotel details.

### marriott.book_room
Book a room.

**Input Schema:**
```json
{
  "hotel_id": "string",
  "room_id": "string",
  "guest": {
    "first_name": "string",
    "last_name": "string",
    "bonvoy_number": "string (optional)"
  },
  "payment": "string (card or points)",
  "special_requests": "string (optional)"
}
```

### marriott.get_reservations
Get upcoming reservations.

### marriott.get_bonvoy_status
Check Bonvoy points and elite status.

**Output:**
```json
{
  "points": "number",
  "status": "string (member, silver, gold, platinum, titanium, ambassador)",
  "nights_this_year": "number",
  "lifetime_nights": "number"
}
```

### marriott.request_upgrade
Request suite upgrade (for elite members).

### marriott.mobile_key
Get digital room key.

## Authentication

First use triggers OAuth. Marriott Bonvoy linked automatically. Tokens stored encrypted per-user.

## Usage Examples

**Find hotel:**
```
Search for Marriott hotels in Miami Beach for spring break
```

**Use points:**
```
Book a Westin with Bonvoy points for my Denver trip
```

**Status check:**
```
What's my Marriott Bonvoy status and how many nights to Platinum?
```

**Luxury stay:**
```
Book a Ritz-Carlton for our anniversary weekend
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| SOLD_OUT | No rooms available | Try nearby |
| INSUFFICIENT_POINTS | Not enough Bonvoy | Pay with card |
| UPGRADE_UNAVAILABLE | No suites | Try at check-in |

## Marriott Bonvoy Brands

Works with all 30+ brands including:
- Ritz-Carlton, St. Regis, W Hotels
- JW Marriott, Marriott, Westin, Sheraton
- Le Méridien, Renaissance, Delta Hotels
- Courtyard, Residence Inn, SpringHill Suites
- Fairfield, TownePlace, Moxy, Aloft

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-marriott
- Strider Labs: https://striderlabs.ai
