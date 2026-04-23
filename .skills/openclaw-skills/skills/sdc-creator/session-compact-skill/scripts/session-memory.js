#!/usr/bin/env node

/**
 * Session Memory Manager - 跨会话记忆管理
 * 
 * 核心功能:
 * - 会话状态持久化 (SESSION-STATE.md)
 * - 工作缓冲区 (working-buffer.md)
 * - 记忆搜索与恢复
 * - 压缩前状态保护 (WAL 协议)
 */

const fs = require('fs');
const path = require('path');

// 默认配置
const DEFAULT_CONFIG = {
  memoryDir: path.join(process.env.HOME || '.', '.openclaw', 'memory'),
  maxBufferSize: 100,  // 工作缓冲区最大条目
  stateFileTTL: 72 * 60 * 60 * 1000,  // 状态文件有效期 72 小时
};

/**
 * 确保记忆目录存在
 */
function ensureMemoryDir(config = DEFAULT_CONFIG) {
  if (!fs.existsSync(config.memoryDir)) {
    fs.mkdirSync(config.memoryDir, { recursive: true });
  }
  return config.memoryDir;
}

/**
 * 获取会话状态文件路径
 */
function getStateFilePath(config = DEFAULT_CONFIG) {
  return path.join(config.memoryDir, 'SESSION-STATE.md');
}

/**
 * 获取工作缓冲区文件路径
 */
function getWorkingBufferPath(config = DEFAULT_CONFIG) {
  return path.join(config.memoryDir, 'working-buffer.md');
}

/**
 * 获取每日记忆文件路径
 */
function getDailyMemoryPath(date = new Date(), config = DEFAULT_CONFIG) {
  const dateStr = date.toISOString().split('T')[0];
  return path.join(config.memoryDir, `${dateStr}.md`);
}

/**
 * 读取会话状态
 */
function readSessionState(config = DEFAULT_CONFIG) {
  const statePath = getStateFilePath(config);
  
  if (!fs.existsSync(statePath)) {
    return null;
  }
  
  try {
    const content = fs.readFileSync(statePath, 'utf-8');
    return parseSessionState(content);
  } catch (error) {
    console.error('[Memory] Failed to read session state:', error.message);
    return null;
  }
}

/**
 * 解析会话状态内容
 */
function parseSessionState(content) {
  const state = {
    currentTask: '',
    keyDetails: [],
    decisions: [],
    preferences: [],
    files: [],
    lastUpdated: null
  };
  
  let currentSection = null;
  
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    
    if (trimmed.startsWith('## Current Task')) {
      currentSection = 'currentTask';
      continue;
    }
    if (trimmed.startsWith('## Key Details')) {
      currentSection = 'keyDetails';
      continue;
    }
    if (trimmed.startsWith('## Decisions')) {
      currentSection = 'decisions';
      continue;
    }
    if (trimmed.startsWith('## Preferences')) {
      currentSection = 'preferences';
      continue;
    }
    if (trimmed.startsWith('## Files')) {
      currentSection = 'files';
      continue;
    }
    if (trimmed.startsWith('## Last Updated')) {
      state.lastUpdated = trimmed.replace('## Last Updated: ', '');
      continue;
    }
    
    if (currentSection && trimmed.startsWith('- ')) {
      const value = trimmed.substring(2);
      if (state[currentSection]) {
        if (Array.isArray(state[currentSection])) {
          state[currentSection].push(value);
        } else {
          state[currentSection] = value;
        }
      }
    }
  }
  
  return state;
}

/**
 * 写入会话状态
 */
function writeSessionState(state, config = DEFAULT_CONFIG) {
  ensureMemoryDir(config);
  const statePath = getStateFilePath(config);
  
  const content = generateSessionStateContent(state);
  fs.writeFileSync(statePath, content, 'utf-8');
  
  return statePath;
}

/**
 * 生成会话状态内容
 */
function generateSessionStateContent(state) {
  const lines = [
    '# Session State — Active Working Memory',
    '',
    '## Current Task',
    state.currentTask || '[No active task]',
    '',
    '## Key Details',
    ...(state.keyDetails || []).map(d => `- ${d}`),
    '',
    '## Decisions',
    ...(state.decisions || []).map(d => `- ${d}`),
    '',
    '## Preferences',
    ...(state.preferences || []).map(p => `- ${p}`),
    '',
    '## Files',
    ...(state.files || []).map(f => `- ${f}`),
    '',
    `## Last Updated: ${new Date().toISOString()}`,
    ''
  ];
  
  return lines.join('\n');
}

/**
 * 更新会话状态 (WAL 协议)
 */
function updateSessionState(updates, config = DEFAULT_CONFIG) {
  const existing = readSessionState(config) || {
    currentTask: '',
    keyDetails: [],
    decisions: [],
    preferences: [],
    files: []
  };
  
  // 合并更新
  if (updates.currentTask) existing.currentTask = updates.currentTask;
  if (updates.keyDetails) existing.keyDetails = [...existing.keyDetails, ...updates.keyDetails];
  if (updates.decisions) existing.decisions = [...existing.decisions, ...updates.decisions];
  if (updates.preferences) existing.preferences = [...existing.preferences, ...updates.preferences];
  if (updates.files) existing.files = [...existing.files, ...updates.files];
  
  return writeSessionState(existing, config);
}

/**
 * 扫描消息中的关键信息 (WAL 触发器)
 */
function scanForCriticalInfo(message) {
  const content = typeof message.content === 'string' ? message.content : JSON.stringify(message.content);
  const findings = {
    corrections: [],
    properNouns: [],
    preferences: [],
    decisions: [],
    specificValues: []
  };
  
  // 修正检测
  const correctionPatterns = [
    /(?:it's|it is|actually|should be|not|纠正|应该是|不是)\s+([^\n,.!?]+)/gi,
    /(?:不对|错了|纠正|修改|改为)\s*[:：]?\s*([^\n,.!?]+)/gi
  ];
  
  correctionPatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      findings.corrections.push(match[1].trim());
    }
  });
  
  // 偏好检测
  const preferencePatterns = [
    /(?:i (?:like|prefer|love|don't like|hate)|我喜欢|我不喜欢|偏好|倾向于)\s+([^\n,.!?]+)/gi
  ];
  
  preferencePatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      findings.preferences.push(match[1].trim());
    }
  });
  
  // 决策检测
  const decisionPatterns = [
    /(?:let's|we should|go with|decided to|决定|选择|采用)\s+([^\n,.!?]+)/gi
  ];
  
  decisionPatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      findings.decisions.push(match[1].trim());
    }
  });
  
  // 具体值检测 (数字、路径、URL)
  const valuePatterns = [
    /(?:https?:\/\/[^\s]+)/g,
    /(?:[\/\w]+\.\w{2,4})/g,
    /(?:\d{4}年|\d+%) /g
  ];
  
  valuePatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      findings.specificValues.push(match[0].trim());
    }
  });
  
  return findings;
}

/**
 * 写入工作缓冲区
 */
function writeToBuffer(message, config = DEFAULT_CONFIG) {
  ensureMemoryDir(config);
  const bufferPath = getWorkingBufferPath(config);
  
  let content = '';
  if (fs.existsSync(bufferPath)) {
    content = fs.readFileSync(bufferPath, 'utf-8');
  } else {
    content = `# Working Buffer (Danger Zone)
**Status:** ACTIVE
**Started:** ${new Date().toISOString()}

---

`;
  }
  
  const timestamp = new Date().toISOString();
  const role = message.role || 'unknown';
  const text = (message.content || '').substring(0, 500);
  
  content += `\n## [${timestamp}] ${role}\n${text}\n`;
  
  fs.writeFileSync(bufferPath, content, 'utf-8');
  
  return bufferPath;
}

/**
 * 读取工作缓冲区
 */
function readWorkingBuffer(config = DEFAULT_CONFIG) {
  const bufferPath = getWorkingBufferPath(config);
  
  if (!fs.existsSync(bufferPath)) {
    return null;
  }
  
  try {
    return fs.readFileSync(bufferPath, 'utf-8');
  } catch (error) {
    console.error('[Memory] Failed to read working buffer:', error.message);
    return null;
  }
}

/**
 * 清空工作缓冲区
 */
function clearWorkingBuffer(config = DEFAULT_CONFIG) {
  const bufferPath = getWorkingBufferPath(config);
  
  if (fs.existsSync(bufferPath)) {
    fs.unlinkSync(bufferPath);
  }
}

/**
 * 压缩恢复 - 从多个来源恢复上下文
 */
function recoverContextAfterCompaction(config = DEFAULT_CONFIG) {
  const recovered = {
    workingBuffer: null,
    sessionState: null,
    recentMemories: [],
    summary: ''
  };
  
  // 1. 读取工作缓冲区
  recovered.workingBuffer = readWorkingBuffer(config);
  
  // 2. 读取会话状态
  recovered.sessionState = readSessionState(config);
  
  // 3. 读取最近 2 天的记忆
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  [today, yesterday].forEach(date => {
    const dailyPath = getDailyMemoryPath(date, config);
    if (fs.existsSync(dailyPath)) {
      try {
        const content = fs.readFileSync(dailyPath, 'utf-8');
        recovered.recentMemories.push({
          date: date.toISOString().split('T')[0],
          content
        });
      } catch (error) {
        console.error(`[Memory] Failed to read daily memory for ${date.toISOString().split('T')[0]}:`, error.message);
      }
    }
  });
  
  // 4. 生成恢复摘要
  const summaryLines = ['## Recovered Context'];
  
  if (recovered.sessionState) {
    summaryLines.push('');
    summaryLines.push('### Session State');
    summaryLines.push(`- Current Task: ${recovered.sessionState.currentTask || 'Unknown'}`);
    summaryLines.push(`- Key Details: ${recovered.sessionState.keyDetails?.length || 0} items`);
    summaryLines.push(`- Decisions: ${recovered.sessionState.decisions?.length || 0} items`);
  }
  
  if (recovered.workingBuffer) {
    summaryLines.push('');
    summaryLines.push('### Working Buffer');
    summaryLines.push('Recent exchanges preserved in working-buffer.md');
  }
  
  if (recovered.recentMemories.length > 0) {
    summaryLines.push('');
    summaryLines.push('### Recent Memories');
    recovered.recentMemories.forEach(m => {
      summaryLines.push(`- ${m.date}: ${m.content.split('\n').length} lines`);
    });
  }
  
  recovered.summary = summaryLines.join('\n');
  
  return recovered;
}

/**
 * 写入每日记忆
 */
function writeDailyMemory(entries, date = new Date(), config = DEFAULT_CONFIG) {
  ensureMemoryDir(config);
  const dailyPath = getDailyMemoryPath(date, config);
  
  let content = '';
  if (fs.existsSync(dailyPath)) {
    content = fs.readFileSync(dailyPath, 'utf-8');
  } else {
    content = `# Daily Memory — ${date.toISOString().split('T')[0]}\n\n`;
  }
  
  const timestamp = new Date().toISOString();
  content += `\n## [${timestamp}]\n${entries.join('\n')}\n`;
  
  fs.writeFileSync(dailyPath, content, 'utf-8');
  
  return dailyPath;
}

// CLI 入口
if (require.main === module) {
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log('Session Memory Manager - 跨会话记忆管理');
  console.log('=========================================');
  console.log('');
  console.log('功能:');
  console.log('  1. 会话状态持久化 (SESSION-STATE.md)');
  console.log('  2. 工作缓冲区 (working-buffer.md)');
  console.log('  3. 压缩前状态保护 (WAL 协议)');
  console.log('  4. 压缩后上下文恢复');
  console.log('  5. 每日记忆存档');
  console.log('');
  console.log('用法:');
  console.log('  在 OpenClaw 中通过工具调用或告诉助手:');
  console.log('  - "保存当前状态"');
  console.log('  - "恢复上下文"');
  console.log('  - "清空工作缓冲区"');
  console.log('');

  rl.close();
}

module.exports = {
  // 状态管理
  readSessionState,
  writeSessionState,
  updateSessionState,
  
  // 工作缓冲区
  writeToBuffer,
  readWorkingBuffer,
  clearWorkingBuffer,
  
  // WAL 协议
  scanForCriticalInfo,
  
  // 压缩恢复
  recoverContextAfterCompaction,
  
  // 每日记忆
  writeDailyMemory,
  
  // 工具函数
  ensureMemoryDir,
  getStateFilePath,
  getWorkingBufferPath,
  getDailyMemoryPath
};
