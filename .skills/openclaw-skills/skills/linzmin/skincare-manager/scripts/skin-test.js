#!/usr/bin/env node
/**
 * 肤质测试脚本
 * 基于国家标准和公开资料的 9 种肤质分类
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const SKIN_TYPES_FILE = path.join(DATA_DIR, 'skin-types.json');

// 测试问题
const QUESTIONS = [
  {
    question: "洗脸后 1 小时，你的皮肤状态是？",
    options: [
      { text: "全脸出油，可以煎鸡蛋", score: { oily: 3, dry: 0, combination: 1 } },
      { text: "T 区出油，U 区干燥", score: { oily: 1, dry: 1, combination: 3 } },
      { text: "全脸干燥，有紧绷感", score: { oily: 0, dry: 3, combination: 1 } },
      { text: "状态稳定，不油不干", score: { oily: 0, dry: 0, combination: 0, normal: 3 } }
    ]
  },
  {
    question: "你的毛孔情况？",
    options: [
      { text: "毛孔粗大，尤其是 T 区", score: { oily: 3, dry: 0, combination: 2 } },
      { text: "毛孔细小，几乎看不见", score: { oily: 0, dry: 3, combination: 0 } },
      { text: "毛孔中等，T 区稍大", score: { oily: 1, dry: 1, combination: 2 } }
    ]
  },
  {
    question: "你容易长痘吗？",
    options: [
      { text: "经常长，尤其是 T 区", score: { oily: 3, dry: 0, sensitive: 1 } },
      { text: "偶尔长，月经期前后", score: { oily: 1, dry: 0, sensitive: 2 } },
      { text: "很少长痘", score: { oily: 0, dry: 1, sensitive: 0 } }
    ]
  },
  {
    question: "你的皮肤敏感度？",
    options: [
      { text: "很敏感，换产品就泛红", score: { sensitive: 3, dry: 1 } },
      { text: "有点敏感，偶尔泛红", score: { sensitive: 2, dry: 1 } },
      { text: "不敏感，耐受性好", score: { sensitive: 0, dry: 0 } }
    ]
  },
  {
    question: "你的皮肤容易起皮吗？",
    options: [
      { text: "经常起皮，尤其是秋冬", score: { dry: 3, oily: 0 } },
      { text: "偶尔起皮", score: { dry: 2, oily: 0 } },
      { text: "从不起皮", score: { dry: 0, oily: 1 } }
    ]
  }
];

// 肤质类型数据
const SKIN_TYPES = {
  oily: {
    name: "油性皮肤",
    emoji: "🌟",
    features: ["全脸出油", "毛孔粗大", "易长痘", "妆容易脱"],
    care_tips: ["控油", "深层清洁", "清爽保湿", "定期去角质"],
    recommended_ingredients: ["烟酰胺", "水杨酸", "锌"]
  },
  dry: {
    name: "干性皮肤",
    emoji: "💧",
    features: ["皮肤干燥", "易起皮", "细纹明显", "易敏感"],
    care_tips: ["补水", "保湿", "滋润", "温和清洁"],
    recommended_ingredients: ["透明质酸", "神经酰胺", "角鲨烷"]
  },
  combination: {
    name: "混合性皮肤",
    emoji: "⚖️",
    features: ["T 区油腻", "U 区干燥", "毛孔中等", "偶尔长痘"],
    care_tips: ["T 区控油", "U 区保湿", "分区护理"],
    recommended_ingredients: ["烟酰胺", "透明质酸", "甘油"]
  },
  sensitive: {
    name: "敏感性皮肤",
    emoji: "🌸",
    features: ["易泛红", "易刺痛", "易过敏", "角质层薄"],
    care_tips: ["温和", "修护屏障", "避免刺激", "简化护肤"],
    recommended_ingredients: ["神经酰胺", "积雪草", "维生素 B5"]
  },
  normal: {
    name: "中性皮肤",
    emoji: "✨",
    features: ["水油平衡", "毛孔细致", "不易过敏", "状态稳定"],
    care_tips: ["基础保湿", "防晒", "维持现状"],
    recommended_ingredients: ["透明质酸", "维生素 E", "抗氧化成分"]
  }
};

function askQuestion(questionData) {
  return new Promise((resolve) => {
    console.log(`\n${questionData.question}`);
    questionData.options.forEach((opt, index) => {
      console.log(`  ${index + 1}. ${opt.text}`);
    });
    
    const readline = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    readline.question('\n请选择 (1-4): ', (answer) => {
      readline.close();
      const index = parseInt(answer) - 1;
      if (index >= 0 && index < questionData.options.length) {
        resolve(questionData.options[index].score);
      } else {
        console.log('无效选择，跳过此题');
        resolve({});
      }
    });
  });
}

async function runTest() {
  console.log('🧴 肤质测试');
  console.log('═'.repeat(50));
  console.log('请根据实际情况回答以下问题：\n');
  
  const scores = { oily: 0, dry: 0, combination: 0, sensitive: 0, normal: 0 };
  
  // 回答问题
  for (const q of QUESTIONS) {
    const score = await askQuestion(q);
    for (const [type, points] of Object.entries(score)) {
      scores[type] = (scores[type] || 0) + points;
    }
  }
  
  // 计算结果
  const maxScore = Math.max(...Object.values(scores));
  const resultType = Object.keys(scores).find(key => scores[key] === maxScore);
  
  // 显示结果
  console.log('\n' + '═'.repeat(50));
  console.log('📊 测试结果');
  console.log('═'.repeat(50));
  
  const result = SKIN_TYPES[resultType];
  console.log(`\n你的肤质类型：${result.emoji} ${result.name}`);
  
  console.log('\n### 特征');
  result.features.forEach(f => console.log(`  • ${f}`));
  
  console.log('\n### 护肤建议');
  result.care_tips.forEach(tip => console.log(`  • ${tip}`));
  
  console.log('\n### 推荐成分');
  result.recommended_ingredients.forEach(ing => console.log(`  • ${ing}`));
  
  console.log('\n' + '═'.repeat(50));
  console.log('⚠️  免责声明：测试结果仅供参考，不构成专业建议。');
  console.log('   如有皮肤问题请咨询专业皮肤科医生。');
  console.log('═'.repeat(50));
  
  // 保存结果
  const resultFile = path.join(DATA_DIR, 'skin-test-result.json');
  const resultData = {
    type: resultType,
    scores: scores,
    tested_at: new Date().toISOString()
  };
  fs.writeFileSync(resultFile, JSON.stringify(resultData, null, 2));
  
  console.log(`\n💾 结果已保存：${resultFile}`);
}

// 运行测试
runTest().catch(console.error);
