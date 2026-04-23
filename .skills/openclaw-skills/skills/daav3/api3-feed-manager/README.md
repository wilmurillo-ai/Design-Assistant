# Api3 Feed Manager

A small OpenClaw skill for figuring out what Api3 feeds exist, which chains support them, and whether a feed is actually activatable or already retired.

## What it helps with

- find supported Api3 chain aliases
- audit feed coverage across chains
- separate activatable feeds from retired or delisted ones
- inspect queue tiers and default activation choices
- prepare non-sending Market contract calls

## What it does not do

- broadcast transactions
- pretend retired feeds are still available
- replace `SKILL.md` as the agent-facing instruction file

## Main files

- `SKILL.md` - instructions for the agent
- `scripts/bin/api3-feed-manager.js` - local CLI entrypoint
- `scripts/api3-feed-manager.js` - bundled runtime

## Quick examples

```bash
node ./scripts/bin/api3-feed-manager.js supported-chains
node ./scripts/bin/api3-feed-manager.js coverage-audit --chain arbitrum --limit 20
node ./scripts/bin/api3-feed-manager.js queue-plan --dapi-name ETH/USD --rpc-url https://arb1.arbitrum.io/rpc --chain arbitrum
```
