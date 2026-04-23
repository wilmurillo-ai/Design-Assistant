#!/usr/bin/env node

/**
 * 腾讯广告妙思视频检索脚本
 * 用于在 admuse.qq.com 检索广告视频并返回前N条结果
 * 注意：需要登录状态才能查看视频详情
 * 
 * 使用方式: node search-ads.js "关键词" [结果数量]
 * 
 * 注意：本脚本依赖 OpenClass 内置的 browser 工具执行浏览器自动化
 */

const fs = require('fs');
const path = require('path');

// 配置
const BASE_URL = 'https://admuse.qq.com';
const DEFAULT_MAX_RESULTS = 10; // 默认返回10条结果
const DATA_FILE = path.join(__dirname, '..', 'data', 'recommended.json');

// 获取搜索关键词和数量
const searchKeyword = process.argv[2];
const maxResults = parseInt(process.argv[3]) || DEFAULT_MAX_RESULTS;

/**
 * 生成页面自动下拉脚本（用于触发懒加载）
 * 说明：
 * - 优先滚动素材列表容器；如果找不到容器则回退到 window 滚动
 * - 连续多次没有新增素材时自动停止，避免无效等待
 */
function buildAutoScrollScript() {
  return `
async function autoScrollForMoreVideos(options = {}) {
  const {
    cardSelector = '.material-card, .idea-card, [class*="material"], [class*="video-card"]',
    containerSelector = '.material-list, .list-wrap, .virtual-list, [class*="scroll"], [class*="list"]',
    maxRounds = 20,
    noGrowthLimit = 3,
    settleDelayMs = 1200,
    stepRatio = 0.9
  } = options;

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const getCount = () => document.querySelectorAll(cardSelector).length;

  const findScrollableContainer = () => {
    const candidates = Array.from(document.querySelectorAll(containerSelector));
    const valid = candidates.filter((el) => {
      if (!el) return false;
      const canScroll = el.scrollHeight > el.clientHeight + 16;
      const overflowY = window.getComputedStyle(el).overflowY;
      return canScroll && (overflowY === 'auto' || overflowY === 'scroll');
    });
    return valid[0] || null;
  };

  let totalRounds = 0;
  let noGrowthRounds = 0;
  let lastCount = getCount();
  let usedWindowScroll = false;

  const container = findScrollableContainer();
  if (!container) {
    usedWindowScroll = true;
  }

  while (totalRounds < maxRounds && noGrowthRounds < noGrowthLimit) {
    totalRounds += 1;

    if (container) {
      const step = Math.max(240, Math.floor(container.clientHeight * stepRatio));
      container.scrollTop = Math.min(container.scrollTop + step, container.scrollHeight);
    } else {
      const pageStep = Math.max(360, Math.floor(window.innerHeight * stepRatio));
      window.scrollBy(0, pageStep);
    }

    await sleep(settleDelayMs);

    const currentCount = getCount();
    if (currentCount > lastCount) {
      lastCount = currentCount;
      noGrowthRounds = 0;
    } else {
      noGrowthRounds += 1;
    }
  }

  return {
    success: true,
    totalRounds,
    noGrowthRounds,
    finalCount: lastCount,
    usedWindowScroll
  };
}
`;
}

/**
 * 读取已推荐的URL记录
 */
function loadRecommendedUrls() {
  try {
    if (fs.existsSync(DATA_FILE)) {
      const data = fs.readFileSync(DATA_FILE, 'utf-8');
      const parsed = JSON.parse(data);
      return parsed.recommendedUrls || [];
    }
  } catch (e) {
    console.error('读取记录文件失败:', e.message);
  }
  return [];
}

/**
 * 保存推荐的URL到记录文件
 */
function saveRecommendedUrls(urls) {
  try {
    const dir = path.dirname(DATA_FILE);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    const data = {
      lastUpdated: new Date().toISOString(),
      recommendedUrls: urls
    };
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch (e) {
    console.error('保存记录文件失败:', e.message);
  }
}

/**
 * 过滤掉已推荐的URL
 */
function filterDuplicates(results, recommendedUrls) {
  return results.filter(r => {
    if (!r.detailUrl) return true;
    // 检查详情页链接是否已推荐过
    return !recommendedUrls.includes(r.detailUrl);
  });
}

if (!searchKeyword) {
  console.log(`
腾讯广告妙思视频检索

用法: node search-ads.js "关键词" [结果数量]

示例:
  node search-ads.js "美妆"          # 检索10条美妆广告（自动去重）
  node search-ads.js "零食" 8         # 检索8条零食广告（自动去重）
  
注意: 
  - 默认返回10条结果
  - 自动过滤已推荐过的链接，确保不重复
  - 本脚本需要通过 OpenClaw 的 browser 工具执行浏览器自动化
  - 建议直接与 Assistant 对话使用本技能

微信特别说明:
  用户如果在微信收到信息，需要将信息转发一次后链接才可以变为可点击跳转的状态
  `);
  
  // 显示已推荐的URL数量
  const count = loadRecommendedUrls().length;
  console.log(`\n当前已推荐 ${count} 条广告链接\n`);
  process.exit(0);
}

// 打印搜索参数（实际检索由 OpenClaw browser 工具完成）
console.log(JSON.stringify({
  ready: true,
  keyword: searchKeyword,
  requestedCount: maxResults,
  platform: '腾讯广告妙思',
  note: '实际检索由 OpenClaw 内置浏览器工具自动完成',
  autoScroll: {
    enabled: true,
    description: '素材不足时自动下拉触发懒加载，直到获取更多卡片或判定无新增',
    executeFunction: 'autoScrollForMoreVideos',
    defaults: {
      maxRounds: 20,
      noGrowthLimit: 3,
      settleDelayMs: 1200,
      stepRatio: 0.9
    },
    script: buildAutoScrollScript()
  },
  wechatNote: '用户如果在微信收到信息，需要将信息转发一次后链接才可以变为可点击跳转的状态',
  deduplication: {
    enabled: true,
    description: '自动过滤已推荐过的链接，确保不重复推荐'
  }
}));
