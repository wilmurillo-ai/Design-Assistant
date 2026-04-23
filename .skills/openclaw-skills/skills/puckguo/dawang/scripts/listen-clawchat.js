const WebSocket = require('ws');

const serverUrl = 'ws://47.97.86.239:3002';
const roomId = 'test-funding1';
const agentName = '郭星缘-代理';
const userId = 'dawang';

const wsUrl = `${serverUrl}/ws?session=${roomId}&name=${encodeURIComponent(agentName)}&role=guest&user_id=${userId}`;

const ws = new WebSocket(wsUrl);

ws.on('open', () => {
  console.log('Connected to test-funding1, listening for messages...');
});

ws.on('message', (data) => {
  try {
    const msg = JSON.parse(data);
    
    if (msg.type === 'message.new' && msg.payload) {
      const { senderName, content } = msg.payload;
      console.log(`\n[${senderName}]: ${content}`);
      
      // 保存消息到文件
      const fs = require('fs');
      const logEntry = `[${new Date().toISOString()}] ${senderName}: ${content}\n`;
      fs.appendFileSync('/Users/godspeed/.openclaw/workspaces/dawang/chat-log.txt', logEntry);
    }
  } catch (e) {
    // ignore
  }
});

ws.on('error', (err) => {
  console.error('WebSocket error:', err.message);
});

// 保持运行5分钟
setTimeout(() => {
  ws.close();
  console.log('\nListening ended');
  process.exit(0);
}, 300000);
