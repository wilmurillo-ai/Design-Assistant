/**
 * Trading Decision Pro - Test Suite
 */

const { TradingDecisionPro } = require('../index');

function assert(condition, message) {
  if (!condition) {
    throw new Error(`❌ ASSERTION FAILED: ${message}`);
  }
  console.log(`✅ ${message}`);
}

async function runTests() {
  console.log('\n🧪 Running Trading Decision Pro Tests...\n');
  
  const trader = new TradingDecisionPro({
    markets: ['crypto'],
    riskProfile: 'moderate',
    maxPositionSize: 0.1
  });

  try {
    // Test 1: Get Sentiment
    console.log('Test 1: Get Sentiment');
    const sentiment = await trader.getSentiment('BTC');
    assert(sentiment.score >= 0 && sentiment.score <= 100, 'Sentiment score in valid range');
    assert(['Bullish', 'Slightly Bullish', 'Neutral', 'Slightly Bearish', 'Bearish'].includes(sentiment.label), 'Valid sentiment label');
    assert(sentiment.trend, 'Trend is present');
    console.log(`   Result: ${sentiment.label} (${sentiment.score}/100) - ${sentiment.trend}\n`);

    // Test 2: Analyze Trade - Long
    console.log('Test 2: Analyze Trade (Long)');
    const tradeAnalysis = await trader.analyzeTrade({
      symbol: 'BTC/USDT',
      direction: 'long',
      entryPrice: 67500,
      stopLoss: 65000,
      takeProfit: 72000
    });
    assert(['ENTER', 'HOLD', 'AVOID'].includes(tradeAnalysis.recommendation), 'Valid recommendation');
    assert(tradeAnalysis.confidence >= 0 && tradeAnalysis.confidence <= 100, 'Confidence in valid range');
    assert(tradeAnalysis.riskReward > 0, 'Risk/Reward is positive');
    assert(tradeAnalysis.reasoning.length > 0, 'Has reasoning');
    console.log(`   Result: ${tradeAnalysis.recommendation} (${tradeAnalysis.confidence}% confidence, R:R ${tradeAnalysis.riskReward}:1)\n`);

    // Test 3: Calculate Position Size
    console.log('Test 3: Calculate Position Size');
    const position = trader.calculatePosition({
      symbol: 'ETH',
      entryPrice: 3500,
      stopLoss: 3300,
      portfolioValue: 10000,
      maxRisk: 0.02
    });
    assert(position.positionSize > 0, 'Position size is positive');
    assert(position.portfolioPercent <= 100, 'Portfolio percent <= 100%');
    assert(position.riskPercent <= 2.5, 'Risk percent within expected range');
    console.log(`   Result: ${position.positionSize} ETH ($${position.positionValue}, ${position.portfolioPercent}% of portfolio)\n`);

    // Test 4: Portfolio Risk Assessment
    console.log('Test 4: Portfolio Risk Assessment');
    const portfolioRisk = await trader.getPortfolioRisk({
      positions: [
        { symbol: 'BTC', size: 0.5, entryPrice: 65000 },
        { symbol: 'ETH', size: 2.0, entryPrice: 3400 }
      ],
      totalValue: 50000
    });
    assert(portfolioRisk.totalExposure >= 0, 'Exposure is non-negative');
    assert(['LOW', 'MEDIUM', 'HIGH'].includes(portfolioRisk.correlationRisk), 'Valid correlation risk');
    assert(portfolioRisk.recommendations.length > 0, 'Has recommendations');
    console.log(`   Result: ${portfolioRisk.totalExposure * 100}% exposure, ${portfolioRisk.correlationRisk} correlation risk\n`);

    // Test 5: Multi-Timeframe Analysis
    console.log('Test 5: Multi-Timeframe Analysis');
    const mtf = await trader.multiTimeframeAnalysis('BTC', {
      timeframes: ['15m', '1h', '4h', '1d'],
      indicators: ['RSI', 'MACD', 'EMA']
    });
    assert(['bullish', 'bearish'].includes(mtf.overallDirection), 'Valid overall direction');
    assert(mtf.confluenceScore >= 0 && mtf.confluenceScore <= 100, 'Confluence score in valid range');
    assert(Object.keys(mtf.timeframes).length === 4, 'All timeframes present');
    console.log(`   Result: ${mtf.overallDirection} (${mtf.confluenceScore}% confluence)\n`);

    // Test 6: Pattern Detection
    console.log('Test 6: Pattern Detection');
    const patterns = await trader.detectPatterns('ETH', {
      patterns: ['head-shoulders', 'triangle', 'flag', 'double-top', 'double-bottom'],
      minReliability: 0.6
    });
    assert(patterns.patternsDetected >= 0, 'Pattern count is non-negative');
    if (patterns.patternsDetected > 0) {
      assert(patterns.patterns.every(p => p.reliability >= 60), 'All patterns meet min reliability');
    }
    console.log(`   Result: ${patterns.patternsDetected} patterns detected\n`);

    // Test 7: Backtest
    console.log('Test 7: Backtest Strategy');
    const backtest = await trader.backtest({
      symbol: 'BTC/USDT',
      strategy: 'sentiment-follow',
      startDate: '2025-01-01',
      endDate: '2026-03-19',
      initialCapital: 10000
    });
    assert(backtest.trades.total > 0, 'Has trades');
    assert(backtest.trades.winRate > 0 && backtest.trades.winRate <= 100, 'Win rate in valid range');
    assert(backtest.performance.sharpeRatio > 0, 'Sharpe ratio is positive');
    console.log(`   Result: ${backtest.trades.total} trades, ${backtest.trades.winRate}% win rate, Sharpe ${backtest.performance.sharpeRatio}\n`);

    // Test 8: Risk Profile Impact
    console.log('Test 8: Risk Profile Impact');
    const conservative = new TradingDecisionPro({ riskProfile: 'conservative', maxPositionSize: 0.1 });
    const aggressive = new TradingDecisionPro({ riskProfile: 'aggressive', maxPositionSize: 0.1 });
    
    const consPos = conservative.calculatePosition({
      entryPrice: 100, stopLoss: 90, portfolioValue: 10000, maxRisk: 0.02
    });
    const aggPos = aggressive.calculatePosition({
      entryPrice: 100, stopLoss: 90, portfolioValue: 10000, maxRisk: 0.02
    });
    
    assert(aggPos.positionSize > consPos.positionSize, 'Aggressive has larger position');
    console.log(`   Result: Conservative ${consPos.portfolioPercent}% vs Aggressive ${aggPos.portfolioPercent}%\n`);

    console.log('========================================');
    console.log('✅ All tests passed!');
    console.log('========================================\n');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    process.exit(1);
  }
}

runTests();
