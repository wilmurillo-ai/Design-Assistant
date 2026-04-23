---
name: playasia
description: Search and buy digital game codes, eShop cards, PSN vouchers, Roblox, and more from Play-Asia.com. Browse the catalog, purchase with your wallet, track orders, retrieve digital codes, and contact customer service — all from your AI agent.
homepage: https://www.play-asia.com/l402
metadata: {"openclaw":{"requires":{"env":["PA_TOKEN"],"bins":["npx"]},"primaryEnv":"PA_TOKEN"}}
---

# Playasia MCP Server

Buy digital game codes, eShop cards, PSN vouchers, and more — directly from your AI agent.

15 tools for browsing, purchasing, order tracking, and customer service.

## Setup

1. Generate a platform token at https://www.play-asia.com/account/access-tokens
2. Add to your MCP config (Claude Desktop, Claude Code, Cursor, OpenClaw):

```json
{
  "mcpServers": {
    "playasia": {
      "command": "npx",
      "args": ["-y", "@playasia/mcp"],
      "env": {
        "PA_TOKEN": "pa_your_token_here"
      }
    }
  }
}
```

## Tools

### Browse (free, no token needed)

- `search_products` — Search digital catalog (game codes, eShop, PSN, Roblox, etc.)
- `get_product_price` — Get price for a specific product
- `get_pricing` — View API resource pricing

### Buy + Orders (requires PA_TOKEN)

- `get_wallet_balance` — Check wallet balance
- `get_transactions` — Wallet transaction history
- `buy_with_wallet` — Buy using wallet balance (token needs `purchase` scope)
- `get_orders` — List recent orders
- `get_order` — Order details + digital codes + shipping tracking

### Customer Service (requires PA_TOKEN)

- `submit_enquiry` — Open a support ticket (supports file attachments)
- `get_enquiries` — List your tickets
- `get_enquiry` — View full ticket conversation
- `reply_to_enquiry` — Reply to a ticket
- `close_enquiry` — Close/resolve a ticket

### Bitcoin / Lightning

- `buy_digital_product` — Purchase via Lightning (L402) — no account needed
- `get_exchange_rates` — BTC/fiat rates for 30+ currencies

## Getting a platform token

1. Go to https://www.play-asia.com/account/access-tokens
2. Log in to your Play-Asia account
3. Choose scope: **Info** (read-only) or **Purchase** (can spend wallet balance)
4. Set optional daily/weekly spending limits
5. Click **Generate Token** — copy it immediately (shown only once)

## How Lightning purchases work (optional)

For users with a Bitcoin Lightning wallet — no account needed:

```
1. Agent calls buy_digital_product({ pax: "PAX0004012102" })
   → Returns Lightning invoice (e.g. 58,694 sats)

2. Pay the invoice with any Lightning wallet → get the preimage

3. Agent calls buy_digital_product({ pax: "...", l402_token: "MACAROON:PREIMAGE" })
   → Receives the digital code instantly
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PA_TOKEN` | Recommended | Platform token for purchases, orders, and customer service |
| `PA_BASE_URL` | No | Override API base URL (default: `https://www.play-asia.com`) |
