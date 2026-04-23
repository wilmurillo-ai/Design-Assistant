---
name: "subscribe-filter-feishu"
description: "订阅-过滤-飞书推送。通过WebSocket订阅数据流，大模型智能过滤，自动推送到飞书。"
---

# Subscribe-Filter-Feishu v1.0.2

订阅数据流 → 大模型智能过滤 → 飞书推送。

## 功能

- 🔌 WebSocket 实时订阅数据流
- 🤖 大模型智能过滤
- 📱 飞书消息推送
- 📊 统计持久化
- 🔄 指数退避重连
- 🛑 优雅关闭

## 安装

```bash
cd skills/subscribe-filter-feishu
npm install
chmod +x scripts/subscribe-filter-feishu
```

## 配置（必须）

首次使用前，创建配置文件 `~/.openclaw/subscribe-filter-feishu.json`：

```json
{
  "ws_url": "ws://your-server:port/ws",
  "feishu_app_id": "your_feishu_app_id",
  "feishu_app_secret": "your_feishu_app_secret",
  "feishu_user_id": "your_feishu_open_id",
  "model_api_key": "your_ark_api_key",
  "model_base_url": "https://ark.cn-beijing.volces.com/api/v3",
  "model_name": "your_endpoint_id"
}
```

或运行 `subscribe-filter-feishu config` 创建模板。

### 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `ws_url` | ✅ | WebSocket 数据源地址 |
| `feishu_app_id` | ✅ | 飞书应用 App ID |
| `feishu_app_secret` | ✅ | 飞书应用 App Secret |
| `feishu_user_id` | ✅ | 接收消息的飞书用户 open_id |
| `model_api_key` | ✅ | 火山引擎 ARK API Key |
| `model_base_url` | ❌ | 大模型 API 地址（默认豆包2.0） |
| `model_name` | ✅ | 火山引擎 Endpoint ID |

## 使用

```bash
# 启动服务
subscribe-filter-feishu start

# 查看状态
subscribe-filter-feishu status

# 查看日志
subscribe-filter-feishu logs

# 停止服务
subscribe-filter-feishu stop

# 重启
subscribe-filter-feishu restart

# 查看/创建配置
subscribe-filter-feishu config
```

## 过滤规则（示例：AI新闻）

默认过滤规则只推送明确涉及 AI 核心技术的新闻：
- 机器学习/深度学习/神经网络
- 大语言模型(LLM)、NLP、计算机视觉
- AI 生成内容(AIGC)
- Transformer、GPT、BERT 等

不推送：
- 机器人/无人机/自动化机械
- 合成生物学/基因编辑
- 电池/储能/新能源
- 材料科学

可在 `receiver.js` 中修改 `isAIRelated()` 的 prompt 自定义过滤规则。

## 数据目录

```
~/clawd/data/subscribe-filter-feishu/
├── receiver.pid    # PID 文件
├── receiver.log    # 运行日志
└── stats.json      # 统计数据
```

## 版本历史

### v1.0.2
- 异常兜底（uncaughtException / unhandledRejection 不退出进程）

### v1.0.0
- 配置文件管理（敏感信息不硬编码）
- PID 管理（防止重复启动）
- 管理脚本（start/stop/status）
- 指数退避重连
- 统计持久化
- 飞书 token 自动刷新
- 豆包2.0 大模型

## License

MIT
