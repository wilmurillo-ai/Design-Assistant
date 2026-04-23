---
name: chainstream-quant
description: Quantitative trading and DeFi operations on DEXes. Use when executing token swaps, bridging cross-chain, launching tokens, backtesting strategies, generating trading signals, or monitoring positions. Covers Jupiter, Uniswap, PancakeSwap, LiFi, PumpFun, Raydium across Solana/BSC/Base/Ethereum.
metadata: {"clawdbot":{"emoji":"📈","requires":{"anyBins":["curl"]},"os":["linux","darwin","win32"]}}
---

# ChainStream Quant

Quantitative trading and DeFi operations across decentralized exchanges. Execute swaps, bridge tokens cross-chain, launch tokens on bonding curves, backtest strategies with historical data, and monitor positions -- all via 15+ REST API endpoints and multi-language SDKs.

- **Base URL**: `https://api.chainstream.io`
- **Documentation**: [docs.chainstream.io](https://docs.chainstream.io)
- **MCP Server**: `https://mcp.chainstream.io/mcp` (streamable-http)

## When to Use

- Executing token swaps on DEXes (Jupiter, Uniswap, PancakeSwap, Kyberswap, OpenOcean)
- Getting swap quotes and optimal routing across liquidity pools
- Bridging tokens cross-chain via LiFi aggregator
- Launching new tokens on PumpFun or Raydium LaunchLab
- Generating and backtesting trading strategies with historical data
- Estimating gas costs and sending signed transactions
- Monitoring async DeFi jobs (swap completion, bridge progress)

## Authentication

Three options (choose one):

| Method | Setup | Best For |
|--------|-------|----------|
| **Bearer Token** | `Authorization: Bearer <token>` | API key subscribers (dashboard) |
| **OAuth 2.0** | Client Credentials -> JWT | Server-to-server integration |
| **x402 Wallet Auth** | USDC quota purchase + wallet signature | No account needed, AI agents |

### x402 Wallet Auth

x402 uses a **quota-based billing model**: purchase a USDC plan to get a pool of Compute Units (CU), then consume them with API calls over 30 days.

| Plan | Price (USDC) | Quota (CU) | Duration |
|------|-------------|------------|----------|
| nano | $1 | 50,000 | 30 days |
| micro | $5 | 350,000 | 30 days |
| starter | $20 | 1,500,000 | 30 days |

**When encountering HTTP 401/402**, inform the user and get confirmation before purchasing:

1. "ChainStream requires authentication. You can purchase a quota plan with USDC (e.g., nano: $1 for 50K calls). Would you like to proceed?"
2. After confirmation: `POST /x402/purchase` -> sign USDC payment -> quota allocated
3. Subsequent requests: sign with wallet auth headers (`X-Wallet-Address`, `X-Wallet-Chain`, `X-Wallet-Signature`, `X-Wallet-Timestamp`, `X-Wallet-Nonce`)

Wallet-agnostic: works with any EVM/Solana wallet. See [x402 Auth Reference](references/x402-auth.md).

## DeFi Quick Reference

### Get a Swap Quote

```bash
curl "https://api.chainstream.io/v2/dex/sol/quote?inputMint=So111...&outputMint=EPjFW...&amount=1000000000&slippage=1"
```

```typescript
import { ChainStreamClient } from '@chainstream-io/sdk';
const client = new ChainStreamClient('YOUR_TOKEN');

const quote = await client.dex.quote({
  chain: 'sol',
  inputMint: 'So11111111111111111111111111111111111111112',
  outputMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
  amount: '1000000000',
  slippage: 1,
});
```

### Calculate Optimal Route

```bash
curl -X POST "https://api.chainstream.io/v2/dex/sol/route" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputMint":"So111...","outputMint":"EPjFW...","amount":"1000000000","slippage":1}'
```

### Execute a Swap

Swaps involve real funds. Always get user confirmation before executing.

```bash
curl -X POST "https://api.chainstream.io/v2/dex/sol/swap" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userAddress":"WALLET","inputMint":"So111...","outputMint":"EPjFW...","amount":"1000000000","slippage":1}'
```

```typescript
const result = await client.dex.swap({
  chain: 'sol',
  userAddress: 'WALLET',
  inputMint: 'So11111111111111111111111111111111111111112',
  outputMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
  amount: '1000000000',
  slippage: 1,
});
const job = await client.job.waitForJob(result.jobId);
```

### Create Token on Launchpad

```bash
curl -X POST "https://api.chainstream.io/v2/dex/sol/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userAddress":"WALLET","name":"My Token","symbol":"MTK","uri":"https://arweave.net/metadata.json"}'
```

## Trading Workflow

### Step 1: Gather Market Context

Use chainstream-data endpoints to analyze tokens and market trends.

### Step 2: Generate Strategy

Describe your strategy in natural language:

```
"Buy when 24h volume exceeds 3x the 7-day average and holder concentration
is below 30%. Take profit at +30%, stop loss at -15%. Hold max 24 hours."
```

### Step 3: Backtest

```bash
curl -X POST "https://api.chainstream.io/v2/trading/backtest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"chain":"sol","token":"TOKEN_ADDR","strategy":{...},"startTime":"2025-01-01","endTime":"2025-03-01","initialCapital":1000}'
```

```typescript
const backtest = await client.trading.backtest({
  chain: 'sol', token: 'TOKEN_ADDR',
  strategy: { /* strategy object */ },
  startTime: '2025-01-01', endTime: '2025-03-01', initialCapital: 1000,
});
console.log(`Sharpe: ${backtest.sharpeRatio}, MaxDD: ${backtest.maxDrawdown}`);
```

### Step 4: Execute (requires user confirmation)

Always confirm with the user before executing real trades.

### Step 5: Monitor Position

```typescript
client.stream.subscribeWalletPnl(
  { chain: 'sol', wallet: 'WALLET' },
  (pnl) => console.log(`PnL: $${pnl.piu}`)
);
```

## DeFi API Endpoints

### Swap and Routing

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v2/dex/{chain}/quote` | Swap quote (amounts, price impact) |
| POST | `/v2/dex/{chain}/route` | Optimal route across pools |
| POST | `/v2/dex/{chain}/swap` | Execute swap (returns jobId) |
| POST | `/v2/dex/{chain}/create` | Create token on launchpad |

### Aggregator / Provider / Bridge / Launchpad

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v2/dex/swap/quote/{builderId}` | Quote from specific provider |
| POST | `/v2/dex/aggregator/swap/{builderId}` | Swap via aggregator |
| POST | `/v2/bridge/quote/{builderId}` | Bridge quote |
| POST | `/v2/bridge/swap-and-bridge/{builderId}` | Swap + bridge |
| POST | `/v2/dex/launchpad/create-and-buy/{builderId}` | Create + buy |

### Transaction and Job

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v2/transaction/{chain}/gas-price` | Current gas price |
| POST | `/v2/transaction/{chain}/send` | Broadcast signed tx |
| GET | `/v2/job/{id}` | Poll job status |
| GET | `/v2/job/{id}/streaming` | SSE job progress |

## Supported Protocols

| Builder ID | Protocol | Type | Chains |
|-----------|----------|------|--------|
| `jupiter` | Jupiter | Aggregator | Solana |
| `kyberswap` | Kyberswap | Aggregator | BSC, ETH, Base, Polygon, Arbitrum |
| `openocean` | OpenOcean | Aggregator | BSC, ETH, Base, Polygon, Arbitrum |
| `uniswap` | Uniswap V3 | DEX | ETH, Base, Arbitrum, Polygon |
| `pancakeswap` | PancakeSwap | DEX | BSC, ETH, Base |
| `lifi` | LiFi | Bridge | All EVM + Solana |
| `pumpfun` | PumpFun | Launchpad | Solana |
| `raydium-launchlab` | Raydium LaunchLab | Launchpad | Solana |

## Safety

Operations involving real funds (swaps, trades, token creation, tx broadcast) should always get explicit user confirmation before execution.

Configurable limits:

```yaml
max_position_usd: 1000    # Max single trade size
slippage_limit: 3          # Max slippage %
```

## Tips

- When encountering 401/402, inform the user about x402 quota plans and get confirmation before purchasing.
- Always get a `quote` before executing a `swap`. Reject swaps with >5% price impact.
- DeFi operations return a `jobId`. Poll `GET /v2/job/{id}` or use SSE at `/v2/job/{id}/streaming`.
- Jupiter is the default Solana aggregator. For EVM, use Kyberswap or OpenOcean.
- Bridge operations via LiFi can take 2-30 minutes. Always poll job status.
- PumpFun token creation requires a metadata URI. Use `/v2/ipfs/presign` to upload first.
- Always call `estimate-gas-limit` before `send` on EVM chains.
- A Sharpe ratio >1.5 with max drawdown <20% is generally acceptable for backtests.
- Slippage on low-liquidity tokens can exceed 10%. Use explicit limits.

## References

- [DeFi Operations](references/defi-operations.md) -- swap, bridge, launchpad, transaction, job
- [Builders and Protocols](references/builders-and-protocols.md) -- supported DEXes, aggregators, bridges
- [Trading Patterns](references/trading-patterns.md) -- trading strategies with backtest examples
- [Strategy Templates](references/strategy-templates.md) -- ready-to-use strategy configs
- [x402 Auth](references/x402-auth.md) -- x402 protocol, wallet auth, plans, signature format

## Related Skills

- [chainstream-data](../chainstream-data/) -- on-chain data: token search, wallet PnL, market trends, KYT, WebSocket
