#!/usr/bin/env node
/**
 * 导出 contextToken 工具
 * 用于查看、导出、清理已保存的微信 contextToken
 */

const fs = require('fs');
const path = require('path');

const TOKEN_DIR = path.join(process.env.HOME || '~', '.openclaw/openclaw-weixin/context-tokens');

function printUsage() {
  console.log(`
🦆 contextToken 导出工具

用法：
  ./export-context-token.js [command] [options]

命令：
  list              列出所有已保存的 token
  show <user-id>    显示指定用户的 token
  export <user-id>  导出指定用户的 token（JSON 格式）
  clean             清理过期 token（30 天以上）
  help              显示帮助信息

示例：
  ./export-context-token.js list
  ./export-context-token.js show o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat
  ./export-context-token.js export o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat
  ./export-context-token.js clean
`);
}

function getTokenFile(userId) {
  const safeUser = userId.replace(/[@:]/g, '_');
  // 查找匹配的 token 文件
  const files = fs.readdirSync(TOKEN_DIR);
  const targetFile = files.find(f => f.includes(safeUser));
  return targetFile ? path.join(TOKEN_DIR, targetFile) : null;
}

function listTokens() {
  console.log('📋 已保存的 contextToken：\n');
  
  if (!fs.existsSync(TOKEN_DIR)) {
    console.log('  (暂无 token 文件)');
    return;
  }
  
  const files = fs.readdirSync(TOKEN_DIR);
  if (files.length === 0) {
    console.log('  (暂无 token 文件)');
    return;
  }
  
  console.log('  文件'.padEnd(50) + '保存时间');
  console.log('  ' + '='.repeat(70));
  
  files.forEach(file => {
    const filePath = path.join(TOKEN_DIR, file);
    const stats = fs.statSync(filePath);
    const mtime = new Date(stats.mtime).toLocaleString('zh-CN');
    console.log(`  ${file.padEnd(48)} ${mtime}`);
  });
}

function showToken(userId) {
  const filePath = getTokenFile(userId);
  
  if (!filePath) {
    console.error(`❌ 未找到用户 ${userId} 的 token`);
    return false;
  }
  
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  
  console.log('\n📄 Token 信息：\n');
  console.log(`  账号 ID:   ${data.accountId}`);
  console.log(`  用户 ID:   ${data.userId}`);
  console.log(`  Token:     ${data.token.substring(0, 20)}...${data.token.substring(data.token.length - 20)}`);
  console.log(`  保存时间： ${new Date(data.savedAt).toLocaleString('zh-CN')}`);
  console.log('');
  
  return true;
}

function exportToken(userId) {
  const filePath = getTokenFile(userId);
  
  if (!filePath) {
    console.error(`❌ 未找到用户 ${userId} 的 token`);
    return false;
  }
  
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  console.log(JSON.stringify(data, null, 2));
  
  return true;
}

function cleanTokens() {
  console.log('🧹 清理过期 token（30 天以上）...\n');
  
  if (!fs.existsSync(TOKEN_DIR)) {
    console.log('  (暂无 token 文件)');
    return;
  }
  
  const files = fs.readdirSync(TOKEN_DIR);
  const now = Date.now();
  const thirtyDays = 30 * 24 * 60 * 60 * 1000;
  let cleaned = 0;
  
  files.forEach(file => {
    const filePath = path.join(TOKEN_DIR, file);
    const stats = fs.statSync(filePath);
    
    if (now - stats.mtimeMs > thirtyDays) {
      fs.unlinkSync(filePath);
      console.log(`  ✅ 已删除：${file}`);
      cleaned++;
    }
  });
  
  console.log(`\n  清理完成，共删除 ${cleaned} 个过期 token`);
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === 'help' || command === '-h' || command === '--help') {
    printUsage();
    process.exit(0);
  }
  
  switch (command) {
    case 'list':
      listTokens();
      break;
      
    case 'show':
      if (!args[1]) {
        console.error('❌ 请提供用户 ID');
        printUsage();
        process.exit(1);
      }
      showToken(args[1]);
      break;
      
    case 'export':
      if (!args[1]) {
        console.error('❌ 请提供用户 ID');
        printUsage();
        process.exit(1);
      }
      exportToken(args[1]);
      break;
      
    case 'clean':
      cleanTokens();
      break;
      
    default:
      console.error(`❌ 未知命令：${command}`);
      printUsage();
      process.exit(1);
  }
}

main();
