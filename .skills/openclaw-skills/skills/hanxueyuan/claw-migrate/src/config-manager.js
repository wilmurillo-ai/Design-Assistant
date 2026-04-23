#!/usr/bin/env node

/**
 * 配置管理模块
 * 支持查看、修改、重置配置
 */

const readline = require('readline');
const { getOpenClawEnv } = require('./openclaw-env');
const { 
  loadConfig, 
  saveConfig, 
  deleteConfig,
  getConfigPath,
  ensureConfigDir 
} = require('./config-loader');
const { printHeader, printSuccess, printError, printWarning, printInfo } = require('./logger');

class ConfigManager {
  constructor() {
    this.config = null;
  }

  // 初始化
  async init() {
    const ocEnv = await getOpenClawEnv();
    ensureConfigDir();
    
    // 加载配置
    this.config = await loadConfig();
    
    return this;
  }

  // 保存配置
  async saveConfig() {
    return await saveConfig(this.config);
  }

  // 显示配置
  async showConfig() {
    printHeader('当前配置');
    
    if (!this.config) {
      console.log('\n⚠️  未找到配置文件\n');
      console.log('   请运行：openclaw skill run claw-migrate setup\n');
      return;
    }
    
    console.log('\n📋 配置信息\n');
    console.log(`   仓库：${this.config.repo}`);
    console.log(`   分支：${this.config.branch}`);
    console.log(`   认证：${this.config.auth?.method || 'env'}`);
    console.log(`   备份内容：${this.config.backup?.content?.join(', ') || '未配置'}`);
    console.log(`   敏感信息：${this.config.backup?.optionalContent?.join(', ') || '无'}`);
    console.log(`   备份频率：${this.config.backup?.frequency || 'manual'}`);
    console.log(`   创建时间：${this.config.createdAt || '未知'}`);
    console.log(`   更新时间：${this.config.updatedAt || '未知'}\n`);
  }

  // 修改配置
  async editConfig() {
    printHeader('修改配置');
    
    if (!this.config) {
      console.log('\n⚠️  未找到配置文件\n');
      console.log('   请运行：openclaw skill run claw-migrate setup\n');
      return;
    }
    
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const question = (query) => new Promise((resolve) => {
      rl.question(query, resolve);
    });
    
    try {
      console.log('\n📝 修改配置\n');
      console.log('   当前配置：');
      console.log(`   • 仓库：${this.config.repo}`);
      console.log(`   • 分支：${this.config.branch}`);
      console.log(`   • 备份频率：${this.config.backup?.frequency || 'manual'}\n`);
      
      // 修改仓库
      const repo = await question(`   新的仓库名称 (默认：${this.config.repo}): `);
      if (repo.trim()) {
        this.config.repo = repo.trim();
      }
      
      // 修改分支
      const branch = await question(`   新的分支名称 (默认：${this.config.branch}): `);
      if (branch.trim()) {
        this.config.branch = branch.trim();
      }
      
      // 修改备份内容
      console.log('\n   备份内容选择 (空格分隔，回车确认)：');
      console.log('   • core - 核心配置');
      console.log('   • skills - 技能文件');
      console.log('   • memory - 记忆文件');
      console.log('   • learnings - 学习记录\n');
      
      const contentInput = await question(`   当前：${this.config.backup?.content?.join(' ')}\n   新的选择：`);
      if (contentInput.trim()) {
        this.config.backup.content = contentInput.trim().split(/\s+/);
      }
      
      // 修改备份频率
      console.log('\n   备份频率选择：');
      console.log('   1. 每天凌晨 2 点 (daily)');
      console.log('   2. 每周一凌晨 2 点 (weekly)');
      console.log('   3. 每月 1 号凌晨 2 点 (monthly)');
      console.log('   4. 仅手动备份 (manual)\n');
      
      const freqInput = await question(`   当前：${this.config.backup?.frequency || 'manual'}\n   新的选择 [1-4]: `);
      const freqMap = { '1': 'daily', '2': 'weekly', '3': 'monthly', '4': 'manual' };
      if (freqMap[freqInput.trim()]) {
        this.config.backup.frequency = freqMap[freqInput.trim()];
      }
      
      // 保存配置
      const confirm = await question('\n   确认保存配置？(y/n): ');
      if (confirm.trim().toLowerCase() === 'y') {
        await this.saveConfig();
        printSuccess('\n✅ 配置已更新！\n');
      } else {
        console.log('\n⚠️  配置已取消修改\n');
      }
      
    } catch (err) {
      printError(`❌ 修改配置失败：${err.message}`);
    } finally {
      rl.close();
    }
  }

  // 重置配置
  async resetConfig() {
    printHeader('重置配置');
    
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const question = (query) => new Promise((resolve) => {
      rl.question(query, resolve);
    });
    
    try {
      console.log('\n⚠️  警告：这将删除所有配置信息\n');
      
      const confirm = await question('   确认重置配置？(y/n): ');
      
      if (confirm.trim().toLowerCase() === 'y') {
        await deleteConfig();
        printSuccess('\n✅ 配置已重置！\n');
        console.log('   请运行：openclaw skill run claw-migrate setup\n');
      } else {
        console.log('\n⚠️  重置已取消\n');
      }
      
    } catch (err) {
      printError(`❌ 重置配置失败：${err.message}`);
    } finally {
      rl.close();
    }
  }

  // 显示状态
  async showStatus() {
    printHeader('备份状态');
    
    if (!this.config) {
      console.log('\n⚠️  未配置备份\n');
      console.log('   请运行：openclaw skill run claw-migrate setup\n');
      return;
    }
    
    console.log('\n📊 状态信息\n');
    console.log(`   仓库：${this.config.repo}`);
    console.log(`   分支：${this.config.branch}`);
    console.log(`   状态：✅ 已配置`);
    console.log(`   备份频率：${this.config.backup?.frequency || 'manual'}`);
    
    // 计算下次备份时间
    const nextBackup = this.getNextBackupTime();
    if (nextBackup) {
      console.log(`   下次备份：${nextBackup}\n`);
    } else {
      console.log(`   下次备份：手动触发\n`);
    }
    
    // 显示备份历史
    console.log('📜 最近备份:\n');
    console.log('   待实现...\n');
  }

  // 计算下次备份时间
  getNextBackupTime() {
    const frequency = this.config.backup?.frequency;
    
    if (!frequency || frequency === 'manual') {
      return null;
    }
    
    const now = new Date();
    const next = new Date(now);
    next.setHours(2, 0, 0, 0); // 凌晨 2 点
    
    if (next <= now) {
      next.setDate(next.getDate() + 1);
    }
    
    if (frequency === 'weekly') {
      // 下周一
      const day = next.getDay();
      const daysUntilMonday = (1 - day + 7) % 7 || 7;
      next.setDate(next.getDate() + daysUntilMonday);
    } else if (frequency === 'monthly') {
      // 下月 1 号
      next.setMonth(next.getMonth() + 1);
      next.setDate(1);
    }
    
    return next.toLocaleString('zh-CN');
  }
}

module.exports = { ConfigManager };
