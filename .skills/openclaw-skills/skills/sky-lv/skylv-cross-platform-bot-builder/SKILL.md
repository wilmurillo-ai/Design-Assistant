---
name: cross-platform-bot-builder
slug: skylv-cross-platform-bot-builder
version: 1.0.2
description: Cross-platform Bot generator. One-command Telegram/WeChat/Discord Bot creation with unified API and multi-platform deployment. Triggers: telegram bot, discord bot, wechat bot, bot builder.
author: SKY-lv
license: MIT
tags: [bot, telegram, wechat, discord, cross-platform, automation]
keywords: openclaw, skill, automation, ai-agent
triggers: cross platform bot builder
---

# Cross-Platform Bot Builder — 跨平台 Bot 生成器

## 功能说明

一键生成 Telegram、微信、抖音、Discord 等多平台 Bot，统一 API 接口，一次开发，多平台部署。支持消息处理、命令响应、媒体发送、用户管理等功能。

## 支持平台

| 平台 | 消息 | 命令 | 媒体 | 支付 | 状态 |
|------|------|------|------|------|------|
| Telegram | ✅ | ✅ | ✅ | ✅ | 完全支持 |
| Discord | ✅ | ✅ | ✅ | ❌ | 完全支持 |
| 微信公众号 | ✅ | ✅ | ✅ | ✅ | 完全支持 |
| 企业微信 | ✅ | ✅ | ✅ | ❌ | 完全支持 |
| 抖音 | ✅ | ✅ | ✅ | ✅ | 完全支持 |
| Slack | ✅ | ✅ | ✅ | ❌ | 完全支持 |
| WhatsApp | ✅ | ✅ | ✅ | ❌ | 测试中 |

## 快速开始

### 方式一：CLI 创建

```bash
# 创建新 Bot 项目
npx bot-builder create my-bot

# 选择平台
? Select platforms:
  ◉ Telegram
  ◉ Discord
  ◉ WeChat
  ◉ Douyin

# 生成项目结构
my-bot/
├── src/
│   ├── handlers/
│   │   ├── message.js
│   │   ├── command.js
│   │   └── event.js
│   ├── adapters/
│   │   ├── telegram.js
│   │   ├── discord.js
│   │   └── wechat.js
│   └── index.js
├── config/
│   └── platforms.json
├── .env
└── package.json
```

### 方式二：代码创建

```javascript
const { BotBuilder } = require('@skylv/bot-builder');

const bot = new BotBuilder({
  name: 'my-assistant',
  platforms: ['telegram', 'discord', 'wechat']
});

// 添加消息处理器
bot.onMessage(async (ctx) => {
  await ctx.reply(`收到：${ctx.message.text}`);
});

// 添加命令处理器
bot.onCommand('/start', async (ctx) => {
  await ctx.reply('欢迎使用！');
});

// 部署到多平台
await bot.deploy();
```

### 方式三：配置文件

```yaml
# bot.yaml
name: my-assistant
version: 1.0.0

platforms:
  telegram:
    enabled: true
    token: ${TELEGRAM_BOT_TOKEN}
    webhook: https://your-domain.com/telegram/webhook
  
  discord:
    enabled: true
    token: ${DISCORD_BOT_TOKEN}
    intents:
      - GUILD_MESSAGES
      - DIRECT_MESSAGES
  
  wechat:
    enabled: true
    appId: ${WECHAT_APP_ID}
    appSecret: ${WECHAT_APP_SECRET}
    token: ${WECHAT_TOKEN}

handlers:
  - type: message
    pattern: ".*"
    handler: ./src/handlers/message.js
  
  - type: command
    commands: ["/start", "/help"]
    handler: ./src/handlers/command.js
```

## 统一 API

### 消息处理

```javascript
// 统一消息上下文
{
  platform: 'telegram',
  userId: '123456',
  chatId: 'chat_789',
  message: {
    type: 'text',  // text|image|voice|video|document
    content: 'Hello',
    timestamp: 1234567890
  },
  user: {
    id: '123456',
    name: '张三',
    avatar: 'https://...'
  }
}

// 统一回复接口
ctx.reply('文本消息')
ctx.replyImage(imageUrl)
ctx.replyVoice(audioUrl)
ctx.replyVideo(videoUrl)
ctx.replyDocument(fileUrl)
```

### 命令处理

```javascript
// 命令注册
bot.command('/start', async (ctx) => {
  await ctx.reply('欢迎！使用 /help 查看帮助');
});

bot.command('/help', async (ctx) => {
  const helpText = `
可用命令:
/start - 开始
/help - 帮助
/settings - 设置
`;
  await ctx.reply(helpText);
});

// 命令参数解析
bot.command('/search <query>', async (ctx) => {
  const { query } = ctx.args;
  const results = await search(query);
  await ctx.reply(JSON.stringify(results));
});
```

### 事件处理

```javascript
// 用户事件
bot.onEvent('user.joined', async (ctx) => {
  await ctx.reply(`欢迎 ${ctx.user.name}！`);
});

bot.onEvent('user.left', async (ctx) => {
  console.log(`${ctx.user.name} 离开了`);
});

// 消息事件
bot.onEvent('message.edited', async (ctx) => {
  console.log('消息被编辑了');
});

bot.onEvent('message.deleted', async (ctx) => {
  console.log('消息被删除了');
});
```

## 平台适配器

### Telegram Adapter

```javascript
const telegram = require('./adapters/telegram');

telegram.init({
  token: process.env.TELEGRAM_BOT_TOKEN,
  webhook: {
    url: 'https://your-domain.com/telegram/webhook',
    port: 8443
  }
});

// 特有功能
telegram.sendPoll({
  chatId,
  question: '你喜欢什么？',
  options: ['A', 'B', 'C'],
  multiple: false
});

telegram.sendLocation({
  chatId,
  latitude: 39.9,
  longitude: 116.4
});
```

### Discord Adapter

```javascript
const discord = require('./adapters/discord');

discord.init({
  token: process.env.DISCORD_BOT_TOKEN,
  intents: ['GUILD_MESSAGES', 'DIRECT_MESSAGES']
});

// 特有功能
discord.createEmbed({
  title: '标题',
  description: '描述',
  color: 0x00AE86,
  fields: [
    { name: '字段 1', value: '值 1' },
    { name: '字段 2', value: '值 2' }
  ]
});

discord.addReaction({
  messageId,
  emoji: '👍'
});
```

### 微信 Adapter

```javascript
const wechat = require('./adapters/wechat');

wechat.init({
  appId: process.env.WECHAT_APP_ID,
  appSecret: process.env.WECHAT_APP_SECRET,
  token: process.env.WECHAT_TOKEN,
  encodingAESKey: process.env.WECHAT_AES_KEY
});

// 特有功能
wechat.sendTemplateMessage({
  toUser: userId,
  templateId: 'TEMPLATE_ID',
  data: {
    first: { value: '您好' },
    keyword1: { value: '订单完成' },
    remark: { value: '感谢使用' }
  }
});

wechat.createQRCode({
  sceneId: '123',
  expireSeconds: 2592000
});
```

## 部署方案

### Docker 部署

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 8443

CMD ["node", "src/index.js"]
```

```bash
# 构建镜像
docker build -t my-bot .

# 运行容器
docker run -d \
  --name my-bot \
  -p 8443:8443 \
  -e TELEGRAM_BOT_TOKEN=xxx \
  -e DISCORD_BOT_TOKEN=xxx \
  my-bot
```

### Serverless 部署

```yaml
# vercel.json
{
  "version": 2,
  "builds": [
    { "src": "src/index.js", "use": "@vercel/node" }
  ],
  "routes": [
    { "src": "/telegram/webhook", "dest": "src/index.js" },
    { "src": "/discord/webhook", "dest": "src/index.js" },
    { "src": "/wechat/webhook", "dest": "src/index.js" }
  ]
}
```

```bash
# 部署到 Vercel
vercel deploy
```

## 工具函数

### create_bot

```python
def create_bot(name: str, platforms: list, config: dict) -> dict:
    """
    创建 Bot 项目
    
    Args:
        name: Bot 名称
        platforms: 平台列表
        config: 配置字典
    
    Returns:
        {
            "project_path": "/path/to/my-bot",
            "files_created": [...],
            "next_steps": ["配置 Token", "部署 webhook", "启动服务"]
        }
    """
```

### deploy_to_platform

```python
def deploy_to_platform(platform: str, bot_config: dict) -> dict:
    """
    部署到指定平台
    
    Args:
        platform: 平台名称
        bot_config: Bot 配置
    
    Returns:
        {
            "status": "success",
            "webhook_url": "https://...",
            "test_message": "发送测试消息"
        }
    """
```

### analyze_bot_performance

```python
def analyze_bot_performance(bot_id: str, time_range: str = "24h") -> dict:
    """
    分析 Bot 性能
    
    Args:
        bot_id: Bot ID
        time_range: 时间范围
    
    Returns:
        {
            "total_messages": 10000,
            "active_users": 500,
            "avg_response_time": 0.5,
            "error_rate": 0.01,
            "platform_breakdown": {...}
        }
    """
```

## 相关文件

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Discord Developer Portal](https://discord.com/developers)
- [微信公众号开发](https://developers.weixin.qq.com/doc/offiaccount/)
- [抖音开放平台](https://open.douyin.com/)

## 触发词

- 自动：检测 bot、telegram、wechat、discord、cross-platform 相关关键词
- 手动：/bot-builder, /create-bot, /multi-platform-bot
- 短语：创建 Bot、Telegram Bot、微信 Bot、跨平台 Bot

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
