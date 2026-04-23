#!/usr/bin/env node

/**
 * 工具函数模块
 * 
 * 注意：以下函数已迁移到其他模块：
 * - printHeader, printSuccess, printError, printWarning, printInfo, printProgress → logger.js
 * - walkDirectory, ensureDirExists, safeWriteFile → file-utils.js
 * - getToken → auth.js
 * - loadConfig, saveConfig, validateConfig → config-loader.js
 */

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的大小
 */
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * 格式化持续时间
 * @param {number} ms - 毫秒数
 * @returns {string} 格式化后的时间
 */
function formatDuration(ms) {
  if (ms < 1000) return ms + 'ms';
  return (ms / 1000).toFixed(1) + 's';
}

/**
 * 休眠指定时间
 * @param {number} ms - 毫秒数
 * @returns {Promise<void>}
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 生成唯一 ID
 * @returns {string} 唯一 ID
 */
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * 深拷贝对象
 * @param {Object} obj - 要拷贝的对象
 * @returns {Object} 拷贝后的对象
 */
function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * 检查对象是否为空
 * @param {Object} obj - 要检查的对象
 * @returns {boolean} 是否为空
 */
function isEmpty(obj) {
  if (obj == null) return true;
  if (typeof obj === 'string') return obj.trim() === '';
  if (Array.isArray(obj)) return obj.length === 0;
  if (typeof obj === 'object') return Object.keys(obj).length === 0;
  return false;
}

/**
 * 延迟执行函数
 * @param {Function} fn - 要执行的函数
 * @param {number} delayMs - 延迟毫秒数
 * @returns {Function} 包装后的函数
 */
function debounce(fn, delayMs) {
  let timeoutId = null;
  return function(...args) {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delayMs);
  };
}

/**
 * 限制函数执行频率
 * @param {Function} fn - 要执行的函数
 * @param {number} limitMs - 最小间隔毫秒数
 * @returns {Function} 包装后的函数
 */
function throttle(fn, limitMs) {
  let lastCall = 0;
  return function(...args) {
    const now = Date.now();
    if (now - lastCall >= limitMs) {
      lastCall = now;
      return fn.apply(this, args);
    }
  };
}

module.exports = {
  formatFileSize,
  formatDuration,
  sleep,
  generateId,
  deepClone,
  isEmpty,
  debounce,
  throttle
};
