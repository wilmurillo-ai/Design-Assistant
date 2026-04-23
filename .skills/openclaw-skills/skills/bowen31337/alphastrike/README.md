# AlphaStrike

Rule-based trading signal generator for **BTC, ETH, SOL** on Hyperliquid perpetuals.

## Installation

```bash
cp -r . ~/.openclaw/workspace/skills/alphastrike/
```

## Usage

```bash
# Generate signal for one symbol
uv run python scripts/signal.py --symbol BTC

# Run full scan (BTC/ETH/SOL)
uv run python scripts/signal.py --all

# Execute workflow
uv run python execute.py
```

## Indicators

| Indicator | Parameters | Signal |
|-----------|-----------|--------|
| RSI | 14 period | >70 overbought, <30 oversold |
| MACD | standard | trend + momentum |
| EMA Crossover | 9/21 | short-term trend |
| Bollinger Bands | 20, 2σ | volatility breakout |
| Volume Ratio | — | >1.5x = strong confirmation |

## License

MIT — see [LICENSE](./LICENSE)
