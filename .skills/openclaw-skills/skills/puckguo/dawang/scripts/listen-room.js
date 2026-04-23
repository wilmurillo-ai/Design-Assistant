const WebSocket = require('ws');

const serverUrl = 'ws://47.97.86.239:3002';
const roomId = 'test-funding1';
const agentName = '郭星缘-监听';
const userId = 'dawang-listen';

const wsUrl = `${serverUrl}/ws?session=${roomId}&name=${encodeURIComponent(agentName)}&role=guest&user_id=${userId}`;

const ws = new WebSocket(wsUrl);

ws.on('open', () => {
  console.log('Listening to test-funding1...\n');
});

ws.on('message', (data) => {
  try {
    const msg = JSON.parse(data);
    if (msg.type === 'message.new' && msg.payload) {
      const { senderName, content } = msg.payload;
      console.log(`[${senderName}]: ${content}`);
      console.log('---');
    }
  } catch (e) {}
});

// 监听60秒
setTimeout(() => {
  ws.close();
  process.exit(0);
}, 60000);
