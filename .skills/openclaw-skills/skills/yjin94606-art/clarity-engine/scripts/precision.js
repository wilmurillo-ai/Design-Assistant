#!/usr/bin/env node
/**
 * Prompt Precision - 精准模式入口
 * 接收用户输入，返回精准化后的结构
 */

const { transform, formatOutput } = require('./precision-engine.js');

// 获取用户输入
let input = process.argv.slice(2).join(' ');

// 无输入时显示帮助
if (!input || input === '--help' || input === '-h') {
  console.log(`
🎯 Prompt Precision - 精准模式

用法:
  precision <用户输入>
  precision --test        运行测试
  precision --interactive 交互模式
  precision --help       显示帮助

示例:
  precision "你好，我想请教一下，关于Python代码的for循环，为什么它运行这么慢啊，谢谢"
  
输出:
  [意图]性能优化
  [语言]Python
  [关注点]循环结构
  [目标]分析for循环执行效率，给出优化建议
`);
  process.exit(0);
}

// 测试模式
if (input === '--test') {
  runTests();
  process.exit(0);
}

// 执行转换
let result = transform(input);
console.log(formatOutput(result));

// 调试模式：显示原始输入
if (process.argv.includes('--debug')) {
  console.log('\n--- 调试信息 ---');
  console.log('原始输入:', result.original);
  console.log('意图:', result.metadata.intent);
  console.log('语言:', result.metadata.languages);
  console.log('关注点:', result.metadata.focus);
  console.log('目标:', result.metadata.goal);
}

// ============================================
// 测试用例
// ============================================

function runTests() {
  console.log('🧪 运行测试...\n');
  
  const tests = [
    {
      input: '你好，我想请教一下，关于Python代码的for循环，为什么它运行这么慢啊，谢谢',
      expected: { intent: '性能优化', hasLanguage: 'Python', hasFocus: '循环结构' }
    },
    {
      input: '帮我看看这个代码有什么问题谢谢',
      expected: { intent: '代码调试', hasFocus: '代码逻辑' }
    },
    {
      input: '能不能帮我把这段JavaScript代码改成TypeScript啊',
      expected: { intent: '代码修改', hasLanguage: 'JavaScript', hasLanguage2: 'TypeScript' }
    },
    {
      input: '什么是React的useEffect',
      expected: { intent: '概念解释', hasLanguage: 'React' }
    },
    {
      input: '写一个排序算法',
      expected: { intent: '代码创建', hasFocus: '算法' }
    },
    {
      input: '谢谢你的帮助',
      expected: { intent: '一般请求' }
    },
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (let i = 0; i < tests.length; i++) {
    const test = tests[i];
    let result = transform(test.input);
    
    let ok = true;
    let issues = [];
    
    // 检查意图
    if (test.expected.intent && result.metadata.intent !== test.expected.intent) {
      ok = false;
      issues.push(`意图: ${result.metadata.intent} (期望: ${test.expected.intent})`);
    }
    
    // 检查语言
    if (test.expected.hasLanguage) {
      if (!result.metadata.languages.includes(test.expected.hasLanguage)) {
        ok = false;
        issues.push(`语言: ${result.metadata.languages.join(',')} (期望含: ${test.expected.hasLanguage})`);
      }
    }
    
    if (test.expected.hasLanguage2) {
      if (!result.metadata.languages.includes(test.expected.hasLanguage2)) {
        ok = false;
        issues.push(`语言2: ${result.metadata.languages.join(',')} (期望含: ${test.expected.hasLanguage2})`);
      }
    }
    
    // 检查关注点
    if (test.expected.hasFocus) {
      let focusOk = result.metadata.focus.some(f => test.expected.hasFocus.includes(f) || f.includes(test.expected.hasFocus));
      if (!focusOk) {
        ok = false;
        issues.push(`关注点: ${result.metadata.focus.join(',')} (期望含: ${test.expected.hasFocus})`);
      }
    }
    
    if (ok) {
      console.log(`✅ 测试 ${i + 1}: 通过`);
      passed++;
    } else {
      console.log(`❌ 测试 ${i + 1}: 失败`);
      console.log(`   输入: ${test.input}`);
      console.log(`   问题: ${issues.join(', ')}`);
      failed++;
    }
  }
  
  console.log(`\n📊 结果: ${passed} 通过, ${failed} 失败`);
  
  if (failed === 0) {
    console.log('🎉 所有测试通过!');
  }
}
