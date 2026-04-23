const assert = require('assert');
const DecisionDeck = require('../src/index.js');

function run() {
  const engine = new DecisionDeck();
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    try {
      fn();
      console.log(`PASS ${name}`);
      passed += 1;
    } catch (error) {
      console.log(`FAIL ${name}: ${error.message}`);
      failed += 1;
    }
  }

  const briefText = `
我们要决定 Knowledge Connector 后面先做什么产出层。
用户访谈里 6 次提到老板看不懂长报告，客户也更想要一页结论。
方案A 继续扩展连接器来源，价值更全，但实现更重、上线更慢。
方案B 先做一页式决策简报，最快本周能验证，和现有资料输入更贴近。
另一份内部 memo 认为应该先做协作批注，但证据主要来自 1 个客户反馈。
当前资源只有 1 名前端和 1 名产品，本月需要出一个能演示的结果。
是否需要做协作批注仍待确认。
建议先做方案B，并保留后续扩展空间。
`;

  const kickoffText = `
目标是把零散资料变成一个能拿去和老板拍板的一页 brief。
用户反馈主要集中在现有输出太长、太散、结论不够直接。
方案A 做长报告模板，方案B 做 one-pager，方案C 做协作批注。
当前团队排期只有两周，且演示版本必须在月底前可用。
先安排 3 个真实材料样本做 one-pager 验证。
`;

  const gapText = `
现在更倾向方案B。
但还不清楚老板更关心拍板速度，还是要完整论证？
客户是否真的会为 one-pager 付费也待确认。
法务是否要求保留证据出处同样需要确认。
`;

  test('distill detects options, constraints, and unknowns', () => {
    const distilled = engine.distill(briefText, {});
    assert(distilled.options.some((item) => item.option === '方案A'));
    assert(distilled.options.some((item) => item.option === '方案B'));
    assert(distilled.constraints.some((item) => item.includes('当前资源只有 1 名前端和 1 名产品')));
    assert(distilled.unknowns.some((item) => item.includes('是否需要做协作批注仍待确认')));
  });

  test('brief recommends the stronger option', () => {
    const result = engine.brief({ text: briefText });
    assert(result.recommendation.includes('方案B'));
    assert(result.optionsOnTable.length >= 2);
  });

  test('compare ranks options and returns winner', () => {
    const result = engine.compare({ text: briefText });
    assert.strictEqual(result.recommendedOption, '方案B');
    assert(result.ranking.length >= 2);
  });

  test('conflicts surfaces disagreement', () => {
    const result = engine.conflicts({ text: briefText });
    assert(result.conflicts.length >= 1);
    assert(result.whatCanStillBeDecided.includes('方案B'));
  });

  test('kickoff builds a starting scope and next step', () => {
    const result = engine.kickoff({ text: kickoffText });
    assert(result.recommendedStartingScope.length > 0);
    assert(result.nextStep.length > 0);
  });

  test('gaps surfaces explicit unknowns', () => {
    const result = engine.gaps({ text: gapText });
    assert(result.missingEvidence.length >= 2);
  });

  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed > 0 ? 1 : 0);
}

run();
