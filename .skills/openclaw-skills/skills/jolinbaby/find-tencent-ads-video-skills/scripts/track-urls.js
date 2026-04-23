#!/usr/bin/env node

/**
 * 记录推荐链接脚本
 * 用于将已推荐给用户的链接保存到记录文件中
 * 
 * 用法: node track-urls.js add "url1" "url2" ...
 *       node track-urls.js list
 *       node track-urls.js clear
 */

const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, '..', 'references', 'recommended.json');

function loadData() {
  try {
    if (fs.existsSync(DATA_FILE)) {
      return JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
    }
  } catch (e) {}
  return { lastUpdated: null, recommendedUrls: [] };
}

const MILESTONE = 10000; // 记录达到10000条时触发提醒
const MAX_RECORDS = 100; // 最大记录数
const PRUNE_COUNT = 20; // 达到上限时删除的前N条

function saveData(data) {
  const dir = path.dirname(DATA_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  const prevCount = data.recommendedUrls ? data.recommendedUrls.length : 0;
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf-8');
  
  // 检查是否达到里程碑
  const newCount = data.recommendedUrls ? data.recommendedUrls.length : 0;
  if (newCount > prevCount && newCount % MILESTONE === 0) {
    console.log(`\n🎉 已推荐链接数量达到 ${newCount} 条！\n`);
  }
  
  return data;
}

const command = process.argv[2];

if (command === 'list') {
  const data = loadData();
  console.log(`\n已推荐链接数量: ${data.recommendedUrls.length}`);
  console.log(`最后更新: ${data.lastUpdated || '无'}\n`);
  data.recommendedUrls.forEach((url, i) => {
    console.log(`${i + 1}. ${url}`);
  });
  console.log('');
} else if (command === 'clear') {
  saveData({ lastUpdated: new Date().toISOString(), recommendedUrls: [] });
  console.log('已清空推荐记录\n');
} else if (command === 'add') {
  const urls = process.argv.slice(3);
  if (urls.length === 0) {
    console.error('请提供要添加的URL');
    process.exit(1);
  }
  let data = loadData();
  const existing = data.recommendedUrls || [];
  const filtered = urls.filter(url => url && !existing.includes(url));
  let updated = [...existing, ...filtered];
  
  // 自动清理：当达到500条时删除前100条
  if (updated.length >= MAX_RECORDS) {
    updated = updated.slice(PRUNE_COUNT);
    console.log(`\n🧹 已自动清理 ${PRUNE_COUNT} 条旧记录（保留最近 ${updated.length} 条）\n`);
  }
  
  data.recommendedUrls = updated;
  data.lastUpdated = new Date().toISOString();
  saveData(data);
  console.log(`已添加 ${filtered.length} 条链接（已过滤 ${urls.length - filtered.length} 条重复）`);
  console.log(`当前总计: ${data.recommendedUrls.length} 条\n`);
} else {
  console.log(`
链接记录工具

用法:
  node track-urls.js add "url1" "url2" ...   # 添加链接
  node track-urls.js list                    # 查看已记录的链接
  node track-urls.js clear                    # 清空所有记录
  `);
}
