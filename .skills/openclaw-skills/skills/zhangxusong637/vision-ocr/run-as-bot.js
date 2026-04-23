#!/usr/bin/env node

/**
 * vision-ocr 机器人入口
 * 
 * 此脚本用于在 OpenClaw 主 session 中直接运行 vision-ocr，
 * 自动获取当前飞书会话上下文，实现自动发送。
 * 
 * 使用方式：
 *   node run-as-bot.js --image /path/to/image.jpg
 */

const visionOcr = require('./index.js');
const path = require('path');
const os = require('os');

// 从命令行参数获取图片路径
const args = process.argv.slice(2);
const imagePath = args.find(arg => arg.startsWith('--image=') || arg === '--image');
let actualPath = imagePath;

if (imagePath) {
  if (imagePath.startsWith('--image=')) {
    actualPath = imagePath.split('=')[1];
  } else {
    const idx = args.indexOf('--image');
    if (idx >= 0 && args[idx + 1]) {
      actualPath = args[idx + 1];
    }
  }
}

if (!actualPath) {
  console.log('用法：node run-as-bot.js --image /path/to/image.jpg');
  process.exit(1);
}

// 构建 OpenClaw 会话上下文
const context = {
  session: {
    chatId: process.env.OPENCLAW_CHAT_ID || 'chat_placeholder',
    senderId: process.env.OPENCLAW_SENDER_ID || 'sender_placeholder',
    isGroup: (process.env.OPENCLAW_IS_GROUP || 'false') === 'true'
  },
  message: {
    text: `识别图片 ${actualPath}`
  },
  replyText: async (msg) => {
    console.log('📤 回复消息:', msg);
  }
};

console.log('🤖 使用机器人模式运行 vision-ocr...');
console.log('会话上下文:', context.session);

visionOcr.run(context)
  .then(() => {
    console.log('✅ 处理完成');
    process.exit(0);
  })
  .catch(error => {
    console.error('❌ 处理失败:', error.message);
    process.exit(1);
  });
