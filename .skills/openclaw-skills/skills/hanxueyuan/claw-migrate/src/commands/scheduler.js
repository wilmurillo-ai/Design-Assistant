#!/usr/bin/env node

/**
 * 调度器命令处理
 */

const { BackupScheduler } = require('../scheduler');
const { loadConfig } = require('../config-loader');
const { printError, printInfo } = require('../logger');

/**
 * 执行调度器命令
 * @param {Object} options - 命令行选项
 */
async function executeScheduler(options) {
  const config = await loadConfig();
  
  if (!config) {
    printError('❌ 错误：未找到配置文件');
    console.log('   请先运行：openclaw skill run claw-migrate setup');
    process.exit(1);
  }
  
  const scheduler = new BackupScheduler(config, options?.verbose || false);
  await scheduler.init();
  
  if (options?.action === 'start') {
    await scheduler.start();
  } else if (options?.action === 'stop') {
    await scheduler.stop();
  } else if (options?.action === 'logs') {
    await scheduler.showLogs();
  } else {
    // 默认显示帮助
    printInfo('📅 定时任务管理\n');
    console.log('用法:\n');
    console.log('   openclaw skill run claw-migrate scheduler --start   启动定时任务');
    console.log('   openclaw skill run claw-migrate scheduler --stop    停止定时任务');
    console.log('   openclaw skill run claw-migrate scheduler --logs    查看日志\n');
  }
}

module.exports = {
  executeScheduler
};
