#!/usr/bin/env node

/**
 * 迁移执行模块
 * 处理从 GitHub 仓库拉取配置的逻辑
 */

const fs = require('fs');
const readline = require('readline');

const { GitHubReader } = require('./github');
const { Merger } = require('./merger');
const { Writer } = require('./writer');
const { printError, printSuccess, printWarning, printInfo, printConnecting, printFileCount, printDivider } = require('./logger');

/**
 * 交互式获取 GitHub Token
 * @returns {Promise<string>} GitHub Token
 */
async function promptForToken() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    console.log('\n⚠️  未检测到 GITHUB_TOKEN 环境变量');
    console.log('   请输入您的 GitHub Personal Access Token:');
    console.log('   （Token 仅用于本次会话，不会被保存）\n');
    
    rl.question('GitHub Token: ', (token) => {
      rl.close();
      resolve(token.trim());
    });
  });
}

/**
 * 执行迁移（pull 模式）
 * @param {Object} options - 命令行选项
 */
async function executeMigration(options) {
  // 验证必填参数
  if (!options.repo) {
    printError('❌ 错误：必须指定 --repo 参数');
    console.log('用法：openclaw skill run claw-migrate --repo <owner/repo>');
    console.log('使用 --help 查看帮助信息');
    process.exit(1);
  }

  // 验证 repo 格式
  if (!options.repo.includes('/')) {
    printError('❌ 错误：仓库格式应为 owner/repo（例如：owner/repo）');
    process.exit(1);
  }

  // 验证 type 参数
  const validTypes = ['all', 'config', 'memory', 'learnings', 'skills'];
  if (!validTypes.includes(options.type)) {
    printError(`❌ 错误：无效的 type 参数，应为 ${validTypes.join(', ')}`);
    process.exit(1);
  }

  // 获取 GitHub Token
  let token = options.token;
  if (!token) {
    // 尝试从 gh CLI 获取
    try {
      const { execSync } = require('child_process');
      token = execSync('gh auth token', { encoding: 'utf8' }).trim();
      if (options.verbose) {
        printInfo('✓ 从 gh CLI 获取 Token');
      }
    } catch (e) {
      // gh CLI 不可用或未登录
    }
  }

  if (!token) {
    token = await promptForToken();
    if (!token) {
      printError('❌ 错误：需要 GitHub Token 才能访问私有仓库');
      process.exit(1);
    }
  }

  // 初始化组件
  const reader = new GitHubReader(token, options.repo, options.branch, options.path);
  const merger = new Merger(options.verbose);
  const writer = new Writer(options.dryRun, options.noBackup, options.verbose);

  try {
    // 测试连接
    printConnecting('GitHub');
    const repoInfo = await reader.testConnection();
    printSuccess(`✓ 已连接到仓库：${repoInfo.full_name}`);
    if (repoInfo.private) {
      console.log(`   类型：私有仓库`);
    }

    // 确定要迁移的文件
    console.log('\n📋 正在分析文件...');
    const filesToMigrate = await reader.getFileList(options.type);
    console.log(`   发现 ${filesToMigrate.length} 个文件待迁移`);

    if (filesToMigrate.length === 0) {
      printWarning('⚠️  没有找到需要迁移的文件');
      process.exit(0);
    }

    // 预览模式
    if (options.dryRun) {
      console.log('\n📝 预览将迁移的文件:\n');
      filesToMigrate.forEach(file => {
        console.log(`   + ${file.path}`);
      });
      console.log('\n💡 使用 --dry-run 以外的参数执行实际迁移');
      process.exit(0);
    }

    // 创建备份
    if (!options.noBackup) {
      console.log('\n💾 正在创建备份...');
      const backupPath = await writer.createBackup();
      printSuccess(`✓ 备份已创建：${backupPath}`);
    }

    // 执行迁移
    console.log('\n🚀 开始迁移...\n');
    
    let migrated = 0;
    let skipped = 0;
    let errors = 0;

    for (const file of filesToMigrate) {
      const localPath = require('path').join(process.cwd(), file.path);
      const existsLocally = fs.existsSync(localPath);

      try {
        // 获取远端文件内容
        const content = await reader.getFileContent(file.path);

        // 判断是否需要迁移
        if (existsLocally) {
          // 本地已有文件，根据策略处理
          const shouldMerge = merger.shouldMerge(file.category);
          
          if (shouldMerge) {
            // 合并模式
            const localContent = fs.readFileSync(localPath, 'utf8');
            const mergedContent = merger.merge(file.category, localContent, content);
            await writer.writeFile(file.path, mergedContent);
            console.log(`   🔄 ${file.path} (已合并)`);
          } else {
            // 跳过
            console.log(`   ⏭️  ${file.path} (本地已有，跳过)`);
            skipped++;
            continue;
          }
        } else {
          // 本地没有，直接复制
          await writer.writeFile(file.path, content);
          console.log(`   ✓ ${file.path}`);
        }

        migrated++;
      } catch (err) {
        printError(`   ✗ ${file.path}: ${err.message}`);
        errors++;
      }
    }

    // 输出统计
    printDivider();
    printSuccess('✅ 迁移完成!');
    console.log(`   成功：${migrated} 个文件`);
    console.log(`   跳过：${skipped} 个文件`);
    if (errors > 0) {
      printWarning(`   失败：${errors} 个文件`);
    }

    // 迁移后提示
    console.log('\n📌 后续步骤:');
    if (!options.noBackup) {
      console.log('   • 检查配置是否正确，如有问题可从备份恢复');
    }
    if (options.type === 'all' || options.type === 'config') {
      console.log('   • 验证 AGENTS.md, SOUL.md 等配置文件');
    }
    if (options.type === 'all' || options.type === 'skills') {
      console.log('   • 检查新技能是否正常工作');
    }

  } catch (err) {
    printError(`❌ 迁移失败：${err.message}`);
    if (options.verbose) {
      console.error(err.stack);
    }
    process.exit(1);
  }
}

module.exports = {
  executeMigration,
  promptForToken
};
