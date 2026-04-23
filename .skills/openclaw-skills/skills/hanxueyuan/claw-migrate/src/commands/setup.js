#!/usr/bin/env node

/**
 * 设置向导命令处理
 */

const { SetupWizard } = require('../setup');
const { saveConfig } = require('../config-loader');
const { RestoreExecutor } = require('../restore');

/**
 * 执行设置向导命令
 * @param {Object} options - 命令行选项
 */
async function executeSetup(options) {
  const wizard = new SetupWizard();
  const choice = await wizard.showMainMenu();
  
  if (choice === 1) {
    // 开始备份配置
    const config = await wizard.backupWizard();
    if (config) {
      await saveConfig({
        version: '1.0',
        repo: config.repo,
        branch: config.branch,
        auth: {
          method: config.auth,
          tokenEnv: 'GITHUB_TOKEN'
        },
        backup: {
          content: config.content,
          optionalContent: config.optionalContent,
          frequency: config.frequency
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
    }
  } else if (choice === 2) {
    // 开始恢复配置
    const config = await wizard.restoreWizard();
    if (config) {
      await executeRestoreFromWizard(config);
    }
  }
  
  wizard.close();
}

/**
 * 执行向导中的恢复操作
 * @param {Object} config - 配置对象
 */
async function executeRestoreFromWizard(config) {
  const executor = new RestoreExecutor(config, true);
  await executor.init();
  await executor.execute();
}

module.exports = {
  executeSetup
};
