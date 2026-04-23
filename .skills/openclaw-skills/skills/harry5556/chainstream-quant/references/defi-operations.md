# DeFi Operations Reference

Complete reference for all DeFi API endpoints and workflows.

## Swap Workflow

The typical swap flow: **Quote → Route → Swap → Track Job**

### 1. Get Quote

```bash
GET /v2/dex/{chain}/quote?inputMint=TOKEN_A&outputMint=TOKEN_B&amount=AMOUNT&slippage=SLIPPAGE
```

Response:

```json
{
  "inputMint": "So111...",
  "outputMint": "EPjFW...",
  "inputAmount": "1000000000",
  "expectedOutput": "5234567",
  "minimumOutput": "5182221",
  "priceImpact": "0.15",
  "route": [{"dex": "Raydium", "pool": "POOL_ADDR", "percent": 60}, {"dex": "Orca", "pool": "POOL_ADDR", "percent": 40}]
}
```

### 2. Calculate Route

```bash
POST /v2/dex/{chain}/route
Content-Type: application/json

{
  "inputMint": "So111...",
  "outputMint": "EPjFW...",
  "amount": "1000000000",
  "slippage": 1
}
```

### 3. Execute Swap

```bash
POST /v2/dex/{chain}/swap
Content-Type: application/json

{
  "userAddress": "WALLET_ADDRESS",
  "inputMint": "So111...",
  "outputMint": "EPjFW...",
  "amount": "1000000000",
  "slippage": 1
}
```

Response:

```json
{
  "jobId": "job_abc123",
  "status": "pending"
}
```

### 4. Track Job

```bash
# Poll
GET /v2/job/{jobId}

# Stream (SSE)
GET /v2/job/{jobId}/streaming
```

```typescript
const result = await client.dex.swap({ /* params */ });
const completion = await client.job.waitForJob(result.jobId);
console.log(`Tx: ${completion.transactionHash}, Status: ${completion.status}`);
```

## Bridge Workflow

Cross-chain token transfer: **Get Route → Execute Bridge → Track**

### Quote a Bridge

```bash
POST /v2/bridge/quote/{builderId}
Content-Type: application/json

{
  "fromChain": "sol",
  "toChain": "base",
  "fromToken": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "toToken": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "amount": "1000000",
  "userAddress": "WALLET"
}
```

### Execute Bridge

```bash
POST /v2/bridge/swap-and-bridge/{builderId}
Content-Type: application/json

{
  "fromChain": "sol",
  "toChain": "base",
  "fromToken": "EPjFW...",
  "toToken": "0x8335...",
  "amount": "1000000",
  "userAddress": "WALLET",
  "slippage": 1
}
```

Bridge operations return a `jobId`. Poll for completion — bridges can take 2-30 minutes.

## Launchpad Workflow

Create a new token on PumpFun or Raydium LaunchLab.

### Create Token

```bash
POST /v2/dex/{chain}/create
Content-Type: application/json

{
  "userAddress": "WALLET",
  "name": "My Token",
  "symbol": "MTK",
  "uri": "https://arweave.net/METADATA_HASH"
}
```

### Create and Buy (Launchpad-specific)

```bash
POST /v2/dex/launchpad/create-and-buy/{builderId}
Content-Type: application/json

{
  "userAddress": "WALLET",
  "name": "My Token",
  "symbol": "MTK",
  "uri": "https://arweave.net/METADATA_HASH",
  "buyAmount": "100000000"
}
```

### Metadata Upload

Before creating a token, upload metadata to IPFS:

```bash
# Get presigned URL
POST /v2/ipfs/presign

# Upload to returned URL, then use the IPFS hash as uri
```

## Transaction Operations

### Get Gas Price

```bash
GET /v2/transaction/{chain}/gas-price
```

```json
{
  "chain": "eth",
  "gasPrice": "25000000000",
  "maxFeePerGas": "30000000000",
  "maxPriorityFeePerGas": "1500000000"
}
```

### Estimate Gas Limit

```bash
POST /v2/transaction/{chain}/estimate-gas-limit
Content-Type: application/json

{
  "from": "0xSENDER",
  "to": "0xRECEIVER",
  "data": "0xCALLDATA",
  "value": "0"
}
```

### Send Transaction

```bash
POST /v2/transaction/{chain}/send
Content-Type: application/json

{
  "signedTransaction": "BASE64_SIGNED_TX"
}
```

## Job Status Reference

| Status | Description |
|--------|-------------|
| `pending` | Job created, not yet processing |
| `processing` | Transaction submitted, awaiting confirmation |
| `completed` | Transaction confirmed on-chain |
| `failed` | Transaction failed (reverted, timeout, insufficient balance) |

Job response includes:

```json
{
  "id": "job_abc123",
  "status": "completed",
  "transactionHash": "0x...",
  "chain": "sol",
  "createdAt": "2025-03-01T12:00:00Z",
  "completedAt": "2025-03-01T12:00:15Z",
  "result": { /* operation-specific data */ }
}
```

## Aggregator vs Provider Endpoints

**Aggregators** find the best price across multiple DEXes:

```
POST /v2/dex/aggregator/quote/{builderId}
POST /v2/dex/aggregator/swap/{builderId}
```

**Providers** route through a single DEX:

```
POST /v2/dex/swap/quote/{builderId}
POST /v2/dex/swap/swap/{builderId}
```

Use aggregators (Jupiter, Kyberswap, OpenOcean) for best prices. Use providers (Uniswap, PancakeSwap) when targeting a specific pool.

## Trading Backtest

```bash
POST /v2/trading/backtest
Content-Type: application/json

{
  "chain": "sol",
  "token": "TOKEN_ADDRESS",
  "strategy": {
    "trigger": "volume_24h > 3x avg_volume_7d",
    "entry": "market_buy",
    "exit": {
      "take_profit": 0.3,
      "stop_loss": -0.15,
      "time_limit": "24h"
    }
  },
  "startTime": "2025-01-01",
  "endTime": "2025-03-01",
  "initialCapital": 1000
}
```

### Strategy Validation

```bash
POST /v2/trading/strategy/validate
Content-Type: application/json

{
  "strategy": { /* strategy object */ }
}
```

### Available Indicators

```bash
GET /v2/trading/indicators
```

Returns supported technical indicators: RSI, MACD, Bollinger Bands, EMA, SMA, Volume profile, etc.
