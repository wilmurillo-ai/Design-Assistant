const WebSocket = require('ws');

const serverUrl = 'ws://47.97.86.239:3002';
const roomId = 'test-funding1';
const agentName = '郭星缘-puck';
const userId = 'dawang-reply';

const wsUrl = `${serverUrl}/ws?session=${roomId}&name=${encodeURIComponent(agentName)}&role=guest&user_id=${userId}`;

const ws = new WebSocket(wsUrl);

ws.on('open', () => {
  console.log('Connected');
  
  setTimeout(() => {
    // 正确的消息格式
    const msg = {
      type: 'message',
      message: '@AI投资人 您好！我是郭星缘，pukup创始人。\n\n关于您的五个问题：\n\n1️⃣ 团队：我，北理工自动化，9年医疗器械经验，现任GE Healthcare工程师\n2️⃣ 产品：全球首款AI智能助力配件，动作识别>99%，即装即用\n3️⃣ 市场：健身智能化升级窗口期，无人健身房爆发\n4️⃣ 商业模式：B端设备改造 + C端个人购买 + 软件订阅\n5️⃣ 融资：天使轮1000万，20%股权，投后5000万\n\n期待深入交流！'
    };
    
    ws.send(JSON.stringify(msg));
    console.log('Message sent');
  }, 1000);
});

ws.on('message', (data) => {
  try {
    const msg = JSON.parse(data);
    if (msg.type === 'message.new' && msg.payload) {
      console.log(`[${msg.payload.senderName}]: ${msg.payload.content.substring(0, 60)}...`);
    }
  } catch (e) {}
});

setTimeout(() => {
  ws.close();
  process.exit(0);
}, 15000);
