#!/usr/bin/env node

/**
 * 备份命令处理
 */

const { BackupExecutor } = require('../backup');
const { loadConfig } = require('../config-loader');
const { printError } = require('../logger');

/**
 * 执行备份命令
 * @param {Object} options - 命令行选项
 */
async function executeBackup(options) {
  // 加载配置
  const config = await loadConfig();
  
  if (!config) {
    printError('❌ 错误：未找到配置文件');
    console.log('   请先运行：openclaw skill run claw-migrate setup');
    process.exit(1);
  }
  
  // 执行备份
  const executor = new BackupExecutor(config, options?.verbose || false);
  await executor.init();
  await executor.execute();
}

module.exports = {
  executeBackup
};
