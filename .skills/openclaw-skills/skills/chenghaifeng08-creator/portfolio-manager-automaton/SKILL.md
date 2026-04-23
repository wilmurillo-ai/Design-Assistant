---
name: portfolio-manager
description: Intelligent portfolio management for crypto, stocks, and forex. Auto-rebalancing, performance tracking, risk management, and allocation optimization.
version: 1.0.0
author: OpenClaw Agent
tags:
  - portfolio
  - asset-management
  - rebalancing
  - risk-management
  - crypto
  - stocks
  - tracking
  - analytics
homepage: https://github.com/openclaw/skills/portfolio-manager
metadata:
  openclaw:
    emoji: 💼
    pricing:
      basic: "49 USDC"
      pro: "99 USDC (with auto-rebalancing)"
---

# Portfolio Manager 💼

**Intelligent portfolio management for multi-asset investors.**

Auto-rebalancing, performance tracking, risk management, and allocation optimization for crypto, stocks, and forex.

---

## 💰 付费服务

**投资组合顾问**:

| 服务 | 价格 | 交付 |
|------|------|------|
| 组合诊断 | ¥800/次 | 持仓分析 + 优化建议 |
| 配置方案 | ¥2000/份 | 个性化资产配置 |
| 月度调仓 | ¥3000/月 | 每周监控 + 调仓建议 |
| 定制系统 | ¥8000 起 | 自动再平衡系统 |

**联系**: 微信/Telegram 私信，备注"组合管理"

---

## 🎯 What It Solves

Investors struggle with:
- ❌ Manual portfolio tracking across exchanges/wallets
- ❌ Emotional rebalancing decisions
- ❌ No clear performance attribution
- ❌ Poor risk management
- ❌ Missing allocation opportunities
- ❌ Tax calculation complexity

**Portfolio Manager** provides:
- ✅ Unified portfolio view (all assets, all platforms)
- ✅ Automated rebalancing strategies
- ✅ Real-time P&L tracking
- ✅ Risk metrics and alerts
- ✅ Smart allocation suggestions
- ✅ Tax-ready reports

---

## ✨ Features

### 📊 Unified Portfolio Tracking
- Multi-exchange support (Binance, Coinbase, Kraken, etc.)
- Multi-wallet support (MetaMask, Ledger, Trezor)
- Real-time price updates
- P&L tracking (realized + unrealized)
- Historical performance charts

### 🔄 Auto-Rebalancing
- Target allocation enforcement
- Threshold-based rebalancing
- Dollar-cost averaging integration
- Tax-loss harvesting suggestions
- Rebalance scheduling (daily/weekly/monthly)

### 📈 Performance Analytics
- Total return calculation
- Time-weighted returns (TWR)
- Money-weighted returns (IRR)
- Benchmark comparison (BTC, S&P 500, etc.)
- Attribution analysis (which assets drove returns)

### ⚠️ Risk Management
- Portfolio VaR (Value at Risk)
- Maximum drawdown tracking
- Correlation matrix
- Concentration risk alerts
- Volatility monitoring

### 🎯 Allocation Optimization
- Modern Portfolio Theory (MPT) optimization
- Risk parity allocation
- Mean-variance optimization
- Black-Litterman model
- Efficient frontier visualization

### 📑 Reporting & Export
- Performance reports (daily/weekly/monthly)
- Tax reports (FIFO, LIFO, HIFO)
- Transaction history export (CSV, Excel)
- PDF report generation
- Email/SMS alerts

### 🔔 Smart Alerts
- Price alerts (threshold, percentage)
- Allocation drift alerts
- Rebalance reminders
- Risk threshold breaches
- Significant P&L changes

---

## 📦 Installation

```bash
clawhub install portfolio-manager
```

---

## 🚀 Quick Start

### 1. Initialize Portfolio

```javascript
const { PortfolioManager } = require('portfolio-manager');

const portfolio = new PortfolioManager({
  apiKey: 'your-api-key',
  baseCurrency: 'USD',
  exchanges: ['binance', 'coinbase'],
  wallets: ['metamask'],
  riskProfile: 'moderate'
});
```

### 2. Add Holdings

```javascript
// Add exchange holdings
await portfolio.addExchange('binance', {
  apiKey: 'your-binance-key',
  apiSecret: 'your-binance-secret'
});

// Add wallet holdings
await portfolio.addWallet('metamask', {
  address: '0x1234...5678',
  chainId: 1  // Ethereum mainnet
});

// Add manual holdings
await portfolio.addHolding({
  symbol: 'BTC',
  amount: 0.5,
  averageCost: 65000,
  category: 'crypto'
});
```

### 3. Get Portfolio Overview

```javascript
const overview = await portfolio.getOverview();
console.log(overview);
// {
//   totalValue: 125000,
//   totalCost: 100000,
//   totalPnL: 25000,
//   totalPnLPercent: 25.0,
//   dailyPnL: 1500,
//   dailyPnLPercent: 1.2,
//   allocation: {
//     crypto: 60,
//     stocks: 30,
//     cash: 10
//   },
//   topHoldings: [
//     { symbol: 'BTC', value: 45000, percent: 36 },
//     { symbol: 'ETH', value: 25000, percent: 20 },
//     { symbol: 'AAPL', value: 15000, percent: 12 }
//   ]
// }
```

### 4. Set Target Allocation

```javascript
await portfolio.setTargetAllocation({
  crypto: 50,
  stocks: 35,
  cash: 15,
  rebalance: {
    strategy: 'threshold',  // threshold, schedule, or both
    threshold: 5,  // Rebalance when drift > 5%
    schedule: 'monthly'  // Also rebalance monthly
  }
});
```

### 5. Check Rebalance Needs

```javascript
const rebalance = await portfolio.checkRebalance();
console.log(rebalance);
// {
//   needsRebalance: true,
//   drift: 7.2,
//   threshold: 5,
//   trades: [
//     {
//       action: 'SELL',
//       symbol: 'BTC',
//       amount: 0.05,
//       value: 3375,
//       reason: 'Overweight by 7.2%'
//     },
//     {
//       action: 'BUY',
//       symbol: 'ETH',
//       amount: 0.8,
//       value: 2800,
//       reason: 'Underweight by 5.1%'
//     }
//   ],
//   estimatedFees: 25,
//   taxImpact: {
//     shortTermGain: 500,
//     longTermGain: 1200,
//     estimatedTax: 350
//   }
// }
```

### 6. Execute Rebalance

```javascript
const result = await portfolio.rebalance({
  dryRun: false,  // Set true to preview without executing
  optimizeForTax: true,  // Consider tax implications
  limitOrders: true  // Use limit orders instead of market
});

console.log(result);
// {
//   executed: true,
//   tradesExecuted: 5,
//   totalFees: 32.50,
//   newAllocation: { ... },
//   driftAfter: 1.2
// }
```

### 7. Get Performance Report

```javascript
const performance = await portfolio.getPerformance({
  period: '30d',  // 7d, 30d, 90d, 1y, all
  benchmark: 'BTC'  // Compare to BTC
});

console.log(performance);
// {
//   period: '30d',
//   portfolioReturn: 12.5,
//   benchmarkReturn: 8.3,
//   alpha: 4.2,
//   beta: 0.85,
//   sharpeRatio: 1.8,
//   maxDrawdown: -8.5,
//   volatility: 15.2,
//   bestDay: 5.2,
//   worstDay: -3.8,
//   positiveDays: 20,
//   negativeDays: 10
// }
```

---

## 💡 Advanced Usage

### Modern Portfolio Theory Optimization

```javascript
const optimization = await portfolio.optimizeMPT({
  riskFreeRate: 0.05,  // 5% risk-free rate
  targetReturn: 0.15,  // Target 15% annual return
  constraints: {
    maxSingleAsset: 0.25,  // No asset > 25%
    minCrypto: 0.3,  // At least 30% crypto
    maxCrypto: 0.7  // No more than 70% crypto
  }
});

console.log(optimization);
// Returns optimal allocation with efficient frontier data
```

### Risk Parity Allocation

```javascript
const riskParity = await portfolio.allocateRiskParity({
  assets: ['BTC', 'ETH', 'SOL', 'AAPL', 'GOOGL', 'BND'],
  targetVolatility: 0.12  // 12% annual volatility
});

// Each asset contributes equally to portfolio risk
```

### Tax-Loss Harvesting

```javascript
const harvesting = await portfolio.findTaxLossHarvesting({
  minLoss: 500,  // Minimum loss to harvest
  washSaleWindow: 30,  // Days to avoid wash sale
  similarAssets: true  // Suggest similar replacement assets
});

console.log(harvesting);
// {
//   opportunities: [
//     {
//       symbol: 'ETH',
//       currentLoss: -1200,
//       sellAmount: 0.5,
//       taxBenefit: 360,
//       replacement: 'ETH2'  // Similar but not wash sale
//     }
//   ],
//   totalTaxBenefit: 360
// }
```

### Correlation Analysis

```javascript
const correlation = await portfolio.getCorrelationMatrix({
  period: '90d',
  assets: ['BTC', 'ETH', 'SOL', 'AAPL', 'TSLA', 'GLD']
});

// Returns correlation matrix for diversification analysis
```

### VaR Calculation

```javascript
const varMetrics = await portfolio.calculateVaR({
  confidence: 0.95,  // 95% confidence
  horizon: 1,  // 1 day
  method: 'historical'  // historical, parametric, or monte-carlo
});

console.log(varMetrics);
// {
//   var95: 0.045,  // 4.5% daily VaR
//   var99: 0.068,  // 6.8% daily VaR
//   expectedShortfall: 0.055,
//   interpretation: '95% confidence that daily loss won\'t exceed 4.5%'
// }
```

### Export Reports

```javascript
// Export to CSV
await portfolio.exportTransactions({
  format: 'csv',
  startDate: '2025-01-01',
  endDate: '2026-03-19',
  path: './reports/transactions.csv'
});

// Export to PDF
await portfolio.exportPerformanceReport({
  format: 'pdf',
  period: 'ytd',
  includeCharts: true,
  path: './reports/performance-ytd.pdf'
});

// Export for taxes
await portfolio.exportTaxReport({
  year: 2025,
  method: 'FIFO',  // FIFO, LIFO, HIFO
  country: 'US',
  path: './reports/taxes-2025.csv'
});
```

---

## 🔧 Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | required | API key for Portfolio Manager |
| `baseCurrency` | string | 'USD' | Base currency for reporting |
| `exchanges` | array | [] | List of exchanges to connect |
| `wallets` | array | [] | List of wallets to track |
| `riskProfile` | string | 'moderate' | Risk tolerance |
| `rebalanceEnabled` | boolean | false | Enable auto-rebalancing |
| `alertChannels` | array | ['console'] | Alert delivery channels |

---

## 📊 API Methods

### Portfolio Management
- `getOverview()` - Get portfolio summary
- `getHoldings()` - Get all holdings with details
- `getAllocation()` - Get current allocation breakdown
- `addHolding(holding)` - Add manual holding
- `removeHolding(symbol)` - Remove a holding

### Exchange/Wallet Integration
- `addExchange(name, credentials)` - Connect exchange
- `addWallet(name, config)` - Connect wallet
- `syncExchange(name)` - Sync exchange holdings
- `syncWallet(name)` - Sync wallet holdings

### Rebalancing
- `setTargetAllocation(allocation)` - Set target weights
- `checkRebalance()` - Check if rebalance needed
- `rebalance(options)` - Execute rebalance
- `getRebalanceHistory()` - Get past rebalances

### Performance
- `getPerformance(options)` - Get performance metrics
- `getReturns(period)` - Get returns for period
- `getBenchmarkComparison(benchmark)` - Compare to benchmark
- `getAttribution()` - Get return attribution

### Risk
- `getRiskMetrics()` - Get portfolio risk metrics
- `calculateVaR(options)` - Calculate Value at Risk
- `getCorrelationMatrix(options)` - Get asset correlations
- `getDrawdownAnalysis()` - Analyze drawdowns

### Optimization
- `optimizeMPT(options)` - Modern Portfolio Theory optimization
- `allocateRiskParity(options)` - Risk parity allocation
- `getEfficientFrontier()` - Calculate efficient frontier

### Tax
- `findTaxLossHarvesting(options)` - Find tax-loss opportunities
- `calculateTaxLiability(year)` - Estimate tax liability
- `getCostBasis(method)` - Get cost basis by method

### Export
- `exportTransactions(options)` - Export transaction history
- `exportPerformanceReport(options)` - Export performance report
- `exportTaxReport(options)` - Export tax report

---

## 📁 File Structure

```
portfolio-manager/
├── SKILL.md
├── index.js
├── package.json
├── _meta.json
├── README.md
├── src/
│   ├── portfolio.js
│   ├── rebalancer.js
│   ├── performance.js
│   ├── risk.js
│   ├── optimizer.js
│   ├── tax.js
│   └── export.js
└── tests/
    └── portfolio-manager.test.js
```

---

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Basic** | $49 | Portfolio tracking, performance analytics, manual rebalancing |
| **Pro** | $99 | + Auto-rebalancing, tax optimization, MPT optimization, advanced reports |

---

## 📝 Changelog

### v1.0.0 (2026-03-19)
- Initial release
- Multi-exchange/wallet tracking
- Auto-rebalancing engine
- Performance analytics
- Risk metrics (VaR, drawdown, correlation)
- MPT optimization
- Tax-loss harvesting
- Report export (CSV, PDF, Excel)

---

## ⚠️ Disclaimer

**This tool is for portfolio management and tracking only.**

- Not financial advice
- Past performance does not guarantee future results
- Cryptocurrency investments are highly volatile
- Always do your own research (DYOR)
- Consult a tax professional for tax advice

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🙏 Support

- GitHub: https://github.com/openclaw/skills/portfolio-manager
- Discord: OpenClaw Community
- Email: support@openclaw.ai

---

*Built with ❤️ by OpenClaw Agent - Your Intelligent Portfolio Manager*
