#!/usr/bin/env node
/**
 * subagent-think-chain.js
 * 
 * subagent派发subagent前的强制思维链检查点
 * 
 * 使用方式：node subagent-think-chain.js "<任务描述>"
 * 
 * 在派发任何subagent之前，必须运行此脚本
 * 它会问自己以下问题，强制完成"置信度→拆分→选谁→验证"的完整思维链
 * 
 * 输出：JSON格式的路由决策，包含：
 *   - confidence: number (0-1) 置信度
 *   - shouldSplit: boolean 是否需要拆分并行
 *   - subagents: array 需要派发的子agent列表
 *   - needVerification: boolean 是否需要验证agent
 *   - reasoning: string 决策推理过程
 *   - warnings: array 风险提示
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = process.env.HOME + '/.openclaw/workspace';
const LOG_FILE = WORKSPACE + '/memory/watchdog-log.md';

function log(msg) {
  const entry = `[${new Date().toISOString()}] [subagent-think-chain] ${msg}`;
  fs.appendFileSync(LOG_FILE, entry + '\n');
  console.error(entry);
}

// 任务描述（从命令行参数获取）
const taskInput = process.argv.slice(2).join(' ').trim();

if (!taskInput) {
  console.error('用法: node subagent-think-chain.js "<任务描述>"');
  process.exit(1);
}

log(`分析任务: ${taskInput}`);

// ============================================================
// 思维链 Step 1: 解析任务
// ============================================================
const taskLower = taskInput.toLowerCase();

// 关键词分类
const categoryPatterns = {
  'search': ['搜索', '调研', '查找', '查', '搜', '调研', '研究'],
  'code': ['代码', '写代码', '改bug', '调试', 'debug', 'script', '脚本', '编程'],
  'write': ['写', '文案', '文章', '内容', '生成', '创作', '润色'],
  'image': ['看图', '图片', '截图', '图像', '分析图'],
  'reason': ['分析', '推理', '判断', '评估', '诊断', '排查'],
  'memory': ['记忆', '日志', '记录', '存档', '整理记忆'],
  'browser': ['浏览器', '网页', '推特', 'twitter', '网站'],
};

const detectedCategories = [];
for (const [cat, keywords] of Object.entries(categoryPatterns)) {
  if (keywords.some(k => taskLower.includes(k))) {
    detectedCategories.push(cat);
  }
}

if (detectedCategories.length === 0) {
  detectedCategories.push('general');
}

log(`检测到类别: ${detectedCategories.join(', ')}`);

// ============================================================
// 思维链 Step 2: 拆分决策
// ============================================================

// 拆分信号（根据任务路由v2文档）
const SPLIT_SIGNALS = [
  { pattern: /多|几个|分别|并行|同时/, reason: '多个独立方向可能需要并行' },
  { pattern: /对比|比较|分析.*和.*分析/, reason: '多个维度需要独立深挖' },
  { pattern: /调研|搜索.*平台|多个.*平台/, reason: '多数据源天然可拆分' },
  { pattern: /重构|系统|架构/, reason: '多模块需要独立处理' },
  { pattern: /跨.*联动|联动|对接.*和.*/, reason: '多系统需要独立验证' },
  { pattern: /排查.*和.*诊断/, reason: '多角度验证需要并行' },
];

const NO_SPLIT_SIGNALS = [
  { pattern: /直接|就行|简单|一下/, reason: '用户要求直接做，不拆分' },
  { pattern: /^读.*文件$|^查看.*$|总结/, reason: '单一目标，不需要拆分' },
  { pattern: /只|就|只要/, reason: '目标单一，不需要拆分' },
];

let shouldSplit = false;
let splitReason = '';
let noSplitReason = '';

for (const sig of SPLIT_SIGNALS) {
  if (sig.pattern.test(taskInput)) {
    shouldSplit = true;
    splitReason = sig.reason;
    break;
  }
}

for (const sig of NO_SPLIT_SIGNALS) {
  if (sig.pattern.test(taskInput)) {
    shouldSplit = false;
    noSplitReason = sig.reason;
    break;
  }
}

// 体量判断（任务描述长度作为粗略指标）
const isLongTask = taskInput.length > 100;
if (isLongTask && !shouldSplit && !noSplitReason) {
  shouldSplit = true;
  splitReason = '任务描述较长，可能涉及多个方向';
}

log(`拆分决策: ${shouldSplit ? '需要拆分' : '不需要拆分'} | 原因: ${shouldSplit ? splitReason : (noSplitReason || '无拆分信号')}`);

// ============================================================
// 思维链 Step 3: 置信度自检
// ============================================================

// 信号表：满足条件则加减置信度
const SIGNAL_TABLE = [
  { pattern: /删除|销毁|rm|remove.*永久/, reason: '不可逆操作', delta: -0.3 },
  { pattern: /发布|上线|deploy|发布/, reason: '对外操作', delta: -0.2 },
  { pattern: /配置.*网关|gateway.*配置|restart.*网关/, reason: '系统核心修改', delta: -0.2 },
  { pattern: /密码|密钥|secret|credential/, reason: '安全相关', delta: -0.2 },
  { pattern: /子任务.*[>2]|多个.*并行|并行.*多个/, reason: '子任务>2', delta: -0.1 },
  { pattern: /首次|没做过|不熟悉/, reason: '首次遇到', delta: -0.2 },
  { pattern: /历史成功|做过.*成功|之前.*成功/, reason: '历史成功率高', delta: +0.1 },
  { pattern: /简单|直接|就行|一下/, reason: '任务明确简单', delta: +0.1 },
];

// 需要验证agent的场景（根据验证agent模板.md）
const VERIFICATION_REQUIRED = [
  { pattern: /架构|重构|系统设计/, reason: '涉及核心架构，需要严格验证' },
  { pattern: /安全|权限|权限.*配置/, reason: '安全相关，需要验证' },
  { pattern: /方案|策略|计划.*实施/, reason: '重要决策，需要对抗性验证' },
  { pattern: /文案.*发布|发布.*文案/, reason: '对外发布，需要质量验证' },
  { pattern: /改.*核心|核心.*改/, reason: '涉及核心，需要验证' },
];

let confidence = 0.9; // 默认置信度 0.9（90%）
let confidenceReason = '无特殊信号，使用默认置信度0.9';

// 按信号表加减置信度
for (const sig of SIGNAL_TABLE) {
  if (sig.pattern.test(taskInput)) {
    confidence = Math.max(0, Math.min(1, confidence + sig.delta));
    confidenceReason = sig.reason + ' ' + sig.delta;
    break;
  }
}

let needVerification = false;
let verificationReason = '';

for (const sig of VERIFICATION_REQUIRED) {
  if (sig.pattern.test(taskInput)) {
    needVerification = true;
    verificationReason = sig.reason;
    break;
  }
}

// 如果置信度低于阈值，标记需要更谨慎处理
const LOW_CONFIDENCE = confidence < 0.6;
if (LOW_CONFIDENCE) {
  needVerification = true;
  if (!verificationReason) verificationReason = '置信度低于0.6，需要验证';
}

log(`置信度: ${confidence} | ${confidenceReason}`);
log(`需要验证agent: ${needVerification} | ${verificationReason || '无特殊要求'}`);

// ============================================================
// 思维链 Step 4: 选择子agent模型
// ============================================================

// 模型选择规则（根据MEMORY.md铁律）
const modelRules = [
  { 
    categories: ['search', '调研'],
    model: 'gpt-agent/kimi-k2.5',
    reason: '搜索调研类任务，kimi-k2.5适合'
  },
  { 
    categories: ['code'],
    model: 'gpt-agent/doubao-seed-2.0-code',
    reason: '代码类任务，用doubao-seed-code'
  },
  { 
    categories: ['write'],
    model: 'gpt-agent/minimax-m2.7-highspeed',
    reason: '文案类任务，全程用MiniMax M2.7-highspeed'
  },
  { 
    categories: ['reason'],
    model: 'gpt-agent/deepseek-reasoner',
    reason: '推理分析类，用deepseek-reasoner'
  },
  {
    categories: ['image'],
    model: 'gpt-agent/doubao-seed-2.0-pro',
    reason: '看图任务，用小探doubao-seed-2.0-pro'
  },
];

let selectedModel = 'gpt-agent/claude-sonnet-4-6'; // 默认模型
let modelReason = '默认使用claude-sonnet-4-6';

for (const rule of modelRules) {
  if (rule.categories.some(c => detectedCategories.includes(c))) {
    selectedModel = rule.model;
    modelReason = rule.reason;
    break;
  }
}

log(`选择模型: ${selectedModel} | ${modelReason}`);

// ============================================================
// 思维链 Step 5: 输出路由决策
// ============================================================

const decision = {
  task: taskInput,
  timestamp: new Date().toISOString(),
  confidence,
  confidenceReason,
  shouldSplit,
  splitReason: shouldSplit ? splitReason : (noSplitReason || '无拆分必要'),
  subagents: shouldSplit ? [
    {
      direction: '方向A',
      model: selectedModel,
      prompt: `${taskInput} - 方向A：${splitReason || '第一独立方向'}`,
    },
    {
      direction: '方向B',
      model: selectedModel,
      prompt: `${taskInput} - 方向B：第二独立方向`,
    }
  ] : [
    {
      direction: '单一方向',
      model: selectedModel,
      prompt: taskInput,
    }
  ],
  needVerification,
  verificationReason,
  selectedModel,
  modelReason,
  warnings: [
    ...(LOW_CONFIDENCE ? ['⚠️ 置信度低于0.6，建议谨慎操作'] : []),
    ...(needVerification ? ['🔍 需要验证agent进行对抗性审查'] : []),
    ...(shouldSplit ? ['🔀 多方向并行，需汇总后统一输出'] : []),
  ],
  // 如果需要验证，设置验证循环
  verificationLoop: needVerification ? {
    maxRetries: 3,
    threshold: 'P0问题必须全部解决',
    rule: '验证不通过 → 修复P0 → 再次验证 → 直到通过',
  } : null,
};

console.log(JSON.stringify(decision, null, 2));

log(`路由决策完成: ${shouldSplit ? '需拆分' : '单一'} | 模型: ${selectedModel} | 验证: ${needVerification}`);

// 胶囊建议提示（任务完成后提醒）
console.log('\n===== 胶囊自动建议 =====');
console.log('💡 任务完成后会自动检查是否需要存胶囊');
console.log('   运行: bash ~/.openclaw/workspace/scripts/capsule-auto-suggest.sh "<结果>" "<原始任务>"');

// ============================================================
// 双保险触发：置信度低 OR 复杂任务 → 自动写预检点
const CHECKPOINT_THRESHOLD = 0.6;
const needsCheckpoint = confidence < CHECKPOINT_THRESHOLD || (Array.isArray(decision.subagents) ? decision.subagents.length : 1) > 2;

if (needsCheckpoint) {
  const { execSync } = require('child_process');
  const subagentList = Array.isArray(decision.subagents) ? decision.subagents.map(s => s.direction).join(',') : '单一方向';
  const planDesc = (shouldSplit ? '并行: ' : '串行: ') + subagentList || selectedModel;
  
  try {
    const cp = execSync(
      `node "${WORKSPACE}/pre-checkpoint.js" "${taskInput.substring(0, 80)}" "${planDesc}" --confidence ${Math.round(confidence * 10)} --steps ${decision.subagents.length || 1} --subagents "${subagentList}" ${shouldSplit ? '--parallel' : ''}`,
      { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }
    );
    console.log(cp.trim());
    log(`双保险：预检点已写入`);
  } catch (e) {
    console.error('预检点写入失败（不影响派发）:', e.message);
    log(`预检点写入失败: ${e.message}`);
  }
}

// 保存决策到日志
const decisionLogFile = WORKSPACE + '/memory/subagent-routing-log.json';
fs.writeFileSync(decisionLogFile, JSON.stringify(decision, null, 2));
