#!/usr/bin/env node
/**
 * 查看产品列表脚本
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const PRODUCTS_FILE = path.join(DATA_DIR, 'products.json');

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--expiring') {
      result.expiring = true;
    } else if (args[i] === '--expired') {
      result.expired = true;
    } else if (args[i] === '--category' && args[i + 1]) {
      result.category = args[++i];
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

function daysUntil(dateStr) {
  if (!dateStr) return null;
  const today = new Date();
  const target = new Date(dateStr);
  const diff = target - today;
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

function displayProducts(products, options) {
  let filtered = products;
  
  const today = new Date();
  
  // 过滤即将到期
  if (options.expiring) {
    filtered = products.filter(p => {
      const days = daysUntil(p.expiry_date);
      return days !== null && days >= 0 && days <= 30;
    });
  }
  
  // 过滤已过期
  if (options.expired) {
    filtered = products.filter(p => {
      const days = daysUntil(p.expiry_date);
      return days !== null && days < 0;
    });
  }
  
  // 按类别过滤
  if (options.category) {
    filtered = filtered.filter(p => 
      p.category.toLowerCase().includes(options.category.toLowerCase())
    );
  }
  
  if (filtered.length === 0) {
    console.log('📦 暂无产品');
    console.log('\n💡 提示：使用 ./add-product.js 添加产品');
    return;
  }
  
  // 按到期日排序
  filtered.sort((a, b) => {
    if (!a.expiry_date) return 1;
    if (!b.expiry_date) return -1;
    return new Date(a.expiry_date) - new Date(b.expiry_date);
  });
  
  console.log(`\n📦 产品列表 (${filtered.length}个)`);
  console.log('═'.repeat(60));
  
  filtered.forEach((p, index) => {
    const days = daysUntil(p.expiry_date);
    let status = '';
    
    if (days === null) {
      status = '📅 未设置到期日';
    } else if (days < 0) {
      status = `❌ 已过期 ${Math.abs(days)}天`;
    } else if (days <= 7) {
      status = `🚨 ${days}天后到期`;
    } else if (days <= 30) {
      status = `⚠️ ${days}天后到期`;
    } else {
      status = `✅ ${days}天后到期`;
    }
    
    console.log(`\n${index + 1}. ${p.name}`);
    console.log(`   类别：${p.category}`);
    console.log(`   状态：${status}`);
    
    if (p.expiry_date) {
      console.log(`   到期：${p.expiry_date}`);
    }
    if (p.opened_date) {
      console.log(`   开封：${p.opened_date}`);
    }
    if (p.paq_months) {
      console.log(`   PAQ: ${p.paq_months}个月`);
    }
    if (p.notes) {
      console.log(`   备注：${p.notes}`);
    }
  });
  
  console.log('\n' + '═'.repeat(60));
  
  // 统计信息
  const total = products.length;
  const expired = products.filter(p => daysUntil(p.expiry_date) < 0).length;
  const expiring30 = products.filter(p => {
    const days = daysUntil(p.expiry_date);
    return days !== null && days >= 0 && days <= 30;
  }).length;
  const noExpiry = products.filter(p => !p.expiry_date).length;
  
  console.log(`\n📊 库存统计:`);
  console.log(`   总计：${total}个产品`);
  console.log(`   已过期：${expired}个`);
  console.log(`   即将到期 (30 天内): ${expiring30}个`);
  console.log(`   未设置到期日：${noExpiry}个`);
}

function main() {
  const args = process.argv.slice(2);
  const options = parseArgs(args);
  
  const products = loadProducts();
  
  console.log('📦 护肤产品管理');
  console.log('═'.repeat(50));
  
  displayProducts(products.products, options);
  
  console.log('\n💡 提示:');
  console.log('  添加产品：./add-product.js "产品名" --expiry 2027-12-31');
  console.log('  只看即将到期：./list-products.js --expiring');
  console.log('  只看已过期：./list-products.js --expired');
  console.log('  按类别筛选：./list-products.js --category 精华');
  console.log('═'.repeat(50));
}

main();
