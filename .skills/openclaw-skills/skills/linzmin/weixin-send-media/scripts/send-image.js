#!/usr/bin/env node
/**
 * 微信发送图片脚本
 * 用法：./send-image.js <user-id> <image-path> [caption]
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 配置（从环境变量或默认值读取）
const CHANNEL = process.env.WEIXIN_CHANNEL || 'openclaw-weixin';
const ACCOUNT = process.env.WEIXIN_ACCOUNT || 'd72d5b576646-im-bot';

function printUsage() {
  console.log(`
🦆 微信发图片脚本

用法：
  ./send-image.js <user-id> <image-path> [caption]

参数：
  user-id     目标用户 ID（如：o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat）
  image-path  图片路径（本地路径或 URL）
  caption     图片说明（可选）

环境变量：
  WEIXIN_CHANNEL  微信渠道 ID（默认：openclaw-weixin）
  WEIXIN_ACCOUNT  微信账号 ID（默认：d72d5b576646-im-bot）

示例：
  ./send-image.js o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat ./qr.png "扫码绑定"
  ./send-image.js o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat https://example.com/img.jpg "网络图片"
`);
}

function validateImage(imagePath) {
  // 如果是 URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return true;
  }
  
  // 如果是本地文件，检查是否存在
  if (!fs.existsSync(imagePath)) {
    console.error(`❌ 图片文件不存在：${imagePath}`);
    return false;
  }
  
  // 检查文件大小（微信限制 20MB）
  const stats = fs.statSync(imagePath);
  const maxSize = 20 * 1024 * 1024; // 20MB
  if (stats.size > maxSize) {
    console.error(`❌ 图片文件过大：${(stats.size / 1024 / 1024).toFixed(2)}MB（最大 20MB）`);
    return false;
  }
  
  return true;
}

function sendImage(userId, imagePath, caption = '') {
  const cmd = `openclaw message send \\
    --channel ${CHANNEL} \\
    --account ${ACCOUNT} \\
    --target ${userId} \\
    --media ${imagePath} \\
    --message "${caption}"`;
  
  console.log(`📤 发送图片到：${userId}`);
  console.log(`📷 图片路径：${imagePath}`);
  console.log(`📝 说明：${caption || '(无)'}`);
  console.log('');
  
  try {
    const output = execSync(cmd, { encoding: 'utf8', stdio: 'inherit' });
    console.log('✅ 发送成功！');
    return true;
  } catch (error) {
    console.error('❌ 发送失败');
    console.error(error.message);
    return false;
  }
}

// 主程序
function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2 || args.includes('-h') || args.includes('--help')) {
    printUsage();
    process.exit(args.includes('-h') || args.includes('--help') ? 0 : 1);
  }
  
  const [userId, imagePath, ...captionParts] = args;
  const caption = captionParts.join(' ');
  
  if (!validateImage(imagePath)) {
    process.exit(1);
  }
  
  const success = sendImage(userId, imagePath, caption);
  process.exit(success ? 0 : 1);
}

main();
