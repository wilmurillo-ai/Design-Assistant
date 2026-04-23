# Trading Decision Pro 🧠

> AI-powered trading decision assistant with market sentiment analysis, risk assessment, and real-time trade recommendations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.com)

## 🎯 What It Does

Trading Decision Pro helps traders make better decisions by providing:

- **Market Sentiment Analysis** - Multi-source sentiment scoring (social, news, technical, on-chain)
- **Trade Setup Analyzer** - Entry, stop-loss, take-profit recommendations with confidence scores
- **Position Sizing Calculator** - Risk-based position sizing for optimal capital allocation
- **Portfolio Risk Assessment** - Correlation analysis, exposure tracking, drawdown protection
- **Pattern Recognition** - Automated chart pattern detection with reliability scoring
- **Smart Alerts** - Price breakouts, sentiment shifts, risk threshold breaches

## 📦 Installation

```bash
# Install via ClawHub
npx clawhub@latest install trading-decision-pro

# Or clone manually
git clone https://github.com/openclaw/skills/trading-decision-pro
cd trading-decision-pro
npm install
```

## 🚀 Quick Start

```javascript
const { TradingDecisionPro } = require('trading-decision-pro');

const trader = new TradingDecisionPro({
  apiKey: 'your-api-key',
  markets: ['crypto', 'stocks'],
  riskProfile: 'moderate',
  maxPositionSize: 0.1
});

// Get sentiment
const sentiment = await trader.getSentiment('BTC');
console.log(sentiment);

// Analyze trade
const analysis = await trader.analyzeTrade({
  symbol: 'BTC/USDT',
  direction: 'long',
  entryPrice: 67500,
  stopLoss: 65000,
  takeProfit: 72000
});
console.log(analysis);

// Calculate position size
const sizing = await trader.calculatePosition({
  symbol: 'ETH',
  entryPrice: 3500,
  stopLoss: 3300,
  portfolioValue: 10000,
  maxRisk: 0.02
});
console.log(sizing);
```

## 📊 API Reference

### `getSentiment(symbol)`
Get market sentiment score for a symbol.

**Returns:**
```javascript
{
  symbol: 'BTC',
  score: 72,  // 0-100 (bullish)
  label: 'Bullish',
  sources: { social: 68, news: 75, technical: 74 },
  trend: 'improving',
  confidence: 0.85
}
```

### `analyzeTrade(tradeSetup)`
Analyze a specific trade setup.

**Parameters:**
- `symbol` - Trading pair (e.g., 'BTC/USDT')
- `direction` - 'long' or 'short'
- `entryPrice` - Entry price
- `stopLoss` - Stop loss price
- `takeProfit` - Take profit price

**Returns:**
```javascript
{
  recommendation: 'ENTER',  // ENTER, HOLD, or AVOID
  confidence: 78,  // 0-100
  riskReward: 1.8,
  winProbability: 0.65,
  suggestedSize: 0.08,  // 8% of portfolio
  reasoning: [...],
  warnings: [...]
}
```

### `calculatePosition(params)`
Calculate optimal position size.

**Parameters:**
- `symbol` - Trading symbol
- `entryPrice` - Entry price
- `stopLoss` - Stop loss price
- `portfolioValue` - Total portfolio value
- `maxRisk` - Maximum risk as % (default: 0.02 = 2%)

**Returns:**
```javascript
{
  positionSize: 0.57,  // Asset amount
  positionValue: 1995,  // USD
  portfolioPercent: 19.95,
  riskAmount: 114,  // USD at stop
  riskPercent: 1.14
}
```

### `getPortfolioRisk(params)`
Assess overall portfolio risk.

**Parameters:**
- `positions` - Array of current positions
- `totalValue` - Total portfolio value

**Returns:**
```javascript
{
  totalExposure: 0.65,
  correlationRisk: 'HIGH',
  maxDrawdown: 0.18,
  var95: 0.12,
  recommendations: [...]
}
```

### `multiTimeframeAnalysis(symbol, options)`
Analyze multiple timeframes for confluence.

### `detectPatterns(symbol, options)`
Detect chart patterns with reliability scoring.

### `backtest(strategy, options)`
Backtest trading strategies with historical data.

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Basic** | $39 | Sentiment analysis, trade analysis, position sizing |
| **Pro** | $79 | + Pattern recognition, backtesting, advanced alerts, portfolio risk |

## ⚠️ Risk Disclaimer

**Trading involves substantial risk of loss.**

This tool provides analysis and recommendations, not financial advice. Past performance does not guarantee future results. Always do your own research (DYOR) and never risk more than you can afford to lose.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Support

- **GitHub**: https://github.com/openclaw/skills/trading-decision-pro
- **Discord**: OpenClaw Community
- **Email**: support@openclaw.ai

---

*Built with ❤️ by OpenClaw Agent*
