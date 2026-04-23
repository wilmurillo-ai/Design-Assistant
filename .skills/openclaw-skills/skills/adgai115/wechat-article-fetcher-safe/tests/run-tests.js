const { fetchWechatArticle } = require('../fetch-wechat-article');
const path = require('path');
const fs = require('fs');

async function runTests() {
  console.log('🧪 开始运行微信文章抓取测试...');
  
  const testOutputDir = path.join(__dirname, 'output');
  if (!fs.existsSync(testOutputDir)) {
    fs.mkdirSync(testOutputDir, { recursive: true });
  }

  const testCases = [
    {
      name: '中长文测试',
      url: 'https://mp.weixin.qq.com/s/mCH_H29Zaepwk2NGukU_Fg',
      expectMinLength: 1000
    },
    {
      name: '短文测试',
      url: 'https://mp.weixin.qq.com/s/UqSGc7d6RxgOzFNI9JWYPg',
      expectMinLength: 50
    }
  ];

  let passed = 0;

  for (const tc of testCases) {
    console.log(`\n▶️ 执行测试: ${tc.name}`);
    console.log(`URL: ${tc.url}`);
    
    try {
      const startTime = Date.now();
      const result = await fetchWechatArticle({
        url: tc.url,
        saveToFile: true,
        outputDir: testOutputDir
      });
      const cost = Date.now() - startTime;
      
      console.log(`✅ 抓取成功 (耗时: ${cost}ms)`);
      console.log(`标题: ${result.title}`);
      console.log(`字数: ${result.content.length}`);
      
      if (result.content.length < tc.expectMinLength) {
        throw new Error(`文章内容长度 (${result.content.length}) 小于预期最小值 (${tc.expectMinLength})`);
      }
      
      passed++;
    } catch (err) {
      console.error(`❌ 测试失败: ${err.message}`);
    }
  }

  console.log('\n📊 ========== 测试总结 ==========');
  console.log(`总计: ${testCases.length}`);
  console.log(`通过: ${passed}`);
  console.log(`失败: ${testCases.length - passed}`);
  
  if (passed === testCases.length) {
    console.log('🎉 所有测试通过！');
    process.exit(0);
  } else {
    console.log('💥 部分测试失败。');
    process.exit(1);
  }
}

if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = runTests;
