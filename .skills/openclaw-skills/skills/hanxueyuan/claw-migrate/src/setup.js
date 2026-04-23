#!/usr/bin/env node

/**
 * 安装后配置向导
 * 提供简洁的二选一：备份 or 恢复
 */

const readline = require('readline');
const { printHeader, printSuccess, printError, printWarning } = require('./utils');

class SetupWizard {
  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  // 显示主菜单（二选一）
  async showMainMenu() {
    printHeader('claw-migrate 安装完成！');
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    console.log('📋 请选择你要进行的操作：\n');
    console.log('   1. 🔵 开始备份配置');
    console.log('      将本地配置备份到 GitHub 私有仓库');
    console.log('      适合：首次使用、定期备份\n');
    console.log('   2. 🟢 恢复/迁移配置');
    console.log('      从 GitHub 仓库恢复配置到本地');
    console.log('      适合：新机器、配置恢复\n');
    console.log('   3. ⚪ 稍后配置');
    console.log('      跳过向导，稍后手动配置\n');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    return new Promise((resolve) => {
      let timeout = null;
      let answered = false;

      const ask = () => {
        if (answered) return;
        
        this.rl.question('   选择 [1-3，10 秒后自动选择 3]: ', (answer) => {
          answered = true;
          clearTimeout(timeout);
          const choice = parseInt(answer.trim()) || 3;
          resolve(choice);
        });
      };

      ask();

      // 10 秒超时自动选择 3
      timeout = setTimeout(() => {
        if (!answered) {
          answered = true;
          console.log('\n⏰ 超时，已选择：3. 稍后配置');
          resolve(3);
        }
      }, 10000);
    });
  }

  // 备份配置向导
  async backupWizard() {
    printSuccess('\n✅ 好的，让我们配置备份！\n');

    const config = {
      repo: '',
      branch: 'main',
      auth: 'env',
      content: ['core', 'skills', 'memory', 'learnings'],
      optionalContent: [],
      frequency: 'daily'
    };

    // Step 1: GitHub 仓库
    console.log('📝 备份配置向导 - 第 1 步 / 第 5 步\n');
    config.repo = await this.askQuestion(
      '❓ GitHub 仓库名称 (格式：owner/repo):\n   > ',
      (v) => v.includes('/'),
      '仓库格式应为 owner/repo，例如：hanxueyuan/openclaw-backup'
    );

    config.branch = await this.askQuestion(
      '\n❓ 分支名称 (默认：main):\n   > ',
      () => true,
      null,
      'main'
    );

    // Step 2: 认证方式
    console.log('\n📝 备份配置向导 - 第 2 步 / 第 5 步\n');
    console.log('❓ 认证方式:\n');
    console.log('   1. 使用 GITHUB_TOKEN 环境变量 (推荐)');
    console.log('   2. 使用 gh CLI (需要已登录)');
    console.log('   3. 手动输入 Token\n');
    
    const authChoice = await this.askQuestion(
      '   选择 [1-3]: ',
      (v) => ['1', '2', '3'].includes(v.trim())
    );
    config.auth = { '1': 'env', '2': 'gh-cli', '3': 'token' }[authChoice.trim()];

    // Step 3: 备份内容选择
    console.log('\n📝 备份配置向导 - 第 3 步 / 第 5 步\n');
    console.log('❓ 备份内容选择\n');
    console.log('我们为你推荐了以下默认配置：\n');
    console.log('✅ 默认备份内容（推荐）：');
    console.log('   • 核心配置 (AGENTS.md, SOUL.md, USER.md 等)');
    console.log('   • 技能文件 (skills/)');
    console.log('   • 记忆文件 (MEMORY.md, memory/)');
    console.log('   • 学习记录 (.learnings/)\n');
    console.log('⚠️  以下内容默认不备份（可选）：');
    console.log('   • Channel 配置 (feishu/, telegram/ 等)');
    console.log('     └─ 机器特定配置，多设备同步时建议备份');
    console.log('   • 环境配置 (.env 等敏感信息)');
    console.log('     └─ 包含 API keys，仅在可信仓库备份\n');

    const contentChoice = await this.askQuestion(
      '   你的选择 [1. 使用默认配置 2. 自定义选择]: ',
      (v) => ['1', '2'].includes(v.trim())
    );

    if (contentChoice.trim() === '2') {
      config.content = await this.selectBackupContent();
    }

    // Step 4: 敏感信息选择
    console.log('\n📝 备份配置向导 - 第 4 步 / 第 5 步\n');
    console.log('❓ 敏感信息选择\n');
    console.log('以下文件包含敏感信息，请选择是否备份：\n');
    console.log('   1. .env 文件 (API keys, 密码等)');
    console.log('   2. Channel pairing 信息 (认证 token)');
    console.log('   3. 会话数据 (sessions/)');
    console.log('   4. 都不备份 (推荐)\n');

    const sensitiveChoice = await this.askQuestion(
      '   选择 [1-4]: ',
      (v) => ['1', '2', '3', '4'].includes(v.trim())
    );

    if (sensitiveChoice.trim() === '1') {
      config.optionalContent.push('.env');
    } else if (sensitiveChoice.trim() === '2') {
      config.optionalContent.push('pairing');
    } else if (sensitiveChoice.trim() === '3') {
      config.optionalContent.push('sessions');
    }

    // Step 5: 备份频率
    console.log('\n📝 备份配置向导 - 第 5 步 / 第 5 步\n');
    console.log('❓ 备份频率:\n');
    console.log('   1. 每天凌晨 2 点 (推荐)');
    console.log('   2. 每周一凌晨 2 点');
    console.log('   3. 每月 1 号凌晨 2 点');
    console.log('   4. 仅手动备份\n');

    const freqChoice = await this.askQuestion(
      '   选择 [1-4]: ',
      (v) => ['1', '2', '3', '4'].includes(v.trim())
    );
    config.frequency = { '1': 'daily', '2': 'weekly', '3': 'monthly', '4': 'manual' }[freqChoice.trim()];

    // 确认配置
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    console.log('📊 配置摘要\n');
    console.log(`   仓库：${config.repo}`);
    console.log(`   分支：${config.branch}`);
    console.log(`   认证：${config.auth}`);
    console.log(`   备份内容：${config.content.join(', ')}`);
    console.log(`   敏感信息：${config.optionalContent.length > 0 ? config.optionalContent.join(', ') : '无'}`);
    console.log(`   备份频率：${config.frequency}\n`);

    const confirm = await this.askQuestion('   确认配置？(y/n): ', (v) => ['y', 'n'].includes(v.trim().toLowerCase()));
    
    if (confirm.trim().toLowerCase() === 'y') {
      printSuccess('\n✅ 备份配置已保存！\n');
      console.log('📌 后续步骤：\n');
      console.log('   1. 执行首次备份');
      console.log('      openclaw skill run claw-migrate backup\n');
      console.log('   2. 查看备份状态');
      console.log('      openclaw skill run claw-migrate status\n');
      console.log('   3. 修改配置');
      console.log('      openclaw skill run claw-migrate config --edit\n');
      return config;
    } else {
      console.log('\n⚠️  配置已取消，可以重新运行 setup 开始配置\n');
      return null;
    }
  }

  // 恢复配置向导
  async restoreWizard() {
    printSuccess('\n✅ 好的，让我们恢复配置！\n');

    const config = {
      repo: '',
      branch: 'main',
      auth: 'env',
      strategy: 'safe',
      customContent: []
    };

    // Step 1: GitHub 仓库
    console.log('📝 恢复配置向导 - 第 1 步 / 第 5 步\n');
    config.repo = await this.askQuestion(
      '❓ GitHub 仓库名称 (格式：owner/repo):\n   > ',
      (v) => v.includes('/'),
      '仓库格式应为 owner/repo，例如：hanxueyuan/openclaw-backup'
    );

    config.branch = await this.askQuestion(
      '\n❓ 分支名称 (默认：main):\n   > ',
      () => true,
      null,
      'main'
    );

    // Step 2: 认证方式
    console.log('\n📝 恢复配置向导 - 第 2 步 / 第 5 步\n');
    console.log('❓ 认证方式:\n');
    console.log('   1. 使用 GITHUB_TOKEN 环境变量 (推荐)');
    console.log('   2. 使用 gh CLI (需要已登录)');
    console.log('   3. 手动输入 Token\n');
    
    const authChoice = await this.askQuestion(
      '   选择 [1-3]: ',
      (v) => ['1', '2', '3'].includes(v.trim())
    );
    config.auth = { '1': 'env', '2': 'gh-cli', '3': 'token' }[authChoice.trim()];

    // Step 3: 恢复策略选择
    console.log('\n📝 恢复配置向导 - 第 3 步 / 第 5 步\n');
    console.log('❓ 恢复策略\n');
    console.log('   请选择恢复内容：\n');
    console.log('   1. 仅恢复通用配置 (推荐)');
    console.log('      • 核心配置、技能、记忆、学习记录');
    console.log('      • 保留当前机器的 Channel 配置');
    console.log('      • 保留当前机器的 .env 配置\n');
    console.log('   2. 完整恢复');
    console.log('      • 恢复所有备份的内容');
    console.log('      • 覆盖当前机器的配置');
    console.log('      • 需要重新配置 Channel 和 API keys\n');
    console.log('   3. 自定义选择');
    console.log('      • 手动选择要恢复的内容\n');

    const strategyChoice = await this.askQuestion(
      '   选择 [1-3]: ',
      (v) => ['1', '2', '3'].includes(v.trim())
    );
    config.strategy = { '1': 'safe', '2': 'full', '3': 'custom' }[strategyChoice.trim()];

    // Step 4: 自定义选择（如果选择自定义）
    if (config.strategy === 'custom') {
      console.log('\n📝 恢复配置向导 - 第 4 步 / 第 5 步\n');
      console.log('❓ 请选择要恢复的内容 (空格键切换，回车确认):\n');
      console.log('   ✅ [x] 1. 核心配置 (AGENTS.md, SOUL.md, USER.md 等)');
      console.log('   ✅ [x] 2. 技能文件 (skills/)');
      console.log('   ✅ [x] 3. 记忆文件 (MEMORY.md, memory/)');
      console.log('   ✅ [x] 4. 学习记录 (.learnings/)');
      console.log('   ⚠️  [ ] 5. Channel 配置 (feishu/, telegram/ 等)');
      console.log('   ⚠️  [ ] 6. 环境配置 (.env 等敏感信息)\n');
      
      // TODO: 实现交互式选择
      config.customContent = ['core', 'skills', 'memory', 'learnings'];
    }

    // Step 5: 预览恢复内容
    console.log('\n📝 恢复配置向导 - 第 5 步 / 第 5 步\n');
    console.log('📊 预览恢复内容\n');
    console.log('   将恢复以下文件：\n');
    console.log('   ✓ AGENTS.md');
    console.log('   ✓ SOUL.md');
    console.log('   ✓ USER.md');
    console.log('   ✓ skills/');
    console.log('   ✓ MEMORY.md (合并)');
    
    if (config.strategy === 'safe') {
      console.log('   ⏭️ .env (保留本地)');
      console.log('   ⏭️ feishu/pairing/ (保留本地)');
    } else {
      console.log('   ⚠️ .env (覆盖)');
      console.log('   ⚠️ feishu/pairing/ (覆盖)');
    }
    
    console.log('\n   提示：实际文件列表将在连接仓库后显示\n');

    const confirm = await this.askQuestion('   确认恢复？(y/n): ', (v) => ['y', 'n'].includes(v.trim().toLowerCase()));
    
    if (confirm.trim().toLowerCase() === 'y') {
      printSuccess('\n✅ 开始恢复配置...\n');
      return config;
    } else {
      console.log('\n⚠️  恢复已取消\n');
      return null;
    }
  }

  // 选择备份内容
  async selectBackupContent() {
    console.log('\n❓ 请选择要备份的内容 (空格键切换，回车确认):\n');
    console.log('默认备份内容：');
    console.log('   ✅ [x] 1. 核心配置 (AGENTS.md, SOUL.md, USER.md 等)');
    console.log('   ✅ [x] 2. 技能文件 (skills/)');
    console.log('   ✅ [x] 3. 记忆文件 (MEMORY.md, memory/)');
    console.log('   ✅ [x] 4. 学习记录 (.learnings/)');
    console.log('\n可选内容：');
    console.log('   ⚠️  [ ] 5. Channel 配置 (feishu/, telegram/ 等)');
    console.log('         └─ 包含机器特定配置，多设备同步时建议备份');
    console.log('   ⚠️  [ ] 6. 环境配置 (.env 等敏感信息)');
    console.log('         └─ 包含 API keys，仅在可信仓库备份\n');
    console.log('   提示：输入数字选择，例如：1,2,3,4,5\n');

    const answer = await this.askQuestion('   你的选择 [1-6，逗号分隔]: ', () => true);
    
    const choices = answer.split(',').map(v => v.trim());
    const content = [];
    
    if (choices.includes('1')) content.push('core');
    if (choices.includes('2')) content.push('skills');
    if (choices.includes('3')) content.push('memory');
    if (choices.includes('4')) content.push('learnings');
    if (choices.includes('5')) content.push('channel');
    if (choices.includes('6')) content.push('env');
    
    return content;
  }

  // 通用提问方法
  async askQuestion(question, validator, errorMsg = null, defaultValue = null) {
    return new Promise((resolve) => {
      const ask = () => {
        this.rl.question(question, (answer) => {
          const value = answer.trim() || defaultValue;
          if (validator(value)) {
            resolve(value);
          } else {
            if (errorMsg) {
              printWarning(`\n   ⚠️  ${errorMsg}\n`);
            }
            ask();
          }
        });
      };
      ask();
    });
  }

  // 关闭 readline
  close() {
    this.rl.close();
  }
}

module.exports = { SetupWizard };
