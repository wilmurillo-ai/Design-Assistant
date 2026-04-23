#!/usr/bin/env node
/**
 * 添加产品脚本
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const PRODUCTS_FILE = path.join(DATA_DIR, 'products.json');

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--expiry' && args[i + 1]) {
      result.expiry = args[++i];
    } else if (args[i] === '--category' && args[i + 1]) {
      result.category = args[++i];
    } else if (args[i] === '--opened' && args[i + 1]) {
      result.opened = args[++i];
    } else if (args[i] === '--paq' && args[i + 1]) {
      result.paq = parseInt(args[++i]);
    } else if (args[i] === '--notes' && args[i + 1]) {
      result.notes = args[++i];
    } else if (!args[i].startsWith('--')) {
      result.name = args[i];
    }
  }
  return result;
}

function loadProducts() {
  try {
    const data = fs.readFileSync(PRODUCTS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return { products: [], updated_at: '' };
  }
}

function saveProducts(data) {
  data.updated_at = new Date().toISOString();
  fs.writeFileSync(PRODUCTS_FILE, JSON.stringify(data, null, 2));
}

function calculatePAQExpiry(openedDate, paqMonths) {
  const date = new Date(openedDate);
  date.setMonth(date.getMonth() + paqMonths);
  return date.toISOString().split('T')[0];
}

function addProduct(options) {
  const { name, expiry, category = '未分类', opened, paq, notes = '' } = options;
  
  if (!name) {
    console.log('❌ 缺少产品名称');
    console.log('\n用法：');
    console.log('  ./add-product.js <产品名> [选项]');
    console.log('\n选项:');
    console.log('  --expiry    到期日期 (YYYY-MM-DD)');
    console.log('  --category  类别 (洁面/精华/面霜/防晒等)');
    console.log('  --opened    开封日期 (YYYY-MM-DD)');
    console.log('  --paq       开封后保质期 (月)');
    console.log('  --notes     备注');
    console.log('\n示例:');
    console.log('  ./add-product.js "SK-II 神仙水" --expiry 2027-12-31 --category 精华水');
    console.log('  ./add-product.js "兰蔻小黑瓶" --opened 2026-04-01 --paq 12');
    return false;
  }
  
  const products = loadProducts();
  
  // 检查是否已存在
  const exists = products.products.find(p => p.name === name);
  
  if (exists) {
    console.log(`⚠️  产品 "${name}" 已存在，是否更新？(y/n)`);
    const readline = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    return new Promise((resolve) => {
      readline.question('> ', (answer) => {
        readline.close();
        if (answer.toLowerCase() === 'y') {
          if (expiry) exists.expiry_date = expiry;
          if (category) exists.category = category;
          if (opened) exists.opened_date = opened;
          if (paq) exists.paq_months = paq;
          if (notes) exists.notes = notes;
          exists.updated_at = new Date().toISOString();
          saveProducts(products);
          console.log('✅ 已更新产品');
          resolve(true);
        } else {
          console.log('❌ 已取消');
          resolve(false);
        }
      });
    });
  }
  
  // 计算到期日期
  let finalExpiry = expiry;
  if (opened && paq && !expiry) {
    finalExpiry = calculatePAQExpiry(opened, paq);
    console.log(`📅 根据开封日期和 PAQ，自动计算到期日：${finalExpiry}`);
  }
  
  // 添加新产品
  const product = {
    id: `prod_${Date.now()}`,
    name,
    category,
    expiry_date: finalExpiry || null,
    opened_date: opened || null,
    paq_months: paq || null,
    notes,
    status: 'active',
    created_at: new Date().toISOString()
  };
  
  products.products.push(product);
  saveProducts(products);
  
  console.log('✅ 已添加产品');
  console.log(`\n📦 产品信息:`);
  console.log(`   名称：${name}`);
  console.log(`   类别：${category}`);
  if (finalExpiry) {
    console.log(`   到期：${finalExpiry}`);
  }
  if (opened) {
    console.log(`   开封：${opened}`);
  }
  if (paq) {
    console.log(`   PAQ: ${paq}个月`);
  }
  
  return true;
}

// 主程序
const args = process.argv.slice(2);
const options = parseArgs(args);

if (args.length === 0) {
  console.log('📦 添加产品');
  console.log('═'.repeat(50));
  console.log('\n用法：');
  console.log('  ./add-product.js <产品名> [选项]');
  console.log('\n示例:');
  console.log('  ./add-product.js "SK-II 神仙水" --expiry 2027-12-31 --category 精华水');
  console.log('  ./add-product.js "兰蔻小黑瓶" --opened 2026-04-01 --paq 12');
  console.log('═'.repeat(50));
  process.exit(0);
}

try {
  addProduct(options);
} catch (error) {
  console.error(error);
}
