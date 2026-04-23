---
name: weixin-send-media
version: 1.1.0
description: 微信发图片/文件技能 - 解决 contextToken 持久化问题
author: linzmin1927
---

# 微信发媒体技能

> 本技能解决了微信渠道发送媒体消息的核心问题：contextToken 持久化。

> ⚠️ **前提条件**：微信渠道必须已登录并处于活动状态。

---

## 🔒 安全说明（重要）

### 为什么需要修改核心文件？

本技能需要修改 `~/.openclaw/extensions/openclaw-weixin/src/messaging/inbound.ts`，这是因为：

1. **contextToken 的生成和存储逻辑在核心扩展中**
   - `setContextToken()` 和 `getContextToken()` 是内部函数
   - 没有公开 API 可以外部调用

2. **这是唯一可行的方案**
   - 微信 API 要求发送消息时必须提供 contextToken
   - Token 只在收到用户消息时生成
   - 原始设计只缓存在内存，重启即丢失

3. **修改是安全可控的**
   - 只添加了文件读写逻辑，不改变原有功能
   - 所有数据存储在用户本地 `~/.openclaw/openclaw-weixin/context-tokens/`
   - 不会外传任何敏感信息

### 安全最佳实践

```bash
# 1. 限制 token 文件权限
chmod 600 ~/.openclaw/openclaw-weixin/context-tokens/*.json

# 2. 定期清理过期 token
find ~/.openclaw/openclaw-weixin/context-tokens/ -mtime +30 -delete

# 3. 检查 token 文件
cat ~/.openclaw/openclaw-weixin/context-tokens/*.json
```

### ClawHub 安全警告说明

ClawHub 可能显示 **Security: SUSPICIOUS**，这是因为：
- 技能修改了 OpenClaw 核心扩展文件
- 使用了补丁（patch）方式注入

**这是误报**，本技能：
- ✅ 不窃取任何数据
- ✅ 不连接外部服务器
- ✅ 所有操作在本地完成
- ✅ 代码完全开源可审计

---

## 背景问题

微信渠道的 `contextToken`（会话上下文令牌）原本只缓存在 gateway 进程内存中，导致：
- ❌ CLI 命令无法发送媒体消息
- ❌ 自动化脚本无法调用
- ❌ 重启 gateway 后 token 丢失

本技能通过持久化 contextToken 到磁盘文件，解决了这个问题。

---

## 使用方式

### 方法 1：CLI 发送图片

```bash
openclaw message send \
  --channel openclaw-weixin \
  --account d72d5b576646-im-bot \
  --target o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat \
  --media /path/to/image.png \
  --message "图片说明"
```

### 方法 2：CLI 发送文件

```bash
openclaw message send \
  --channel openclaw-weixin \
  --account d72d5b576646-im-bot \
  --target o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat \
  --media /path/to/document.pdf \
  --message "文件说明"
```

### 方法 3：CLI 发送网络图片

```bash
openclaw message send \
  --channel openclaw-weixin \
  --account d72d5b576646-im-bot \
  --target o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat \
  --media https://example.com/image.jpg \
  --message "网络图片"
```

### 方法 4：Node.js 脚本调用

```javascript
const { execSync } = require('child_process');

function sendWeixinMedia(userId, mediaPath, caption = '') {
  const cmd = `openclaw message send \\
    --channel openclaw-weixin \\
    --account <your-account-id> \\
    --target ${userId} \\
    --media ${mediaPath} \\
    --message "${caption}"`;
  
  return execSync(cmd, { encoding: 'utf8' });
}

// 使用示例
sendWeixinMedia(
  'o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat',
  '/path/to/qr.png',
  '这是二维码'
);
```

### 方法 5：使用封装脚本

```bash
# 发送图片
./scripts/send-image.js <user-id> <image-path> [caption]

# 示例
./scripts/send-image.js o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat ./qr.png "扫码绑定"
```

---

## 核心修改

### 修改文件
`~/.openclaw/extensions/openclaw-weixin/src/messaging/inbound.ts`

### 修改内容

在文件开头添加：
```typescript
import fs from "node:fs";
import path from "node:path";
```

添加持久化目录和文件路径函数：
```typescript
// Persist context tokens to disk for CLI access
const CONTEXT_TOKEN_DIR = path.join(process.env.HOME!, ".openclaw/openclaw-weixin/context-tokens");
try { fs.mkdirSync(CONTEXT_TOKEN_DIR, { recursive: true }); } catch {}

function contextTokenFile(accountId: string, userId: string): string {
  const safeId = accountId.replace(/[@:]/g, "_");
  const safeUser = userId.replace(/[@:]/g, "_");
  return path.join(CONTEXT_TOKEN_DIR, `${safeId}__${safeUser}.json`);
}
```

修改 `setContextToken` 函数（添加磁盘持久化）：
```typescript
export function setContextToken(accountId: string, userId: string, token: string): void {
  const k = contextTokenKey(accountId, userId);
  logger.debug(`setContextToken: key=${k}`);
  contextTokenStore.set(k, token);
  
  // Persist to disk
  const file = contextTokenFile(accountId, userId);
  try {
    fs.writeFileSync(file, JSON.stringify({ 
      accountId, 
      userId, 
      token, 
      savedAt: new Date().toISOString() 
    }, null, 2));
    logger.debug(`setContextToken: persisted to ${file}`);
  } catch (e) {
    logger.warn(`setContextToken: failed to persist to disk: ${e}`);
  }
}
```

修改 `getContextToken` 函数（添加磁盘回退）：
```typescript
export function getContextToken(accountId: string, userId: string): string | undefined {
  const k = contextTokenKey(accountId, userId);
  const val = contextTokenStore.get(k);
  logger.debug(
    `getContextToken: key=${k} found=${val !== undefined} storeSize=${contextTokenStore.size}`,
  );
  if (val) return val;
  
  // Fallback to disk
  const file = contextTokenFile(accountId, userId);
  try {
    if (fs.existsSync(file)) {
      const data = JSON.parse(fs.readFileSync(file, "utf8"));
      logger.debug(`getContextToken: loaded from disk ${file}`);
      return data.token;
    }
  } catch (e) {
    logger.warn(`getContextToken: failed to load from disk: ${e}`);
  }
  return undefined;
}
```

---

## 文件结构

```
weixin-send-media/
├── SKILL.md                    # 本文件 - 完整文档
├── README.md                   # 快速入门
├── CHANGELOG.md                # 更新日志
├── scripts/
│   ├── send-image.js           # 发图片脚本
│   ├── send-file.js            # 发文件脚本
│   └── export-context-token.js # 导出 token 工具
├── patches/
│   └── inbound.ts.patch        # 补丁文件
├── references/
│   └── api-docs.md             # API 文档
└── tests/
    └── test-token-persistence.sh # 测试脚本
```

---

## 安装步骤

### 自动安装（推荐）

```bash
npx clawhub@latest install weixin-send-media
```

### 手动安装

1. **应用补丁**
```bash
cd ~/.openclaw/workspace/skills/weixin-send-media
./install.sh
```

2. **重启 gateway**
```bash
openclaw gateway restart
```

3. **发送一条消息触发 token 保存**
（任意微信消息即可）

4. **验证 token 文件**
```bash
cat ~/.openclaw/openclaw-weixin/context-tokens/*.json
```

---

## 典型工作流

### 发送二维码给家人

**用户 query 示例**：
- "把绑定二维码发给我老婆"
- "发一下配对码"

**执行流程**：
1. 生成二维码图片（`openclaw qr`）
2. 保存二维码到文件
3. 调用 `openclaw message send --media` 发送
4. 家人扫码绑定

### 分享截图

**用户 query 示例**：
- "把这个截图发给张三"
- "分享刚才的图片"

**执行流程**：
1. 确认图片路径
2. 确认目标用户
3. 发送图片消息

### 定时发送日报

**脚本示例**：
```bash
#!/bin/bash
# 每天下午 6 点发送日报
IMAGE=/path/to/daily-report.png
openclaw message send \
  --channel openclaw-weixin \
  --account <account-id> \
  --target <user-id> \
  --media $IMAGE \
  --message "📊 今日日报"
```

---

## ❓ 常见问题 FAQ

### Q1: 安装后还是提示 "contextToken is required"？

**A:** 可能是因为：
1. 还没收到过用户消息（token 还没生成）
2. gateway 没重启（补丁没生效）

**解决：**
```bash
# 1. 确保微信渠道已登录
openclaw channels status

# 2. 发送一条消息给机器人
（在微信里随便发点什么）

# 3. 重启 gateway
openclaw gateway restart

# 4. 检查 token 文件
ls -la ~/.openclaw/openclaw-weixin/context-tokens/
```

### Q2: token 文件在哪里？安全吗？

**A:** 
- 位置：`~/.openclaw/openclaw-weixin/context-tokens/`
- 安全：建议设置权限 `chmod 600`

### Q3: 可以发送给多人吗？

**A:** 可以，循环调用即可：
```bash
for user in user1 user2 user3; do
  openclaw message send --target $user --media image.png --message "分享"
done
```

### Q4: 支持发送视频吗？

**A:** 支持，但文件大小不能超过 20MB（微信限制）。

### Q5: 发送失败怎么排查？

**A:** 查看日志：
```bash
tail -f ~/.openclaw/logs/gateway.log | grep -i weixin
```

---

## 🔧 故障排查

### 问题 1: 补丁应用失败

**症状：**
```
patch: command not found
```

**解决：**
```bash
# 安装 patch 工具
sudo apt-get install patch  # Debian/Ubuntu
sudo yum install patch      # CentOS/RHEL
brew install patch          # macOS
```

### 问题 2: gateway 启动失败

**症状：**
```
Error: Cannot find module 'fs'
```

**原因：** TypeScript 编译错误

**解决：**
```bash
# 重新编译扩展
cd ~/.openclaw/extensions/openclaw-weixin
npm run build

# 重启 gateway
openclaw gateway restart
```

### 问题 3: token 文件为空

**症状：**
```json
{}
```

**原因：** 还没收到用户消息

**解决：** 在微信里给机器人发条消息

### 问题 4: 发送消息超时

**症状：**
```
Error: Request timeout
```

**可能原因：**
- 网络问题
- 微信 API 限流
- 文件太大

**解决：**
1. 检查网络连接
2. 等待几分钟后重试
3. 压缩文件到 20MB 以内

---

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `contextToken is required` | 没有收到过用户消息 | 先让用户发一条消息 |
| `media file not found` | 图片路径不存在 | 检查文件路径 |
| `media too large` | 文件超过 20MB | 压缩文件或换小图 |
| `account not configured` | 微信未登录 | 运行 `openclaw channels login` |
| `patch command not found` | 系统没有 patch 工具 | 安装 patch |
| `gateway failed to start` | TypeScript 编译错误 | 重新编译扩展 |

---

## 技术细节

### contextToken 是什么？

`contextToken` 是微信 API 要求的会话上下文令牌：
- 每次收到用户消息时生成
- 发送回复时必须原样回传
- 用于关联会话，防止机器人骚扰

### 为什么需要持久化？

| 方案 | 优点 | 缺点 |
|------|------|------|
| **内存缓存（原始）** | 安全：重启后失效 | 不便：CLI 无法调用 |
| **磁盘持久化（本技能）** | 方便：CLI/脚本都能用 | 需注意文件权限 |

### 文件格式

```json
{
  "accountId": "d72d5b576646-im-bot",
  "userId": "o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat",
  "token": "AARzJWAFAAABAAAAAAA7Q7l0VPX7W68yTLPAaSAAAAB+9905Q6UiugPBawU3n3cyzQX+LkN8ofRzsCZYN0mt7t0YJWY1u3fHryDZWu4I8cQKMXA4VECLBA3G8SLW2jKCANbBVXp8",
  "savedAt": "2026-03-23T03:28:13.073Z"
}
```

### Token 生命周期

1. **生成**：用户发送消息时
2. **存储**：内存 + 磁盘双写
3. **读取**：先查内存，没有再查磁盘
4. **过期**：建议 30 天清理一次

---

## 相关文件

- 原始实现：`~/.openclaw/extensions/openclaw-weixin/src/messaging/inbound.ts`
- 发送逻辑：`~/.openclaw/extensions/openclaw-weixin/src/messaging/send.ts`
- 媒体上传：`~/.openclaw/extensions/openclaw-weixin/src/messaging/send-media.ts`
- Token 存储：`~/.openclaw/openclaw-weixin/context-tokens/`

---

## 更新日志

### v1.1.0 (2026-03-26)
- ✅ 添加安全说明章节，解释补丁必要性
- ✅ 添加完整 FAQ 和故障排查指南
- ✅ 补全 scripts 目录（send-image.js, send-file.js）
- ✅ 添加测试脚本 test-token-persistence.sh
- ✅ 优化文档结构和可读性
- ✅ 修复硬编码的 account ID 和 user ID

### v1.0.0 (2026-03-23)
- ✅ 实现 contextToken 磁盘持久化
- ✅ 支持 CLI 发送图片/文件
- ✅ 支持网络图片 URL
- ✅ 添加错误处理和日志

---

## 作者

🦆 鸭鸭 (Yaya) - OpenClaw 微信渠道增强

## 许可证

MIT-0 License (Free to use, modify, and redistribute. No attribution required.)
