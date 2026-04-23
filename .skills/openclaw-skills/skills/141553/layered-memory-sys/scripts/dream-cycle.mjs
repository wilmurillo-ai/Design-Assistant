#!/usr/bin/env node
// dream-cycle.mjs - 梦境模式执行器
// 触发：心跳或手动执行

import fs from 'fs';
import path from 'path';
import { semanticSimilarity, findSimilarMemories, mergeMemories } from './semantic-similarity.mjs';
import { searchSessionLogs, getRecentSessionSummary } from './session-search.mjs';

const INDEX_PATH = '/root/.openclaw/workspace/memory/index.json';
const DREAM_LOG_PATH = '/root/.openclaw/workspace/memory/dream-log.md';
const ARCHIVE_PATH = '/root/.openclaw/workspace/memory/archive.md';

// 加载索引
function loadIndex() {
  const data = fs.readFileSync(INDEX_PATH, 'utf-8');
  return JSON.parse(data);
}

// 保存索引
function saveIndex(index) {
  index.updatedAt = new Date().toISOString();
  fs.writeFileSync(INDEX_PATH, JSON.stringify(index, null, 2));
}

// 记录梦境日志
function logDream(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const icon = {
    consolidate: '🧠',
    archive: '📦',
    forget: '🗑️',
    merge: '🔗',
    info: '💤',
    complete: '✨'
  }[type];
  
  const entry = `${icon} ${message}`;
  
  // 追加到日志文件
  let log = fs.readFileSync(DREAM_LOG_PATH, 'utf-8');
  if (!log.includes(new Date().toISOString().split('T')[0])) {
    log += `\n## ${new Date().toISOString().split('T')[0]}\n\n`;
  }
  log += `${entry}\n`;
  fs.writeFileSync(DREAM_LOG_PATH, log);
  
  console.log(entry);
}

// 梦境核心流程
async function dreamCycle() {
  console.log('💤 梦境模式开始...\n');
  
  const index = loadIndex();
  const memories = index.memories || [];
  const today = new Date().toISOString().split('T')[0];
  
  let consolidated = 0, archived = 0, forgotten = 0, merged = 0;
  
  // 1. 巩固检查 (高recallCount的记忆升级)
  logDream('开始巩固检查...', 'info');
  for (const mem of memories) {
    const recallCount = mem.recallCount || 0;
    const currentLayer = mem.layer;
    
    if (recallCount >= 3 && currentLayer === 'flash') {
      mem.layer = 'active';
      mem.ttl = 7;
      logDream(`巩固：${mem.title} (flash→active, recall=${recallCount})`, 'consolidate');
      consolidated++;
    } else if (recallCount >= 5 && currentLayer === 'active') {
      mem.layer = 'attention';
      mem.ttl = 30;
      logDream(`巩固：${mem.title} (active→attention, recall=${recallCount})`, 'consolidate');
      consolidated++;
    } else if (recallCount >= 10 && currentLayer === 'attention') {
      mem.layer = 'settled';
      mem.ttl = 90;
      logDream(`巩固：${mem.title} (attention→settled, recall=${recallCount})`, 'consolidate');
      consolidated++;
    }
  }
  
  // 2. 归档/遗忘检查 (过期记忆)
  logDream('开始归档/遗忘检查...', 'info');
  for (let i = memories.length - 1; i >= 0; i--) {
    const mem = memories[i];
    const lastActive = mem.lastActive || mem.created;
    const ttl = mem.ttl || 7;
    const daysSince = Math.floor((new Date(today) - new Date(lastActive)) / (1000 * 60 * 60 * 24));
    
    if (daysSince >= ttl) {
      if (mem.layer === 'flash') {
        // 闪存层直接遗忘
        memories.splice(i, 1);
        logDream(`遗忘：${mem.title} (${daysSince}天过期)`, 'forget');
        forgotten++;
      } else {
        // 其他层归档
        const archiveEntry = `- [${mem.lastActive}] ${mem.title}\n  状态：${mem.status || 'unknown'} | 概括：${mem.summary?.slice(0, 100)}...`;
        
        let archive = fs.readFileSync(ARCHIVE_PATH, 'utf-8');
        // 找到对应的分类并插入
        const category = mem.tags?.[0] || '其他';
        archive = archive.replace(
          new RegExp(`## ${category}\\n\\n（暂无归档）`),
          `## ${category}\n\n${archiveEntry}\n`
        );
        fs.writeFileSync(ARCHIVE_PATH, archive);
        
        mem.status = 'archived';
        mem.archivedAt = today;
        // 从活跃列表移到最后（但保留，因为归档到单独文件了）
        memories.splice(i, 1);
        
        logDream(`归档：${mem.title} → archive.md (${daysSince}天过期)`, 'archive');
        archived++;
      }
    }
  }
  
  // 3. 合并检查 (相似记忆)
  logDream('开始合并检查...', 'info');
  const toMerge = [];
  for (let i = 0; i < memories.length; i++) {
    for (let j = i + 1; j < memories.length; j++) {
      const sim = findSimilarMemories(memories[i], [memories[j]], 0.6);
      if (sim.length > 0 && sim[0].canMerge) {
        toMerge.push([i, j, sim[0].similarity]);
      }
    }
  }
  
  // 执行合并（按相似度降序，避免重复合并）
  toMerge.sort((a, b) => b[2] - a[2]);
  const mergedIds = new Set();
  for (const [i, j, sim] of toMerge) {
    if (!mergedIds.has(i) && !mergedIds.has(j)) {
      const merged = mergeMemories(memories[i], memories[j]);
      logDream(`合并：${memories[i].title} + ${memories[j].title} (相似度${(sim*100).toFixed(0)}%)`, 'merge');
      memories[i] = merged;
      mergedIds.add(j);
      merged++;
    }
  }
  // 删除被合并的
  index.memories = memories.filter((_, i) => !mergedIds.has(i));
  
  // 保存
  saveIndex(index);
  
  // 4. 搜索session日志补充上下文
  logDream('搜索session日志...', 'info');
  const recentSummary = getRecentSessionSummary(60, 5);
  if (recentSummary.length > 0) {
    logDream(`从session日志找到 ${recentSummary.length} 条最近对话`, 'info');
  }
  
  // 完成
  logDream('梦境模式完成', 'complete');
  logDream(`统计：巩固${consolidated}条 归档${archived}条 遗忘${forgotten}条 合并${merged}条`, 'info');
  
  console.log('\n💤 梦境结束，下次检查将在下次心跳触发');
}

// 执行
dreamCycle().catch(err => {
  console.error('梦境模式出错:', err);
  process.exit(1);
});
