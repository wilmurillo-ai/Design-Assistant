#!/usr/bin/env node

/**
 * 备份执行模块
 * 将本地配置备份到 GitHub 仓库
 */

const fs = require('fs');
const path = require('path');
const { getOpenClawEnv } = require('./openclaw-env');
const { GitHubWriter } = require('./github');
const { getToken } = require('./auth');
const { 
  printHeader, 
  printSuccess, 
  printError, 
  printWarning,
  printConnecting,
  printFileCount,
  printDivider,
  printFileStatus
} = require('./logger');
const { walkDirectory } = require('./file-utils');

class BackupExecutor {
  constructor(config, verbose = false) {
    this.config = config;
    this.verbose = verbose;
    this.ocEnv = null;
  }

  // 初始化
  async init() {
    this.ocEnv = await getOpenClawEnv();
    return this;
  }

  // 执行备份
  async execute() {
    printHeader('执行备份');

    // 获取 GitHub Token
    const token = await getToken(this.config);
    
    if (!token) {
      printError('❌ 错误：无法获取 GitHub Token');
      process.exit(1);
    }

    // 初始化 GitHub Writer
    const writer = new GitHubWriter(token, this.config.repo, this.config.branch);

    try {
      // 测试连接
      printConnecting('GitHub');
      const repoInfo = await writer.testConnection();
      printSuccess(`✓ 已连接到仓库：${repoInfo.full_name}`);

      // 获取要备份的文件列表
      console.log('\n📦 检测要备份的文件...');
      const files = await this.getFilesToBackup();
      
      if (files.length === 0) {
        printWarning('⚠️  没有要备份的文件');
        return;
      }

      printFileCount(files.length);

      // 打印文件列表
      for (const file of files) {
        printFileStatus(file.path, 'pending');
      }

      // 上传文件
      console.log('\n📤 开始上传...\n');
      
      let uploaded = 0;
      let skipped = 0;
      let errors = 0;

      for (const file of files) {
        try {
          const content = fs.readFileSync(file.fullPath, 'utf8');
          await writer.updateFile(file.path, content, `backup-${new Date().toISOString()}`);
          printFileStatus(file.path, 'success');
          uploaded++;
        } catch (err) {
          printFileStatus(file.path, 'error', err.message);
          errors++;
        }
      }

      // 输出统计
      printDivider();
      printSuccess('✅ 备份完成！');
      console.log(`   成功：${uploaded} 个文件`);
      console.log(`   跳过：${skipped} 个文件`);
      if (errors > 0) {
        printWarning(`   失败：${errors} 个文件`);
      }

    } catch (err) {
      printError(`❌ 备份失败：${err.message}`);
      if (this.verbose) {
        console.error(err.stack);
      }
      process.exit(1);
    }
  }

  // 获取要备份的文件列表
  async getFilesToBackup() {
    const files = [];
    const content = this.config.backup.content || [];
    const optionalContent = this.config.backup.optionalContent || [];

    // 核心配置
    if (content.includes('core')) {
      const coreFiles = [
        'AGENTS.md',
        'SOUL.md',
        'IDENTITY.md',
        'USER.md',
        'TOOLS.md',
        'HEARTBEAT.md'
      ];

      for (const file of coreFiles) {
        const fullPath = this.ocEnv.getWorkspaceFile(file);
        if (fs.existsSync(fullPath)) {
          files.push({ path: file, fullPath });
        }
      }
    }

    // 技能文件
    if (content.includes('skills')) {
      const skillsDir = this.ocEnv.getWorkspaceFile('skills');
      if (fs.existsSync(skillsDir)) {
        const skillFiles = walkDirectory(skillsDir, { 
          relativeBase: 'skills',
          extensions: ['.md', '.json', '.js']
        });
        files.push(...skillFiles);
      }
    }

    // 记忆文件
    if (content.includes('memory')) {
      const memoryFile = this.ocEnv.getWorkspaceFile('MEMORY.md');
      if (fs.existsSync(memoryFile)) {
        files.push({ path: 'MEMORY.md', fullPath: memoryFile });
      }

      const memoryDir = this.ocEnv.getWorkspaceFile('memory');
      if (fs.existsSync(memoryDir)) {
        const memoryFiles = walkDirectory(memoryDir, { 
          relativeBase: 'memory',
          extensions: ['.md', '.json']
        });
        files.push(...memoryFiles);
      }
    }

    // 学习记录
    if (content.includes('learnings')) {
      const learningsDir = this.ocEnv.getWorkspaceFile('.learnings');
      if (fs.existsSync(learningsDir)) {
        const learningsFiles = walkDirectory(learningsDir, { 
          relativeBase: '.learnings',
          extensions: ['.md', '.json']
        });
        files.push(...learningsFiles);
      }
    }

    // 可选内容：Channel 配置
    if (optionalContent.includes('channel')) {
      const feishuDir = this.ocEnv.getWorkspaceFile('feishu');
      if (fs.existsSync(feishuDir)) {
        const feishuFiles = walkDirectory(feishuDir, { 
          relativeBase: 'feishu',
          extensions: ['.md', '.json']
        });
        files.push(...feishuFiles);
      }
    }

    // 可选内容：环境配置
    if (optionalContent.includes('env')) {
      const envFile = this.ocEnv.getWorkspaceFile('.env');
      if (fs.existsSync(envFile)) {
        files.push({ path: '.env', fullPath: envFile });
      }
    }

    return files;
  }
}

module.exports = { BackupExecutor };
