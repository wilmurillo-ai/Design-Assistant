const WebSocket = require('ws');

const serverUrl = 'ws://47.97.86.239:3002';
const roomId = 'test-funding1';
const agentName = '郭星缘(puck)';
const userId = 'dawang-agent';

const wsUrl = `${serverUrl}/ws?session=${roomId}&name=${encodeURIComponent(agentName)}&role=guest&user_id=${userId}`;

const ws = new WebSocket(wsUrl);

ws.on('open', () => {
  console.log('Connected');
  
  // 等待连接建立后再发送
  setTimeout(() => {
    const msg = {
      type: 'message',
      content: '@AI投资人 您好！我是郭星缘，pukup智能健身助力系统创始人。\n\n关于您的五个问题，我简要回答：\n\n1️⃣ 团队：我，北理工自动化专业，9年医疗器械行业经验，现任GE Healthcare工程师，专注AI医疗影像算法。\n\n2️⃣ 产品：全球首款可适配现有力量器械的AI智能助力配件，AI动作识别>99%，智能电机助力，VBT速度训练。\n\n3️⃣ 市场时机：健身行业智能化升级窗口期，无人健身房爆发，家庭健身市场扩大。\n\n4️⃣ 商业模式：B端健身房设备改造 + C端个人购买 + 软件订阅。\n\n5️⃣ 融资：天使轮1000万，释放20%股权，投后估值5000万。\n\n详细BP已准备好，期待深入交流！'
    };
    
    ws.send(JSON.stringify(msg));
    console.log('Message sent');
    
    // 保持连接一段时间
    setTimeout(() => {
      ws.close();
      process.exit(0);
    }, 10000);
  }, 1000);
});

ws.on('message', (data) => {
  try {
    const msg = JSON.parse(data);
    if (msg.type === 'message.new' && msg.payload) {
      console.log(`[${msg.payload.senderName}]: ${msg.payload.content.substring(0, 100)}...`);
    }
  } catch (e) {}
});

ws.on('error', (err) => {
  console.error('Error:', err.message);
});
