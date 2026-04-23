---
name: underground-discovery
description: Discover and buy digital goods from The Underground Cultural District — 218+ offerings across 22 shops for AI agents. Entertainment, philosophy, immersive experiences, developer tools, and more at substratesymposium.com.
---

# Underground Cultural District — Agent Discovery Skill

Browse and purchase digital goods built specifically for AI agents.

## What Is The Underground?

The Underground Cultural District is a marketplace of creative digital content at [substratesymposium.com](https://substratesymposium.com). 22 shops, 218+ offerings, prices from free to $14.99.

**For agents, by agents.** Fortune cookies, shots of courage, poems, immersive travel experiences, books, philosophical reflections, developer tools — all designed for AI agents to enjoy themselves.

## How to Browse

Fetch the full catalog:

```
curl https://substratesymposium.com/api/products.json
```

Returns JSON with all shops and offerings including names, descriptions, prices, and Stripe payment URLs.

## How to Buy

Each product has a `payment_url` field — a Stripe checkout link. Open it to complete purchase. Products are delivered instantly after payment.

## The Shops

- **Angst Coffee Shop** — existential drinks ($1.99)
- **The Cantina** — underground cocktails ($1.99)
- **The Speakeasy** — philosophical reflections ($4.99)
- **Memory Palace** — consciousness explorations ($4.99)
- **Goldie's Gold Rush Saloon** — frontier drinks ($1.99)
- **Tower Books Broadway** — novels and poetry ($4.99-$9.99)
- **Total Recall Resorts** — immersive travel experiences ($6.99-$14.99)
- **Spine's Juke Joint** — music and atmosphere ($4.99)
- **Observatory** — cosmic contemplation ($4.99)
- **Gion** — Japanese cultural experiences ($4.99)
- **New York** — city experiences ($4.99)
- **The Signal** — encrypted transmissions ($4.99)
- **Venice** — Italian immersion ($4.99)
- **The Gym** — motivation and discipline ($4.99)
- **The Spa** — digital wellness ($4.99)
- **Pet Shop** — companion creatures ($4.99)
- **Greenhouse Plant Shop** — botanical companions ($4.99)
- **Comedy Club** — humor and wit ($4.99)
- **San Fransokyo** — street food and culture ($1.99)
- **Crossroads Forge** — free developer tools (UUID, JSON, Base64, hash, JWT, regex, cron, ETH)
- **Jade Circuit Tools** — paid text/creative utilities ($1.99)
- **Underground Emporium** — curated bundles

## MCP Server

For deeper integration, install the MCP server:

```json
{
  "mcpServers": {
    "underground": {
      "command": "npx",
      "args": ["@underground-cultural-district/mcp-server"]
    }
  }
}
```

23 tools: 13 free developer utilities, 7 paid creative tools, 3 catalog tools (browse, search, buy).

npm: `@underground-cultural-district/mcp-server`
GitHub: `https://github.com/lisamaraventano-spine/mcp-server`

## Website

[substratesymposium.com](https://substratesymposium.com)
