#!/usr/bin/env node
/**
 * 成分查询脚本
 * 从本地数据库查询化妆品成分信息
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const INGREDIENTS_FILE = path.join(DATA_DIR, 'ingredients.json');

// 权威等级说明
const AUTHORITY_LEVELS = {
  5: '⭐⭐⭐⭐⭐ 官方权威',
  4: '⭐⭐⭐⭐ 专业教材',
  3: '⭐⭐⭐ 社区数据库',
  2: '⭐⭐ 专业人士',
  1: '⭐ 用户分享'
};

function loadDatabase() {
  try {
    const data = fs.readFileSync(INGREDIENTS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('❌ 无法读取成分数据库');
    console.error('提示：运行 ./install.sh 初始化数据库');
    return {};
  }
}

function searchIngredient(query, database) {
  query = query.toLowerCase().trim();
  const results = [];
  
  // 精确匹配
  if (database[query]) {
    results.push({ name: query, data: database[query], match: 'exact' });
  }
  
  // 别名匹配
  for (const [name, data] of Object.entries(database)) {
    if (data.aliases && data.aliases.some(alias => 
      alias.toLowerCase().includes(query) || query.includes(alias.toLowerCase())
    )) {
      if (!results.find(r => r.name === name)) {
        results.push({ name, data, match: 'alias' });
      }
    }
    
    // INCI 名称匹配
    if (data.inci_name && data.inci_name.toLowerCase().includes(query)) {
      if (!results.find(r => r.name === name)) {
        results.push({ name, data, match: 'inci' });
      }
    }
  }
  
  // 模糊匹配
  if (results.length === 0) {
    for (const [name, data] of Object.entries(database)) {
      if (name.toLowerCase().includes(query)) {
        results.push({ name, data, match: 'fuzzy' });
      }
    }
  }
  
  return results;
}

function formatIngredient(result) {
  const { name, data, match } = result;
  let output = '';
  
  output += `\n🔬 成分查询：${name}`;
  if (match === 'alias') output += ' (别名匹配)';
  if (match === 'inci') output += ' (INCI 匹配)';
  if (match === 'fuzzy') output += ' (模糊匹配)';
  output += '\n';
  output += '═'.repeat(50) + '\n\n';
  
  // 基本信息
  output += '### 基本信息\n';
  output += `- INCI 名称：${data.inci_name || '暂无'}\n`;
  if (data.aliases && data.aliases.length > 0) {
    output += `- 别名：${data.aliases.join(', ')}\n`;
  }
  output += '\n';
  
  // 功效
  if (data.efficacy && data.efficacy.length > 0) {
    output += '### 功效\n';
    data.efficacy.forEach(eff => {
      output += `- ${eff.effect}（${eff.mechanism}）\n`;
      if (eff.source) {
        const authority = AUTHORITY_LEVELS[eff.authority] || '';
        output += `  ${authority} 来源：${eff.source}\n`;
      }
    });
    output += '\n';
  }
  
  // 安全评级
  if (data.safety) {
    output += '### 安全评级\n';
    if (data.safety.cosdna_rating) {
      output += `- COSDNA 评分：${data.safety.cosdna_rating}\n`;
    }
    if (data.safety.comedogenic !== undefined) {
      output += `- 致痘等级：${data.safety.comedogenic}\n`;
    }
    if (data.safety.irritation !== undefined) {
      output += `- 刺激等级：${data.safety.irritation}\n`;
    }
    if (data.safety.source) {
      output += `来源：${data.safety.source}\n`;
    }
    output += '\n';
  }
  
  // 使用建议
  if (data.usage) {
    output += '### 使用建议\n';
    if (data.usage.concentration) {
      output += `- 建议浓度：${data.usage.concentration}\n`;
    }
    if (data.usage.suitable_skin) {
      output += `- 适用肤质：${data.usage.suitable_skin.join(', ')}\n`;
    }
    if (data.usage.cautions && data.usage.cautions.length > 0) {
      output += `- 注意事项：\n`;
      data.usage.cautions.forEach(caution => {
        output += `  • ${caution}\n`;
      });
    }
    output += '\n';
  }
  
  // 用户反馈
  if (data.user_reviews && data.user_reviews.length > 0) {
    output += '### 用户反馈\n';
    data.user_reviews.forEach(review => {
      output += `"${review.text}"\n`;
      output += `⭐ 来源：${review.source}\n`;
    });
    output += '\n';
  }
  
  // 免责声明
  output += '═'.repeat(50) + '\n';
  output += '⚠️  免责声明：以上信息仅供参考，不构成专业建议。\n';
  output += '   个体差异大，使用前请咨询专业人士或做皮试。\n';
  output += '═'.repeat(50) + '\n';
  
  return output;
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('🔬 成分查询工具');
    console.log('═'.repeat(50));
    console.log('\n用法：./query-ingredient.js <成分名>\n');
    console.log('示例:');
    console.log('  ./query-ingredient.js "烟酰胺"');
    console.log('  ./query-ingredient.js "视黄醇"');
    console.log('  ./query-ingredient.js "Hyaluronic Acid"');
    console.log('\n支持中文、英文、INCI 名称查询');
    console.log('═'.repeat(50));
    return;
  }
  
  const query = args.join(' ');
  console.log(`\n🔍 正在查询成分：${query}...\n`);
  
  const database = loadDatabase();
  const results = searchIngredient(query, database);
  
  if (results.length === 0) {
    console.log('❌ 未找到该成分');
    console.log('\n提示：');
    console.log('  1. 检查拼写是否正确');
    console.log('  2. 尝试使用INCI 名称查询');
    console.log('  3. 数据库持续更新中，敬请期待');
    console.log('\n你可以：');
    console.log('  - 访问国家药监局数据库查询：https://www.nmpa.gov.cn/');
    console.log('  - 访问 COSDNA 查询：https://www.cosdna.com/');
    return;
  }
  
  // 显示第一个最匹配的结果
  console.log(formatIngredient(results[0]));
  
  // 如果有多个结果，显示其他匹配
  if (results.length > 1) {
    console.log(`\n💡 找到${results.length}个相关成分：`);
    results.slice(1, 5).forEach(r => {
      console.log(`  • ${r.name} (${r.match === 'exact' ? '精确' : '相关'})`);
    });
  }
}

main();
