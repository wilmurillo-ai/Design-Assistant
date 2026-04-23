#!/usr/bin/env node

/**
 * GitHub 认证模块
 * 统一处理 Token 获取逻辑
 * 
 * 优先级顺序：
 * 1. 环境变量 GITHUB_TOKEN
 * 2. gh CLI (gh auth token)
 * 3. 配置文件中的 token
 */

/**
 * 从环境变量获取 GitHub Token
 * @returns {string|null} GitHub Token 或 null
 */
function getTokenFromEnv() {
  return process.env.GITHUB_TOKEN || null;
}

/**
 * 从 gh CLI 获取 GitHub Token
 * @returns {string|null} GitHub Token 或 null
 */
function getTokenFromGHCLI() {
  try {
    const { execSync } = require('child_process');
    const token = execSync('gh auth token', { encoding: 'utf8', stdio: 'pipe' }).trim();
    return token || null;
  } catch (e) {
    // gh CLI 不可用或未登录
    return null;
  }
}

/**
 * 从配置文件获取 GitHub Token
 * @param {Object} config - 配置对象
 * @returns {string|null} GitHub Token 或 null
 */
function getTokenFromConfig(config) {
  return config?.auth?.token || null;
}

/**
 * 获取 GitHub Token 的统一入口
 * 按优先级尝试不同的获取方式
 * 
 * @param {Object} config - 配置对象（可选）
 * @returns {Promise<string|null>} GitHub Token 或 null
 */
async function getToken(config = null) {
  // 策略 1: 环境变量
  const envToken = getTokenFromEnv();
  if (envToken) {
    return envToken;
  }

  // 策略 2: gh CLI
  const cliToken = getTokenFromGHCLI();
  if (cliToken) {
    return cliToken;
  }

  // 策略 3: 配置文件
  const configToken = getTokenFromConfig(config);
  if (configToken) {
    return configToken;
  }

  return null;
}

module.exports = {
  getToken,
  getTokenFromEnv,
  getTokenFromGHCLI,
  getTokenFromConfig
};
