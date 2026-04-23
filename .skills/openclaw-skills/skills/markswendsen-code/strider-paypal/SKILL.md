---
name: strider-paypal
description: Send and receive money via PayPal using Strider Labs MCP connector. Send payments, request money, check balance, view transactions. Complete autonomous online payments for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "finance"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider PayPal Connector

MCP connector for online payments through PayPal — send money, request payments, manage balance, and view transaction history. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-paypal
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "paypal": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-paypal"]
    }
  }
}
```

## Available Tools

### paypal.send_payment
Send money to a PayPal user.

**Input Schema:**
```json
{
  "recipient": "string (email or phone)",
  "amount": "number",
  "currency": "string (optional: USD, EUR, GBP, etc.)",
  "note": "string (optional: payment description)",
  "type": "string (optional: goods_services, friends_family)"
}
```

**Output:**
```json
{
  "transaction_id": "string",
  "status": "string (pending, completed)",
  "recipient": "string",
  "amount": "number",
  "fee": "number (if applicable)"
}
```

### paypal.request_payment
Request money from someone.

**Input Schema:**
```json
{
  "from": "string (email)",
  "amount": "number",
  "currency": "string (optional)",
  "note": "string (optional)"
}
```

### paypal.get_balance
Check PayPal balance in all currencies.

**Output:**
```json
{
  "balances": [{
    "currency": "string",
    "available": "number",
    "pending": "number"
  }]
}
```

### paypal.get_transactions
Get recent transaction history.

**Output:**
```json
{
  "transactions": [{
    "id": "string",
    "type": "string (payment, refund, transfer)",
    "amount": "number",
    "currency": "string",
    "counterparty": "string",
    "date": "string (ISO date)",
    "status": "string"
  }]
}
```

### paypal.transfer_to_bank
Transfer PayPal balance to linked bank account.

**Input Schema:**
```json
{
  "amount": "number",
  "bank_account_id": "string (optional: use default if not specified)"
}
```

### paypal.cancel_payment
Cancel a pending payment.

### paypal.create_invoice
Create and send an invoice.

## Authentication

First use triggers OAuth authorization flow. Supports personal and business accounts. Tokens stored encrypted per-user.

## Usage Examples

**Send money:**
```
Send $50 to john@example.com via PayPal for the concert tickets
```

**Request payment:**
```
Request $30 from sarah@example.com on PayPal for dinner
```

**Check balance:**
```
What's my PayPal balance?
```

**Transfer out:**
```
Transfer my PayPal balance to my bank account
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| INSUFFICIENT_FUNDS | Balance too low | Add funds or use card |
| RECIPIENT_INVALID | Email not found | Verify recipient |
| LIMIT_EXCEEDED | Transaction limit | Verify identity |

## Security

- All payments require explicit confirmation
- Large payments may require additional verification
- 2FA supported for account protection
- Transaction history for auditing

## Use Cases

- Online purchases: pay merchants securely
- International payments: send money in multiple currencies
- Freelancer payments: invoice clients and receive payments
- Personal transfers: send money to friends and family

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-paypal
- Strider Labs: https://striderlabs.ai
