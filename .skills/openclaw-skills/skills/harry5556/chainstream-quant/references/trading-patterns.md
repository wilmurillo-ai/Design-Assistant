# Trading Patterns

Common trading strategies for ChainStream's quantitative trading tools.

## MEME Coin Sniper

Monitor new token listings and buy early high-potential tokens.

**Signal**: New token with volume > $100K in first 5 minutes AND holder concentration < 30%.

```json
{
  "strategy": {
    "trigger": "is_new AND volume_5m_usd > 100000 AND top10_holder_pct < 30",
    "entry": "market_buy",
    "exit": {
      "take_profit": 0.5,
      "stop_loss": -0.2,
      "time_limit": "2h"
    }
  }
}
```

**Data gathering**:

```bash
# Monitor new tokens in real-time
{"tool": "market/trending", "arguments": {"chain": "sol", "category": "new", "limit": 20}}

# Analyze a candidate
{"tool": "tokens/analyze", "arguments": {"chain": "sol", "address": "NEW_TOKEN", "sections": ["overview","holders","security"]}}
```

**Key checks before entry**:
- Security scan passes (no honeypot, no freeze authority)
- Deployer wallet has good history (`/v2/token/{chain}/dev/{devAddress}/tokens`)
- Top 10 holders own < 30%
- Liquidity > $50K

## Smart Money Follow

Track whale wallets and mirror profitable trades.

**Signal**: Known profitable wallet buys token with > $10K position.

```json
{
  "strategy": {
    "trigger": "smart_money_buy AND buy_amount_usd > 10000",
    "entry": "market_buy",
    "entry_delay": "5m",
    "position_size": "1%",
    "exit": {
      "take_profit": 0.3,
      "stop_loss": -0.15,
      "time_limit": "48h"
    }
  }
}
```

**Workflow**:

```bash
# Find top traders
GET /v2/trade/sol/top-traders

# Profile a whale wallet
{"tool": "wallets/profile", "arguments": {"chain": "sol", "address": "WHALE_WALLET", "include": ["holdings","pnl"]}}

# Monitor their trades in real-time
# WebSocket: dex-wallet-trade:sol_WHALE_WALLET

# When they buy, analyze the token
{"tool": "tokens/analyze", "arguments": {"chain": "sol", "address": "TOKEN_THEY_BOUGHT"}}
```

## Mean Reversion

Buy oversold tokens and sell when indicators normalize.

**Signal**: RSI < 30 on 4h timeframe with volume above average.

```json
{
  "strategy": {
    "trigger": "rsi_4h < 30 AND volume_24h > avg_volume_7d",
    "entry": "market_buy",
    "exit": {
      "rsi_target": 55,
      "stop_loss": -0.2,
      "time_limit": "7d"
    }
  }
}
```

**Backtest**:

```bash
{"tool": "trading/backtest", "arguments": {"chain": "sol", "token": "TOKEN", "strategy": {"trigger": "rsi_4h < 30 AND volume_24h > avg_volume_7d", "entry": "market_buy", "exit": {"rsi_target": 55, "stop_loss": -0.2, "time_limit": "7d"}}, "startTime": "2024-06-01", "endTime": "2025-03-01", "initialCapital": 5000}}
```

## Volume Breakout

Enter on volume spikes signaling momentum.

**Signal**: 24h volume exceeds 3x the 7-day average.

```json
{
  "strategy": {
    "trigger": "volume_24h > 3 * avg_volume_7d",
    "entry": "market_buy",
    "exit": {
      "take_profit": 0.3,
      "stop_loss": -0.15,
      "time_limit": "24h"
    }
  }
}
```

## Graduation Play

Buy tokens about to graduate from bonding curve to full DEX listing.

**Signal**: Bonding curve progress > 85% with growing holder count.

```json
{
  "strategy": {
    "trigger": "bonding_progress > 85 AND holder_growth_1h > 10",
    "entry": "market_buy",
    "exit": {
      "take_profit": 1.0,
      "stop_loss": -0.3,
      "time_limit": "6h"
    }
  }
}
```

**Data gathering**:

```bash
{"tool": "market/trending", "arguments": {"chain": "sol", "category": "graduating", "limit": 10}}
```

## Holder Concentration Alert

Buy tokens with decentralized holding patterns and high volume.

```json
{
  "strategy": {
    "trigger": "top10_holder_pct < 25 AND volume_24h_usd > 500000",
    "entry": "market_buy",
    "exit": {
      "take_profit": 0.5,
      "stop_loss": -0.2,
      "time_limit": "48h"
    }
  }
}
```

## Cross-Chain Arbitrage

Detect price differences across chains and bridge for profit.

**Workflow**:

```bash
# Compare same token on different chains
{"tool": "tokens/compare", "arguments": {"tokens": [{"chain": "sol", "address": "USDC_SOL"}, {"chain": "base", "address": "USDC_BASE"}]}}

# If spread > bridge cost + slippage:
# 1. Swap to bridge token
# 2. Bridge via LiFi
# 3. Swap on destination chain
POST /v2/bridge/swap-and-bridge/lifi
```

## Risk Management Rules

Apply these rules across all strategies:

| Rule | Value | Reason |
|------|-------|--------|
| Max position per trade | 2-5% of portfolio | Prevent single-trade blowup |
| Max concurrent positions | 5 | Diversification |
| Daily loss limit | -10% | Circuit breaker |
| Min liquidity | $50K | Avoid slippage traps |
| Security check | Required | No honeypots or frozen tokens |
