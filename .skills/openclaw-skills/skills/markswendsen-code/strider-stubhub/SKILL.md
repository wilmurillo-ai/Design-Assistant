---
name: strider-stubhub
description: Buy and sell tickets via StubHub using Strider Labs MCP connector. Search resale tickets, compare prices, buy guaranteed tickets, list your own. Complete autonomous ticket marketplace for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "entertainment"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider StubHub Connector

MCP connector for the StubHub ticket marketplace — buy resale tickets, compare prices, sell your tickets, all with FanProtect guarantee. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-stubhub
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "stubhub": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-stubhub"]
    }
  }
}
```

## Available Tools

### stubhub.search_events
Search for events with available tickets.

**Input Schema:**
```json
{
  "query": "string (artist, team, show)",
  "location": "string (city)",
  "date_from": "string (optional: YYYY-MM-DD)",
  "date_to": "string (optional: YYYY-MM-DD)",
  "category": "string (optional: concerts, sports, theater)"
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
    "min_price": "number",
    "ticket_count": "number"
  }]
}
```

### stubhub.get_listings
Get available ticket listings for an event.

**Input Schema:**
```json
{
  "event_id": "string",
  "quantity": "number",
  "sort": "string (optional: price, value, section)"
}
```

**Output:**
```json
{
  "listings": [{
    "id": "string",
    "section": "string",
    "row": "string",
    "quantity": "number",
    "price_per_ticket": "number",
    "total_with_fees": "number",
    "notes": "string (aisle, obstructed view, etc.)"
  }]
}
```

### stubhub.purchase_tickets
Buy tickets from a listing.

**Input Schema:**
```json
{
  "listing_id": "string",
  "quantity": "number",
  "delivery_method": "string (instant_download, email)",
  "payment_method_id": "string"
}
```

### stubhub.list_tickets
List your tickets for sale.

**Input Schema:**
```json
{
  "event_id": "string",
  "section": "string",
  "row": "string",
  "seats": ["string"],
  "price_per_ticket": "number",
  "quantity": "number"
}
```

### stubhub.get_my_listings
Get your active ticket listings.

### stubhub.update_listing
Update price or details on a listing.

### stubhub.get_my_purchases
Get purchased tickets.

### stubhub.cancel_listing
Remove tickets from sale.

## Authentication

First use triggers OAuth. FanProtect guarantee covers all purchases. Tokens stored encrypted per-user.

## Usage Examples

**Find tickets:**
```
Search StubHub for tickets to the Super Bowl
```

**Best deal:**
```
Find the cheapest lower level tickets on StubHub for the Lakers game tonight
```

**Sell tickets:**
```
List my 2 Taylor Swift tickets on StubHub for $400 each
```

**Track sales:**
```
Have my StubHub tickets sold yet?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| LISTING_SOLD | Tickets no longer available | Find alternatives |
| BELOW_MIN_PRICE | Price too low | Increase price |
| INVALID_TICKETS | Can't verify tickets | Check barcode |

## Use Cases

- Sold-out events: find tickets after sellout
- Last-minute plans: instant download tickets
- Reselling: sell tickets you can't use
- Price hunting: compare across listings

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-stubhub
- Strider Labs: https://striderlabs.ai
