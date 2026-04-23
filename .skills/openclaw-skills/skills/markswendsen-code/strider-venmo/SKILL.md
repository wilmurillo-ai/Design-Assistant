---
name: strider-venmo
description: Send and receive money via Venmo using Strider Labs MCP connector. Pay friends, request payments, split bills, check balances. Complete autonomous P2P payments for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "finance"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Venmo Connector

MCP connector for P2P payments through Venmo — send money, request payments, split bills, and manage your balance. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-venmo
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "venmo": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-venmo"]
    }
  }
}
```

## Available Tools

### venmo.send_payment
Send money to a Venmo user.

**Input Schema:**
```json
{
  "recipient": "string (username, phone, or email)",
  "amount": "number",
  "note": "string (required: payment description)",
  "audience": "string (optional: private, friends, public)"
}
```

**Output:**
```json
{
  "payment_id": "string",
  "status": "string (pending, completed)",
  "recipient": "string",
  "amount": "number",
  "fee": "number (if applicable)"
}
```

### venmo.request_payment
Request money from a Venmo user.

**Input Schema:**
```json
{
  "from": "string (username, phone, or email)",
  "amount": "number",
  "note": "string (required: request description)"
}
```

### venmo.get_balance
Check current Venmo balance.

**Output:**
```json
{
  "balance": "number",
  "pending_payments": "number",
  "pending_requests": "number"
}
```

### venmo.get_transactions
Get recent transaction history.

**Output:**
```json
{
  "transactions": [{
    "id": "string",
    "type": "string (payment, request, charge)",
    "amount": "number",
    "note": "string",
    "user": "string",
    "date": "string (ISO date)",
    "status": "string"
  }]
}
```

### venmo.search_users
Find Venmo users by name, username, or phone.

### venmo.cancel_request
Cancel a pending payment request.

### venmo.split_bill
Split a bill among multiple people.

**Input Schema:**
```json
{
  "total": "number",
  "participants": ["string (usernames)"],
  "note": "string"
}
```

## Authentication

First use triggers OAuth authorization flow. Requires 2FA confirmation for payments above thresholds. Tokens stored encrypted per-user.

## Usage Examples

**Pay a friend:**
```
Send $25 to @john-smith on Venmo for dinner last night
```

**Request money:**
```
Request $50 from Sarah on Venmo for concert tickets
```

**Split a bill:**
```
Split this $120 restaurant bill on Venmo between me, @mike, and @lisa
```

**Check balance:**
```
What's my Venmo balance?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| INSUFFICIENT_FUNDS | Balance too low | Add funds or use bank |
| USER_NOT_FOUND | Recipient doesn't exist | Verify username |
| LIMIT_EXCEEDED | Weekly limit reached | Wait or verify identity |

## Security

- All payments require explicit user confirmation
- Large payments (>$100) may require additional 2FA
- Private mode available for sensitive transactions
- Payment history accessible for auditing

## Use Cases

- Split expenses: restaurants, trips, household bills
- Rent payments: recurring payments to roommates
- Reimbursements: pay back friends quickly
- Group events: collect money for gifts or activities

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-venmo
- Strider Labs: https://striderlabs.ai
