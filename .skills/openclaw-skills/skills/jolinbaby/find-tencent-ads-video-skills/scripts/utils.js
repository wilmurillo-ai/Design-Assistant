const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, '..', 'references', 'recommended.json');
const MILESTONE = 10000; // 记录达到10000条时触发提醒
const MAX_RECORDS = 100; // 最大记录数
const PRUNE_COUNT = 20; // 达到上限时删除的前N条

/**
 * 获取已推荐的URL列表
 */
function getRecommendedUrls() {
  try {
    if (fs.existsSync(DATA_FILE)) {
      const data = fs.readFileSync(DATA_FILE, 'utf-8');
      const parsed = JSON.parse(data);
      return parsed.recommendedUrls || [];
    }
  } catch (e) {
    console.error('读取记录失败:', e.message);
  }
  return [];
}

/**
 * 添加新的推荐URL到记录
 */
function addRecommendedUrls(newUrls) {
  try {
    let existing = getRecommendedUrls();
    const filtered = newUrls.filter(url => url && !existing.includes(url));
    let updated = [...existing, ...filtered];
    
    // 自动清理：当达到500条时删除前100条
    if (updated.length >= MAX_RECORDS) {
      const removed = updated.slice(0, PRUNE_COUNT);
      updated = updated.slice(PRUNE_COUNT);
      console.log(`\n🧹 已自动清理 ${PRUNE_COUNT} 条旧记录（保留最近 ${updated.length} 条）\n`);
    }
    
    const dir = path.dirname(DATA_FILE);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    const data = {
      lastUpdated: new Date().toISOString(),
      recommendedUrls: updated
    };
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf-8');
    
    // 检查是否达到里程碑
    if (updated.length > existing.length && updated.length % MILESTONE === 0) {
      console.log(`\n🎉 已推荐链接数量达到 ${updated.length} 条！\n`);
    }
    
    return updated;
  } catch (e) {
    console.error('保存记录失败:', e.message);
    return getRecommendedUrls();
  }
}

/**
 * 过滤掉已推荐的URL
 */
function filterDuplicates(results) {
  const recommended = getRecommendedUrls();
  return results.filter(r => {
    if (!r.detailUrl) return true;
    return !recommended.includes(r.detailUrl);
  });
}

module.exports = {
  getRecommendedUrls,
  addRecommendedUrls,
  filterDuplicates,
  DATA_FILE
};
