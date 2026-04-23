#!/usr/bin/env node
/**
 * 飞书子 Agent 配置更新工具
 * 自动读取和修改 openclaw.json，无需用户手动编辑
 * 
 * 用法：
 * node update-config.js --agent-id xxx --agent-name xxx --app-id xxx --app-secret xxx
 */

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG_FILE = '/home/gem/workspace/agent/openclaw.json';
const WORKSPACE_BASE = '/home/gem/workspace/agent/agents';

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1];
      params[key] = value;
      i++;
    }
  }
  
  return params;
}

// 验证必填参数
function validateParams(params) {
  const required = ['agent-id', 'agent-name', 'app-id', 'app-secret'];
  const missing = required.filter(key => !params[key]);
  
  if (missing.length > 0) {
    console.error(`❌ 缺少必填参数：${missing.join(', ')}`);
    console.error('');
    console.error('必填参数：');
    console.error('  --agent-id      Agent 的唯一标识');
    console.error('  --agent-name    Agent 的显示名称');
    console.error('  --app-id        飞书应用的 App ID');
    console.error('  --app-secret    飞书应用的 App Secret');
    process.exit(1);
  }
  
  // 验证 Agent ID 格式
  if (!/^[a-z0-9-]+$/.test(params['agent-id'])) {
    console.error('❌ Agent ID 格式错误，只能包含小写字母、数字和短横线');
    process.exit(1);
  }
  
  // 验证 App ID 格式
  if (!/^cli_[a-z0-9]+$/.test(params['app-id'])) {
    console.error('❌ App ID 格式错误，应该是 cli_ 开头');
    process.exit(1);
  }
}

// 备份配置文件
function backupConfig(configPath) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupPath = `${configPath}.bak.${timestamp}`;
  fs.copyFileSync(configPath, backupPath);
  console.log(`✅ 配置已备份：${backupPath}`);
  return backupPath;
}

// 读取配置文件
function readConfig(configPath) {
  const content = fs.readFileSync(configPath, 'utf8');
  return JSON.parse(content);
}

// 写入配置文件
function writeConfig(configPath, config) {
  const content = JSON.stringify(config, null, 2);
  fs.writeFileSync(configPath, content, 'utf8');
}

// 更新配置
function updateConfig(config, params) {
  const agentId = params['agent-id'];
  const agentName = params['agent-name'];
  const appId = params['app-id'];
  const appSecret = params['app-secret'];
  const model = params['model'] || 'miaoda/glm-5';
  
  const agentDir = path.join(WORKSPACE_BASE, agentId);
  const workspace = path.join(agentDir, 'workspace');
  const agentDirPath = path.join(agentDir, 'agent');
  
  // 1. 添加 agent 到 agents.list
  if (!config.agents) {
    config.agents = { list: [] };
  }
  if (!config.agents.list) {
    config.agents.list = [];
  }
  
  const existingAgent = config.agents.list.find(a => a.id === agentId);
  if (existingAgent) {
    console.log(`⚠️  Agent ${agentId} 已存在，将更新配置`);
    Object.assign(existingAgent, {
      name: agentName,
      workspace,
      agentDir: agentDirPath,
      model
    });
  } else {
    config.agents.list.push({
      id: agentId,
      name: agentName,
      workspace,
      agentDir: agentDirPath,
      model
    });
  }
  console.log(`✅ 已添加 agent 到 agents.list`);
  
  // 2. 添加飞书账户
  if (!config.channels) {
    config.channels = {};
  }
  if (!config.channels.feishu) {
    config.channels.feishu = {};
  }
  if (!config.channels.feishu.accounts) {
    config.channels.feishu.accounts = {};
  }
  
  config.channels.feishu.accounts[agentId] = {
    appId,
    appSecret,
    name: agentName,
    streamingCard: true,
    groups: {
      '*': {
        enabled: true
      }
    }
  };
  console.log(`✅ 已添加飞书账户到 channels.feishu.accounts`);
  
  // 3. 添加 binding
  if (!config.bindings) {
    config.bindings = [];
  }
  
  const existingBinding = config.bindings.find(
    b => b.agentId === agentId && b.match?.channel === 'feishu'
  );
  if (existingBinding) {
    console.log(`⚠️  Binding 已存在，将更新配置`);
    Object.assign(existingBinding, {
      agentId,
      match: {
        channel: 'feishu',
        accountId: agentId
      }
    });
  } else {
    config.bindings.push({
      agentId,
      match: {
        channel: 'feishu',
        accountId: agentId
      }
    });
  }
  console.log(`✅ 已添加路由绑定到 bindings`);
  
  // 4. 更新 agentToAgent.allow
  if (!config.tools) {
    config.tools = {};
  }
  if (!config.tools.agentToAgent) {
    config.tools.agentToAgent = { enabled: true, allow: [] };
  }
  if (!config.tools.agentToAgent.allow) {
    config.tools.agentToAgent.allow = [];
  }
  
  if (!config.tools.agentToAgent.allow.includes(agentId)) {
    config.tools.agentToAgent.allow.push(agentId);
  }
  console.log(`✅ 已更新 agentToAgent 允许列表`);
  
  // 5. 确保 session.dmScope 设置正确
  if (!config.session) {
    config.session = {};
  }
  if (!config.session.dmScope) {
    config.session.dmScope = 'per-channel-peer';
    console.log(`✅ 已设置 session.dmScope`);
  }
  
  return config;
}

// 主函数
function main() {
  console.log('');
  console.log('==========================================');
  console.log('🤖 飞书子 Agent 配置更新工具');
  console.log('==========================================');
  console.log('');
  
  const params = parseArgs();
  validateParams(params);
  
  console.log('配置信息：');
  console.log(`  Agent ID: ${params['agent-id']}`);
  console.log(`  Agent 名称：${params['agent-name']}`);
  console.log(`  飞书 App ID: ${params['app-id']}`);
  console.log(`  模型：${params['model'] || 'miaoda/glm-5'}`);
  console.log('');
  
  // 检查配置文件是否存在
  if (!fs.existsSync(CONFIG_FILE)) {
    console.error(`❌ 未找到配置文件：${CONFIG_FILE}`);
    process.exit(1);
  }
  
  // 备份配置
  backupConfig(CONFIG_FILE);
  
  // 读取配置
  console.log('正在读取现有配置...');
  let config = readConfig(CONFIG_FILE);
  
  // 更新配置
  console.log('正在更新配置...');
  config = updateConfig(config, params);
  
  // 写入配置
  writeConfig(CONFIG_FILE, config);
  console.log('✅ 配置已保存到：' + CONFIG_FILE);
  
  console.log('');
  console.log('==========================================');
  console.log('✅ 配置更新完成！');
  console.log('==========================================');
  console.log('');
  console.log('下一步：重启 Gateway 使配置生效');
  console.log('  sh scripts/restart.sh');
  console.log('');
}

main();
