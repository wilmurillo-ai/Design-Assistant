#!/usr/bin/env node

/**
 * daily-writer.js - Daily 笔记写入工具。Daily note writer utility.
 * 
 * 负责生成和写入格式化的 Daily 笔记，使用大模型优化笔记格式和内容。
 * Generates and writes formatted Daily notes, uses LLM to optimize note format and content.
 * 
 * 特性：
 * - LLM 生成格式化笔记
 * - 模板降级方案
 * - 支持追加/覆盖写入
 * - 日期时间格式化
 * 
 * Features:
 * - LLM-generated formatted notes
 * - Template fallback
 * - Supports append/overwrite write
 * - Date/time formatting
 */

const fs = require('fs');
const path = require('path');
const { generateDailyNote } = require('./subagent-runner');

/**
 * formatDate - 格式化日期。Format date.
 * @param {Date} date - 日期对象。Date object.
 * @returns {string} 格式化后的日期（YYYY-MM-DD）。Formatted date.
 */
function formatDate(date = new Date()) {
  return date.toISOString().split('T')[0];
}

/**
 * formatTime - 格式化时间。Format time.
 * @param {number|string} timestamp - 时间戳。Timestamp.
 * @returns {string} 格式化后的时间（HH:mm）。Formatted time.
 */
function formatTime(timestamp) {
  if (!timestamp) return '未知';
  
  const date = new Date(timestamp);
  if (isNaN(date.getTime())) {
    return '未知';
  }
  
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

/**
 * generateDailyNoteWithLLM - 使用 LLM 生成格式化的 Daily 笔记。Generate formatted Daily note using LLM.
 * @param {Array} sessionInfos - 会话信息列表。Session infos list.
 * @param {Date} date - 日期。Date.
 * @returns {Promise<string>} Daily 笔记内容。Daily note content.
 */
async function generateDailyNoteWithLLM(sessionInfos, date = new Date()) {
  const dateStr = formatDate(date);
  
  try {
    console.log('  🤖 使用 LLM 生成 Daily 笔记...');
    const dailyNote = await generateDailyNote(sessionInfos, dateStr);
    
    // 确保包含日期标题。Ensure date header is included.
    if (!dailyNote.includes(`# ${dateStr}`)) {
      return `# ${dateStr} 聊天记录\n\n` + dailyNote;
    }
    
    return dailyNote;
  } catch (error) {
    console.error('  ⚠️  LLM 生成 Daily 笔记失败，使用模板生成:', error.message);
    return generateDailyNoteTemplate(sessionInfos, date);
  }
}

/**
 * 使用模板生成 Daily 笔记（降级方案）
 */
function generateDailyNoteTemplate(sessionInfos, date = new Date()) {
  const dateStr = formatDate(date);
  
  // 统计信息
  const total = sessionInfos.length;
  const active = sessionInfos.filter(s => s.status === '✅').length;
  const deleted = sessionInfos.filter(s => s.status === '❌').length;
  const reset = sessionInfos.filter(s => s.status === '🔄').length;
  
  // 提取主要话题
  const allTopics = new Set();
  sessionInfos.forEach(info => {
    const topics = Array.isArray(info.topics) ? info.topics : [info.topics];
    topics.forEach(topic => {
      if (topic) allTopics.add(topic.replace(/#/g, ''));
    });
  });
  
  // 提取关键决策
  const allDecisions = sessionInfos.flatMap(s => s.decisions || []);
  const keyDecisions = allDecisions.slice(0, 3).join('; ') || '无';
  
  // 生成笔记内容
  let content = `# ${dateStr} 聊天记录\n\n`;
  
  content += `## 📊 当日总结\n\n`;
  content += `- 总会话数：**${total}** 个\n`;
  content += `- 活跃：**${active}** | 删除：**${deleted}** | 重置：**${reset}**\n`;
  content += `- 主要话题：${Array.from(allTopics).join(', ') || '日常'}\n`;
  content += `- 关键决策：${keyDecisions}\n\n`;
  
  content += `## 💬 会话详情\n\n`;
  
  // 添加每个 session 的详情
  for (const info of sessionInfos) {
    const topicTitle = info.title || (Array.isArray(info.topics) ? info.topics.join(' - ') : '未命名会话');
    const tags = Array.isArray(info.topics) ? info.topics.join(' ') : (info.topics || '#日常');
    
    content += `### 📋 ${topicTitle}\n\n`;
    content += `**标签：** ${info.status} | ${tags}\n\n`;
    content += `**时间：** ${formatTime(info.startTime)}-${formatTime(info.endTime)}\n\n`;
    content += `**消息数：** ${info.messageCount || 0} 条\n\n`;
    content += `**摘要：** ${info.summary || '无摘要'}\n\n`;
    
    if (info.decisions && info.decisions.length > 0) {
      content += `**关键发现/决策：**\n\n`;
      for (const decision of info.decisions) {
        content += `- ${decision}\n`;
      }
      content += '\n';
    }
    
    content += `---\n\n`;
  }
  
  return content;
}

/**
 * 写入 Daily 笔记文件
 */
function writeDailyNote(content, date = new Date(), dailyDir) {
  try {
    // 确保目录存在
    if (!fs.existsSync(dailyDir)) {
      fs.mkdirSync(dailyDir, { recursive: true });
    }
    
    const filePath = path.join(dailyDir, `${formatDate(date)}.md`);
    
    // 检查文件是否已存在
    if (fs.existsSync(filePath)) {
      // 读取现有内容，避免重复
      const existing = fs.readFileSync(filePath, 'utf-8');
      
      // 简单检查：如果已包含类似内容，则不重复写入
      if (existing.includes('## 💬 会话详情')) {
        // 追加到现有内容后面
        fs.writeFileSync(filePath, existing + '\n\n---\n\n' + content, 'utf-8');
      } else {
        // 覆盖写入
        fs.writeFileSync(filePath, content, 'utf-8');
      }
    } else {
      fs.writeFileSync(filePath, content, 'utf-8');
    }
    
    return {
      success: true,
      path: filePath,
      date: formatDate(date)
    };
  } catch (error) {
    console.error('写入 Daily 笔记失败:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 读取现有 Daily 笔记
 */
function readDailyNote(date = new Date(), dailyDir) {
  const filePath = path.join(dailyDir, `${formatDate(date)}.md`);
  
  if (!fs.existsSync(filePath)) {
    return null;
  }
  
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch (error) {
    console.error('读取 Daily 笔记失败:', error.message);
    return null;
  }
}

/**
 * 检查日期是否已有笔记
 */
function hasDailyNote(date = new Date(), dailyDir) {
  const filePath = path.join(dailyDir, `${formatDate(date)}.md`);
  return fs.existsSync(filePath);
}

module.exports = {
  formatDate,
  formatTime,
  generateDailyNoteWithLLM,
  generateDailyNoteTemplate,
  writeDailyNote,
  readDailyNote,
  hasDailyNote
};
