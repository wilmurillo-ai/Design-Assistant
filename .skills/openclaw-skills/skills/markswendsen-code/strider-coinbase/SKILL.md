---
name: strider-coinbase
description: Trade crypto, check balances, and manage your portfolio on Coinbase via Strider Labs MCP connector. Execute market and limit orders, view transaction history, and monitor real-time prices.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "finance"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Coinbase Connector

MCP connector for Coinbase cryptocurrency trading and portfolio management. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-coinbase
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "coinbase": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-coinbase"]
    }
  }
}
```

## Available Tools

### coinbase.get_portfolio
Get current portfolio balances across all assets.

**Output:**
```json
{
  "balances": [{
    "asset": "BTC",
    "amount": "0.5423",
    "usd_value": "32538.00"
  }],
  "total_usd": "45230.50"
}
```

### coinbase.get_price
Get current price for a cryptocurrency.

**Input Schema:**
```json
{
  "asset": "string (BTC, ETH, SOL, etc.)"
}
```

### coinbase.place_order
Place a buy or sell order.

**Input Schema:**
```json
{
  "side": "buy | sell",
  "asset": "string",
  "amount": "number (in USD for buy, in asset for sell)",
  "order_type": "market | limit",
  "limit_price": "number (required for limit orders)"
}
```

### coinbase.get_transactions
Get recent transaction history.

**Input Schema:**
```json
{
  "asset": "string (optional, filter by asset)",
  "limit": "number (default 20)"
}
```

### coinbase.cancel_order
Cancel a pending limit order.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Coinbase to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

No API key required — connector manages OAuth flow.

## Usage Examples

**Check your portfolio:**
```
Show me my Coinbase portfolio balance
```

**Buy Bitcoin:**
```
Buy $100 worth of Bitcoin on Coinbase
```

**Set a limit order:**
```
Place a limit order to buy 0.1 ETH at $2,000 on Coinbase
```

**Check prices:**
```
What's the current price of SOL on Coinbase?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| INSUFFICIENT_FUNDS | Not enough balance | Check portfolio first |
| RATE_LIMITED | Too many requests | Retry after delay |
| INVALID_ORDER | Order parameters wrong | Validate inputs |

## Use Cases

- Portfolio monitoring: track balances and performance
- Trading: execute market and limit orders
- Price alerts: monitor crypto prices
- DCA automation: schedule recurring purchases
- Tax reporting: export transaction history

## Security Notes

- OAuth tokens are encrypted at rest
- No API keys stored in config
- Supports Coinbase's 2FA requirements
- Read-only mode available for monitoring without trading

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-coinbase
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
