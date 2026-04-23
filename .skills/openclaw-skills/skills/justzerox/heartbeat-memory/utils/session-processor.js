#!/usr/bin/env node

/**
 * session-processor.js - Session 处理工具
 * 
 * 负责读取、解析和提取 session 的关键信息
 */

const fs = require('fs');
const path = require('path');

/**
 * 读取 session 消息（文件系统降级方案）
 * @param {string} sessionPath - session 文件路径
 * @returns {Array|null} 消息列表
 */
function readSessionMessages(sessionPath) {
  try {
    if (!sessionPath || !fs.existsSync(sessionPath)) {
      return null;
    }

    if (sessionPath.endsWith('.jsonl')) {
      const content = fs.readFileSync(sessionPath, 'utf-8');
      const lines = content.trim().split('\n');
      const messages = [];

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const entry = JSON.parse(line);
          if (entry.type === 'message' && entry.message) {
            messages.push({
              role: entry.message.role,
              content: Array.isArray(entry.message.content)
                ? entry.message.content.map(c => c.text || '').join('')
                : (entry.message.content || ''),
              timestamp: entry.timestamp
            });
          }
        } catch (e) {
          // 跳过无效行
        }
      }

      return messages.length > 0 ? messages : null;
    }

    // 目录格式
    const messagesPath = path.join(sessionPath, 'messages.json');
    if (fs.existsSync(messagesPath)) {
      return JSON.parse(fs.readFileSync(messagesPath, 'utf-8'));
    }

    return null;
  } catch (error) {
    console.error(`读取 session 消息失败：${error.message}`);
    return null;
  }
}

/**
 * 判断 session 状态（返回字符串，展示层转 emoji）
 * @param {Object} session - session 对象
 * @returns {string} 'active' | 'deleted' | 'reset'
 */
function determineSessionStatus(session) {
  // 优先用 session.kind（如果存在）
  if (session.kind) {
    if (session.kind === 'deleted') return 'deleted';
    if (session.kind === 'reset') return 'reset';
  }

  // 检查 sessionKey/sessionId 中是否包含标记
  const id = (session.sessionKey || session.sessionId || '').toLowerCase();
  if (id.includes('deleted') || id.includes('removed')) return 'deleted';
  if (id.includes('reset') || id.includes('restart')) return 'reset';

  return 'active';
}

/**
 * 展示层：将状态字符串转为 emoji
 * @param {string} status - 状态字符串
 * @returns {string} emoji
 */
function statusEmoji(status) {
  const map = { active: '✅', deleted: '❌', reset: '🔄' };
  return map[status] || '✅';
}

/**
 * 兼容多种 session 路径字段
 * @param {Object} session - session 对象
 * @returns {string|null} session 路径
 */
function getSessionPath(session) {
  return session.transcriptPath ||
    session.path ||
    session.key ||
    session.sessionKey ||
    null;
}

/**
 * 简单摘要（降级方案，无 LLM 时使用）
 * @param {Array} messages - 消息列表
 * @param {string} sessionId - session ID
 * @returns {Object} 摘要结果
 */
function summarizeSessionLocal(messages, sessionId) {
  if (!messages || messages.length === 0) {
    return {
      title: '未命名会话',
      summary: '无内容',
      decisions: [],
      topics: ['#日常'],
      status: 'active'
    };
  }

  const firstMsg = messages.find(m => m.role === 'user');
  const title = firstMsg?.content?.substring(0, 30) || '未命名会话';

  const summary = messages.slice(0, 3)
    .map(m => m.content || '')
    .join('\n')
    .substring(0, 300);

  const tags = [];
  const fullText = JSON.stringify(messages).toLowerCase();

  if (fullText.includes('技能') || fullText.includes('skill')) tags.push('#Skill');
  if (fullText.includes('配置') || fullText.includes('config')) tags.push('#配置');
  if (fullText.includes('安装') || fullText.includes('install')) tags.push('#安装');
  if (fullText.includes('错误') || fullText.includes('error')) tags.push('#错误');
  if (fullText.includes('修复') || fullText.includes('fix')) tags.push('#修复');
  if (fullText.includes('飞书') || fullText.includes('feishu')) tags.push('#飞书');

  return {
    title: title.trim(),
    summary: summary.trim(),
    decisions: [],
    topics: tags.length > 0 ? tags : ['#日常'],
    status: 'active'
  };
}

/**
 * 获取时间范围
 * @param {Array} messages - 消息列表
 * @param {Object} session - session 对象
 * @returns {Object} { startTime, endTime }
 */
function getTimeRange(messages, session) {
  const timestamps = (messages || [])
    .map(msg => msg.timestamp || msg.create_time)
    .filter(Boolean)
    .map(ts => typeof ts === 'string' ? new Date(ts).getTime() : ts);

  let startTime, endTime;
  if (timestamps.length > 0) {
    startTime = Math.min(...timestamps);
    endTime = Math.max(...timestamps);
  } else {
    startTime = session.modified || Date.now();
    endTime = session.modified || Date.now();
  }

  return { startTime, endTime };
}

/**
 * 处理单个 session（本地降级方案）
 * @param {Object} session - session 对象
 * @returns {Object|null} 处理结果
 */
function processSessionLocal(session) {
  const sessionPath = getSessionPath(session);
  const messages = readSessionMessages(sessionPath);

  if (!messages || messages.length === 0) {
    return null;
  }

  const status = determineSessionStatus(session);
  const summary = summarizeSessionLocal(messages, session.sessionKey || session.sessionId);
  const { startTime, endTime } = getTimeRange(messages, session);

  return {
    id: session.sessionKey || session.sessionId,
    status,
    title: summary.title,
    topics: summary.topics,
    decisions: summary.decisions,
    summary: summary.summary,
    startTime,
    endTime,
    messageCount: messages.length
  };
}

module.exports = {
  readSessionMessages,
  determineSessionStatus,
  statusEmoji,
  getSessionPath,
  summarizeSessionLocal,
  getTimeRange,
  processSessionLocal
};
