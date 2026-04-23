#!/usr/bin/env node
/**
 * AI News Feishu v2.0
 * WebSocket 数据接收 + 大模型过滤 + 飞书推送
 */

const WebSocket = require('ws');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ============ 配置加载 ============
const CONFIG_PATH = path.join(os.homedir(), '.openclaw', 'subscribe-filter-feishu.json');
const DATA_DIR = path.join(os.homedir(), 'clawd', 'data', 'subscribe-filter-feishu');
const PID_FILE = path.join(DATA_DIR, 'receiver.pid');
const LOG_FILE = path.join(DATA_DIR, 'receiver.log');
const STATS_FILE = path.join(DATA_DIR, 'stats.json');

// 默认配置（敏感信息必须从配置文件读取）
const DEFAULT_CONFIG = {
  ws_url: '',  // 必填
  feishu_app_id: '',  // 必填
  feishu_app_secret: '',  // 必填
  feishu_user_id: '',  // 必填
  model_api_key: '',  // 必填
  model_base_url: 'https://ark.cn-beijing.volces.com/api/v3',
  model_name: '',
  reconnect_delay: 2,
  reconnect_max_delay: 60,
};

let config = { ...DEFAULT_CONFIG };

function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    console.error('❌ 配置文件不存在:', CONFIG_PATH);
    console.error('');
    console.error('请创建配置文件:');
    console.error(`mkdir -p ~/.openclaw && cat > ${CONFIG_PATH} << 'EOF'`);
    console.error(JSON.stringify({
      ws_url: 'ws://your-server:port/ws',
      feishu_app_id: 'your_app_id',
      feishu_app_secret: 'your_app_secret',
      feishu_user_id: 'your_open_id',
      model_api_key: 'your_api_key',
    }, null, 2));
    console.error('EOF');
    process.exit(1);
  }

  try {
    const fileConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    config = { ...DEFAULT_CONFIG, ...fileConfig };
  } catch (e) {
    console.error('❌ 配置文件解析失败:', e.message);
    process.exit(1);
  }

  // 验证必填项
  const required = ['ws_url', 'feishu_app_id', 'feishu_app_secret', 'feishu_user_id', 'model_api_key', 'model_name'];
  const missing = required.filter(k => !config[k]);
  if (missing.length > 0) {
    console.error('❌ 缺少必填配置:', missing.join(', '));
    console.error('请编辑配置文件:', CONFIG_PATH);
    process.exit(1);
  }
}

// ============ 日志 ============
function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function log(msg) {
  const line = `${new Date().toISOString()} - ${msg}`;
  console.log(line);
  try {
    fs.appendFileSync(LOG_FILE, line + '\n');
  } catch (e) {}
}

// ============ PID 管理 ============
function writePid() {
  fs.writeFileSync(PID_FILE, process.pid.toString());
  log(`PID ${process.pid} written to ${PID_FILE}`);
}

function removePid() {
  try {
    if (fs.existsSync(PID_FILE)) {
      fs.unlinkSync(PID_FILE);
    }
  } catch (e) {}
}

function isAlreadyRunning() {
  if (!fs.existsSync(PID_FILE)) return false;
  
  try {
    const pid = parseInt(fs.readFileSync(PID_FILE, 'utf-8').trim());
    // 检查进程是否存在
    process.kill(pid, 0);
    return true;
  } catch (e) {
    // 进程不存在，清理残留 PID 文件
    removePid();
    return false;
  }
}

// ============ 统计持久化 ============
let stats = { totalReceived: 0, totalAI: 0, lastUpdate: null };

function loadStats() {
  try {
    if (fs.existsSync(STATS_FILE)) {
      stats = JSON.parse(fs.readFileSync(STATS_FILE, 'utf-8'));
    }
  } catch (e) {}
}

function saveStats() {
  stats.lastUpdate = new Date().toISOString();
  try {
    fs.writeFileSync(STATS_FILE, JSON.stringify(stats, null, 2));
  } catch (e) {}
}

// ============ 全局状态 ============
let feishuAccessToken = '';
let feishuTokenExpiry = 0;
let reconnectCount = 0;
let ws = null;

// ============ 飞书 Token ============
async function getFeishuToken() {
  // 检查 token 是否还有效（提前 5 分钟刷新）
  if (feishuAccessToken && Date.now() < feishuTokenExpiry - 300000) {
    return feishuAccessToken;
  }

  try {
    const response = await axios.post(
      'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal',
      {
        app_id: config.feishu_app_id,
        app_secret: config.feishu_app_secret,
      }
    );
    feishuAccessToken = response.data.app_access_token;
    // token 有效期 2 小时
    feishuTokenExpiry = Date.now() + response.data.expire * 1000;
    log('✅ 飞书 Token 获取成功');
    return feishuAccessToken;
  } catch (err) {
    log('❌ 飞书 Token 获取失败: ' + err.message);
    return null;
  }
}

// ============ 发送飞书消息 ============
async function sendToFeishu(news, llmAnswer, sendDelay, processDelay) {
  const token = await getFeishuToken();
  if (!token) return false;

  try {
    let timing = '';
    if (sendDelay !== null) {
      const total = sendDelay + processDelay;
      timing = `\n\n⏱️ 耗时: 服务端 ${sendDelay}ms + 处理 ${processDelay}ms = 总计 ${total}ms`;
    }
    
    const content = `【${news.title}】

${news.content}

🔗 ${news.url}${timing}

🤖 AI判断: ${llmAnswer}`;

    await axios.post(
      'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id',
      {
        receive_id: config.feishu_user_id,
        msg_type: 'text',
        content: JSON.stringify({ text: content })
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    log(`✅ 已推送: ${news.title}`);
    return true;
  } catch (err) {
    log('❌ 推送失败: ' + err.message);
    // token 过期，清除缓存
    if (err.response?.status === 401) {
      feishuAccessToken = '';
      feishuTokenExpiry = 0;
    }
    return false;
  }
}

// ============ 大模型判断 ============
async function isAIRelated(news) {
  const prompt = `严格判断以下新闻是否与AI（人工智能）核心技术的应用相关。

AI核心技术包括：机器学习、深度学习、神经网络、大语言模型(LLM)、自然语言处理(NLP)、计算机视觉(CV)、强化学习、Transformer架构、GPT/BERT等模型、AIGC（AI生成内容）等。

只回答"是"或"否"，不要解释：

新闻标题：${news.title}
新闻内容：${news.content}`;

  try {
    const response = await axios.post(
      `${config.model_base_url}/chat/completions`,
      {
        model: config.model_name,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 10,
        temperature: 0,
      },
      {
        headers: {
          'Authorization': `Bearer ${config.model_api_key}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000,
      }
    );

    const answer = response.data.choices[0].message.content.trim();
    log(`  [LLM] "${news.title.slice(0, 30)}..." -> ${answer}`);
    return { isAI: answer.includes('是') || answer.toLowerCase().includes('yes'), answer };
  } catch (err) {
    log('❌ LLM 调用失败: ' + err.message);
    return { isAI: false, answer: '调用失败' };
  }
}

// ============ 处理新闻 ============
async function processNews(news) {
  const receiveTime = Date.now();
  
  let sendDelay = null;
  if (news.timestamp) {
    let ts = news.timestamp;
    if (ts < 1e12) ts = ts * 1000;
    sendDelay = receiveTime - ts;
  }
  
  stats.totalReceived++;
  const llmResult = await isAIRelated(news);
  const processDelay = Date.now() - receiveTime;
  
  if (llmResult.isAI) {
    stats.totalAI++;
    log(`🤖 [${stats.totalReceived}] AI新闻: ${news.title}`);
    await sendToFeishu(news, llmResult.answer, sendDelay, processDelay);
  } else {
    log(`📰 [${stats.totalReceived}] 非AI: ${news.title}`);
  }
  
  // 每 10 条保存一次统计
  if (stats.totalReceived % 10 === 0) {
    saveStats();
  }
}

// ============ 指数退避 ============
function calculateBackoff() {
  const delay = Math.min(
    config.reconnect_delay * Math.pow(2, reconnectCount),
    config.reconnect_max_delay
  );
  return delay * 1000;
}

// ============ WebSocket 连接 ============
function connect() {
  log(`🔌 Connecting to ${config.ws_url}...`);
  
  ws = new WebSocket(config.ws_url);
  
  ws.on('open', () => {
    log('✅ Connected!');
    reconnectCount = 0;  // 重置重连计数
  });
  
  ws.on('message', async (data) => {
    try {
      const json = JSON.parse(data.toString());
      await processNews(json);
    } catch (e) {
      // 忽略解析错误
    }
  });
  
  ws.on('close', () => {
    const delay = calculateBackoff();
    reconnectCount++;
    log(`⚠️ Disconnected, reconnecting in ${delay/1000}s... (attempt #${reconnectCount})`);
    setTimeout(connect, delay);
  });
  
  ws.on('error', (e) => {
    log('❌ WebSocket Error: ' + e.message);
  });
}

// ============ 优雅关闭 ============
function shutdown() {
  log('\n🛑 Shutting down...');
  log(`📊 总计接收: ${stats.totalReceived}, AI新闻: ${stats.totalAI}`);
  saveStats();
  removePid();
  if (ws) {
    ws.close();
  }
  process.exit(0);
}

// ============ 异常兜底 ============
process.on('uncaughtException', (err) => {
  log(`💥 未捕获异常: ${err.message}`);
  log(err.stack || '');
  // 不退出，继续运行
});

process.on('unhandledRejection', (reason) => {
  log(`💥 未处理的 Promise 拒绝: ${reason}`);
  // 不退出，继续运行
});

// ============ 主入口 ============
async function main() {
  ensureDataDir();
  loadConfig();
  
  // 检查是否已运行
  if (isAlreadyRunning()) {
    console.error('❌ 已有实例在运行，请先停止');
    console.error('使用: ai-news-feishu stop');
    process.exit(1);
  }
  
  writePid();
  loadStats();
  
  log('='.repeat(60));
  log('🚀 Subscribe-Filter-Feishu v1.0.0 Started');
  log(`📡 WebSocket: ${config.ws_url}`);
  log(`🤖 Model: ${config.model_name}`);
  log(`📊 历史统计: 接收 ${stats.totalReceived}, AI ${stats.totalAI}`);
  log('='.repeat(60));
  
  // 预先获取飞书 token
  await getFeishuToken();
  
  connect();
  
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main();
