#!/usr/bin/env node
/**
 * 查看护肤流程脚本
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const ROUTINES_FILE = path.join(DATA_DIR, 'routines.json');

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

function displayRoutine(time, routines) {
  const emoji = time === 'morning' ? '🌅' : '🌙';
  const title = time === 'morning' ? '晨间' : '夜间';
  
  console.log(`\n${emoji} ${title}护肤流程`);
  console.log('─'.repeat(40));
  
  if (routines.length === 0) {
    console.log('  暂无流程，使用 --add 添加');
    return;
  }
  
  routines.forEach(r => {
    console.log(`步骤${r.step}: ${r.product}`);
    if (r.amount) {
      console.log(`  用量：${r.amount}`);
    }
    if (r.notes) {
      console.log(`  备注：${r.notes}`);
    }
  });
  
  console.log('─'.repeat(40));
}

function main() {
  const args = process.argv.slice(2);
  const timeFilter = args[0];
  
  const routines = loadRoutines();
  
  console.log('💆 护肤流程');
  console.log('═'.repeat(50));
  
  if (!timeFilter || timeFilter === 'morning') {
    displayRoutine('morning', routines.morning);
  }
  
  if (!timeFilter || timeFilter === 'night') {
    displayRoutine('night', routines.night);
  }
  
  if (routines.updated_at) {
    const date = new Date(routines.updated_at);
    console.log(`\n📝 最后更新：${date.toLocaleString('zh-CN')}`);
  }
  
  console.log('\n💡 提示:');
  console.log('  添加流程：./add-routine.js --time morning --product "洁面"');
  console.log('  只看晨间：./list-routine.js morning');
  console.log('  只看夜间：./list-routine.js night');
  console.log('═'.repeat(50));
}

main();
