---
metadata.openclaw:
  always: true
  reason: "AlphaStrike trading strategy — always relevant for this workspace"
---


# AlphaStrike v2

Rule-based trading signal generator for **BTC, ETH, SOL** on Hyperliquid perpetuals.

## Indicators

| Indicator | Parameters | Signal |
|-----------|-----------|--------|
| RSI | 14 period | >70 overbought, <30 oversold |
| MACD | standard | trend + momentum |
| EMA Crossover | 9/21 | short-term trend |
| Bollinger Bands | 20, 2σ | volatility breakout |
| Volume Ratio | — | >1.5x = strong confirmation |

## Quick Start

```bash
cd ~/.openclaw/workspace/skills/alphastrike

# Generate signal for one symbol
uv run python scripts/signal.py --symbol BTC

# Run full scan (BTC/ETH/SOL)
uv run python scripts/signal.py --all

# Execute workflow
uv run python execute.py
```

## Output Format

```json
{
  "symbol": "BTC",
  "signal": "LONG",
  "confidence": 0.78,
  "indicators": { "rsi": 28, "macd": "bullish", "ema_cross": "golden" },
  "reasoning": "RSI oversold + MACD bullish cross + volume confirmation"
}
```

## Files

- `scripts/signal.py` — signal generator
- `execute.py` — workflow runner
- `workflows/` — workflow definitions
- `data/` — historical data cache
