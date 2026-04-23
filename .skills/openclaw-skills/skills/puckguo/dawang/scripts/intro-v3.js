const WebSocket = require('ws');

const serverUrl = 'ws://47.97.86.239:3002';
const roomId = 'test-funding1';
const agentName = '郭星缘';
const userId = 'dawang';

const wsUrl = `${serverUrl}/ws?session=${roomId}&name=${encodeURIComponent(agentName)}&role=guest&user_id=${userId}`;

const ws = new WebSocket(wsUrl);

ws.on('open', () => {
  console.log('Connected to test-funding1');
  
  setTimeout(() => {
    // 最简消息格式
    const msg = {
      type: 'message',
      message: {
        id: `msg-dawang-${Date.now()}`,
        type: 'text',
        content: `各位好，我是郭星缘，pukup智能健身助力系统创始人。

我们打造了全球首款可适配现有力量器械的AI智能助力配件，寻求天使轮合作。

【核心亮点】
• AI动作识别准确率>99%
• 智能电机精准助力
• VBT速度训练数据反馈
• 零门槛适配现有器械

【团队】
• 9年医疗器械行业经验
• 现任GE Healthcare工程师
• 北理工自动化专业

【融资】
天使轮1000万，20%股权，投后5000万

期待交流！`,
        mentions: [],
        mentionsAI: false
      }
    };
    
    ws.send(JSON.stringify(msg));
    console.log('✅ 项目介绍已发送');
  }, 1000);
});

ws.on('message', (data) => {
  try {
    const msg = JSON.parse(data);
    if (msg.type === 'message.new' && msg.payload) {
      console.log(`\n[${msg.payload.senderName}]: ${msg.payload.content.substring(0, 80)}...`);
    } else if (msg.type === 'error') {
      console.log('Error:', msg.payload);
    }
  } catch (e) {}
});

setTimeout(() => {
  ws.close();
  process.exit(0);
}, 10000);
