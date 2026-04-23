/**
 * SEO Keyword Pro - Test Suite
 */

const { SEOKeywordPro } = require('../index');

function assert(condition, message) {
  if (!condition) {
    throw new Error(`❌ ASSERTION FAILED: ${message}`);
  }
  console.log(`✅ ${message}`);
}

async function runTests() {
  console.log('\n🧪 Running SEO Keyword Pro Tests...\n');
  
  const seo = new SEOKeywordPro({
    niche: 'crypto trading',
    targetCountry: 'US'
  });

  try {
    // Test 1: Find Keywords
    console.log('Test 1: Find Keywords');
    const keywords = await seo.findKeywords({
      seed: 'bitcoin trading',
      minVolume: 100,
      maxDifficulty: 50,
      count: 20
    });
    assert(Array.isArray(keywords), 'Keywords is array');
    assert(keywords.length > 0, 'Has keywords');
    const kw = keywords[0];
    assert(kw.keyword, 'Has keyword text');
    assert(typeof kw.volume === 'number', 'Has volume');
    assert(typeof kw.difficulty === 'number', 'Has difficulty');
    assert(['informational', 'commercial', 'transactional'].includes(kw.intent), 'Valid intent');
    assert(typeof kw.opportunity === 'number', 'Has opportunity score');
    console.log(`   Found ${keywords.length} keywords, best opportunity: ${Math.max(...keywords.map(k => k.opportunity))}\n`);

    // Test 2: Find Golden Keywords
    console.log('Test 2: Find Golden Keywords (Low Competition)');
    const golden = await seo.findGoldenKeywords({
      seed: 'cryptocurrency',
      minVolume: 500,
      maxDifficulty: 30,
      minOpportunity: 70
    });
    assert(Array.isArray(golden), 'Golden keywords is array');
    if (golden.length > 0) {
      assert(golden.every(k => k.difficulty <= 30), 'All KD <= 30');
      assert(golden.every(k => k.opportunity >= 70), 'All opportunity >= 70');
      console.log(`   Found ${golden.length} golden keywords\n`);
    } else {
      console.log('   No golden keywords found (strict criteria)\n');
    }

    // Test 3: Analyze Intent
    console.log('Test 3: Analyze Search Intent');
    const intent = await seo.analyzeIntent({
      keyword: 'best crypto exchange 2026'
    });
    assert(intent.primaryIntent, 'Has primary intent');
    assert(['informational', 'commercial', 'transactional', 'navigational'].includes(intent.primaryIntent), 'Valid intent');
    assert(typeof intent.confidence === 'number', 'Has confidence');
    assert(Array.isArray(intent.serpFeatures), 'Has SERP features');
    assert(intent.userGoal, 'Has user goal');
    console.log(`   Intent: ${intent.primaryIntent} (${intent.confidence * 100}% confidence)\n`);

    // Test 4: Generate Content Brief
    console.log('Test 4: Generate Content Brief');
    const brief = await seo.generateContentBrief({
      keyword: 'how to trade bitcoin',
      targetLength: 'long',
      includeFAQ: true
    });
    assert(brief.keyword, 'Has keyword');
    assert(brief.title, 'Has title suggestions');
    assert(Array.isArray(brief.outline), 'Has outline');
    assert(typeof brief.targetWordCount === 'number', 'Has word count');
    assert(Array.isArray(brief.targetKeywords.secondary), 'Has secondary keywords');
    assert(Array.isArray(brief.faqs), 'Has FAQs');
    console.log(`   Brief: ${brief.targetWordCount} words, ${brief.outline.length} sections, ${brief.faqs.length} FAQs\n`);

    // Test 5: Track Rankings
    console.log('Test 5: Track Rankings');
    const rankings = await seo.trackRankings({
      keywords: ['bitcoin trading', 'crypto exchange'],
      domain: 'yoursite.com',
      period: '30d'
    });
    assert(rankings.domain, 'Has domain');
    assert(Array.isArray(rankings.rankings), 'Has rankings');
    assert(typeof rankings.averagePosition === 'number', 'Has avg position');
    assert(typeof rankings.keywordsInTop10 === 'number', 'Has top 10 count');
    console.log(`   Tracking ${rankings.rankings.length} keywords, avg position: ${rankings.averagePosition}\n`);

    // Test 6: Analyze Competitor
    console.log('Test 6: Analyze Competitor');
    const competitor = await seo.analyzeCompetitor({
      domain: 'competitor.com',
      niche: 'crypto'
    });
    assert(competitor.domain, 'Has domain');
    assert(typeof competitor.authority === 'number', 'Has authority');
    assert(typeof competitor.estimatedTraffic === 'number', 'Has traffic');
    assert(Array.isArray(competitor.topKeywords), 'Has top keywords');
    assert(Array.isArray(competitor.opportunities), 'Has opportunities');
    console.log(`   Authority: ${competitor.authority}, Traffic: ${competitor.estimatedTraffic}/mo\n`);

    // Test 7: Keyword Gap Analysis
    console.log('Test 7: Keyword Gap Analysis');
    const gap = await seo.keywordGap({
      yourDomain: 'yoursite.com',
      competitorDomains: ['competitor1.com', 'competitor2.com']
    });
    assert(gap.yourDomain, 'Has your domain');
    assert(Array.isArray(gap.competitorDomains), 'Has competitors');
    assert(Array.isArray(gap.gaps), 'Has gaps');
    assert(typeof gap.totalGaps === 'number', 'Has total gaps');
    console.log(`   Found ${gap.totalGaps} keyword gaps, ${gap.highOpportunityGaps} high opportunity\n`);

    // Test 8: Keyword Variations
    console.log('Test 8: Keyword Variations Generation');
    const variations = seo._generateVariations('bitcoin');
    assert(Array.isArray(variations), 'Variations is array');
    assert(variations.length > 5, 'Has multiple variations');
    assert(variations.some(v => v.includes('how to')), 'Has "how to" variation');
    assert(variations.some(v => v.includes('best')), 'Has "best" variation');
    console.log(`   Generated ${variations.length} variations\n`);

    // Test 9: Opportunity Score Calculation
    console.log('Test 9: Opportunity Score Calculation');
    const testMetrics = { volume: 5000, difficulty: 25 };
    const score = seo._calculateOpportunity(testMetrics);
    assert(typeof score === 'number', 'Score is number');
    assert(score >= 0 && score <= 100, 'Score in valid range');
    // High volume + low difficulty = high score
    assert(score >= 70, 'High volume + low KD = high score');
    console.log(`   Opportunity score: ${score}/100\n`);

    // Test 10: SERP Features Detection
    console.log('Test 10: SERP Features Detection');
    const features1 = seo._getSERPFeatures('how to trade');
    const features2 = seo._getSERPFeatures('best exchange');
    assert(Array.isArray(features1), 'Features is array');
    assert(features1.includes('featured snippet'), 'How-to has featured snippet');
    assert(features2.includes('people also ask'), 'Best has PAA');
    console.log(`   SERP features detected correctly\n`);

    // Test 11: Intent Pattern Matching
    console.log('Test 11: Intent Pattern Matching');
    const commercial = await seo.analyzeIntent({ keyword: 'best crypto wallet' });
    const informational = await seo.analyzeIntent({ keyword: 'how to buy crypto' });
    const transactional = await seo.analyzeIntent({ keyword: 'buy bitcoin online' });
    assert(commercial.primaryIntent === 'commercial', 'Commercial intent detected');
    assert(informational.primaryIntent === 'informational', 'Informational intent detected');
    assert(transactional.primaryIntent === 'transactional', 'Transactional intent detected');
    console.log('   All intent types detected correctly\n');

    // Test 12: Content Title Generation
    console.log('Test 12: Content Title Generation');
    const titles = seo._generateTitles('bitcoin trading', 'informational');
    assert(Array.isArray(titles), 'Titles is array');
    assert(titles.length >= 5, 'Has multiple titles');
    assert(titles.some(t => t.includes('Guide')), 'Has "Guide" title');
    assert(titles.some(t => t.includes('How to')), 'Has "How to" title');
    console.log(`   Generated ${titles.length} title variations\n`);

    console.log('========================================');
    console.log('✅ All tests passed!');
    console.log('========================================\n');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

runTests();
