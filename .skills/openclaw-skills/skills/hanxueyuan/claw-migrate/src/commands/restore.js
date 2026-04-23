#!/usr/bin/env node

/**
 * 恢复命令处理
 */

const { RestoreExecutor } = require('../restore');
const { loadConfig } = require('../config-loader');
const { printError } = require('../logger');

/**
 * 执行恢复命令
 * @param {Object} options - 命令行选项
 */
async function executeRestore(options) {
  // 加载配置
  const config = await loadConfig();
  
  if (!config) {
    printError('❌ 错误：未找到配置文件');
    console.log('   请先运行：openclaw skill run claw-migrate setup');
    process.exit(1);
  }
  
  // 执行恢复
  const executor = new RestoreExecutor(config, options?.verbose || false);
  await executor.init();
  await executor.execute();
}

module.exports = {
  executeRestore
};
