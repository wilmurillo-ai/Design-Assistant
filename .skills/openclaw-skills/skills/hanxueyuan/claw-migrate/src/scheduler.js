#!/usr/bin/env node

/**
 * 定时任务调度器
 * 支持每日/每周/每月自动备份
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { getOpenClawEnv } = require('./openclaw-env');
const { printHeader, printSuccess, printError, printWarning, printInfo } = require('./utils');

class BackupScheduler {
  constructor(config, verbose = false) {
    this.config = config;
    this.verbose = verbose;
    this.ocEnv = null;
    this.schedulerPath = null;
    this.logPath = null;
  }

  // 初始化
  async init() {
    this.ocEnv = await getOpenClawEnv();
    
    const schedulerDir = path.join(this.ocEnv.workspace, '.claw-migrate', 'scheduler');
    this.schedulerPath = path.join(schedulerDir, 'schedule.json');
    this.logPath = path.join(schedulerDir, 'scheduler.log');
    
    // 确保目录存在
    if (!fs.existsSync(schedulerDir)) {
      fs.mkdirSync(schedulerDir, { recursive: true });
    }
    
    return this;
  }

  // 启动定时任务
  async start() {
    printHeader('启动定时备份');
    
    const frequency = this.config.backup?.frequency;
    
    if (!frequency || frequency === 'manual') {
      console.log('\n⚠️  手动备份模式，无需启动定时任务\n');
      console.log('   运行备份：openclaw skill run claw-migrate backup\n');
      return;
    }
    
    // 计算 cron 表达式
    const cronExpression = this.getCronExpression(frequency);
    
    console.log(`\n📅 备份频率：${frequency}`);
    console.log(`⏰ Cron 表达式：${cronExpression}`);
    
    // 保存调度配置
    await this.saveSchedule(cronExpression);
    
    // 尝试设置系统 cron
    const systemCronSuccess = await this.setupSystemCron(cronExpression);
    
    if (systemCronSuccess) {
      printSuccess('\n✅ 定时任务已启动！\n');
      console.log('📌 管理命令：\n');
      console.log('   • 查看状态：openclaw skill run claw-migrate status');
      console.log('   • 停止任务：openclaw skill run claw-migrate scheduler stop');
      console.log('   • 查看日志：openclaw skill run claw-migrate scheduler logs\n');
    } else {
      printWarning('\n⚠️  无法设置系统 cron，使用内部调度器\n');
      console.log('\n💡 提示：');
      console.log('   内部调度器需要保持 OpenClaw 运行\n');
      console.log('   建议手动设置系统 cron：\n');
      console.log(`   ${this.getCronManualSetup(frequency)}\n`);
    }
  }

  // 停止定时任务
  async stop() {
    printHeader('停止定时备份');
    
    // 删除调度配置
    if (fs.existsSync(this.schedulerPath)) {
      fs.unlinkSync(this.schedulerPath);
    }
    
    // 删除系统 cron
    await this.removeSystemCron();
    
    printSuccess('\n✅ 定时任务已停止！\n');
  }

  // 查看日志
  async showLogs(lines = 20) {
    printHeader('备份日志');
    
    if (!fs.existsSync(this.logPath)) {
      console.log('\n⚠️  暂无日志\n');
      return;
    }
    
    try {
      const content = fs.readFileSync(this.logPath, 'utf8');
      const logLines = content.split('\n').slice(-lines);
      
      console.log('\n' + logLines.join('\n') + '\n');
    } catch (err) {
      printError(`❌ 读取日志失败：${err.message}`);
    }
  }

  // 获取 cron 表达式
  getCronExpression(frequency) {
    switch (frequency) {
      case 'daily':
        return '0 2 * * *'; // 每天凌晨 2 点
      case 'weekly':
        return '0 2 * * 1'; // 每周一凌晨 2 点
      case 'monthly':
        return '0 2 1 * *'; // 每月 1 号凌晨 2 点
      default:
        return '0 2 * * *';
    }
  }

  // 获取手动设置 cron 的命令
  getCronManualSetup(frequency) {
    const cronExpr = this.getCronExpression(frequency);
    const workspace = this.ocEnv.workspace;
    const command = `cd ${workspace} && openclaw skill run claw-migrate backup >> .claw-migrate/scheduler/backup.log 2>&1`;
    
    return `crontab -e\n\n# 添加以下行：\n${cronExpr} ${command}`;
  }

  // 保存调度配置
  async saveSchedule(cronExpression) {
    const schedule = {
      cron: cronExpression,
      frequency: this.config.backup.frequency,
      repo: this.config.repo,
      branch: this.config.branch,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    fs.writeFileSync(this.schedulerPath, JSON.stringify(schedule, null, 2), 'utf8');
  }

  // 设置系统 cron
  async setupSystemCron(cronExpression) {
    try {
      const workspace = this.ocEnv.workspace;
      const command = `cd ${workspace} && openclaw skill run claw-migrate backup >> ${this.logPath} 2>&1`;
      
      // 获取当前 cron
      const currentCron = await this.execCommand('crontab -l');
      
      // 检查是否已存在
      if (currentCron.includes('claw-migrate backup')) {
        printInfo('   定时任务已存在');
        return true;
      }
      
      // 添加新任务
      const newCron = currentCron.trim() ? `${currentCron.trim()}\n` : '';
      const fullCron = `${newCron}${cronExpression} ${command}`;
      
      // 写入 cron
      const tmpFile = `/tmp/claw-migrate-cron-${Date.now()}`;
      fs.writeFileSync(tmpFile, fullCron);
      
      await this.execCommand(`crontab ${tmpFile}`);
      fs.unlinkSync(tmpFile);
      
      this.log(`定时任务已设置：${cronExpression}`);
      return true;
      
    } catch (err) {
      this.log(`设置系统 cron 失败：${err.message}`);
      return false;
    }
  }

  // 删除系统 cron
  async removeSystemCron() {
    try {
      const currentCron = await this.execCommand('crontab -l');
      
      // 过滤掉 claw-migrate 相关行
      const newCron = currentCron
        .split('\n')
        .filter(line => !line.includes('claw-migrate backup'))
        .join('\n');
      
      if (newCron.trim()) {
        const tmpFile = `/tmp/claw-migrate-cron-${Date.now()}`;
        fs.writeFileSync(tmpFile, newCron);
        await this.execCommand(`crontab ${tmpFile}`);
        fs.unlinkSync(tmpFile);
      } else {
        await this.execCommand('crontab -r');
      }
      
      this.log('定时任务已删除');
      return true;
      
    } catch (err) {
      this.log(`删除系统 cron 失败：${err.message}`);
      return false;
    }
  }

  // 执行命令
  execCommand(command) {
    return new Promise((resolve, reject) => {
      const child = spawn('sh', ['-c', command], {
        stdio: ['pipe', 'pipe', 'pipe']
      });
      
      let stdout = '';
      let stderr = '';
      
      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      child.on('close', (code) => {
        if (code === 0) {
          resolve(stdout.trim());
        } else {
          reject(new Error(stderr.trim() || `命令退出码：${code}`));
        }
      });
    });
  }

  // 记录日志
  log(message) {
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] ${message}\n`;
    
    fs.appendFileSync(this.logPath, logLine);
    
    if (this.verbose) {
      console.log(logLine.trim());
    }
  }
}

module.exports = { BackupScheduler };
