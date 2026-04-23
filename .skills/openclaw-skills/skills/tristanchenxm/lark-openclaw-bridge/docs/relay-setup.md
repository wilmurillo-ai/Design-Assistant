# Lark OpenClaw Bridge — Relay 部署指南

通过中继服务（relay），用户本机无需公网 IP，即可接入飞书 Bot。

## 架构

```
飞书服务器
    ↓ POST /lark/webhook/{appId}
Relay 服务（jvs，公网可访问）
    ↕ WebSocket 长连接
lark-openclaw-bridge（用户本机）
    ↓ HTTP
OpenClaw Gateway（用户本机）
```

---

## 第一步：Relay 服务器部署（管理员操作，一次性）

### 安装

```bash
git clone https://repo.advai.net/atome-efficiency/lark-openclaw-bridge
cd lark-openclaw-bridge
npm install
```

### 启动

```bash
RELAY_PORT=18787 \
RELAY_SECRET=<自定义密钥> \
RELAY_STATUS_TOKEN=<自定义密钥> \
pm2 start scripts/relay-server.mjs --name lark-relay

pm2 save && pm2 startup
```

| 环境变量 | 说明 | 默认值 |
|---|---|---|
| `RELAY_PORT` | 监听端口 | `18787` |
| `RELAY_SECRET` | Bridge 连接认证密钥 | 空（不鉴权） |
| `RELAY_STATUS_TOKEN` | /status 和 /logs 访问密钥 | 同 RELAY_SECRET |

### 验证

```bash
curl https://oc.atomecorp.net/lark/health
# → {"status":"ok","bridges":0,"uptime":...}
```

日志观测：`https://oc.atomecorp.net/lark/logs?token=<密钥>&format=html`

---

## 第二步：申请飞书 Bot（每个用户操作一次）

1. 打开 [飞书开放平台](https://open.larksuite.com)，点击「创建企业自建应用」
2. 填写应用名称、描述，上传图标
3. 进入「权限管理」，申请以下权限：
   - `im:message:receive_v1`（接收消息）
   - `im:message`（发送消息）
   - `im:chat`（获取群信息）
4. 进入「事件订阅」：
   - 请求 URL 填：`https://oc.atomecorp.net/lark/webhook/<你的AppID>`
   - 添加事件：`接收消息 im.message.receive_v1`
   - 点击「验证」，出现绿色对勾即成功
5. 发布应用版本，等待管理员审批

---

## 第三步：用户本机安装 Bridge

### 安装 OpenClaw

```bash
npm install -g openclaw
openclaw configure  # 按提示填写配置
```

### 安装 Bridge

```bash
git clone https://repo.advai.net/atome-efficiency/lark-openclaw-bridge
cd lark-openclaw-bridge
npm install
```

### 配置环境变量

复制 `.env.example` 为 `.env`，填写以下内容：

```bash
# 飞书应用凭证（从开放平台获取）
LARK_APP_ID=cli_xxxxxxxxxxxxxxxx
LARK_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Relay 模式
RELAY_SERVER_URL=wss://oc.atomecorp.net/lark/bridge
RELAY_SECRET=<管理员提供的密钥>
```

### 启动

```bash
npm start
```

启动成功后，日志会显示：

```
[OK] Lark webhook bridge started
    Mode: relay (wss://oc.atomecorp.net/lark/bridge)
[RELAY-CLIENT] Connected to relay
[RELAY-CLIENT] Registered as appId=cli_xxx
```

---

## 验证整个链路

1. 在飞书里向你的 Bot 发一条消息
2. 观察 `https://oc.atomecorp.net/lark/logs?token=<密钥>&format=html`，应看到：
   ```
   [RELAY] [ROUTED] appId=cli_xxx event=im.message.receive_v1
   ```
3. OpenClaw 应正常收到消息并回复

---

## 常见问题

**Bridge 连不上 relay？**
- 检查 `RELAY_SECRET` 是否和服务器一致
- 检查防火墙是否放行 18789 端口（nginx）

**飞书 URL 验证失败？**
- 确认 Relay 服务正在运行：`curl https://oc.atomecorp.net/lark/health`
- 确认 AppID 填写正确

**消息没到 OpenClaw？**
- 查看 relay 日志，确认 bridge 已注册（`[CONNECTED] appId=xxx`）
- 检查本机 OpenClaw Gateway 是否在运行：`openclaw health`
