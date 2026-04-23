#!/usr/bin/env node

/**
 * 配置命令处理
 */

const { ConfigManager } = require('../config-manager');
const { printError } = require('../logger');

/**
 * 执行配置命令
 * @param {Object} options - 命令行选项
 */
async function executeConfig(options) {
  const manager = new ConfigManager();
  await manager.init();
  
  if (options?.reset) {
    await manager.resetConfig();
  } else if (options?.edit) {
    await manager.editConfig();
  } else if (options?.status) {
    await manager.showStatus();
  } else {
    await manager.showConfig();
  }
}

module.exports = {
  executeConfig
};
