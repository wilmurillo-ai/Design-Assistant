#!/usr/bin/env node
/**
 * 微信发送文件脚本
 * 用法：./send-file.js <user-id> <file-path> [description]
 */

const { execSync } = require('child_process');
const fs = require('fs');

// 配置
const CHANNEL = process.env.WEIXIN_CHANNEL || 'openclaw-weixin';
const ACCOUNT = process.env.WEIXIN_ACCOUNT || 'd72d5b576646-im-bot';

function printUsage() {
  console.log(`
🦆 微信发文件脚本

用法：
  ./send-file.js <user-id> <file-path> [description]

参数：
  user-id      目标用户 ID
  file-path    文件路径
  description  文件说明（可选）

支持的文件类型：
  - PDF 文档
  - Word 文档 (.doc, .docx)
  - Excel 表格 (.xls, .xlsx)
  - ZIP 压缩包
  - 其他常见格式

文件大小限制：20MB

示例：
  ./send-file.js o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat ./report.pdf "月度报告"
  ./send-file.js o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat ./data.xlsx "销售数据"
`);
}

function validateFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.error(`❌ 文件不存在：${filePath}`);
    return false;
  }
  
  const stats = fs.statSync(filePath);
  const maxSize = 20 * 1024 * 1024; // 20MB
  
  if (stats.size > maxSize) {
    console.error(`❌ 文件过大：${(stats.size / 1024 / 1024).toFixed(2)}MB（最大 20MB）`);
    return false;
  }
  
  return true;
}

function sendFile(userId, filePath, description = '') {
  const cmd = `openclaw message send \\
    --channel ${CHANNEL} \\
    --account ${ACCOUNT} \\
    --target ${userId} \\
    --media ${filePath} \\
    --message "${description}"`;
  
  console.log(`📤 发送文件到：${userId}`);
  console.log(`📁 文件路径：${filePath}`);
  console.log(`📝 说明：${description || '(无)'}`);
  console.log('');
  
  try {
    execSync(cmd, { encoding: 'utf8', stdio: 'inherit' });
    console.log('✅ 发送成功！');
    return true;
  } catch (error) {
    console.error('❌ 发送失败');
    console.error(error.message);
    return false;
  }
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2 || args.includes('-h') || args.includes('--help')) {
    printUsage();
    process.exit(args.includes('-h') || args.includes('--help') ? 0 : 1);
  }
  
  const [userId, filePath, ...descParts] = args;
  const description = descParts.join(' ');
  
  if (!validateFile(filePath)) {
    process.exit(1);
  }
  
  const success = sendFile(userId, filePath, description);
  process.exit(success ? 0 : 1);
}

main();
