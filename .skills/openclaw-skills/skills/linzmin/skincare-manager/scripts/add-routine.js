#!/usr/bin/env node
/**
 * 添加护肤流程脚本
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const ROUTINES_FILE = path.join(DATA_DIR, 'routines.json');

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--time' && args[i + 1]) {
      result.time = args[++i];
    } else if (args[i] === '--product' && args[i + 1]) {
      result.product = args[++i];
    } else if (args[i] === '--step' && args[i + 1]) {
      result.step = parseInt(args[++i]);
    } else if (args[i] === '--amount' && args[i + 1]) {
      result.amount = args[++i];
    } else if (args[i] === '--notes' && args[i + 1]) {
      result.notes = args[++i];
    }
  }
  return result;
}

function loadRoutines() {
  try {
    const data = fs.readFileSync(ROUTINES_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return {
      user_id: 'default',
      morning: [],
      night: [],
      updated_at: ''
    };
  }
}

function saveRoutines(data) {
  data.updated_at = new Date().toISOString();
  fs.writeFileSync(ROUTINES_FILE, JSON.stringify(data, null, 2));
}

function addRoutine(options) {
  const { time, product, step = 1, amount = '适量', notes = '' } = options;
  
  if (!time || !product) {
    console.log('❌ 缺少必要参数');
    console.log('\n用法：');
    console.log('  ./add-routine.js --time <morning/night> --product <产品名> [选项]');
    console.log('\n选项:');
    console.log('  --time      护肤时间 (morning/night) [必填]');
    console.log('  --product   产品名称 [必填]');
    console.log('  --step      步骤顺序 (默认：1)');
    console.log('  --amount    使用量 (默认：适量)');
    console.log('  --notes     备注');
    return false;
  }
  
  if (!['morning', 'night'].includes(time)) {
    console.log('❌ --time 必须是 morning 或 night');
    return false;
  }
  
  const routines = loadRoutines();
  
  // 检查是否已存在
  const exists = routines[time].find(r => 
    r.step === step || r.product === product
  );
  
  if (exists) {
    console.log('⚠️  该步骤或产品已存在，是否更新？(y/n)');
    const readline = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    return new Promise((resolve) => {
      readline.question('> ', (answer) => {
        readline.close();
        if (answer.toLowerCase() === 'y') {
          exists.product = product;
          exists.amount = amount;
          exists.notes = notes;
          saveRoutines(routines);
          console.log('✅ 已更新');
          resolve(true);
        } else {
          console.log('❌ 已取消');
          resolve(false);
        }
      });
    });
  }
  
  // 添加新流程
  routines[time].push({
    step,
    product,
    amount,
    notes,
    created_at: new Date().toISOString()
  });
  
  // 按步骤排序
  routines[time].sort((a, b) => a.step - b.step);
  
  saveRoutines(routines);
  
  console.log('✅ 已添加护肤流程');
  console.log(`\n📝 ${time === 'morning' ? '🌅' : '🌙'} ${time === 'morning' ? '晨间' : '夜间'}护肤流程`);
  console.log(`   步骤${step}: ${product} (${amount})`);
  
  return true;
}

// 主程序
const args = process.argv.slice(2);
const options = parseArgs(args);

if (args.length === 0) {
  console.log('💆 添加护肤流程');
  console.log('═'.repeat(50));
  console.log('\n用法：');
  console.log('  ./add-routine.js --time <morning/night> --product <产品名> [选项]');
  console.log('\n示例:');
  console.log('  ./add-routine.js --time morning --product "氨基酸洁面" --step 1');
  console.log('  ./add-routine.js --time night --product "视黄醇精华" --step 3 --amount "2-3 滴"');
  console.log('═'.repeat(50));
  process.exit(0);
}

addRoutine(options).catch(console.error);
