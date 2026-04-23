#!/usr/bin/env node

/**
 * 文件工具模块
 * 提取重复的文件操作逻辑
 */

const fs = require('fs');
const path = require('path');

/**
 * 递归遍历目录
 * @param {string} dir - 目录路径
 * @param {Object} options - 选项
 * @param {string} options.relativeBase - 相对路径基准
 * @param {string[]} options.extensions - 文件扩展名过滤
 * @param {string[]} options.skipDirs - 要跳过的目录名
 * @returns {Array<{path: string, fullPath: string}>} 文件列表
 */
function walkDirectory(dir, options = {}) {
  const { 
    relativeBase = '', 
    extensions = [], 
    skipDirs = ['node_modules', '.git', '.openclaw'] 
  } = options;
  
  const files = [];
  
  if (!fs.existsSync(dir)) {
    return files;
  }

  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relativePath = path.join(relativeBase, entry.name);

    if (entry.isDirectory()) {
      if (skipDirs.includes(entry.name)) {
        continue;
      }
      
      const subFiles = walkDirectory(fullPath, { 
        ...options, 
        relativeBase: relativePath 
      });
      files.push(...subFiles);
    } else {
      // 扩展名过滤
      if (extensions.length === 0 || 
          extensions.some(ext => entry.name.endsWith(ext))) {
        files.push({ path: relativePath, fullPath });
      }
    }
  }

  return files;
}

/**
 * 确保目录存在
 * @param {string} dirPath - 目录路径
 * @returns {boolean} 是否成功确保目录存在
 */
function ensureDirExists(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
    return true;
  } catch (err) {
    console.error(`❌ 创建目录失败：${err.message}`);
    return false;
  }
}

/**
 * 安全写入文件
 * @param {string} filePath - 文件路径
 * @param {string} content - 文件内容
 * @param {Object} options - 选项
 * @param {string} options.encoding - 编码（默认：utf8）
 * @param {boolean} options.ensureDir - 是否确保目录存在（默认：true）
 * @returns {boolean} 是否写入成功
 */
function safeWriteFile(filePath, content, options = {}) {
  const { 
    encoding = 'utf8', 
    ensureDir = true 
  } = options;
  
  try {
    // 确保目录存在
    if (ensureDir) {
      const dir = path.dirname(filePath);
      ensureDirExists(dir);
    }
    
    // 写入文件
    fs.writeFileSync(filePath, content, encoding);
    return true;
  } catch (err) {
    console.error(`❌ 写入文件失败：${err.message}`);
    return false;
  }
}

/**
 * 安全读取文件
 * @param {string} filePath - 文件路径
 * @param {string} encoding - 编码（默认：utf8）
 * @returns {string|null} 文件内容或 null
 */
function safeReadFile(filePath, encoding = 'utf8') {
  try {
    if (!fs.existsSync(filePath)) {
      return null;
    }
    return fs.readFileSync(filePath, encoding);
  } catch (err) {
    console.error(`❌ 读取文件失败：${err.message}`);
    return null;
  }
}

/**
 * 检查文件是否存在
 * @param {string} filePath - 文件路径
 * @returns {boolean} 文件是否存在
 */
function fileExists(filePath) {
  return fs.existsSync(filePath);
}

/**
 * 删除文件
 * @param {string} filePath - 文件路径
 * @returns {boolean} 是否删除成功
 */
function deleteFile(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
    return true;
  } catch (err) {
    console.error(`❌ 删除文件失败：${err.message}`);
    return false;
  }
}

/**
 * 复制文件
 * @param {string} src - 源文件路径
 * @param {string} dest - 目标文件路径
 * @returns {boolean} 是否复制成功
 */
function copyFile(src, dest) {
  try {
    ensureDirExists(path.dirname(dest));
    fs.copyFileSync(src, dest);
    return true;
  } catch (err) {
    console.error(`❌ 复制文件失败：${err.message}`);
    return false;
  }
}

/**
 * 获取文件大小
 * @param {string} filePath - 文件路径
 * @returns {number|null} 文件大小（字节）或 null
 */
function getFileSize(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return null;
    }
    const stats = fs.statSync(filePath);
    return stats.size;
  } catch (err) {
    return null;
  }
}

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
 * 获取文件修改时间
 * @param {string} filePath - 文件路径
 * @returns {Date|null} 修改时间或 null
 */
function getModifiedTime(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return null;
    }
    const stats = fs.statSync(filePath);
    return stats.mtime;
  } catch (err) {
    return null;
  }
}

module.exports = {
  walkDirectory,
  ensureDirExists,
  safeWriteFile,
  safeReadFile,
  fileExists,
  deleteFile,
  copyFile,
  getFileSize,
  formatFileSize,
  getModifiedTime
};
