#!/usr/bin/env node

/**
 * 文件写入模块
 * 处理文件写入和备份管理
 */

const fs = require('fs');
const path = require('path');
const { MIGRATION_CONFIG } = require('./config');

class Writer {
  constructor(dryRun = false, noBackup = false, verbose = false) {
    this.dryRun = dryRun;
    this.noBackup = noBackup;
    this.verbose = verbose;
    this.backupPath = null;
  }

  // 创建备份
  async createBackup() {
    if (this.noBackup || this.dryRun) {
      return null;
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    this.backupPath = path.join(process.cwd(), MIGRATION_CONFIG.backupDir, timestamp);
    
    // 创建备份目录
    fs.mkdirSync(this.backupPath, { recursive: true });

    // 备份现有配置文件
    const filesToBackup = [
      'AGENTS.md',
      'SOUL.md',
      'IDENTITY.md',
      'USER.md',
      'TOOLS.md',
      'HEARTBEAT.md',
      'MEMORY.md',
      '.env'
    ];

    let backedUp = 0;
    for (const file of filesToBackup) {
      const srcPath = path.join(process.cwd(), file);
      if (fs.existsSync(srcPath)) {
        const destPath = path.join(this.backupPath, file);
        fs.copyFileSync(srcPath, destPath);
        backedUp++;
      }
    }

    // 备份 memory 目录
    const memoryDir = path.join(process.cwd(), 'memory');
    if (fs.existsSync(memoryDir)) {
      const backupMemoryDir = path.join(this.backupPath, 'memory');
      fs.mkdirSync(backupMemoryDir, { recursive: true });
      const memoryFiles = fs.readdirSync(memoryDir);
      for (const file of memoryFiles) {
        const srcPath = path.join(memoryDir, file);
        const destPath = path.join(backupMemoryDir, file);
        fs.copyFileSync(srcPath, destPath);
        backedUp++;
      }
    }

    // 备份 learnings 目录
    const learningsDir = path.join(process.cwd(), '.learnings');
    if (fs.existsSync(learningsDir)) {
      const backupLearningsDir = path.join(this.backupPath, '.learnings');
      fs.mkdirSync(backupLearningsDir, { recursive: true });
      const learningsFiles = fs.readdirSync(learningsDir);
      for (const file of learningsFiles) {
        const srcPath = path.join(learningsDir, file);
        const destPath = path.join(backupLearningsDir, file);
        fs.copyFileSync(srcPath, destPath);
        backedUp++;
      }
    }

    // 备份 skills 目录
    const skillsDir = path.join(process.cwd(), 'skills');
    if (fs.existsSync(skillsDir)) {
      const backupSkillsDir = path.join(this.backupPath, 'skills');
      this.copyDirectory(skillsDir, backupSkillsDir);
    }

    if (this.verbose) {
      console.log(`   备份了 ${backedUp} 个文件`);
    }

    return this.backupPath;
  }

  // 递归复制目录
  copyDirectory(src, dest) {
    fs.mkdirSync(dest, { recursive: true });
    const entries = fs.readdirSync(src, { withFileTypes: true });
    
    for (const entry of entries) {
      const srcPath = path.join(src, entry.name);
      const destPath = path.join(dest, entry.name);
      
      if (entry.isDirectory()) {
        this.copyDirectory(srcPath, destPath);
      } else {
        fs.copyFileSync(srcPath, destPath);
      }
    }
  }

  // 写入文件
  async writeFile(filePath, content) {
    if (this.dryRun) {
      if (this.verbose) {
        console.log(`   [DRY RUN] 将写入：${filePath}`);
      }
      return;
    }

    const fullPath = path.join(process.cwd(), filePath);
    
    // 确保目录存在
    const dir = path.dirname(fullPath);
    fs.mkdirSync(dir, { recursive: true });

    // 原子写入：先写临时文件，再重命名
    const tempPath = fullPath + '.tmp.' + Date.now();
    fs.writeFileSync(tempPath, content, MIGRATION_CONFIG.encoding);
    fs.renameSync(tempPath, fullPath);

    if (this.verbose) {
      console.log(`   已写入：${filePath}`);
    }
  }

  // 恢复备份
  async restoreBackup(backupPath) {
    if (!backupPath) {
      backupPath = this.getLatestBackup();
    }

    if (!backupPath || !fs.existsSync(backupPath)) {
      throw new Error('未找到备份');
    }

    console.log(`正在从备份恢复：${backupPath}`);

    // 恢复所有备份的文件
    const files = fs.readdirSync(backupPath);
    for (const file of files) {
      if (file === 'memory' || file === '.learnings' || file === 'skills') {
        continue; // 目录单独处理
      }
      
      const srcPath = path.join(backupPath, file);
      const destPath = path.join(process.cwd(), file);
      
      if (fs.existsSync(srcPath)) {
        fs.copyFileSync(srcPath, destPath);
        console.log(`  恢复：${file}`);
      }
    }

    // 恢复 memory 目录
    const backupMemoryDir = path.join(backupPath, 'memory');
    if (fs.existsSync(backupMemoryDir)) {
      const memoryDir = path.join(process.cwd(), 'memory');
      fs.mkdirSync(memoryDir, { recursive: true });
      this.copyDirectory(backupMemoryDir, memoryDir);
    }

    // 恢复 learnings 目录
    const backupLearningsDir = path.join(backupPath, '.learnings');
    if (fs.existsSync(backupLearningsDir)) {
      const learningsDir = path.join(process.cwd(), '.learnings');
      fs.mkdirSync(learningsDir, { recursive: true });
      this.copyDirectory(backupLearningsDir, learningsDir);
    }

    console.log('✓ 恢复完成');
  }

  // 获取最新的备份
  getLatestBackup() {
    const backupDir = path.join(process.cwd(), MIGRATION_CONFIG.backupDir);
    
    if (!fs.existsSync(backupDir)) {
      return null;
    }

    const backups = fs.readdirSync(backupDir)
      .filter(name => /^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}/.test(name))
      .sort()
      .reverse();

    if (backups.length === 0) {
      return null;
    }

    return path.join(backupDir, backups[0]);
  }

  // 清理旧备份
  cleanupOldBackups() {
    const backupDir = path.join(process.cwd(), MIGRATION_CONFIG.backupDir);
    
    if (!fs.existsSync(backupDir)) {
      return;
    }

    const backups = fs.readdirSync(backupDir)
      .filter(name => /^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}/.test(name))
      .sort()
      .reverse();

    // 保留最近的 N 个备份
    const toDelete = backups.slice(MIGRATION_CONFIG.maxBackups);
    
    for (const backup of toDelete) {
      const backupPath = path.join(backupDir, backup);
      fs.rmSync(backupPath, { recursive: true, force: true });
      if (this.verbose) {
        console.log(`  清理旧备份：${backup}`);
      }
    }
  }
}

module.exports = { Writer };
