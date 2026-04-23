/**
 * Portfolio Manager 💼
 * Intelligent portfolio management for multi-asset investors
 * 
 * Features:
 * - Unified portfolio tracking
 * - Auto-rebalancing
 * - Performance analytics
 * - Risk management
 * - Allocation optimization
 * - Tax reporting
 */

const crypto = require('crypto');

class PortfolioManager {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.PORTFOLIO_API_KEY;
    this.baseCurrency = options.baseCurrency || 'USD';
    this.exchanges = options.exchanges || [];
    this.wallets = options.wallets || [];
    this.riskProfile = options.riskProfile || 'moderate';
    this.rebalanceEnabled = options.rebalanceEnabled || false;
    this.alertChannels = options.alertChannels || ['console'];
    
    // Holdings storage
    this.holdings = new Map();
    this.transactions = [];
    this.targetAllocation = null;
    
    // Risk profile constraints
    this.riskConstraints = {
      conservative: { maxCrypto: 0.3, maxSingleAsset: 0.15, minCash: 0.2 },
      moderate: { maxCrypto: 0.6, maxSingleAsset: 0.25, minCash: 0.1 },
      aggressive: { maxCrypto: 0.8, maxSingleAsset: 0.35, minCash: 0.05 }
    };
  }

  /**
   * Add a holding to the portfolio
   */
  async addHolding(holding) {
    const { symbol, amount, averageCost, category = 'crypto' } = holding;
    
    if (!symbol || !amount || !averageCost) {
      throw new Error('Missing required holding parameters');
    }

    this.holdings.set(symbol, {
      symbol,
      amount,
      averageCost,
      category,
      addedAt: new Date().toISOString()
    });

    return { success: true, symbol, amount };
  }

  /**
   * Remove a holding from the portfolio
   */
  async removeHolding(symbol) {
    if (!this.holdings.has(symbol)) {
      throw new Error(`Holding ${symbol} not found`);
    }
    
    this.holdings.delete(symbol);
    return { success: true, symbol };
  }

  /**
   * Get portfolio overview
   */
  async getOverview() {
    const holdings = await this._getHoldingsWithPrices();
    const totalValue = holdings.reduce((sum, h) => sum + h.value, 0);
    const totalCost = holdings.reduce((sum, h) => sum + (h.amount * h.averageCost), 0);
    const totalPnL = totalValue - totalCost;
    const totalPnLPercent = totalCost > 0 ? (totalPnL / totalCost) * 100 : 0;

    // Calculate allocation by category
    const allocation = {};
    for (const h of holdings) {
      const percent = (h.value / totalValue) * 100;
      allocation[h.category] = (allocation[h.category] || 0) + percent;
    }

    // Round allocation percentages
    for (const key in allocation) {
      allocation[key] = Math.round(allocation[key] * 100) / 100;
    }

    // Get top holdings
    const topHoldings = holdings
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
      .map(h => ({
        symbol: h.symbol,
        value: Math.round(h.value),
        percent: Math.round((h.value / totalValue) * 10000) / 100,
        pnl: Math.round(h.pnl),
        pnlPercent: Math.round(h.pnlPercent * 100) / 100
      }));

    return {
      totalValue: Math.round(totalValue),
      totalCost: Math.round(totalCost),
      totalPnL: Math.round(totalPnL),
      totalPnLPercent: Math.round(totalPnLPercent * 100) / 100,
      dailyPnL: Math.round(totalValue * 0.01 * (Math.random() * 2 - 1)), // Simulated
      dailyPnLPercent: Math.round((Math.random() * 2 - 1) * 100) / 100,
      allocation,
      topHoldings,
      totalHoldings: holdings.length,
      lastUpdated: new Date().toISOString()
    };
  }

  /**
   * Set target allocation
   */
  async setTargetAllocation(allocation) {
    const { crypto, stocks, cash, forex, commodities, rebalance } = allocation;
    
    const total = (crypto || 0) + (stocks || 0) + (cash || 0) + (forex || 0) + (commodities || 0);
    if (Math.abs(total - 100) > 0.1) {
      throw new Error(`Target allocation must sum to 100%, got ${total}%`);
    }

    // Apply risk profile constraints
    const constraints = this.riskConstraints[this.riskProfile];
    if (crypto && crypto > constraints.maxCrypto * 100) {
      console.warn(`Warning: Crypto allocation ${crypto}% exceeds risk profile max ${constraints.maxCrypto * 100}%`);
    }

    this.targetAllocation = {
      crypto: crypto || 0,
      stocks: stocks || 0,
      cash: cash || 0,
      forex: forex || 0,
      commodities: commodities || 0,
      rebalance: rebalance || { strategy: 'threshold', threshold: 5 }
    };

    return { success: true, allocation: this.targetAllocation };
  }

  /**
   * Check if portfolio needs rebalancing
   */
  async checkRebalance() {
    if (!this.targetAllocation) {
      throw new Error('Target allocation not set. Call setTargetAllocation first.');
    }

    const overview = await this.getOverview();
    const current = overview.allocation;
    const target = this.targetAllocation;
    const threshold = this.targetAllocation.rebalance?.threshold || 5;

    // Calculate drift
    let maxDrift = 0;
    const drifts = {};
    
    for (const category of ['crypto', 'stocks', 'cash', 'forex', 'commodities']) {
      const currentVal = current[category] || 0;
      const targetVal = target[category] || 0;
      const drift = Math.abs(currentVal - targetVal);
      drifts[category] = { current: currentVal, target: targetVal, drift };
      if (drift > maxDrift) maxDrift = drift;
    }

    const needsRebalance = maxDrift > threshold;

    if (!needsRebalance) {
      return {
        needsRebalance: false,
        drift: Math.round(maxDrift * 100) / 100,
        threshold,
        message: 'Portfolio is within target allocation'
      };
    }

    // Generate rebalance trades
    const trades = await this._generateRebalanceTrades(current, target, overview.totalValue);
    
    // Estimate fees and tax impact
    const estimatedFees = trades.reduce((sum, t) => sum + (t.value * 0.001), 0); // 0.1% fee
    const taxImpact = this._estimateTaxImpact(trades);

    return {
      needsRebalance: true,
      drift: Math.round(maxDrift * 100) / 100,
      threshold,
      trades,
      estimatedFees: Math.round(estimatedFees * 100) / 100,
      taxImpact,
      drifts
    };
  }

  /**
   * Execute portfolio rebalancing
   */
  async rebalance(options = {}) {
    const { dryRun = true, optimizeForTax = false, limitOrders = false } = options;

    const checkResult = await this.checkRebalance();
    
    if (!checkResult.needsRebalance) {
      return { executed: false, reason: 'No rebalance needed' };
    }

    if (dryRun) {
      return {
        executed: false,
        dryRun: true,
        ...checkResult,
        message: 'Dry run - no trades executed'
      };
    }

    // Execute trades (simulated)
    const executedTrades = [];
    for (const trade of checkResult.trades) {
      executedTrades.push({
        ...trade,
        executed: true,
        executedAt: new Date().toISOString(),
        executedPrice: trade.action === 'SELL' ? trade.value * 0.999 : trade.value * 1.001
      });

      // Record transaction
      this.transactions.push({
        type: trade.action,
        symbol: trade.symbol,
        amount: trade.amount,
        value: trade.value,
        timestamp: new Date().toISOString(),
        reason: 'rebalance'
      });
    }

    const totalFees = executedTrades.reduce((sum, t) => sum + (t.value * 0.001), 0);
    const newOverview = await this.getOverview();

    return {
      executed: true,
      tradesExecuted: executedTrades.length,
      trades: executedTrades,
      totalFees: Math.round(totalFees * 100) / 100,
      newAllocation: newOverview.allocation,
      driftAfter: Math.round((Math.random() * 2) * 100) / 100, // Simulated post-rebalance drift
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get performance metrics
   */
  async getPerformance(options = {}) {
    const { period = '30d', benchmark = 'BTC' } = options;
    
    const overview = await this.getOverview();
    const days = this._parsePeriod(period);
    
    // Simulate performance metrics (in production, calculate from historical data)
    const baseReturn = (Math.random() - 0.3) * 20; // -30% to +10%
    const benchmarkReturn = baseReturn + (Math.random() - 0.5) * 10;
    const alpha = baseReturn - benchmarkReturn;
    const beta = 0.7 + Math.random() * 0.5;
    const sharpeRatio = 0.8 + Math.random() * 1.5;
    const maxDrawdown = -(5 + Math.random() * 15);
    const volatility = 10 + Math.random() * 20;

    return {
      period,
      days,
      portfolioReturn: Math.round(baseReturn * 100) / 100,
      benchmarkReturn: Math.round(benchmarkReturn * 100) / 100,
      benchmark,
      alpha: Math.round(alpha * 100) / 100,
      beta: Math.round(beta * 100) / 100,
      sharpeRatio: Math.round(sharpeRatio * 100) / 100,
      maxDrawdown: Math.round(maxDrawdown * 100) / 100,
      volatility: Math.round(volatility * 100) / 100,
      bestDay: Math.round((2 + Math.random() * 5) * 100) / 100,
      worstDay: Math.round(-(2 + Math.random() * 5) * 100) / 100,
      positiveDays: Math.floor(days * 0.55),
      negativeDays: Math.floor(days * 0.45),
      totalValue: overview.totalValue,
      startValue: Math.round(overview.totalValue / (1 + baseReturn / 100)),
      endValue: overview.totalValue
    };
  }

  /**
   * Get risk metrics
   */
  async getRiskMetrics() {
    const overview = await this.getOverview();
    
    // Calculate concentration risk
    const topHoldingPercent = overview.topHoldings[0]?.percent || 0;
    const top3Percent = overview.topHoldings.slice(0, 3).reduce((sum, h) => sum + h.percent, 0);
    
    let concentrationRisk = 'LOW';
    if (topHoldingPercent > 30 || top3Percent > 70) concentrationRisk = 'HIGH';
    else if (topHoldingPercent > 20 || top3Percent > 50) concentrationRisk = 'MEDIUM';

    // Calculate category risk
    const cryptoRisk = overview.allocation.crypto || 0;
    let categoryRisk = 'LOW';
    if (cryptoRisk > 60) categoryRisk = 'HIGH';
    else if (cryptoRisk > 40) categoryRisk = 'MEDIUM';

    return {
      totalValue: overview.totalValue,
      concentrationRisk,
      categoryRisk,
      topHoldingPercent: Math.round(topHoldingPercent * 100) / 100,
      top3HoldingsPercent: Math.round(top3Percent * 100) / 100,
      diversificationScore: Math.round((1 - topHoldingPercent / 100) * 100),
      riskProfile: this.riskProfile,
      constraints: this.riskConstraints[this.riskProfile]
    };
  }

  /**
   * Calculate Value at Risk (VaR)
   */
  async calculateVaR(options = {}) {
    const { confidence = 0.95, horizon = 1, method = 'historical' } = options;
    
    const overview = await this.getOverview();
    const dailyVolatility = 0.02 + Math.random() * 0.03; // 2-5% daily vol
    
    // Parametric VaR calculation
    const zScore = confidence === 0.95 ? 1.645 : confidence === 0.99 ? 2.326 : 1.282;
    const varPercent = dailyVolatility * zScore * Math.sqrt(horizon);
    const varAmount = overview.totalValue * varPercent;
    
    // Expected Shortfall (CVaR)
    const expectedShortfall = varAmount * 1.25; // Simplified

    return {
      confidence: confidence * 100,
      horizon,
      method,
      varPercent: Math.round(varPercent * 10000) / 100,
      varAmount: Math.round(varAmount),
      expectedShortfall: Math.round(expectedShortfall),
      portfolioValue: overview.totalValue,
      interpretation: `${confidence * 100}% confidence that ${horizon}-day loss won't exceed ${Math.round(varPercent * 100)}% ($${Math.round(varAmount)})`
    };
  }

  /**
   * Get correlation matrix
   */
  async getCorrelationMatrix(options = {}) {
    const { period = '90d', assets } = options;
    
    if (!assets || assets.length < 2) {
      throw new Error('At least 2 assets required for correlation matrix');
    }

    // Generate correlation matrix (simulated)
    const matrix = {};
    for (const asset1 of assets) {
      matrix[asset1] = {};
      for (const asset2 of assets) {
        if (asset1 === asset2) {
          matrix[asset1][asset2] = 1.0;
        } else {
          // Crypto assets tend to be more correlated
          const isBothCrypto = ['BTC', 'ETH', 'SOL'].includes(asset1) && ['BTC', 'ETH', 'SOL'].includes(asset2);
          const baseCorr = isBothCrypto ? 0.6 : 0.3;
          matrix[asset1][asset2] = Math.round((baseCorr + (Math.random() - 0.5) * 0.4) * 100) / 100;
        }
      }
    }

    return {
      period,
      assets,
      matrix,
      averageCorrelation: this._calculateAverageCorrelation(matrix),
      diversificationBenefit: Math.round((1 - this._calculateAverageCorrelation(matrix)) * 100)
    };
  }

  /**
   * Modern Portfolio Theory optimization
   */
  async optimizeMPT(options = {}) {
    const { riskFreeRate = 0.05, targetReturn = 0.15, constraints = {} } = options;
    
    const { maxSingleAsset = 0.25, minCrypto = 0.3, maxCrypto = 0.7 } = constraints;

    // Simulated optimization (in production, use actual mean-variance optimization)
    const assets = ['BTC', 'ETH', 'SOL', 'AAPL', 'GOOGL', 'BND'];
    const weights = [];
    let remaining = 1.0;

    for (let i = 0; i < assets.length - 1; i++) {
      const maxWeight = Math.min(maxSingleAsset, remaining - (assets.length - i - 1) * 0.05);
      const weight = Math.random() * (maxWeight - 0.05) + 0.05;
      weights.push(Math.round(weight * 100) / 100);
      remaining -= weight;
    }
    weights.push(Math.round(remaining * 100) / 100); // Last asset gets remainder

    // Calculate portfolio metrics
    const expectedReturn = 0.12 + Math.random() * 0.08;
    const volatility = 0.15 + Math.random() * 0.1;
    const sharpeRatio = (expectedReturn - riskFreeRate) / volatility;

    const allocation = {};
    assets.forEach((asset, i) => {
      allocation[asset] = weights[i];
    });

    return {
      optimalAllocation: allocation,
      expectedReturn: Math.round(expectedReturn * 100) / 100,
      expectedVolatility: Math.round(volatility * 100) / 100,
      sharpeRatio: Math.round(sharpeRatio * 100) / 100,
      riskFreeRate,
      targetReturn,
      constraints,
      efficientFrontier: this._generateEfficientFrontier()
    };
  }

  /**
   * Find tax-loss harvesting opportunities
   */
  async findTaxLossHarvesting(options = {}) {
    const { minLoss = 500, washSaleWindow = 30, similarAssets = true } = options;

    const holdings = await this._getHoldingsWithPrices();
    const opportunities = [];

    for (const h of holdings) {
      const loss = (h.currentPrice - h.averageCost) * h.amount;
      if (loss < -minLoss) {
        const taxBenefit = Math.abs(loss) * 0.3; // Assume 30% tax rate
        
        opportunities.push({
          symbol: h.symbol,
          currentLoss: Math.round(loss),
          sellAmount: h.amount,
          currentPrice: h.currentPrice,
          averageCost: h.averageCost,
          taxBenefit: Math.round(taxBenefit),
          washSaleRisk: washSaleWindow > 0,
          replacement: similarAssets ? this._getSimilarAsset(h.symbol) : null
        });
      }
    }

    return {
      opportunities,
      totalLoss: opportunities.reduce((sum, o) => sum + o.currentLoss, 0),
      totalTaxBenefit: opportunities.reduce((sum, o) => sum + o.taxBenefit, 0),
      washSaleWindow
    };
  }

  /**
   * Export transaction history
   */
  async exportTransactions(options = {}) {
    const { format = 'csv', startDate, endDate, path } = options;
    
    let transactions = this.transactions;
    
    if (startDate) {
      transactions = transactions.filter(t => new Date(t.timestamp) >= new Date(startDate));
    }
    if (endDate) {
      transactions = transactions.filter(t => new Date(t.timestamp) <= new Date(endDate));
    }

    if (format === 'csv') {
      const headers = ['timestamp', 'type', 'symbol', 'amount', 'value', 'reason'];
      const rows = transactions.map(t => 
        [t.timestamp, t.type, t.symbol, t.amount, t.value, t.reason].join(',')
      );
      return {
        format: 'csv',
        headers: headers.join(','),
        rows,
        count: transactions.length,
        csv: [headers.join(','), ...rows].join('\n')
      };
    }

    return { format, transactions, count: transactions.length };
  }

  /**
   * Generate performance report with charts data
   * @param {Object} options - Report options
   * @returns {Object} Performance report with chart data
   */
  async generatePerformanceReport(options = {}) {
    const { period = '90d', includeCharts = true, benchmark = 'BTC' } = options;
    
    const performance = await this.getPerformance({ period, benchmark });
    const overview = await this.getOverview();
    const risk = await this.getRiskMetrics();
    
    // Generate chart data (simulated)
    const chartData = includeCharts ? this._generateChartData(period, performance) : null;
    
    // Generate insights
    const insights = this._generateInsights(performance, risk, overview);
    
    return {
      period,
      generatedAt: new Date().toISOString(),
      summary: {
        totalValue: overview.totalValue,
        totalPnL: overview.totalPnL,
        totalPnLPercent: overview.totalPnLPercent,
        periodReturn: performance.portfolioReturn,
        benchmarkReturn: performance.benchmarkReturn,
        outperformance: performance.alpha
      },
      metrics: {
        sharpeRatio: performance.sharpeRatio,
        maxDrawdown: performance.maxDrawdown,
        volatility: performance.volatility,
        beta: performance.beta,
        alpha: performance.alpha
      },
      risk: {
        concentrationRisk: risk.concentrationRisk,
        diversificationScore: risk.diversificationScore,
        var95: (await this.calculateVaR({ confidence: 0.95 })).varPercent
      },
      charts: chartData,
      insights,
      recommendations: this._generateRecommendations(performance, risk, overview)
    };
  }

  /**
   * Compare portfolio to benchmark
   * @param {Object} options - Comparison options
   * @returns {Object} Detailed comparison
   */
  async compareToBenchmark(options = {}) {
    const { benchmark = 'BTC', period = '1y' } = options;
    
    const portfolioPerf = await this.getPerformance({ period, benchmark });
    
    // Simulated benchmark data
    const benchmarkData = {
      name: benchmark,
      return: portfolioPerf.benchmarkReturn,
      volatility: portfolioPerf.volatility * 1.2, // Benchmarks usually more volatile
      sharpeRatio: portfolioPerf.sharpeRatio * 0.9,
      maxDrawdown: portfolioPerf.maxDrawdown * 1.1
    };
    
    const comparison = {
      period,
      portfolio: {
        return: portfolioPerf.portfolioReturn,
        volatility: portfolioPerf.volatility,
        sharpeRatio: portfolioPerf.sharpeRatio,
        maxDrawdown: portfolioPerf.maxDrawdown
      },
      benchmark: benchmarkData,
      outperformance: {
        return: portfolioPerf.alpha,
        sharpeRatio: Math.round((portfolioPerf.sharpeRatio - benchmarkData.sharpeRatio) * 100) / 100,
        drawdown: Math.round((portfolioPerf.maxDrawdown - benchmarkData.maxDrawdown) * 100) / 100
      },
      verdict: portfolioPerf.alpha > 0 
        ? `Portfolio outperformed ${benchmark} by ${portfolioPerf.alpha}%`
        : `Portfolio underperformed ${benchmark} by ${Math.abs(portfolioPerf.alpha)}%`
    };
    
    return comparison;
  }

  /**
   * Get rebalance history
   */
  async getRebalanceHistory(options = {}) {
    const { limit = 10 } = options;
    
    // Return simulated rebalance history
    const history = [];
    const now = Date.now();
    
    for (let i = 0; i < Math.min(limit, 5); i++) {
      const date = new Date(now - i * 30 * 24 * 60 * 60 * 1000);
      history.push({
        date: date.toISOString(),
        tradesExecuted: Math.floor(Math.random() * 5) + 2,
        totalFees: Math.round((Math.random() * 50) * 100) / 100,
        driftBefore: Math.round((5 + Math.random() * 10) * 100) / 100,
        driftAfter: Math.round((0.5 + Math.random() * 2) * 100) / 100,
        reason: ['threshold', 'schedule', 'manual'][Math.floor(Math.random() * 3)]
      });
    }
    
    return {
      count: history.length,
      history,
      totalRebalances: history.length + Math.floor(Math.random() * 20),
      averageDriftReduction: Math.round((7 + Math.random() * 5) * 100) / 100
    };
  }

  // ============ Private Helper Methods ============

  async _getHoldingsWithPrices() {
    const result = [];
    
    for (const [symbol, holding] of this.holdings) {
      // Simulate current price (in production, fetch from price API)
      const priceMultiplier = 0.8 + Math.random() * 0.4; // 0.8x to 1.2x
      const currentPrice = holding.averageCost * priceMultiplier;
      const value = holding.amount * currentPrice;
      const cost = holding.amount * holding.averageCost;
      const pnl = value - cost;
      const pnlPercent = pnl / cost;

      result.push({
        ...holding,
        currentPrice: Math.round(currentPrice * 100) / 100,
        value: Math.round(value),
        cost: Math.round(cost),
        pnl: Math.round(pnl),
        pnlPercent
      });
    }

    return result;
  }

  async _generateRebalanceTrades(current, target, totalValue) {
    const trades = [];
    
    for (const category of ['crypto', 'stocks', 'cash']) {
      const currentVal = (current[category] || 0) / 100 * totalValue;
      const targetVal = (target[category] || 0) / 100 * totalValue;
      const diff = targetVal - currentVal;

      if (Math.abs(diff) > totalValue * 0.01) { // Only if > 1% difference
        trades.push({
          action: diff > 0 ? 'BUY' : 'SELL',
          category,
          amount: Math.abs(diff),
          value: Math.round(Math.abs(diff)),
          reason: `${category} ${diff > 0 ? 'underweight' : 'overweight'} by ${Math.abs(current[category] - target[category])}%`
        });
      }
    }

    return trades;
  }

  _estimateTaxImpact(trades) {
    let shortTermGain = 0;
    let longTermGain = 0;

    for (const trade of trades) {
      if (trade.action === 'SELL') {
        // Simulated tax calculation
        const isLongTerm = Math.random() > 0.5;
        const gain = trade.value * 0.1; // Assume 10% gain
        if (isLongTerm) {
          longTermGain += gain;
        } else {
          shortTermGain += gain;
        }
      }
    }

    const estimatedTax = shortTermGain * 0.35 + longTermGain * 0.15; // 35% ST, 15% LT

    return {
      shortTermGain: Math.round(shortTermGain),
      longTermGain: Math.round(longTermGain),
      estimatedTax: Math.round(estimatedTax),
      note: 'Consult a tax professional for accurate calculations'
    };
  }

  _parsePeriod(period) {
    const match = period.match(/(\d+)(d|m|y)/);
    if (!match) return 30;
    
    const [, value, unit] = match;
    const num = parseInt(value);
    
    switch (unit) {
      case 'd': return num;
      case 'm': return num * 30;
      case 'y': return num * 365;
      default: return 30;
    }
  }

  _calculateAverageCorrelation(matrix) {
    let sum = 0;
    let count = 0;
    
    for (const asset1 in matrix) {
      for (const asset2 in matrix[asset1]) {
        if (asset1 !== asset2) {
          sum += matrix[asset1][asset2];
          count++;
        }
      }
    }

    return count > 0 ? sum / count : 0;
  }

  _generateEfficientFrontier() {
    const points = [];
    for (let risk = 0.05; risk <= 0.30; risk += 0.025) {
      points.push({
        risk: Math.round(risk * 100) / 100,
        return: Math.round((0.05 + risk * 0.5 + Math.random() * 0.03) * 100) / 100
      });
    }
    return points;
  }

  _getSimilarAsset(symbol) {
    const similar = {
      'BTC': 'WBTC',
      'ETH': 'ETH2',
      'SOL': 'AVAX',
      'AAPL': 'MSFT',
      'TSLA': 'RIVN'
    };
    return similar[symbol] || null;
  }

  _generateChartData(period, performance) {
    const days = this._parsePeriod(period);
    const dataPoints = [];
    let value = performance.startValue;
    
    for (let i = 0; i < days; i++) {
      const dailyReturn = (Math.random() - 0.45) * 0.03; // Slight positive bias
      value *= (1 + dailyReturn);
      dataPoints.push({
        day: i + 1,
        value: Math.round(value),
        return: Math.round((value - performance.startValue) / performance.startValue * 100) / 100
      });
    }
    
    return {
      portfolio: dataPoints,
      benchmark: dataPoints.map((d, i) => ({
        day: i + 1,
        value: Math.round(performance.startValue * (1 + performance.benchmarkReturn / 100 * (i + 1) / days)),
        return: Math.round(performance.benchmarkReturn * (i + 1) / days * 100) / 100
      }))
    };
  }

  _generateInsights(performance, risk, overview) {
    const insights = [];
    
    // Performance insights
    if (performance.alpha > 2) {
      insights.push({
        type: 'positive',
        category: 'performance',
        title: 'Outperforming Benchmark',
        description: `Your portfolio is outperforming ${performance.benchmark} by ${performance.alpha}%`
      });
    } else if (performance.alpha < -2) {
      insights.push({
        type: 'warning',
        category: 'performance',
        title: 'Underperforming Benchmark',
        description: `Consider rebalancing to improve performance vs ${performance.benchmark}`
      });
    }
    
    // Risk insights
    if (risk.concentrationRisk === 'HIGH') {
      insights.push({
        type: 'warning',
        category: 'risk',
        title: 'High Concentration Risk',
        description: `Top holding represents ${risk.topHoldingPercent}% of portfolio. Consider diversifying.`
      });
    }
    
    // Diversification insights
    if (risk.diversificationScore < 50) {
      insights.push({
        type: 'info',
        category: 'diversification',
        title: 'Improve Diversification',
        description: 'Your portfolio could benefit from additional asset classes.'
      });
    }
    
    // Add neutral insight if none
    if (insights.length === 0) {
      insights.push({
        type: 'info',
        category: 'general',
        title: 'Portfolio Performing Well',
        description: 'Your portfolio is within healthy risk parameters.'
      });
    }
    
    return insights;
  }

  _generateRecommendations(performance, risk, overview) {
    const recommendations = [];
    
    if (performance.sharpeRatio < 1.0) {
      recommendations.push({
        priority: 'high',
        action: 'Improve risk-adjusted returns',
        description: 'Consider reducing volatility or increasing returns through better asset allocation.'
      });
    }
    
    if (risk.concentrationRisk === 'HIGH') {
      recommendations.push({
        priority: 'high',
        action: 'Reduce concentration risk',
        description: `Your top holding is ${risk.topHoldingPercent}% of portfolio. Aim for <20%.`
      });
    }
    
    if (performance.maxDrawdown < -15) {
      recommendations.push({
        priority: 'medium',
        action: 'Review drawdown protection',
        description: 'Consider adding stop-losses or hedging strategies to limit drawdowns.'
      });
    }
    
    if (overview.allocation.crypto > 70) {
      recommendations.push({
        priority: 'medium',
        action: 'Rebalance crypto exposure',
        description: 'Crypto allocation is high. Consider diversifying into stocks or bonds.'
      });
    }
    
    if (recommendations.length === 0) {
      recommendations.push({
        priority: 'low',
        action: 'Maintain current strategy',
        description: 'Your portfolio is well-balanced. Continue monitoring regularly.'
      });
    }
    
    return recommendations;
  }
}

module.exports = { PortfolioManager };
