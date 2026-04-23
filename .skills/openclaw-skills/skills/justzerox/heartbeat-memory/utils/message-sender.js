#!/usr/bin/env node

/**
 * message-sender.js - 消息发送工具（工具调用模式）
 * 
 * 直接使用 message 工具发送通知，不依赖 CLI 命令。
 */

// 尝试导入 OpenClaw 工具
let message;
try {
  const openclaw = require('openclaw');
  message = openclaw.message;
  console.log('✅ message 工具可用');
} catch (error) {
  console.log('⚠️  message 工具不可用');
}

/**
 * 发送通知消息
 * @param {Object} options - 选项
 * @param {string} options.target - 目标用户 ID
 * @param {string} options.message - 消息内容
 */
async function send(options) {
  const { target, message: msg } = options;
  
  if (!message) {
    console.error('⚠️  message 工具不可用，无法发送通知');
    return false;
  }
  
  try {
    await message({
      action: 'send',
      target: target,
      message: msg
    });
    
    console.log('✅ 通知已发送');
    return true;
  } catch (error) {
    console.error('⚠️  发送通知失败:', error.message);
    return false;
  }
}

module.exports = {
  send
};
