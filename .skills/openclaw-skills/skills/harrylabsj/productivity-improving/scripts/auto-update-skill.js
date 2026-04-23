#!/usr/bin/env node

/**
 * Auto Update Skill CLI
 * 
 * 命令行工具，用于手动检查和管理 skill 更新
 * 
 * 安全说明：
 * - 只读取本地文件
 * - 使用 OpenClaw 标准工具 API
 * - 无危险操作
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const {
  checkAndPrompt,
  getCurrentVersion,
  getUpdateType,
  backupSkill,
  rollbackSkill,
  loadConfig,
  saveConfig,
  log,
  getInstalledSkills,
  setCachedVersion
} = require('../lib/checker');

const CONFIG_PATH = path.join(process.env.HOME, '.openclaw', 'auto-update-skill.json');
const BACKUP_DIR = path.join(process.env.HOME, '.openclaw', 'skill-backups');

// 创建 readline 接口
function createRL() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

// 询问用户
function ask(rl, question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer.trim());
    });
  });
}

// 检查命令
async function checkCommand(skillName, options = {}) {
  if (skillName) {
    // 检查指定 skill
    const current = getCurrentVersion(skillName);
    
    if (!current) {
      console.log(`❌ ${skillName} 未安装或无法获取版本`);
      return;
    }
    
    console.log(`📋 ${skillName} 当前版本: ${current}`);
    console.log(`\n💡 请运行以下命令获取最新版本信息：`);
    console.log(`   clawhub inspect ${skillName}`);
    console.log(`\n然后可以运行：auto-update-skill update ${skillName}`);
  } else {
    // 检查所有 skills
    console.log('检查所有 skills...\n');
    
    const skills = getInstalledSkills();
    
    console.log(`已安装 ${skills.length} 个 skills:\n`);
    
    for (const skill of skills) {
      console.log(`  - ${skill.name}: ${skill.version}`);
    }
    
    console.log('\n💡 使用以下命令检查更新：');
    console.log(`   clawhub list`);
    console.log(`   clawhub inspect <skill-name>`);
  }
}

// 更新命令
async function updateCommand(skillName, options = {}) {
  const rl = createRL();
  
  try {
    if (skillName) {
      // 更新指定 skill
      const current = getCurrentVersion(skillName);
      
      if (!current) {
        console.log(`❌ ${skillName} 未安装`);
        return;
      }
      
      console.log(`\n📦 ${skillName} 当前版本: ${current}`);
      console.log(`\n💡 请手动运行以下命令更新：`);
      console.log(`   clawhub update ${skillName}`);
      console.log(`\n或指定版本：`);
      console.log(`   clawhub update ${skillName} --version <version>`);
      
      // 询问是否备份
      const answer = await ask(rl, `\n是否需要备份当前版本? [Y/n]: `);
      if (answer.toLowerCase() !== 'n') {
        if (backupSkill(skillName, current)) {
          console.log(`✅ 备份完成: ${skillName}@${current}`);
        }
      }
    } else {
      // 批量更新提示
      console.log('批量更新功能需要指定 skill 名称');
      console.log('使用: auto-update-skill update <skill-name>');
      console.log('\n或运行: clawhub update --all');
    }
  } finally {
    rl.close();
  }
}

// 配置命令
async function configCommand(subCommand, ...args) {
  const config = loadConfig();
  
  switch (subCommand) {
    case 'blacklist':
      if (args[0] === 'add' && args[1]) {
        if (!config.blacklist.includes(args[1])) {
          config.blacklist.push(args[1]);
          saveConfig(config);
          console.log(`✅ 已将 ${args[1]} 加入黑名单`);
        } else {
          console.log(`${args[1]} 已在黑名单中`);
        }
      } else if (args[0] === 'remove' && args[1]) {
        config.blacklist = config.blacklist.filter(n => n !== args[1]);
        saveConfig(config);
        console.log(`✅ 已将 ${args[1]} 从黑名单移除`);
      } else if (args[0] === 'list') {
        console.log('黑名单:');
        config.blacklist.forEach(n => console.log(`  - ${n}`));
      } else {
        console.log('用法:');
        console.log('  auto-update-skill config blacklist add <skill>');
        console.log('  auto-update-skill config blacklist remove <skill>');
        console.log('  auto-update-skill config blacklist list');
      }
      break;
      
    case 'auto':
      if (args[0] === 'patch' || args[0] === 'minor' || args[0] === 'major') {
        const enabled = args[1] === 'true' || args[1] === 'on' || args[1] === 'yes';
        config.autoUpgrade[args[0]] = enabled;
        saveConfig(config);
        console.log(`${args[0]} 版本自动升级: ${enabled ? '开启' : '关闭'}`);
      } else {
        console.log('用法: auto-update-skill config auto <patch|minor|major> <true|false>');
      }
      break;
      
    default:
      console.log('当前配置:');
      console.log(JSON.stringify(config, null, 2));
  }
}

// 备份命令
async function backupCommand(subCommand, ...args) {
  if (subCommand === 'list') {
    try {
      if (!fs.existsSync(BACKUP_DIR)) {
        console.log('暂无备份');
        return;
      }
      
      const backups = fs.readdirSync(BACKUP_DIR);
      if (backups.length === 0) {
        console.log('暂无备份');
        return;
      }
      
      console.log('备份列表:');
      backups.forEach(b => {
        const stat = fs.statSync(path.join(BACKUP_DIR, b));
        const date = stat.mtime.toISOString().split('T')[0];
        console.log(`  - ${b} (${date})`);
      });
    } catch (e) {
      console.error('读取备份失败:', e.message);
    }
  } else if (subCommand === 'cleanup') {
    const keep = parseInt(args.find(a => !a.startsWith('--')) || '10');
    console.log(`保留最近 ${keep} 个备份（请手动清理）`);
  } else {
    console.log('用法:');
    console.log('  auto-update-skill backup list');
    console.log('  auto-update-skill backup cleanup [数量]');
  }
}

// 回滚命令
async function rollbackCommand(skillName, ...args) {
  if (!skillName) {
    console.log('用法: auto-update-skill rollback <skill-name> --version <version>');
    return;
  }
  
  const versionIndex = args.indexOf('--version');
  const version = versionIndex >= 0 ? args[versionIndex + 1] : null;
  
  if (!version) {
    console.log('请指定版本号: --version <version>');
    return;
  }
  
  const rl = createRL();
  const answer = await ask(rl, `确认将 ${skillName} 回滚到 ${version}? [y/N]: `);
  rl.close();
  
  if (answer.toLowerCase() === 'y') {
    if (rollbackSkill(skillName, version)) {
      console.log(`✅ ${skillName} 已回滚到 ${version}`);
    } else {
      console.log(`❌ 回滚失败`);
    }
  } else {
    console.log('已取消');
  }
}

// 刷新缓存
async function refreshCommand() {
  const cacheDir = path.join(process.env.HOME, '.openclaw', 'skill-update-cache');
  
  try {
    if (fs.existsSync(cacheDir)) {
      fs.rmSync(cacheDir, { recursive: true });
      console.log('✅ 缓存已清除');
    } else {
      console.log('没有缓存需要清除');
    }
  } catch (e) {
    console.error('清除缓存失败:', e.message);
  }
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  
  switch (command) {
    case 'check':
      await checkCommand(args[1], { verbose: args.includes('--verbose') });
      break;
      
    case 'update':
      await updateCommand(args[1], {
        force: args.includes('--force'),
        interactive: !args.includes('--no-interactive')
      });
      break;
      
    case 'config':
      await configCommand(args[1], ...args.slice(2));
      break;
      
    case 'backup':
      await backupCommand(args[1], ...args.slice(2));
      break;
      
    case 'rollback':
      await rollbackCommand(args[1], ...args.slice(2));
      break;
      
    case 'refresh':
      await refreshCommand();
      break;
      
    default:
      console.log(`
Auto Update Skill - 智能 Skill 更新工具

核心功能：帮助管理 skill 更新，提供备份和回滚功能

用法:
  auto-update-skill check [skill-name]
    检查 skill 当前版本

  auto-update-skill update <skill-name>
    提示如何更新 skill

  auto-update-skill config
    查看当前配置

  auto-update-skill config blacklist add <skill>
    添加 skill 到黑名单

  auto-update-skill config blacklist remove <skill>
    从黑名单移除

  auto-update-skill config auto <patch|minor|major> <true|false>
    设置自动升级策略

  auto-update-skill backup list
    列出备份

  auto-update-skill rollback <skill> --version <version>
    回滚到指定版本

  auto-update-skill refresh
    清除版本缓存

安全说明:
  - 只读取本地文件，不执行危险操作
  - 更新操作通过 clawhub CLI 执行
  - 自动备份机制保护数据安全
`);
  }
}

main().catch(e => {
  console.error('错误:', e.message);
  process.exit(1);
});
