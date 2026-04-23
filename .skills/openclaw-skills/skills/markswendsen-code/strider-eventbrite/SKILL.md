---
name: strider-eventbrite
description: Discover events, buy tickets, and manage registrations on Eventbrite via Strider Labs MCP connector. Search by location, category, and date. Access your tickets and event details.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "events"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Eventbrite Connector

MCP connector for discovering events, purchasing tickets, and managing event registrations on Eventbrite. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-eventbrite
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "eventbrite": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-eventbrite"]
    }
  }
}
```

## Available Tools

### eventbrite.search_events
Search for events by location, date, and category.

**Input Schema:**
```json
{
  "location": "string (city or address)",
  "radius_miles": "number",
  "start_date": "string (YYYY-MM-DD)",
  "end_date": "string (YYYY-MM-DD)",
  "category": "music | business | food | arts | sports | tech | health | community",
  "price": "free | paid | all"
}
```

**Output:**
```json
{
  "events": [{
    "id": "string",
    "title": "string",
    "datetime": "string",
    "venue": "string",
    "price_range": "$25 - $75",
    "tickets_available": true,
    "category": "music"
  }]
}
```

### eventbrite.get_event_details
Get full details for a specific event.

**Input Schema:**
```json
{
  "event_id": "string"
}
```

**Output:**
```json
{
  "title": "string",
  "description": "string",
  "datetime": "string",
  "venue": {"name": "string", "address": "string"},
  "organizer": "string",
  "ticket_types": [{
    "name": "General Admission",
    "price": 25.00,
    "available": 150
  }],
  "refund_policy": "string"
}
```

### eventbrite.purchase_tickets
Buy tickets for an event.

**Input Schema:**
```json
{
  "event_id": "string",
  "tickets": [{
    "type": "string",
    "quantity": "number"
  }],
  "attendee_info": [{
    "name": "string",
    "email": "string"
  }]
}
```

### eventbrite.get_my_tickets
List tickets and registrations for upcoming events.

### eventbrite.cancel_registration
Cancel a ticket/registration (if refund policy allows).

### eventbrite.get_event_updates
Get announcements and updates from event organizers.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Eventbrite to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

No API key required — connector manages OAuth flow.

## Usage Examples

**Find local events:**
```
Find tech meetups in San Francisco this weekend on Eventbrite
```

**Buy tickets:**
```
Get 2 tickets to the AI conference on Eventbrite event ID 12345
```

**Check my tickets:**
```
Show me my upcoming Eventbrite tickets
```

**Get event details:**
```
What's the schedule for the startup pitch night on Eventbrite?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| SOLD_OUT | Event is sold out | Join waitlist or find alternatives |
| EVENT_CANCELLED | Event has been cancelled | Check for refund |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Event discovery: find concerts, meetups, conferences nearby
- Ticket purchasing: buy and manage event tickets
- Calendar planning: browse events by date range
- Professional networking: find industry events and conferences
- Community engagement: discover local activities and workshops

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-eventbrite
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
