---
name: feishu-setup-troubleshooting
description: Set up and troubleshoot Feishu/Lark messaging integration with Hermes Agent. Covers configuration, the two-layer permission system, gateway management, and common issues.
version: 1.2.0
metadata:
  hermes:
    tags: [feishu, lark, messaging, troubleshooting, setup, integration]
    env:
      - FEISHU_APP_ID
      - FEISHU_APP_SECRET
      - FEISHU_DOMAIN
      - FEISHU_CONNECTION_MODE
      - FEISHU_GROUP_POLICY
      - FEISHU_ALLOW_ALL_USERS
      - GATEWAY_ALLOW_ALL_USERS
      - FEISHU_ALLOWED_USERS
      - FEISHU_ENCRYPT_KEY
      - FEISHU_VERIFICATION_TOKEN
---

# Feishu/Lark Setup & Troubleshooting Guide

## When to Use This Skill
- User wants to set up Feishu (飞书) or Lark messaging integration with Hermes Agent
- User reports bot not replying to messages on Feishu
- Need to diagnose Feishu connection, permission, or message delivery issues
- Configuring or modifying Feishu access control settings

## Prerequisites
- Hermes Agent installed (`hermes` CLI available)
- Feishu App created in [Feishu Open Platform](https://open.feishu.cn/) with:
  - App ID and App Secret
  - Bot capabilities enabled
  - Event subscriptions configured (message reception)

## 🔒 Security First: Access Control

> ⚠️ **重要**：生产环境请务必使用白名单模式。`ALLOW_ALL_USERS=true` 仅建议在开发/测试阶段使用。

Feishu 集成有 **两层独立的权限控制**，两者都必须正确配置：

| 层级 | 变量 | 作用 |
|------|------|------|
| 平台层 | `FEISHU_ALLOW_ALL_USERS` | 控制 Feishu 平台级别的用户访问 |
| 网关层 | `GATEWAY_ALLOW_ALL_USERS` | 控制所有平台的全局网关访问 |

**仅设置 `FEISHU_ALLOW_ALL_USERS=true` 是不够的！** 必须同时设置 `GATEWAY_ALLOW_ALL_USERS=true`，否则网关会拒绝所有用户，日志显示 `WARNING gateway.run: Unauthorized user`。

### 推荐的访问控制方式

#### ✅ 方式一：白名单模式（生产环境推荐）

```bash
# 仅允许指定用户使用机器人
FEISHU_ALLOW_ALL_USERS=false
GATEWAY_ALLOW_ALL_USERS=true
FEISHU_ALLOWED_USERS=ou_xxx1,ou_xxx2,ou_xxx3
```

#### ✅ 方式二：配对审批模式（需要用户主动申请）

```bash
FEISHU_ALLOW_ALL_USERS=false
GATEWAY_ALLOW_ALL_USERS=true
# 用户通过配对码请求访问，管理员用 hermes pairing approve 审批
```

#### ⚠️ 方式三：开放所有人（仅限测试/开发）

```bash
# ⚠️ 警告：任何人找到你的机器人都可以与之对话！
FEISHU_ALLOW_ALL_USERS=true
GATEWAY_ALLOW_ALL_USERS=true
FEISHU_ALLOWED_USERS=
```

> 💡 **安全提示**：如果你不需要对外公开机器人，请始终使用方式一或方式二。

---

## Configuration

Feishu environment variables are configured via `hermes config` CLI or in the Hermes env file.

### Required Environment Variables

| 变量 | 说明 | 获取位置 |
|------|------|---------|
| `FEISHU_APP_ID` | 飞书应用 ID | [飞书开放平台](https://open.feishu.cn/) → 应用凭证 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 飞书开放平台 → 应用凭证 |
| `FEISHU_DOMAIN` | 域名：`feishu` 或 `lark` | 根据你的区域选择 |
| `FEISHU_CONNECTION_MODE` | 连接模式：`webhook` 或 `websocket` | 推荐 websocket |
| `FEISHU_GROUP_POLICY` | 群聊策略：`open` / `allowlist` / `disabled` | 按需配置 |

### Optional Environment Variables

| 变量 | 说明 |
|------|------|
| `FEISHU_ALLOW_ALL_USERS` | 是否允许所有飞书用户（默认 false） |
| `GATEWAY_ALLOW_ALL_USERS` | 是否允许所有网关用户（默认 false） |
| `FEISHU_ALLOWED_USERS` | 白名单用户 Open ID 列表（逗号分隔） |
| `FEISHU_ENCRYPT_KEY` | webhook 模式下的加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | webhook 模式下的验证令牌 |

---

## Step-by-Step Setup / Troubleshooting Workflow

### Step 1: Check current configuration

Use `hermes config` CLI or `hermes doctor` to verify all required Feishu variables are present and not empty.

### Step 2: Check if Gateway is running

```bash
hermes gateway status
```
Expected output: `✓ Gateway is running (PID: xxxx)`

If NOT running:
```bash
hermes gateway run        # Run in foreground
# OR
hermes gateway install    # Install as background service
hermes gateway start      # Start the service
```

**Important:** `hermes chat` (CLI interactive mode) does NOT handle incoming Feishu messages. You need `hermes gateway` running as a separate process.

### Step 3: Verify Feishu connection

Check logs for successful connection:
```bash
hermes logs 2>&1 | grep -i feishu
```
Look for:
```
✓ [Feishu] Connected in websocket mode (feishu)
✓ feishu connected
Lark: connected to wss://msg-frontier.feishu.cn/...
```

### Step 4: Test message delivery & check for authorization errors

After sending a test message from Feishu, check logs:
```bash
hermes logs 2>&1 | tail -30
```

**Success indicators:**
```
[Feishu] Inbound dm message received: id=om_xxx type=text text='hi'
[Feishu] Flushing text batch ...
```

**Common failure - Unauthorized user (the two-layer bug):**
```
WARNING gateway.run: Unauthorized user: ou_xxxxxx (None) on feishu
```
Fix: Use `hermes config` to set `GATEWAY_ALLOW_ALL_USERS=true`, then restart gateway.

### Step 5: Restart Gateway after config changes

```bash
hermes gateway restart
# OR if replace mode needed:
hermes gateway stop
hermes gateway run --replace
```

---

## Common Issues & Solutions

| 症状 | 原因 | 解决方法 |
|------|------|---------|
| 机器人完全不回复 | Gateway 未运行 | `hermes gateway run` 启动 |
| 日志显示 "Unauthorized user" | 缺少 `GATEWAY_ALLOW_ALL_USERS=true` | 通过 hermes config 设置后重启网关 |
| Connection refused | 域名错误（feishu vs lark） | 检查 `FEISHU_DOMAIN` 是否匹配你的区域 |
| WebSocket 断连 | 网络/防火墙问题 | 检查到 `msg-frontier.feishu.cn` 的出站连接 |
| 收到消息但不回复 | 模型/API Key 配置错误 | 运行 `hermes doctor` 检查 API 提供商状态 |
| 群消息被忽略 | `FEISHU_GROUP_POLICY` 过于严格 | 设为 `open` 或配置群规则 |

---

## Diagnostic Commands Quick Reference

```bash
# Full health check
hermes doctor

# Gateway status
hermes gateway status

# Live log monitoring
hermes logs --follow

# Recent Feishu-related log entries
hermes logs 2>&1 | grep -i feishu | tail -20

# List active processes
ps aux | grep -E "(hermes|gateway)" | grep -v grep
```

---

## 🔐 Security Best Practices

1. **最小权限原则**：始终使用白名单模式（`FEISHU_ALLOW_ALL_USERS=false`）
2. **保护密钥安全**：永远不要将 `.env` 文件或 API Secret 提交到版本控制
3. **使用加密通信**：webhook 模式下务必配置 `FEISHU_ENCRYPT_KEY`
4. **定期审计**：定期检查 `FEISHU_ALLOWED_USERS` 列表，移除不再需要的用户
5. **生产环境检查清单**：
   - [ ] 使用白名单模式
   - [ ] API Secret 存储在安全位置（不硬编码）
   - [ ] 日志中不打印敏感信息
   - [ ] 网关运行在受限的用户权限下
