#!/usr/bin/env node

/**
 * 命令分发器
 * 将命令路由到对应的处理模块
 */

const { executeBackup } = require('./backup');
const { executeRestore } = require('./restore');
const { executeConfig } = require('./config');
const { executeScheduler } = require('./scheduler');
const { executeSetup } = require('./setup');
const { loadConfig } = require('../config-loader');
const { printError } = require('../logger');

/**
 * 执行命令
 * @param {string} command - 命令名称
 * @param {Object} options - 命令行选项
 */
async function executeCommand(command, options) {
  const commands = {
    setup: executeSetup,
    backup: executeBackup,
    restore: executeRestore,
    config: executeConfig,
    scheduler: executeScheduler
  };

  const handler = commands[command];
  if (!handler) {
    printError(`❌ 未知命令：${command}`);
    console.log('   使用 --help 查看可用命令');
    process.exit(1);
  }

  try {
    await handler(options);
  } catch (err) {
    printError(`❌ 命令执行失败：${err.message}`);
    if (options?.verbose) {
      console.error(err.stack);
    }
    process.exit(1);
  }
}

/**
 * 检查配置是否存在
 * @returns {Promise<boolean>} 配置是否存在
 */
async function checkConfigExists() {
  const config = await loadConfig();
  return config !== null;
}

/**
 * 需要配置文件的命令
 */
const COMMANDS_REQUIRING_CONFIG = ['backup', 'restore', 'config', 'scheduler'];

/**
 * 检查命令是否需要配置文件
 * @param {string} command - 命令名称
 * @returns {boolean} 是否需要配置文件
 */
function commandRequiresConfig(command) {
  return COMMANDS_REQUIRING_CONFIG.includes(command);
}

module.exports = {
  executeCommand,
  checkConfigExists,
  commandRequiresConfig
};
