#!/usr/bin/env node

/**
 * 配置加载器模块
 * 统一处理配置的加载、保存和验证
 */

const fs = require('fs');
const path = require('path');

/**
 * 获取配置文件路径
 * @returns {string} 配置文件路径
 */
function getConfigPath() {
  return path.join(process.cwd(), '.claw-migrate', 'config.json');
}

/**
 * 获取配置目录路径
 * @returns {string} 配置目录路径
 */
function getConfigDir() {
  return path.join(process.cwd(), '.claw-migrate');
}

/**
 * 确保配置目录存在
 */
function ensureConfigDir() {
  const configDir = getConfigDir();
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
}

/**
 * 加载配置
 * @returns {Promise<Object|null>} 配置对象或 null
 */
async function loadConfig() {
  const configPath = getConfigPath();
  
  if (!fs.existsSync(configPath)) {
    return null;
  }
  
  try {
    const content = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(content);
  } catch (err) {
    console.warn(`⚠️  读取配置文件失败：${err.message}`);
    return null;
  }
}

/**
 * 保存配置
 * @param {Object} config - 配置对象
 * @returns {Promise<boolean>} 是否保存成功
 */
async function saveConfig(config) {
  try {
    ensureConfigDir();
    
    const configPath = getConfigPath();
    config.updatedAt = new Date().toISOString();
    
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');
    return true;
  } catch (err) {
    console.error(`❌ 保存配置失败：${err.message}`);
    return false;
  }
}

/**
 * 验证配置
 * @param {Object} config - 配置对象
 * @returns {Object} 验证结果 { valid: boolean, errors: string[] }
 */
function validateConfig(config) {
  const errors = [];
  
  if (!config) {
    return { valid: false, errors: ['配置对象为空'] };
  }
  
  // 验证必填字段
  if (!config.repo) {
    errors.push('缺少必填字段：repo (GitHub 仓库)');
  } else if (!config.repo.includes('/')) {
    errors.push('仓库格式错误，应为 owner/repo 格式');
  }
  
  if (!config.branch) {
    errors.push('缺少必填字段：branch (分支名)');
  }
  
  // 验证备份配置
  if (!config.backup) {
    errors.push('缺少配置：backup (备份配置)');
  } else {
    if (!Array.isArray(config.backup.content)) {
      errors.push('backup.content 应为数组');
    }
  }
  
  // 验证认证配置
  if (!config.auth) {
    errors.push('缺少配置：auth (认证配置)');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * 创建默认配置
 * @returns {Object} 默认配置对象
 */
function createDefaultConfig() {
  return {
    version: '1.0',
    repo: '',
    branch: 'main',
    auth: {
      method: 'env',
      tokenEnv: 'GITHUB_TOKEN'
    },
    backup: {
      content: ['core', 'skills', 'memory', 'learnings'],
      optionalContent: [],
      frequency: 'manual'
    },
    strategy: {
      default: 'overwrite',
      merge: ['MEMORY.md', 'LEARNINGS.md'],
      append: []
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
}

/**
 * 删除配置
 * @returns {Promise<boolean>} 是否删除成功
 */
async function deleteConfig() {
  try {
    const configPath = getConfigPath();
    if (fs.existsSync(configPath)) {
      fs.unlinkSync(configPath);
    }
    return true;
  } catch (err) {
    console.error(`❌ 删除配置失败：${err.message}`);
    return false;
  }
}

/**
 * 检查配置是否存在
 * @returns {boolean} 配置是否存在
 */
function configExists() {
  return fs.existsSync(getConfigPath());
}

module.exports = {
  loadConfig,
  saveConfig,
  validateConfig,
  createDefaultConfig,
  deleteConfig,
  configExists,
  getConfigPath,
  getConfigDir,
  ensureConfigDir
};
