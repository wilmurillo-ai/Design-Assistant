#!/usr/bin/env node

/**
 * subagent-runner.js - Subagent 调用封装（工具调用模式）
 * 
 * 直接使用 sessions_spawn 工具，不依赖 CLI 命令。
 * 
 * 特性：
 * - 复用主 LLM 配置，无需单独 API Key
 * - 支持超时控制
 * - 自动解析结果
 */

// 尝试导入 OpenClaw 工具
let sessions_spawn;
try {
  const openclaw = require('openclaw');
  sessions_spawn = openclaw.sessions_spawn;
  console.log('✅ sessions_spawn 工具可用');
} catch (error) {
  console.log('⚠️  sessions_spawn 工具不可用，使用降级方案');
}

/**
 * callLLMViaSubagent - 使用 sessions_spawn 调用 LLM
 * @param {string} task - 任务描述
 * @param {Object} options - 选项
 * @param {number} options.timeoutSeconds - 超时秒数
 * @returns {Promise<string>} LLM 返回结果
 */
async function callLLMViaSubagent(task, options = {}) {
  if (!sessions_spawn) {
    throw new Error('sessions_spawn 工具不可用');
  }
  
  const timeout = options.timeoutSeconds || 120;
  
  try {
    const result = await sessions_spawn({
      task: task,
      runtime: 'subagent',
      mode: 'run',
      timeoutSeconds: timeout
    });
    
    return parseSubagentResult(result);
  } catch (error) {
    if (error.message && error.message.includes('timeout')) {
      throw new Error('LLM 调用超时。LLM call timeout.');
    }
    throw error;
  }
}

/**
 * summarizeSession - 提炼会话摘要
 * @param {string} sessionContent - 会话内容
 * @returns {Promise<Object>} 摘要结果
 */
async function summarizeSession(sessionContent) {
  const task = `请分析以下会话内容，提炼：
1. 话题标题（10-20 字，清晰描述话题）
2. 摘要（200-300 字，抓住核心内容）
3. 关键决策/发现（1-3 个要点）
4. 话题标签（3-5 个，#关键词 格式）

会话内容：
${sessionContent.substring(0, 3000)}

请只返回 JSON 格式，不要其他内容：
{
  "title": "话题标题",
  "summary": "摘要内容",
  "decisions": ["决策 1", "决策 2"],
  "tags": ["#标签 1", "#标签 2", "#标签 3"]
}`;
  
  const result = await callLLMViaSubagent(task, { timeoutSeconds: 120 });
  
  try {
    return JSON.parse(result);
  } catch (error) {
    // 如果解析失败，返回简化版本
    return {
      title: sessionContent.split('\n')[0].substring(0, 50),
      summary: sessionContent.substring(0, 300),
      decisions: [],
      tags: ['#会话']
    };
  }
}

/**
 * generateDailyNote - 生成 Daily 笔记
 * @param {Array} sessions - 会话列表
 * @param {string} date - 日期
 * @returns {Promise<string>} Markdown 格式的 Daily 笔记
 */
async function generateDailyNote(sessions, date) {
  const task = `请根据以下会话摘要，生成格式化的 Daily 笔记：

日期：${date}
会话列表：
${sessions.map(s => `- ${s.title}: ${s.summary} [${s.status}]`).join('\n')}

要求：
1. 当日总结（会话数、状态分布、主要话题）
2. 每个会话独立小节（标题、标签、时间、摘要、关键决策）
3. 使用 Markdown 格式
4. 状态标注（✅活跃 / ❌删除 / 🔄重置）

请直接返回 Markdown 内容。`;
  
  return await callLLMViaSubagent(task, { timeoutSeconds: 180 });
}

/**
 * refineMemory - 提炼 MEMORY.md
 * @param {Array<string>} dailyNotes - Daily 笔记数组
 * @returns {Promise<string>} MEMORY.md 的 Markdown 内容
 */
async function refineMemory(dailyNotes) {
  const task = `请从以下 Daily 笔记中提炼长期记忆：

${dailyNotes.join('\n\n')}

提炼类别：
1. 用户偏好（语言、时区、风格、格式偏好）
2. 重要决策（架构决策、工具选择、配置变更）
3. 项目进展（进行中的项目、完成的任务）
4. 待办事项（未完成的任务、计划）
5. 技能配置（安装的 Skill、工具配置）
6. 关键学习（遇到的问题、解决方案、经验教训）

请返回 MEMORY.md 的 Markdown 内容。`;
  
  return await callLLMViaSubagent(task, { timeoutSeconds: 240 });
}

/**
 * parseSubagentResult - 解析 subagent 结果
 * @param {Object} result - subagent 返回结果
 * @returns {string} 解析后的内容
 */
function parseSubagentResult(result) {
  // 如果是对象，提取 content 字段
  if (typeof result === 'object' && result !== null) {
    return result.content || JSON.stringify(result);
  }
  
  // 如果是字符串，直接返回
  return result;
}

module.exports = {
  callLLMViaSubagent,
  summarizeSession,
  generateDailyNote,
  refineMemory
};
