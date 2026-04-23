#!/usr/bin/env node

/**
 * 恢复执行模块
 * 从 GitHub 仓库恢复配置到本地
 */

const fs = require('fs');
const path = require('path');
const { getOpenClawEnv } = require('./openclaw-env');
const { GitHubReader } = require('./github');
const { Merger } = require('./merger');
const { getToken } = require('./auth');
const { 
  printHeader, 
  printSuccess, 
  printError, 
  printWarning,
  printConnecting,
  printFileCount,
  printDivider,
  printFileStatus,
  printNextSteps
} = require('./logger');
const { ensureDirExists } = require('./file-utils');

class RestoreExecutor {
  constructor(config, verbose = false) {
    this.config = config;
    this.verbose = verbose;
    this.ocEnv = null;
    this.merger = new Merger(verbose);
  }

  // 初始化
  async init() {
    this.ocEnv = await getOpenClawEnv();
    return this;
  }

  // 执行恢复
  async execute() {
    printHeader('恢复配置');

    // 获取 GitHub Token
    const token = await getToken(this.config);
    
    if (!token) {
      printError('❌ 错误：无法获取 GitHub Token');
      process.exit(1);
    }

    // 初始化 GitHub Reader
    const reader = new GitHubReader(token, this.config.repo, this.config.branch);

    try {
      // 测试连接
      printConnecting('GitHub');
      const repoInfo = await reader.testConnection();
      printSuccess(`✓ 已连接到仓库：${repoInfo.full_name}`);

      // 获取文件列表
      console.log('\n📦 获取仓库文件列表...');
      const files = await reader.getFileList('all');
      printFileCount(files.length);

      // 生成恢复预览
      const preview = this.merger.generateRestorePreview(files, this.config.strategy);
      this.merger.printRestorePreview(preview);

      // 执行恢复
      console.log('\n🚀 开始恢复...\n');

      let restored = 0;
      let merged = 0;
      let appended = 0;
      let skipped = 0;
      let errors = 0;

      for (const file of files) {
        const strategyDetail = this.merger.getRestoreStrategy(file.path, this.config.strategy);

        if (strategyDetail.action === 'skip') {
          console.log(`   ⏭️ ${file.path} (${strategyDetail.reason})`);
          skipped++;
          continue;
        }

        try {
          // 获取远端文件内容
          const content = await reader.getFileContent(file.path);
          const fullPath = this.ocEnv.getWorkspaceFile(file.path);

          // 确保目录存在
          ensureDirExists(path.dirname(fullPath));

          // 根据策略处理
          if (strategyDetail.action === 'overwrite') {
            fs.writeFileSync(fullPath, content, 'utf8');
            printFileStatus(file.path, 'success', '已覆盖');
            restored++;
          } else if (strategyDetail.action === 'merge') {
            // 合并模式
            let localContent = '';
            if (fs.existsSync(fullPath)) {
              localContent = fs.readFileSync(fullPath, 'utf8');
            }

            const mergedContent = this.merger.merge('MEMORY', localContent, content);
            fs.writeFileSync(fullPath, mergedContent, 'utf8');
            printFileStatus(file.path, 'success', '已合并');
            merged++;
          } else if (strategyDetail.action === 'append') {
            // 追加模式
            let localContent = '';
            if (fs.existsSync(fullPath)) {
              localContent = fs.readFileSync(fullPath, 'utf8');
            }

            const appendedContent = this.merger.merge('LEARNINGS', localContent, content);
            fs.writeFileSync(fullPath, appendedContent, 'utf8');
            printFileStatus(file.path, 'success', '已追加');
            appended++;
          }
        } catch (err) {
          printFileStatus(file.path, 'error', err.message);
          errors++;
        }
      }

      // 输出统计
      printDivider();
      printSuccess('✅ 恢复完成！');
      console.log(`   覆盖：${restored} 个文件`);
      console.log(`   合并：${merged} 个文件`);
      console.log(`   追加：${appended} 个文件`);
      console.log(`   跳过：${skipped} 个文件`);
      if (errors > 0) {
        printWarning(`   失败：${errors} 个文件`);
      }

      // 后续提示
      printNextSteps([
        '检查配置文件是否正确',
        '如需要，配置 Channel pairing',
        '运行 `openclaw memory rebuild` 重建记忆索引'
      ]);

    } catch (err) {
      printError(`❌ 恢复失败：${err.message}`);
      if (this.verbose) {
        console.error(err.stack);
      }
      process.exit(1);
    }
  }
}

module.exports = { RestoreExecutor };
