---
name: strider-united
description: Book United Airlines flights via Strider Labs MCP connector. Search flights, manage reservations, check-in, track MileagePlus. Complete autonomous airline booking for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider United Airlines Connector

MCP connector for booking flights on United Airlines — search flights, manage reservations, check-in, and track MileagePlus miles. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-united
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "united": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-united"]
    }
  }
}
```

## Available Tools

### united.search_flights
Search for United flights.

**Input Schema:**
```json
{
  "origin": "string (airport code)",
  "destination": "string (airport code)",
  "departure_date": "string (YYYY-MM-DD)",
  "return_date": "string (optional)",
  "passengers": "number",
  "cabin": "string (optional: economy, economy_plus, business, polaris)"
}
```

**Output:**
```json
{
  "flights": [{
    "flight_number": "string",
    "departure": "string",
    "arrival": "string",
    "duration": "string",
    "stops": "number",
    "aircraft": "string",
    "price": "number",
    "miles_price": "number"
  }]
}
```

### united.book_flight
Book a flight with passenger details.

### united.check_in
Check in for a flight (24 hours before).

### united.get_reservations
Get upcoming reservations.

### united.get_flight_status
Get real-time flight status.

### united.get_mileageplus
Check MileagePlus balance and status.

**Output:**
```json
{
  "miles_balance": "number",
  "status": "string (member, silver, gold, platinum, 1k, gs)",
  "pqp": "number (premier qualifying points)",
  "pqf": "number (premier qualifying flights)"
}
```

### united.select_seats
Choose seats for a booked flight.

### united.upgrade_cabin
Request or purchase upgrades.

## Authentication

First use triggers OAuth with United account. MileagePlus linked automatically. Tokens stored encrypted per-user.

## Usage Examples

**Book flight:**
```
Book a United flight from ORD to LAX on January 15
```

**Use miles:**
```
How many MileagePlus miles do I need to fly to London? Book with miles.
```

**Check in:**
```
Check me in for my United flight tomorrow
```

**Status:**
```
Is my United flight UA1234 on time?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| SOLD_OUT | Flight full | Suggest alternatives |
| UPGRADE_UNAVAILABLE | No upgrade space | Try at check-in |
| INSUFFICIENT_MILES | Not enough miles | Pay with card |

## Use Cases

- Business travel: frequent flyer with status
- Award flights: book with MileagePlus miles
- Hub connections: ORD, EWR, IAH, DEN, SFO
- Polaris: premium international travel

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-united
- Strider Labs: https://striderlabs.ai
