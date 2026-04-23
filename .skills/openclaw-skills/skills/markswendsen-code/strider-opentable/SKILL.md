---
name: strider-opentable
description: Book restaurant reservations via Strider Labs MCP connector. Search restaurants, check availability, make and manage reservations, and earn OpenTable dining points.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider OpenTable Connector

MCP connector for OpenTable restaurant reservations. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-opentable
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "opentable": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-opentable"]
    }
  }
}
```

## Available Tools

### opentable.search_restaurants
Search restaurants by location and cuisine.

**Input Schema:**
```json
{
  "location": "string (city, neighborhood, or coordinates)",
  "cuisine": "string (optional)",
  "price": "1 | 2 | 3 | 4 (optional, $ to $$$$)",
  "date": "string (YYYY-MM-DD)",
  "time": "string (HH:MM)",
  "party_size": "number"
}
```

**Output:**
```json
{
  "restaurants": [{
    "id": "ot123",
    "name": "Osteria Francescana",
    "cuisine": "Italian",
    "price": 4,
    "rating": 4.8,
    "reviews_count": 2341,
    "available_times": ["18:00", "18:30", "20:00"],
    "neighborhood": "Downtown",
    "image_url": "https://..."
  }]
}
```

### opentable.find_availability
Check specific restaurant availability.

**Input Schema:**
```json
{
  "restaurant_id": "string",
  "date": "string",
  "party_size": "number",
  "time_range": {"start": "17:00", "end": "21:00"}
}
```

### opentable.make_reservation
Book a table.

**Input Schema:**
```json
{
  "restaurant_id": "string",
  "date": "string",
  "time": "string",
  "party_size": "number",
  "special_requests": "string (optional)"
}
```

### opentable.get_reservations
List upcoming reservations.

### opentable.modify_reservation
Change an existing reservation.

### opentable.cancel_reservation
Cancel a booking.

### opentable.get_points
Check OpenTable dining points balance.

## Authentication

First use triggers OAuth authorization:
1. User redirected to OpenTable login
2. Dining points linked automatically
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Find restaurants:**
```
Find Italian restaurants in Manhattan for 4 people Saturday night
```

**Book a table:**
```
Book the 7pm slot at Osteria Francescana for 2
```

**Check reservations:**
```
What restaurant reservations do I have this month?
```

**Modify booking:**
```
Change my OpenTable reservation from 7pm to 8pm
```

**Special requests:**
```
Book a table near the window for our anniversary dinner
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_AVAILABILITY | Time slot taken | Try different time |
| RESTAURANT_CLOSED | Not open on that day | Pick another date |
| PARTY_TOO_LARGE | Exceeds max size | Call restaurant directly |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Date night: find and book romantic restaurants
- Business dinners: reserve private dining
- Group celebrations: book for large parties
- Last-minute reservations: find immediate availability
- Points redemption: use dining rewards

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-opentable
- Strider Labs: https://striderlabs.ai
