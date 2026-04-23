# Strategy Templates

Ready-to-use strategy configurations for `trading/backtest` and `trading/execute`.

## Template: Volume Breakout

```json
{
  "name": "Volume Breakout",
  "trigger": "volume_24h > 3 * avg_volume_7d",
  "entry": "market_buy",
  "exit": {
    "take_profit": 0.3,
    "stop_loss": -0.15,
    "time_limit": "24h"
  },
  "filters": {
    "min_volume_usd": 100000,
    "min_liquidity_usd": 50000,
    "max_top10_holder_pct": 40
  }
}
```

**Expected metrics**: Win rate 40-55%, avg profit/trade 8-15%, Sharpe > 1.0

## Template: Holder Concentration

```json
{
  "name": "Decentralized Holder Entry",
  "trigger": "top10_holder_pct < 25 AND volume_24h_usd > 500000",
  "entry": "market_buy",
  "exit": {
    "take_profit": 0.5,
    "stop_loss": -0.2,
    "time_limit": "48h"
  },
  "filters": {
    "min_holders": 500,
    "security_check": true
  }
}
```

**Expected metrics**: Win rate 35-45%, avg profit/trade 15-25%, higher risk

## Template: New Token Snipe

```json
{
  "name": "New Token Early Entry",
  "trigger": "is_new AND age_minutes < 10 AND volume_usd > 50000",
  "entry": "market_buy",
  "entry_size": "0.5%",
  "exit": {
    "take_profit": 1.0,
    "stop_loss": -0.3,
    "time_limit": "2h"
  },
  "filters": {
    "no_honeypot": true,
    "no_freeze_authority": true,
    "max_top10_holder_pct": 30,
    "min_holder_count": 50
  }
}
```

**Expected metrics**: Win rate 25-35%, avg profit/trade 30-50%, high variance

## Template: RSI Mean Reversion

```json
{
  "name": "RSI Oversold Bounce",
  "trigger": "rsi_4h < 30 AND volume_24h > avg_volume_7d",
  "entry": "market_buy",
  "exit": {
    "rsi_target": 55,
    "stop_loss": -0.2,
    "time_limit": "7d"
  },
  "filters": {
    "min_market_cap_usd": 1000000,
    "min_liquidity_usd": 200000
  }
}
```

**Expected metrics**: Win rate 55-65%, avg profit/trade 5-10%, lower risk

## Template: Graduation Momentum

```json
{
  "name": "Bonding Curve Graduation",
  "trigger": "bonding_progress > 85 AND holder_growth_1h > 10",
  "entry": "market_buy",
  "entry_size": "1%",
  "exit": {
    "take_profit": 1.0,
    "stop_loss": -0.3,
    "time_limit": "6h"
  },
  "filters": {
    "chain": "sol",
    "launchpad": ["pumpfun", "raydium-launchlab"],
    "min_holders": 200
  }
}
```

**Expected metrics**: Win rate 30-40%, avg profit/trade 20-40%, Solana only

## Template: Smart Money Copy

```json
{
  "name": "Whale Copy Trade",
  "trigger": "smart_money_buy AND buy_amount_usd > 10000",
  "entry": "market_buy",
  "entry_delay": "5m",
  "entry_size": "1%",
  "exit": {
    "take_profit": 0.3,
    "stop_loss": -0.15,
    "time_limit": "48h",
    "follow_exit": true
  },
  "filters": {
    "min_wallet_win_rate": 0.6,
    "min_wallet_pnl_usd": 100000
  }
}
```

**Expected metrics**: Win rate 45-55%, avg profit/trade 10-20%, moderate risk

## Template: DCA (Dollar Cost Averaging)

```json
{
  "name": "DCA into Dips",
  "trigger": "price_change_24h < -10",
  "entry": "limit_buy",
  "entry_size": "2%",
  "entry_interval": "4h",
  "max_entries": 5,
  "exit": {
    "take_profit": 0.2,
    "stop_loss": -0.3,
    "time_limit": "14d"
  },
  "filters": {
    "min_market_cap_usd": 10000000,
    "min_liquidity_usd": 500000
  }
}
```

**Expected metrics**: Win rate 60-70%, avg profit/trade 5-8%, low risk

## Backtest Example

```bash
# Using the Volume Breakout template
{"tool": "trading/backtest", "arguments": {
  "chain": "sol",
  "token": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
  "strategy": {
    "trigger": "volume_24h > 3 * avg_volume_7d",
    "entry": "market_buy",
    "exit": {"take_profit": 0.3, "stop_loss": -0.15, "time_limit": "24h"}
  },
  "startTime": "2024-06-01",
  "endTime": "2025-03-01",
  "initialCapital": 1000
}}
```

**Expected output**:

```json
{
  "totalTrades": 47,
  "winRate": 0.489,
  "totalPnl": 1847.23,
  "totalPnlPercent": 84.7,
  "sharpeRatio": 1.32,
  "maxDrawdown": -0.178,
  "avgHoldingPeriod": "8.3h",
  "bestTrade": 312.45,
  "worstTrade": -89.12,
  "pnlCurve": [/* time series */]
}
```

## Interpreting Backtest Results

| Metric | Good | Acceptable | Poor |
|--------|------|-----------|------|
| Sharpe Ratio | > 2.0 | 1.0 - 2.0 | < 1.0 |
| Max Drawdown | < 10% | 10% - 25% | > 25% |
| Win Rate | > 55% | 40% - 55% | < 40% |
| Profit Factor | > 2.0 | 1.5 - 2.0 | < 1.5 |
