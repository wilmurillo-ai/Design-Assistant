---
name: strider-airbnb
description: Search vacation rentals on Airbnb via Strider Labs MCP connector. Find properties by location, dates, and guests. Get listing details, amenities, pricing, and availability.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Airbnb Connector

MCP connector for searching Airbnb vacation rentals and retrieving listing details. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-airbnb
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-airbnb"]
    }
  }
}
```

## Available Tools

### airbnb.search_listings
Search vacation rentals by location, dates, and guest count.

**Input Schema:**
```json
{
  "location": "string (city, address, or region)",
  "checkin": "string (YYYY-MM-DD)",
  "checkout": "string (YYYY-MM-DD)",
  "guests": "number"
}
```

**Output:**
```json
{
  "listings": [{
    "id": "string",
    "title": "string",
    "price_per_night": "number",
    "rating": "number",
    "amenities": ["string"],
    "images": ["string"]
  }]
}
```

### airbnb.get_listing_details
Get full details for a specific listing including host info, house rules, and availability calendar.

### airbnb.check_availability
Check if a listing is available for specific dates.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Airbnb to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

No API key required — connector manages OAuth flow.

## Usage Examples

**Find a rental in Austin for a weekend:**
```
Search Airbnb for a place in Austin, TX from March 22-24 for 2 guests
```

**Look for pet-friendly places:**
```
Find Airbnb listings in Lake Tahoe that allow pets, checking in December 20, checking out December 27, for 4 guests
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| RATE_LIMITED | Too many requests | Retry after delay |
| SERVICE_UNAVAILABLE | Airbnb unavailable | Retry with backoff |

## Use Cases

- Vacation planning: search rentals by destination and dates
- Group trips: find places that accommodate larger parties
- Extended stays: compare monthly rental pricing
- Workations: find rentals with dedicated workspaces

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-airbnb
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
