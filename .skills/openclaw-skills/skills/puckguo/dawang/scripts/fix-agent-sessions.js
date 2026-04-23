#!/usr/bin/env node
/**
 * Agent Session 隔离修复脚本
 * 让每个 agent 的对话存储在自己的 session 目录中
 */

const fs = require('fs');
const path = require('path');

// Agent 配置
const AGENTS = [
  {
    id: 'dawang',
    name: '大汪',
    workspace: '/Users/godspeed/.openclaw/workspaces/dawang',
    stateDir: '/Users/godspeed/.openclaw/agents/dawang'
  },
  {
    id: 'erwang',
    name: '二汪',
    workspace: '/Users/godspeed/.openclaw/workspaces/erwang',
    stateDir: '/Users/godspeed/.openclaw/agents/erwang'
  },
  {
    id: 'wangwang',
    name: '汪汪',
    workspace: '/Users/godspeed/.openclaw/workspaces/wangwang',
    stateDir: '/Users/godspeed/.openclaw/agents/wangwang'
  }
];

class SessionIsolationFix {
  constructor() {
    this.wangwangSessionsDir = '/Users/godspeed/.openclaw/agents/wangwang/agents/wangwang/sessions';
  }

  async fix() {
    console.log('='.repeat(60));
    console.log('🔧 Agent Session 隔离修复');
    console.log('='.repeat(60));

    // 1. 读取 wangwang 的 sessions.json
    const wangwangSessions = this.loadWangwangSessions();
    if (!wangwangSessions) {
      console.error('❌ 无法读取 wangwang 的 sessions.json');
      return;
    }

    // 2. 为每个 agent 创建独立的 session 存储
    for (const agent of AGENTS) {
      await this.fixAgentSessions(agent, wangwangSessions);
    }

    // 3. 更新 agent.json 配置，移除 parentAgent 依赖
    await this.updateAgentConfigs();

    console.log('\n✅ 修复完成！');
    console.log('每个 agent 现在有自己的独立 session 存储。');
  }

  loadWangwangSessions() {
    try {
      const sessionsJsonPath = path.join(this.wangwangSessionsDir, 'sessions.json');
      if (!fs.existsSync(sessionsJsonPath)) {
        console.error(`❌ 文件不存在: ${sessionsJsonPath}`);
        return null;
      }
      const content = fs.readFileSync(sessionsJsonPath, 'utf8');
      return JSON.parse(content);
    } catch (e) {
      console.error('❌ 读取 sessions.json 失败:', e.message);
      return null;
    }
  }

  async fixAgentSessions(agent, wangwangSessions) {
    console.log(`\n📦 处理 ${agent.name} (${agent.id})...`);

    const agentSessionsDir = path.join(agent.stateDir, 'sessions');

    // 确保 sessions 目录存在
    if (!fs.existsSync(agentSessionsDir)) {
      fs.mkdirSync(agentSessionsDir, { recursive: true });
      console.log(`  ✅ 创建目录: ${agentSessionsDir}`);
    }

    // 创建该 agent 的 sessions.json
    const agentSessions = {};

    for (const [sessionKey, sessionData] of Object.entries(wangwangSessions)) {
      // 检查这个 session 是否属于当前 agent
      if (this.isSessionForAgent(sessionKey, sessionData, agent)) {
        // 复制 session 数据
        const newSessionData = { ...sessionData };

        // 更新 session 文件路径
        if (newSessionData.sessionFile) {
          const oldSessionFile = newSessionData.sessionFile;
          const sessionFileName = path.basename(oldSessionFile);
          const newSessionFile = path.join(agentSessionsDir, sessionFileName);

          // 复制 session 文件内容
          if (fs.existsSync(oldSessionFile)) {
            const content = fs.readFileSync(oldSessionFile, 'utf8');
            fs.writeFileSync(newSessionFile, content, 'utf8');
            newSessionData.sessionFile = newSessionFile;
            console.log(`  📄 复制 session: ${sessionFileName}`);
          }
        }

        // 更新 workspaceDir
        if (newSessionData.skillsSnapshot?.systemPromptReport?.workspaceDir) {
          newSessionData.skillsSnapshot.systemPromptReport.workspaceDir = agent.workspace;
        }

        // 修改 sessionKey 以包含 agent ID
        const newSessionKey = sessionKey.replace(/^agent:/, `agent:${agent.id}:`);
        agentSessions[newSessionKey] = newSessionData;
      }
    }

    // 保存该 agent 的 sessions.json
    const sessionsJsonPath = path.join(agentSessionsDir, 'sessions.json');
    fs.writeFileSync(sessionsJsonPath, JSON.stringify(agentSessions, null, 2), 'utf8');
    console.log(`  ✅ 创建 sessions.json: ${Object.keys(agentSessions).length} 个 session`);

    // 创建 .gitignore 防止提交敏感数据
    const gitignorePath = path.join(agentSessionsDir, '.gitignore');
    if (!fs.existsSync(gitignorePath)) {
      fs.writeFileSync(gitignorePath, '*.jsonl\nsessions.json\n', 'utf8');
    }
  }

  isSessionForAgent(sessionKey, sessionData, agent) {
    // 方法1: 检查 sessionKey 中是否包含 agent ID
    if (sessionKey.includes(`:${agent.id}:`) || sessionKey.startsWith(`${agent.id}:`)) {
      return true;
    }

    // 方法2: 检查 workspaceDir
    if (sessionData.skillsSnapshot?.systemPromptReport?.workspaceDir) {
      const workspaceDir = sessionData.skillsSnapshot.systemPromptReport.workspaceDir;
      if (workspaceDir.includes(agent.id)) {
        return true;
      }
    }

    // 方法3: 对于 wangwang，检查是否是其他 agent 的 session
    if (agent.id === 'wangwang') {
      // 如果 session 属于 dawang 或 erwang，则不属于 wangwang
      for (const otherAgent of AGENTS) {
        if (otherAgent.id !== 'wangwang' && this.isSessionForAgent(sessionKey, sessionData, otherAgent)) {
          return false;
        }
      }
      return true;
    }

    return false;
  }

  async updateAgentConfigs() {
    console.log('\n📝 更新 Agent 配置...');

    for (const agent of AGENTS) {
      if (agent.id === 'wangwang') continue;

      const agentJsonPath = path.join(agent.stateDir, 'agent.json');
      if (!fs.existsSync(agentJsonPath)) {
        console.log(`  ⚠️ 配置文件不存在: ${agentJsonPath}`);
        continue;
      }

      const config = JSON.parse(fs.readFileSync(agentJsonPath, 'utf8'));

      // 移除 parentAgent，让每个 agent 独立
      if (config.parentAgent) {
        delete config.parentAgent;
        console.log(`  🔄 移除 ${agent.id} 的 parentAgent 配置`);
      }

      // 确保有独立的配置
      config.independent = true;
      config.sessionsDir = path.join(agent.stateDir, 'sessions');

      fs.writeFileSync(agentJsonPath, JSON.stringify(config, null, 2), 'utf8');
      console.log(`  ✅ 更新 ${agent.id} 配置`);
    }
  }
}

// 运行修复
const fixer = new SessionIsolationFix();
fixer.fix().catch(console.error);
