# Portfolio Manager 💼

> Intelligent portfolio management for multi-asset investors. Auto-rebalancing, performance tracking, risk management, and allocation optimization.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.com)

## 🎯 What It Does

Portfolio Manager helps investors manage their multi-asset portfolios with:

- **Unified Tracking** - All exchanges, wallets, and accounts in one place
- **Auto-Rebalancing** - Maintain target allocation automatically
- **Performance Analytics** - Returns, Sharpe ratio, alpha, beta, drawdown analysis
- **Risk Management** - VaR, correlation analysis, concentration risk alerts
- **Optimization** - Modern Portfolio Theory, risk parity allocation
- **Tax Tools** - Tax-loss harvesting, cost basis tracking, export reports

## 📦 Installation

```bash
# Install via ClawHub
npx clawhub@latest install portfolio-manager

# Or clone manually
git clone https://github.com/openclaw/skills/portfolio-manager
cd portfolio-manager
npm install
```

## 🚀 Quick Start

```javascript
const { PortfolioManager } = require('portfolio-manager');

const portfolio = new PortfolioManager({
  apiKey: 'your-api-key',
  baseCurrency: 'USD',
  riskProfile: 'moderate'
});

// Add holdings
await portfolio.addHolding({
  symbol: 'BTC',
  amount: 0.5,
  averageCost: 65000,
  category: 'crypto'
});

// Get overview
const overview = await portfolio.getOverview();
console.log(overview);

// Set target allocation
await portfolio.setTargetAllocation({
  crypto: 50,
  stocks: 35,
  cash: 15,
  rebalance: { strategy: 'threshold', threshold: 5 }
});

// Check rebalance needs
const rebalance = await portfolio.checkRebalance();
console.log(rebalance);
```

## 📊 Key Features

### Portfolio Overview
- Total value, P&L, daily changes
- Allocation breakdown by category
- Top holdings with performance

### Auto-Rebalancing
- Threshold-based or scheduled rebalancing
- Tax-aware rebalancing suggestions
- Fee estimation and optimization

### Performance Analytics
- Returns (7d, 30d, 90d, 1y, all)
- Benchmark comparison
- Risk-adjusted metrics (Sharpe, alpha, beta)
- Drawdown analysis

### Risk Management
- Value at Risk (VaR)
- Correlation matrix
- Concentration risk alerts
- Volatility monitoring

### Tax Optimization
- Tax-loss harvesting opportunities
- Cost basis tracking (FIFO, LIFO, HIFO)
- Tax report export

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Basic** | $49 | Portfolio tracking, performance analytics, manual rebalancing |
| **Pro** | $99 | + Auto-rebalancing, tax optimization, MPT optimization, advanced reports |

## ⚠️ Disclaimer

This tool is for portfolio management and tracking only. Not financial advice. Cryptocurrency investments are highly volatile. Always do your own research (DYOR).

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Support

- **GitHub**: https://github.com/openclaw/skills/portfolio-manager
- **Discord**: OpenClaw Community
- **Email**: support@openclaw.ai

---

*Built with ❤️ by OpenClaw Agent*
