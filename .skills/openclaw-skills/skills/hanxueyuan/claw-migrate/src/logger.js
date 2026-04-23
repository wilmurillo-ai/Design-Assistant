#!/usr/bin/env node

/**
 * 日志工具模块
 * 统一所有 console.log 打印模式
 */

// 日志前缀图标
const ICONS = {
  header: '',
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️',
  connecting: '📡',
  package: '📦',
  upload: '📤',
  download: '📥',
  merge: '🔄',
  skip: '⏭️',
  check: '✓',
  cross: '✗',
  rocket: '🚀',
  memo: '📌',
  file: '📄',
  folder: '📁',
  config: '⚙️',
  calendar: '📅'
};

/**
 * 打印头部信息
 * @param {string} title - 标题
 */
function printHeader(title) {
  console.log('\n' + '='.repeat(60));
  console.log('  ' + title);
  console.log('='.repeat(60) + '\n');
}

/**
 * 打印成功消息
 * @param {string} message - 消息内容
 */
function printSuccess(message) {
  console.log(`\n${ICONS.success} ${message}`);
}

/**
 * 打印错误消息
 * @param {string} message - 消息内容
 */
function printError(message) {
  console.log(`\n${ICONS.error} ${message}`);
}

/**
 * 打印警告消息
 * @param {string} message - 消息内容
 */
function printWarning(message) {
  console.log(`\n${ICONS.warning} ${message}`);
}

/**
 * 打印信息消息
 * @param {string} message - 消息内容
 */
function printInfo(message) {
  console.log(`\n${ICONS.info} ${message}`);
}

/**
 * 打印进度条
 * @param {number} current - 当前进度
 * @param {number} total - 总进度
 * @param {string} message - 进度描述
 */
function printProgress(current, total, message) {
  const percent = Math.round((current / total) * 100);
  const bar = '█'.repeat(percent / 5) + '░'.repeat(20 - percent / 5);
  process.stdout.write(`\r  [${bar}] ${percent}% - ${message}`);
  if (current === total) {
    console.log();
  }
}

/**
 * 打印连接信息
 * @param {string} service - 服务名称
 */
function printConnecting(service) {
  console.log(`\n${ICONS.connecting} 正在连接 ${service}...`);
}

/**
 * 打印文件数量
 * @param {number} count - 文件数量
 * @param {string} label - 标签（默认：'文件'）
 */
function printFileCount(count, label = '文件') {
  console.log(`   发现 ${count} 个${label}`);
}

/**
 * 打印分割线
 */
function printDivider() {
  console.log('\n' + '='.repeat(50));
}

/**
 * 打印文件状态
 * @param {string} path - 文件路径
 * @param {string} status - 状态 (success/error/skip/merge/pending)
 * @param {string} note - 附加说明（可选）
 */
function printFileStatus(path, status, note = '') {
  const statusIcons = {
    success: ICONS.check,
    error: ICONS.cross,
    skip: ICONS.skip,
    merge: ICONS.merge,
    pending: '•'
  };
  const icon = statusIcons[status] || '•';
  const noteText = note ? ` (${note})` : '';
  console.log(`   ${icon} ${path}${noteText}`);
}

/**
 * 打印章节标题
 * @param {string} title - 章节标题
 */
function printSection(title) {
  console.log('\n' + '='.repeat(50));
  console.log(`  ${title}`);
  console.log('='.repeat(50) + '\n');
}

/**
 * 打印列表项
 * @param {string} text - 列表项内容
 * @param {string} icon - 图标（可选）
 */
function printListItem(text, icon = '•') {
  console.log(`   ${icon} ${text}`);
}

/**
 * 打印后续步骤
 * @param {string[]} steps - 步骤列表
 */
function printNextSteps(steps) {
  console.log(`\n${ICONS.memo} 后续步骤：\n`);
  steps.forEach((step, index) => {
    console.log(`   ${index + 1}. ${step}`);
  });
  console.log();
}

module.exports = {
  printHeader,
  printSuccess,
  printError,
  printWarning,
  printInfo,
  printProgress,
  printConnecting,
  printFileCount,
  printDivider,
  printFileStatus,
  printSection,
  printListItem,
  printNextSteps,
  ICONS
};
