#!/usr/bin/env node

/**
 * OpenClaw 环境变量和配置读取
 * 获取工作区路径、状态目录等系统配置
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class OpenClawEnv {
  constructor() {
    this.home = null;
    this.stateDir = null;
    this.configPath = null;
    this.workspace = null;
    this.config = null;
  }

  // 初始化，读取所有配置
  async init() {
    // 1. OPENCLAW_HOME (最高优先级)
    this.home = process.env.OPENCLAW_HOME || this.expandTilde('~/.openclaw');

    // 2. OPENCLAW_STATE_DIR
    this.stateDir = process.env.OPENCLAW_STATE_DIR || path.join(this.home, 'state');

    // 3. OPENCLAW_CONFIG_PATH
    this.configPath = process.env.OPENCLAW_CONFIG_PATH || path.join(this.home, 'openclaw.json');

    // 4. 读取配置文件
    this.config = await this.loadConfig();

    // 5. 获取工作区路径
    this.workspace = this.getWorkspacePath();

    return this;
  }

  // 加载配置文件
  async loadConfig() {
    if (!fs.existsSync(this.configPath)) {
      console.warn(`⚠️  配置文件不存在：${this.configPath}`);
      return null;
    }

    try {
      const content = fs.readFileSync(this.configPath, 'utf8');
      return JSON.parse(content);
    } catch (err) {
      console.warn(`⚠️  读取配置文件失败：${err.message}`);
      return null;
    }
  }

  // 获取工作区路径
  getWorkspacePath() {
    // 优先使用配置文件中的设置
    if (this.config && this.config.agent && this.config.agent.workspace) {
      return this.expandTilde(this.config.agent.workspace);
    }

    // 默认路径
    const profile = process.env.OPENCLAW_PROFILE;
    if (profile && profile !== 'default') {
      return path.join(this.home, `workspace-${profile}`);
    }

    return path.join(this.home, 'workspace');
  }

  // 展开 ~ 路径
  expandTilde(filePath) {
    if (filePath.startsWith('~/')) {
      return path.join(os.homedir(), filePath.slice(2));
    }
    if (filePath === '~') {
      return os.homedir();
    }
    return filePath;
  }

  // 获取工作区内的文件路径
  getWorkspaceFile(relativePath) {
    return path.join(this.workspace, relativePath);
  }

  // 获取状态目录内的文件路径
  getStateFile(relativePath) {
    return path.join(this.stateDir, relativePath);
  }

  // 打印配置信息
  printConfig() {
    console.log('\n📋 OpenClaw 环境配置\n');
    console.log(`   OPENCLAW_HOME: ${this.home}`);
    console.log(`   OPENCLAW_STATE_DIR: ${this.stateDir}`);
    console.log(`   OPENCLAW_CONFIG_PATH: ${this.configPath}`);
    console.log(`   工作区路径：${this.workspace}`);
    
    if (this.config && this.config.agent) {
      console.log(`   agent.workspace: ${this.config.agent.workspace || '默认'}`);
    }
    
    console.log('');
  }
}

// 单例模式
let instance = null;

async function getOpenClawEnv() {
  if (!instance) {
    instance = new OpenClawEnv();
    await instance.init();
  }
  return instance;
}

module.exports = { OpenClawEnv, getOpenClawEnv };
