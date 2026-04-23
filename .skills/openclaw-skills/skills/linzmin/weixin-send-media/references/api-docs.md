# API 文档

## OpenClaw 微信渠道消息发送 API

### 基础命令

```bash
openclaw message send \
  --channel <channel-id> \
  --account <account-id> \
  --target <user-id> \
  --media <media-path-or-url> \
  --message <caption>
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--channel` | ✅ | 渠道 ID，如 `openclaw-weixin` |
| `--account` | ✅ | 账号 ID，如 `d72d5b576646-im-bot` |
| `--target` | ✅ | 目标用户 ID（微信 openid） |
| `--media` | ✅ | 媒体文件路径或 URL |
| `--message` | ❌ | 媒体说明文字 |

### 支持的媒体类型

#### 图片
- **格式**：PNG, JPG, GIF, WEBP
- **大小**：≤ 20MB
- **示例**：
  ```bash
  openclaw message send \
    --channel openclaw-weixin \
    --account d72d5b576646-im-bot \
    --target o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat \
    --media ./screenshot.png \
    --message "截图"
  ```

#### 文件
- **格式**：PDF, DOC, DOCX, XLS, XLSX, ZIP 等
- **大小**：≤ 20MB
- **示例**：
  ```bash
  openclaw message send \
    --channel openclaw-weixin \
    --account d72d5b576646-im-bot \
    --target o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat \
    --media ./report.pdf \
    --message "月度报告"
  ```

#### 网络图片
- **要求**：必须是公开可访问的 URL
- **示例**：
  ```bash
  openclaw message send \
    --channel openclaw-weixin \
    --account d72d5b576646-im-bot \
    --target o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat \
    --media https://example.com/image.jpg \
    --message "网络图片"
  ```

---

## contextToken 机制

### 什么是 contextToken？

`contextToken` 是微信 API 要求的会话上下文令牌，用于：
- 标识消息发送的会话上下文
- 防止机器人滥用发送能力
- 确保只有收到过用户消息的账号才能回复

### Token 生命周期

```
用户发送消息
    ↓
Gateway 接收消息
    ↓
生成 contextToken
    ↓
存储到内存 + 磁盘  ← 本技能增强点
    ↓
发送消息时使用 Token
    ↓
Token 过期（建议 30 天清理）
```

### Token 文件格式

```json
{
  "accountId": "d72d5b576646-im-bot",
  "userId": "o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat",
  "token": "AARzJWAFAAABAAAAAAA7Q7l0VPX7W68yTLPAaSAAAAB+9905Q6UiugPBawU3n3cyzQX+LkN8ofRzsCZYN0mt7t0YJWY1u3fHryDZWu4I8cQKMXA4VECLBA3G8SLW2jKCANbBVXp8",
  "savedAt": "2026-03-23T03:28:13.073Z"
}
```

### Token 存储位置

```
~/.openclaw/openclaw-weixin/context-tokens/
├── d72d5b576646_im-bot__o9cq802hhREiOXPlXq_Tgb0MjPTo_im.wechat.json
└── ...
```

---

## 错误码参考

| 错误 | HTTP 状态 | 说明 | 解决方案 |
|------|----------|------|----------|
| `contextToken is required` | 400 | 缺少 contextToken | 确保用户已发送过消息 |
| `invalid contextToken` | 401 | Token 无效或过期 | 让用户重新发送消息 |
| `media file not found` | 404 | 文件不存在 | 检查文件路径 |
| `media too large` | 413 | 文件超过 20MB | 压缩文件 |
| `unsupported media type` | 415 | 不支持的格式 | 换用支持的格式 |
| `rate limit exceeded` | 429 | 发送频率过高 | 等待后重试 |

---

## 最佳实践

### 1. 错误重试

```javascript
function sendWithRetry(userId, media, caption, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return sendWeixinMedia(userId, media, caption);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      console.log(`重试 ${i + 1}/${maxRetries}...`);
      sleep(1000 * (i + 1)); // 指数退避
    }
  }
}
```

### 2. 批量发送

```bash
# 使用脚本批量发送
for user in $(cat user-list.txt); do
  ./scripts/send-image.js $user ./promo.png "促销活动"
  sleep 2  # 避免限流
done
```

### 3. Token 管理

```bash
# 定期检查 token 状态
./scripts/export-context-token.js list

# 清理过期 token
./scripts/export-context-token.js clean
```

---

## 相关资源

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [微信渠道配置指南](https://docs.openclaw.ai/channels/weixin)
- [ClawHub 技能市场](https://clawhub.com)
