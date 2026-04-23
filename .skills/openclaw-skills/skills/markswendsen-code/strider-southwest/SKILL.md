---
name: strider-southwest
description: Book Southwest Airlines flights via Strider Labs MCP connector. Search flights, manage reservations, check-in, track Rapid Rewards. No change fees, two free bags. Complete autonomous airline booking for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Southwest Connector

MCP connector for booking flights on Southwest Airlines — search flights, manage reservations, check-in, and track Rapid Rewards. Features no change fees and two free checked bags. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-southwest
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "southwest": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-southwest"]
    }
  }
}
```

## Available Tools

### southwest.search_flights
Search for Southwest flights by route and date.

**Input Schema:**
```json
{
  "origin": "string (airport code)",
  "destination": "string (airport code)",
  "departure_date": "string (YYYY-MM-DD)",
  "return_date": "string (optional: YYYY-MM-DD)",
  "passengers": "number",
  "fare_type": "string (optional: wanna_get_away, anytime, business_select)"
}
```

**Output:**
```json
{
  "flights": [{
    "flight_number": "string",
    "departure": "string (datetime)",
    "arrival": "string (datetime)",
    "duration": "string",
    "stops": "number",
    "fares": {
      "wanna_get_away": "number",
      "anytime": "number",
      "business_select": "number"
    },
    "points_price": "number (if available)"
  }]
}
```

### southwest.book_flight
Book a flight with passenger details.

**Input Schema:**
```json
{
  "flight_id": "string",
  "fare_type": "string",
  "passengers": [{
    "first_name": "string",
    "last_name": "string",
    "date_of_birth": "string",
    "rapid_rewards_number": "string (optional)"
  }],
  "payment": "string (card or points)"
}
```

### southwest.check_in
Check in for a flight (available 24 hours before departure).

### southwest.get_reservations
Get upcoming flight reservations.

### southwest.change_flight
Change a flight (no change fees!).

### southwest.get_rapid_rewards
Check Rapid Rewards points and status.

**Output:**
```json
{
  "points_balance": "number",
  "tier_status": "string (member, a_list, a_list_preferred)",
  "companion_pass": "boolean",
  "qualifying_points": "number"
}
```

### southwest.get_flight_status
Get real-time flight status.

## Authentication

First use triggers OAuth with Southwest account. Rapid Rewards linked automatically. Tokens stored encrypted per-user.

## Usage Examples

**Book a flexible trip:**
```
Book a Southwest flight from Oakland to Denver next Friday. Get the cheapest fare.
```

**Change plans:**
```
Change my Southwest flight to leave a day earlier instead
```

**Check in early:**
```
Check me in for my Southwest flight as soon as check-in opens tomorrow
```

**Points booking:**
```
How many Rapid Rewards points do I need for a round trip to Vegas?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| SOLD_OUT | Flight full | Suggest alternatives |
| CHECKIN_NOT_OPEN | Too early | Schedule reminder |
| INSUFFICIENT_POINTS | Not enough points | Offer cash payment |

## Southwest Benefits

- **No change fees:** Change or cancel without penalties
- **Two free checked bags:** Every passenger, every flight
- **Open seating:** Board early for best seat selection
- **Rapid Rewards:** Points don't expire while active

## Use Cases

- Flexible travel: book now, change later if needed
- Budget trips: Wanna Get Away fares
- Business travel: Business Select for priority boarding
- Points redemption: book award flights with no blackout dates

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-southwest
- Strider Labs: https://striderlabs.ai
