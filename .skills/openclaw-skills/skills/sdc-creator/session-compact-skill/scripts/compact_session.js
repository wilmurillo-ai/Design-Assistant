#!/usr/bin/env node

/**
 * Session Compact Skill - 智能会话压缩
 * 简化版，用于 Skill 类型发布
 *
 * 核心功能:
 * - 自动估算会话 token 数 (1 token ≈ 4 字符)
 * - 当超过阈值时，将早期消息压缩为结构化摘要
 * - 保留最新消息的完整上下文
 * - 提取关键事实、工具调用
 */

const readline = require('readline');

// 默认配置
const DEFAULT_CONFIG = {
  maxTokens: 10000,
  preserveRecent: 4
};

/**
 * 估算文本的 token 数量 (启发式: 字符数 / 4)
 */
function estimateTokens(text) {
  if (typeof text !== 'string') {
    text = JSON.stringify(text);
  }
  return Math.ceil(text.length / 4);
}

/**
 * 估算消息的 token 数量
 */
function estimateMessageTokens(message) {
  const content = message.content || '';
  return estimateTokens(content);
}

/**
 * 估算会话的总 token 数量
 */
function estimateSessionTokens(messages) {
  return messages.reduce((sum, msg) => sum + estimateMessageTokens(msg), 0);
}

/**
 * 从消息中提取关键事实 (正则匹配)
 */
function extractFacts(messages) {
  const facts = [];
  const patterns = [
    /\d{4}年/g,
    /[\d.]+%|涨|降|增加|减少/g,
    /(?:营收|收入|利润|销量|价格|成本)/g,
    /(?:必须|应该|建议|计划|需要)/g,
    /(?:重要|关键|核心|主要)/g,
    /https?:\/\/[^\s]+/g
  ];

  messages.forEach(msg => {
    const content = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content);
    patterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) {
        matches.slice(0, 2).forEach(match => {
          if (!facts.includes(match)) facts.push(match);
        });
      }
    });
  });

  return facts.slice(0, 10);
}

/**
 * 提取文件路径候选
 */
function extractFileCandidates(messages) {
  const files = new Set();
  messages.forEach(msg => {
    const content = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content);
    const matches = content.match(/[\/\w]+\.\w{2,4}/g);
    if (matches) matches.forEach(f => files.add(f));
  });
  return Array.from(files).slice(0, 8);
}

/**
 * 生成会话摘要
 */
function generateSummary(messages) {
  const userMsgs = messages.filter(m => m.role === 'user');
  const assistantMsgs = messages.filter(m => m.role === 'assistant');
  const toolMsgs = messages.filter(m => m.role === 'tool');
  const facts = extractFacts(messages);
  const files = extractFileCandidates(messages);

  const firstUser = userMsgs[0]?.content || '';
  const topic = firstUser.substring(0, 80).trim() + (firstUser.length > 80 ? '...' : '');

  const timeline = messages.slice(-10).map(m => {
    const content = (m.content || '').substring(0, 60);
    return `  - ${m.role}: ${content}${(m.content || '').length > 60 ? '...' : ''}`;
  }).join('\n');

  return `<summary>
- Scope: ${messages.length} earlier messages compacted (user=${userMsgs.length}, assistant=${assistantMsgs.length}, tool=${toolMsgs.length}).
- Recent requests:
  - ${userMsgs.slice(-3).map(m => (m.content || '').substring(0, 80)).join('\n  - ')}
- Pending work:
  - [根据最近消息推断的待办事项]
- Key files:
  - ${files.length > 0 ? files.join('\n  - ') : '[See tool usage]'}
- Tools used:
  - [See tool usage]
- Key timeline:
${timeline}
</summary>`;
}

/**
 * 核心压缩算法
 *
 * @param {Array} messages - 会话消息数组 (OpenAI 格式)
 * @param {Object} options - 配置选项
 * @param {number} [options.maxTokens] - token 阈值
 * @param {number} [options.preserveRecent] - 保留的最新消息数
 * @param {boolean} [options.force] - 是否强制压缩
 * @returns {Object} 压缩结果
 */
async function compactSession(messages, options = {}) {
  const config = { ...DEFAULT_CONFIG, ...options };
  
  const totalTokens = estimateSessionTokens(messages);
  const needsCompact = config.force || totalTokens > config.maxTokens;

  if (!needsCompact) {
    return {
      compacted: false,
      reason: 'Session within token limits',
      totalTokens,
      maxTokens: config.maxTokens,
      savedTokens: 0
    };
  }

  // 保留最新消息
  const recentMessages = messages.slice(-config.preserveRecent);
  const oldMessages = messages.slice(0, -config.preserveRecent);

  // 生成摘要
  const summary = generateSummary(oldMessages);
  const summaryTokens = estimateTokens(summary);
  const oldTokens = estimateSessionTokens(oldMessages);
  const savedTokens = oldTokens - summaryTokens;

  // 构建压缩后的会话
  const compactedMessages = [
    { role: 'system', content: `Summary:\n${summary}` },
    ...recentMessages
  ];

  return {
    compacted: true,
    originalTokens: totalTokens,
    compactedTokens: summaryTokens + estimateSessionTokens(recentMessages),
    savedTokens,
    removedCount: oldMessages.length,
    preservedCount: recentMessages.length,
    compactedMessages
  };
}

// CLI 入口
if (require.main === module) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log('Session Compact Skill - 智能会话压缩');
  console.log('=====================================');
  console.log('');
  console.log('用法:');
  console.log('  1. 在 OpenClaw 中自动触发');
  console.log('  2. 通过工具调用: compact_session');
  console.log('  3. 告诉助手: "压缩当前会话"');
  console.log('');
  console.log('配置:');
  console.log(`  maxTokens: ${DEFAULT_CONFIG.maxTokens}`);
  console.log(`  preserveRecent: ${DEFAULT_CONFIG.preserveRecent}`);
  console.log('');

  rl.close();
}

module.exports = { compactSession, estimateSessionTokens, generateSummary };
