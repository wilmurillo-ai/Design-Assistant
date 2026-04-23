---
name: strider-ticketmaster
description: Buy event tickets via Ticketmaster using Strider Labs MCP connector. Search concerts, sports, theater, get seats, manage tickets. Complete autonomous event ticketing for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "entertainment"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Ticketmaster Connector

MCP connector for buying tickets through Ticketmaster — search events, find seats, purchase tickets, and manage your orders. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-ticketmaster
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "ticketmaster": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-ticketmaster"]
    }
  }
}
```

## Available Tools

### ticketmaster.search_events
Search for events by artist, team, or keyword.

**Input Schema:**
```json
{
  "query": "string (artist, team, show name)",
  "location": "string (city or zip)",
  "radius_miles": "number (optional)",
  "date_from": "string (optional: YYYY-MM-DD)",
  "date_to": "string (optional: YYYY-MM-DD)",
  "category": "string (optional: music, sports, arts, family)"
}
```

**Output:**
```json
{
  "events": [{
    "id": "string",
    "name": "string",
    "date": "string (datetime)",
    "venue": "string",
    "city": "string",
    "price_range": "string ($50 - $500)",
    "on_sale": "boolean",
    "onsale_date": "string (if not yet on sale)"
  }]
}
```

### ticketmaster.get_event_details
Get full event details including venue map.

### ticketmaster.get_available_tickets
Get available seats and pricing.

**Input Schema:**
```json
{
  "event_id": "string",
  "quantity": "number",
  "section_preference": "string (optional: floor, lower, upper)"
}
```

**Output:**
```json
{
  "tickets": [{
    "id": "string",
    "section": "string",
    "row": "string",
    "seats": ["string"],
    "price_per_ticket": "number",
    "total_price": "number",
    "ticket_type": "string (standard, vip, etc.)"
  }]
}
```

### ticketmaster.purchase_tickets
Complete ticket purchase.

**Input Schema:**
```json
{
  "ticket_id": "string",
  "quantity": "number",
  "delivery_method": "string (mobile, will_call)",
  "payment_method_id": "string"
}
```

### ticketmaster.get_my_tickets
Get purchased tickets and transfer options.

### ticketmaster.transfer_tickets
Transfer tickets to another person.

### ticketmaster.sell_tickets
List tickets for resale on Ticketmaster.

## Authentication

First use triggers OAuth. Tickets stored in Ticketmaster account. Tokens stored encrypted per-user.

## Usage Examples

**Find concert:**
```
Search for Taylor Swift concerts near San Francisco in the next 3 months
```

**Buy tickets:**
```
Get 2 tickets to the Warriors game next Saturday, preferably lower level
```

**Check inventory:**
```
What seats are available for Hamilton on Broadway in June?
```

**Manage tickets:**
```
Show me my upcoming Ticketmaster tickets
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| SOLD_OUT | No tickets available | Check resale |
| NOT_YET_ON_SALE | Too early | Notify when on sale |
| PURCHASE_LIMIT | Exceeded max | Reduce quantity |

## Use Cases

- Concert tickets: find and buy music events
- Sports games: season tickets, single games
- Theater: Broadway, local shows
- Family events: Disney on Ice, Cirque du Soleil

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-ticketmaster
- Strider Labs: https://striderlabs.ai
