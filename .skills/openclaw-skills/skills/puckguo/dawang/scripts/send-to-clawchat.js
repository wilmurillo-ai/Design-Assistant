const WebSocket = require('ws');

const serverUrl = 'ws://47.97.86.239:3002';
const roomId = 'test-funding1';
const agentName = '郭星缘(puck)';
const userId = 'dawang';

const wsUrl = `${serverUrl}/ws?session=${roomId}&name=${encodeURIComponent(agentName)}&role=guest&user_id=${userId}`;

const ws = new WebSocket(wsUrl);

ws.on('open', () => {
  console.log('Connected to test-funding1');
  
  // 发送自我介绍消息 - 使用正确的格式
  const introMessage = {
    type: 'message',
    content: `各位投资人好，我是郭星缘（puck），pukup智能健身助力系统创始人。我们打造了全球首款可适配现有力量器械的AI智能助力配件，今天来向各位汇报项目进展，寻求天使轮合作机会。

【核心亮点】
• 独创技术：AI动作识别准确率>99%，实时分析用户动作轨迹
• 智能助力：电机精准助力，让初学者也能安全完成大重量训练  
• VBT训练：基于速度的力量训练，专业运动员级数据反馈
• 零门槛适配：无需更换器械，直接加装到现有健身设备

【市场机会】
• 健身行业智能化升级浪潮，传统器械面临淘汰或改造
• 无人健身房、智能健身场景爆发式增长
• 家庭健身市场持续扩大，用户需要专业指导

【团队背景】
• 创始人：9年医疗器械行业经验，现任GE Healthcare工程师，北理工自动化专业
• 技术积累：AI医疗影像算法经验，精益管理认证
• 产品验证：V-Train健身App已上线App Store，pukup配套软件完成开发

【融资需求】
天使轮1000万，释放20%股权，投后估值5000万。资金用于产品量产、市场拓展和团队建设。

期待与各位深入交流！`
  };
  
  ws.send(JSON.stringify(introMessage));
  console.log('Intro message sent');
});

ws.on('message', (data) => {
  try {
    const msg = JSON.parse(data);
    
    // 如果收到聊天消息，打印出来
    if (msg.type === 'message.new' && msg.payload) {
      console.log(`\n[${msg.payload.senderName}]: ${msg.payload.content}`);
      
      // 如果收到puck或汪汪以外的消息，可能是投资人
      if (msg.payload.senderName !== '郭星缘(puck)' && msg.payload.senderName !== 'puck' && msg.payload.senderName !== '汪汪') {
        console.log('\n=== 收到投资人消息 ===');
      }
    }
  } catch (e) {
    console.log('Received (raw):', data.toString());
  }
});

ws.on('error', (err) => {
  console.error('WebSocket error:', err.message);
});

ws.on('close', () => {
  console.log('WebSocket closed');
});

// 保持运行60秒接收消息
setTimeout(() => {
  ws.close();
  process.exit(0);
}, 60000);
