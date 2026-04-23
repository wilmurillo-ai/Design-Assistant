---
name: strider-booking
description: Book hotels via Booking.com using Strider Labs MCP connector. Search accommodations worldwide, compare prices, manage reservations. Complete autonomous hotel booking for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Booking.com Connector

MCP connector for booking accommodations through Booking.com — search hotels, apartments, and unique stays worldwide with flexible cancellation options. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-booking
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "booking": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-booking"]
    }
  }
}
```

## Available Tools

### booking.search_properties
Search for hotels, apartments, and vacation rentals.

**Input Schema:**
```json
{
  "destination": "string (city, region, or property name)",
  "check_in": "string (YYYY-MM-DD)",
  "check_out": "string (YYYY-MM-DD)",
  "guests": "number",
  "rooms": "number",
  "filters": {
    "star_rating": "number (optional)",
    "free_cancellation": "boolean (optional)",
    "breakfast_included": "boolean (optional)",
    "property_type": "string (hotel, apartment, hostel, etc.)"
  }
}
```

**Output:**
```json
{
  "properties": [{
    "id": "string",
    "name": "string",
    "type": "string",
    "rating": "number",
    "review_score": "number",
    "review_count": "number",
    "price_per_night": "number",
    "total_price": "number",
    "free_cancellation": "boolean",
    "breakfast": "boolean",
    "distance_to_center": "string"
  }]
}
```

### booking.get_property_details
Get full details including photos, amenities, and policies.

### booking.check_availability
Check room availability and prices for specific dates.

### booking.create_booking
Book a property with guest details.

**Input Schema:**
```json
{
  "property_id": "string",
  "room_id": "string",
  "guest": {
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "phone": "string"
  },
  "special_requests": "string (optional)",
  "payment_method_id": "string"
}
```

### booking.get_reservations
Get upcoming and past reservations.

### booking.cancel_reservation
Cancel a booking (if within cancellation policy).

### booking.get_genius_deals
Get Booking.com Genius member-only deals.

## Authentication

First use triggers OAuth. Genius level benefits apply automatically. Tokens stored encrypted per-user.

## Usage Examples

**Find hotels:**
```
Search for hotels in Paris with free cancellation for April 10-14
```

**Budget travel:**
```
Find the cheapest well-rated accommodation in Barcelona for next weekend
```

**Business trip:**
```
Book a hotel in downtown Chicago near the convention center, checking in Monday
```

**Compare options:**
```
Show me apartments vs hotels in Amsterdam for a week-long stay
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| SOLD_OUT | No availability | Try different dates |
| PRICE_CHANGED | Price updated | Confirm new price |
| CANCELLATION_FEE | Penalty applies | Warn user before proceeding |

## Use Cases

- Vacation stays: hotels, apartments, villas
- Business travel: quick bookings near meeting venues
- Long stays: monthly rentals and extended stays
- Group bookings: multiple rooms for events or trips

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-booking
- Strider Labs: https://striderlabs.ai
