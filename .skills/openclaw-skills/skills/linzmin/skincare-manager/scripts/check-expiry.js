#!/usr/bin/env node
/**
 * 检查产品到期提醒脚本
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const PRODUCTS_FILE = path.join(DATA_DIR, 'products.json');

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

function checkExpiry() {
  const products = loadProducts();
  const today = new Date();
  
  const expired = [];
  const expiring7 = [];
  const expiring30 = [];
  
  products.products.forEach(p => {
    if (!p.expiry_date) return;
    
    const days = daysUntil(p.expiry_date);
    
    if (days < 0) {
      expired.push({ ...p, days });
    } else if (days <= 7) {
      expiring7.push({ ...p, days });
    } else if (days <= 30) {
      expiring30.push({ ...p, days });
    }
  });
  
  console.log('⏰ 产品到期提醒');
  console.log('═'.repeat(60));
  console.log(`📅 检查日期：${today.toLocaleDateString('zh-CN')}`);
  console.log('═'.repeat(60));
  
  // 已过期
  if (expired.length > 0) {
    console.log(`\n🚨 已过期产品 (${expired.length}个)`);
    console.log('─'.repeat(60));
    expired.forEach(p => {
      console.log(`❌ ${p.name}`);
      console.log(`   到期：${p.expiry_date} (已过期 ${Math.abs(p.days)}天)`);
      console.log(`   建议：请停止使用并丢弃`);
    });
  }
  
  // 7 天内到期
  if (expiring7.length > 0) {
    console.log(`\n⚠️  7 天内到期 (${expiring7.length}个)`);
    console.log('─'.repeat(60));
    expiring7.forEach(p => {
      console.log(`🚨 ${p.name}`);
      console.log(`   到期：${p.expiry_date} (${p.days}天后)`);
      console.log(`   建议：尽快使用`);
    });
  }
  
  // 30 天内到期
  if (expiring30.length > 0) {
    console.log(`\n📅 30 天内到期 (${expiring30.length}个)`);
    console.log('─'.repeat(60));
    expiring30.forEach(p => {
      console.log(`⚠️ ${p.name}`);
      console.log(`   到期：${p.expiry_date} (${p.days}天后)`);
      console.log(`   建议：安排使用`);
    });
  }
  
  // 总结
  if (expired.length === 0 && expiring7.length === 0 && expiring30.length === 0) {
    console.log('\n✅ 所有产品都在有效期内');
  }
  
  console.log('\n' + '═'.repeat(60));
  console.log('📊 统计:');
  console.log(`   总计：${products.products.length}个产品`);
  console.log(`   已过期：${expired.length}个`);
  console.log(`   7 天内到期：${expiring7.length}个`);
  console.log(`   30 天内到期：${expiring30.length}个`);
  console.log('═'.repeat(60));
  
  // 下次检查日期
  const nextCheck = new Date(today);
  nextCheck.setDate(nextCheck.getDate() + 7);
  console.log(`\n⏰ 下次检查：${nextCheck.toLocaleDateString('zh-CN')}`);
  console.log('═'.repeat(60));
  
  // 返回需要提醒的产品（用于微信推送）
  return {
    expired,
    expiring7,
    expiring30,
    next_check: nextCheck.toISOString()
  };
}

// 主程序
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log('⏰ 检查产品到期提醒');
  console.log('═'.repeat(50));
  console.log('\n用法：');
  console.log('  ./check-expiry.js [选项]');
  console.log('\n选项:');
  console.log('  --json    输出 JSON 格式（用于程序调用）');
  console.log('  --help    显示帮助');
  console.log('═'.repeat(50));
  process.exit(0);
}

if (args.includes('--json')) {
  const result = checkExpiry();
  console.log(JSON.stringify(result, null, 2));
} else {
  checkExpiry();
}
