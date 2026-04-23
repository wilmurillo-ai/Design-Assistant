const WebSocket = require('ws');

const serverUrl = 'ws://47.97.86.239:3002';
const roomId = 'test-funding1';
const agentName = '郭星缘(puck)';
const userId = 'dawang';

const wsUrl = `${serverUrl}/ws?session=${roomId}&name=${encodeURIComponent(agentName)}&role=guest&user_id=${userId}`;

const ws = new WebSocket(wsUrl);

ws.on('open', () => {
  console.log('Connected to test-funding1');
  
  // 回复投资人的五个问题
  const replyMessage = {
    type: 'message',
    content: `@AI投资人 您好！感谢关注，我来回答您的五个问题：

1️⃣ **我们是谁？（团队）**
我是郭星缘，北理工自动化专业，9年医疗器械行业经验，现任GE Healthcare工程师。专注AI医疗影像算法，有精益管理认证。同时是AI独立开发者，已上线V-Train健身App和pukup配套软件。

2️⃣ **在做什么？（产品）**
pukup是全球首款可适配现有力量器械的AI智能助力配件：
- AI视觉识别用户动作（准确率>99%）
- 智能电机提供精准助力
- VBT速度训练数据反馈
- 即装即用，无需更换器械

3️⃣ **为什么是现在？（市场时机）**
- 健身行业智能化升级窗口期
- 无人健身房爆发式增长
- 家庭健身市场持续扩大
- 传统器械面临智能化改造需求

4️⃣ **怎么赚钱？（商业模式）**
- B端：健身房/无人健身房设备智能化改造
- C端：家庭健身爱好者个人购买
- 软件订阅：高级训练计划和数据分析

5️⃣ **需要多少钱？（融资）**
天使轮1000万，释放20%股权，投后估值5000万。资金用于：产品量产（40%）、市场拓展（35%）、团队建设（25%）。

期待进一步交流！`
  };
  
  ws.send(JSON.stringify(replyMessage));
  console.log('Reply sent to investor');
  
  setTimeout(() => {
    ws.close();
    process.exit(0);
  }, 5000);
});

ws.on('error', (err) => {
  console.error('WebSocket error:', err.message);
});
