#!/usr/bin/env node
/**
 * Agent Session 隔离修复脚本 - 完整版
 * 确保每个 agent 有独立的 session 存储
 */

const fs = require('fs');
const path = require('path');

const BASE_DIR = '/Users/godspeed/.openclaw';

const AGENTS = [
  {
    id: 'dawang',
    name: '大汪',
    workspace: `${BASE_DIR}/workspaces/dawang`,
    stateDir: `${BASE_DIR}/agents/dawang`,
    agentDir: `${BASE_DIR}/agents/dawang/agent`
  },
  {
    id: 'erwang',
    name: '二汪',
    workspace: `${BASE_DIR}/workspaces/erwang`,
    stateDir: `${BASE_DIR}/agents/erwang`,
    agentDir: `${BASE_DIR}/agents/erwang/agent`
  },
  {
    id: 'wangwang',
    name: '汪汪',
    workspace: `${BASE_DIR}/workspaces/wangwang`,
    stateDir: `${BASE_DIR}/agents/wangwang`,
    agentDir: `${BASE_DIR}/agents/wangwang/agent`
  }
];

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`  📁 创建目录: ${dir}`);
  }
}

function createSessionsJson(agent) {
  const sessionsDir = path.join(agent.stateDir, 'sessions');
  ensureDir(sessionsDir);

  const sessionsJsonPath = path.join(sessionsDir, 'sessions.json');

  // 如果已经存在，保留现有内容
  if (fs.existsSync(sessionsJsonPath)) {
    console.log(`  ✅ ${agent.name} 已有 sessions.json`);
    return;
  }

  // 创建空的 sessions.json
  const emptySessions = {};
  fs.writeFileSync(sessionsJsonPath, JSON.stringify(emptySessions, null, 2), 'utf8');
  console.log(`  ✅ 创建 ${agent.name} 的 sessions.json`);

  // 创建 .gitignore
  const gitignorePath = path.join(sessionsDir, '.gitignore');
  if (!fs.existsSync(gitignorePath)) {
    fs.writeFileSync(gitignorePath, '*.jsonl\nsessions.json\n', 'utf8');
  }
}

function createAgentDir(agent) {
  // 确保 agentDir 存在
  ensureDir(agent.agentDir);

  // 创建必要的配置文件
  const files = ['auth-profiles.json', 'models.json'];
  for (const file of files) {
    const filePath = path.join(agent.agentDir, file);
    if (!fs.existsSync(filePath)) {
      // 从 wangwang 复制默认配置
      const wangwangPath = path.join(BASE_DIR, 'agents/wangwang/agent', file);
      if (fs.existsSync(wangwangPath)) {
        const content = fs.readFileSync(wangwangPath, 'utf8');
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`  📄 复制 ${file}`);
      }
    }
  }

  // 创建 skills 软链接（如果不存在）
  const skillsLink = path.join(agent.agentDir, 'skills');
  if (!fs.existsSync(skillsLink)) {
    const skillsTarget = path.join(agent.stateDir, 'skills');
    if (fs.existsSync(skillsTarget)) {
      fs.symlinkSync(skillsTarget, skillsLink);
      console.log(`  🔗 创建 skills 软链接`);
    }
  }
}

function updateAgentJson(agent) {
  const agentJsonPath = path.join(agent.stateDir, 'agent.json');

  if (!fs.existsSync(agentJsonPath)) {
    console.log(`  ⚠️ ${agentJsonPath} 不存在，跳过`);
    return;
  }

  const config = JSON.parse(fs.readFileSync(agentJsonPath, 'utf8'));

  // 移除 parentAgent
  if (config.parentAgent) {
    delete config.parentAgent;
    console.log(`  🔄 移除 parentAgent`);
  }

  // 添加独立配置
  config.independent = true;
  config.stateDir = agent.stateDir;
  config.agentDir = agent.agentDir;

  fs.writeFileSync(agentJsonPath, JSON.stringify(config, null, 2), 'utf8');
  console.log(`  ✅ 更新 agent.json`);
}

function createEnvFile(agent) {
  const envPath = path.join(agent.stateDir, '.env');

  const envContent = `# ${agent.name} Environment Configuration
OPENCLAW_STATE_DIR=${agent.stateDir}
OPENCLAW_AGENT_DIR=${agent.agentDir}
OPENCLAW_WORKSPACE=${agent.workspace}
`;

  fs.writeFileSync(envPath, envContent, 'utf8');
  console.log(`  ✅ 创建 .env 文件`);
}

async function main() {
  console.log('='.repeat(60));
  console.log('🔧 Agent Session 隔离修复 - 完整版');
  console.log('='.repeat(60));

  for (const agent of AGENTS) {
    console.log(`\n📦 ${agent.name} (${agent.id}):`);

    // 1. 创建 sessions 目录和文件
    createSessionsJson(agent);

    // 2. 创建 agent 目录结构
    createAgentDir(agent);

    // 3. 更新 agent.json
    updateAgentJson(agent);

    // 4. 创建 .env 文件
    createEnvFile(agent);
  }

  console.log('\n' + '='.repeat(60));
  console.log('✅ 修复完成！');
  console.log('');
  console.log('每个 agent 现在拥有:');
  console.log('  • 独立的 sessions 目录');
  console.log('  • 独立的 agent 配置');
  console.log('  • 独立的 state 存储');
  console.log('');
  console.log('注意: 需要重启 OpenClaw Gateway 使更改生效');
  console.log('  openclaw gateway restart');
  console.log('='.repeat(60));
}

main().catch(console.error);
