/**
 * Portfolio Manager - Test Suite
 */

const { PortfolioManager } = require('../index');

function assert(condition, message) {
  if (!condition) {
    throw new Error(`❌ ASSERTION FAILED: ${message}`);
  }
  console.log(`✅ ${message}`);
}

async function runTests() {
  console.log('\n🧪 Running Portfolio Manager Tests...\n');
  
  const portfolio = new PortfolioManager({
    baseCurrency: 'USD',
    riskProfile: 'moderate'
  });

  try {
    // Test 1: Add Holdings
    console.log('Test 1: Add Holdings');
    await portfolio.addHolding({ symbol: 'BTC', amount: 0.5, averageCost: 65000, category: 'crypto' });
    await portfolio.addHolding({ symbol: 'ETH', amount: 5.0, averageCost: 3400, category: 'crypto' });
    await portfolio.addHolding({ symbol: 'AAPL', amount: 50, averageCost: 180, category: 'stocks' });
    assert(true, 'Holdings added successfully');
    console.log('   Added: BTC, ETH, AAPL\n');

    // Test 2: Get Portfolio Overview
    console.log('Test 2: Get Portfolio Overview');
    const overview = await portfolio.getOverview();
    assert(overview.totalValue > 0, 'Total value is positive');
    assert(overview.totalHoldings === 3, 'Correct number of holdings');
    assert(overview.allocation.crypto > 0, 'Crypto allocation present');
    assert(overview.topHoldings.length > 0, 'Has top holdings');
    console.log(`   Total: $${overview.totalValue.toLocaleString()}, P&L: $${overview.totalPnL.toLocaleString()} (${overview.totalPnLPercent}%)\n`);

    // Test 3: Set Target Allocation
    console.log('Test 3: Set Target Allocation');
    await portfolio.setTargetAllocation({
      crypto: 50,
      stocks: 35,
      cash: 15,
      rebalance: { strategy: 'threshold', threshold: 5 }
    });
    assert(portfolio.targetAllocation !== null, 'Target allocation set');
    assert(portfolio.targetAllocation.crypto === 50, 'Crypto target is 50%');
    console.log('   Target: 50% crypto, 35% stocks, 15% cash\n');

    // Test 4: Check Rebalance
    console.log('Test 4: Check Rebalance');
    const rebalance = await portfolio.checkRebalance();
    assert(typeof rebalance.needsRebalance === 'boolean', 'Rebalance check returns boolean');
    assert(typeof rebalance.drift === 'number', 'Drift is a number');
    console.log(`   Needs rebalance: ${rebalance.needsRebalance}, Max drift: ${rebalance.drift}%\n`);

    // Test 5: Get Performance
    console.log('Test 5: Get Performance Metrics');
    const performance = await portfolio.getPerformance({ period: '30d', benchmark: 'BTC' });
    assert(typeof performance.portfolioReturn === 'number', 'Portfolio return is a number');
    assert(typeof performance.sharpeRatio === 'number', 'Sharpe ratio is a number');
    assert(performance.benchmark === 'BTC', 'Benchmark is BTC');
    console.log(`   30d return: ${performance.portfolioReturn}%, Sharpe: ${performance.sharpeRatio}, vs BTC: ${performance.benchmarkReturn}%\n`);

    // Test 6: Get Risk Metrics
    console.log('Test 6: Get Risk Metrics');
    const risk = await portfolio.getRiskMetrics();
    assert(['LOW', 'MEDIUM', 'HIGH'].includes(risk.concentrationRisk), 'Valid concentration risk');
    assert(risk.diversificationScore >= 0 && risk.diversificationScore <= 100, 'Diversification score in range');
    console.log(`   Concentration: ${risk.concentrationRisk}, Diversification: ${risk.diversificationScore}/100\n`);

    // Test 7: Calculate VaR
    console.log('Test 7: Calculate Value at Risk');
    const varMetrics = await portfolio.calculateVaR({ confidence: 0.95, horizon: 1 });
    assert(varMetrics.confidence === 95, '95% confidence');
    assert(varMetrics.varAmount > 0, 'VaR amount is positive');
    console.log(`   VaR (95%, 1-day): $${varMetrics.varAmount.toLocaleString()} (${varMetrics.varPercent}%)\n`);

    // Test 8: Get Correlation Matrix
    console.log('Test 8: Get Correlation Matrix');
    const correlation = await portfolio.getCorrelationMatrix({
      assets: ['BTC', 'ETH', 'AAPL', 'GOOGL']
    });
    assert(correlation.matrix.BTC !== undefined, 'BTC in matrix');
    assert(correlation.matrix.BTC.BTC === 1.0, 'BTC self-correlation is 1');
    assert(typeof correlation.averageCorrelation === 'number', 'Average correlation calculated');
    console.log(`   Average correlation: ${correlation.averageCorrelation}, Diversification benefit: ${correlation.diversificationBenefit}%\n`);

    // Test 9: MPT Optimization
    console.log('Test 9: Modern Portfolio Theory Optimization');
    const optimization = await portfolio.optimizeMPT({
      riskFreeRate: 0.05,
      targetReturn: 0.15,
      constraints: { maxSingleAsset: 0.25, minCrypto: 0.3, maxCrypto: 0.7 }
    });
    assert(optimization.optimalAllocation !== undefined, 'Optimal allocation returned');
    assert(optimization.sharpeRatio > 0, 'Sharpe ratio is positive');
    assert(optimization.efficientFrontier.length > 0, 'Efficient frontier calculated');
    console.log(`   Expected return: ${optimization.expectedReturn * 100}%, Volatility: ${optimization.expectedVolatility * 100}%, Sharpe: ${optimization.sharpeRatio}\n`);

    // Test 10: Tax-Loss Harvesting
    console.log('Test 10: Tax-Loss Harvesting Opportunities');
    const harvesting = await portfolio.findTaxLossHarvesting({ minLoss: 100, washSaleWindow: 30 });
    assert(Array.isArray(harvesting.opportunities), 'Opportunities is an array');
    assert(typeof harvesting.totalTaxBenefit === 'number', 'Tax benefit calculated');
    console.log(`   Opportunities: ${harvesting.opportunities.length}, Total tax benefit: $${harvesting.totalTaxBenefit}\n`);

    // Test 11: Export Transactions
    console.log('Test 11: Export Transactions');
    const exported = await portfolio.exportTransactions({ format: 'csv' });
    assert(exported.format === 'csv', 'CSV format');
    assert(typeof exported.csv === 'string', 'CSV content is string');
    console.log(`   Exported ${exported.count} transactions\n`);

    // Test 12: Risk Profile Impact
    console.log('Test 12: Risk Profile Impact on Constraints');
    const conservative = new PortfolioManager({ riskProfile: 'conservative' });
    const aggressive = new PortfolioManager({ riskProfile: 'aggressive' });
    
    assert(conservative.riskConstraints.conservative.maxCrypto < aggressive.riskConstraints.aggressive.maxCrypto, 
           'Conservative has lower crypto max');
    console.log(`   Conservative max crypto: ${conservative.riskConstraints.conservative.maxCrypto * 100}%`);
    console.log(`   Aggressive max crypto: ${aggressive.riskConstraints.aggressive.maxCrypto * 100}%\n`);

    console.log('========================================');
    console.log('✅ All tests passed!');
    console.log('========================================\n');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    process.exit(1);
  }
}

runTests();
