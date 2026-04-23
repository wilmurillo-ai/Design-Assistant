---
name: wechat-mp-monitor
version: 1.0.0
description: 微信公众号监控 - 文章阅读量追踪、分享数统计、定时日报
author: linzmin1927
---

# 微信公众号监控技能

> 通过微信官方 API 监控公众号文章数据，生成阅读量和分享数统计报告。

> ⚠️ **前提条件**：需要有自己的微信公众号（订阅号/服务号），并获取 AppID 和 AppSecret。

---

## 功能特性

- 📊 **文章监控** - 自动获取已群发文章列表
- 📈 **阅读追踪** - 统计每篇文章的阅读量/阅读人数
- 📤 **分享统计** - 追踪分享次数/分享人数
- 📅 **定时报告** - 每日/每周自动生成统计报告
- 💬 **微信推送** - 报告通过微信发送
- 📉 **趋势分析** - 阅读量变化趋势图

---

## 快速开始

### 1. 准备微信公众号

1. 注册微信公众号：https://mp.weixin.qq.com/
2. 获取 AppID 和 AppSecret（设置与开发 → 基本配置）
3. 配置 IP 白名单（可选，本地开发可跳过）

### 2. 配置凭证

```bash
# 创建配置文件
mkdir -p ~/.openclaw/wechat-mp
cat > ~/.openclaw/wechat-mp/config.json << 'EOF'
{
  "appId": "你的 APPID",
  "appSecret": "你的 APPSECRET",
  "notifyUser": "你的微信 ID@im.wechat"
}
EOF
```

### 3. 安装技能

```bash
# 通过 clawhub
clawhub install wechat-mp-monitor

# 或手动安装
cd /home/lin/.openclaw/extensions/openclaw-weixin/skills/wechat-mp-monitor
./install.sh
```

### 4. 使用示例

```bash
# 查看今日数据
wechat-mp-monitor today

# 查看昨日数据
wechat-mp-monitor yesterday

# 查看指定日期范围
wechat-mp-monitor --from 2026-03-01 --to 2026-03-23

# 生成日报并发送到微信
wechat-mp-monitor daily-report

# 生成周报
wechat-mp-monitor weekly-report
```

---

## 核心 API

### 获取图文群发总数据

```typescript
GET https://api.weixin.qq.com/datacube/getarticletotaldetail?access_token=ACCESS_TOKEN

Body:
{
  "begin_date": "2026-03-01",
  "end_date": "2026-03-23"
}

Response:
{
  "list": [
    {
      "stat_date": "2026-03-23",
      "msgid": "6245812345678901234",
      "title": "文章标题",
      "int_page_read_count": 1234,      // 图文页阅读次数
      "int_page_read_user_count": 890,  // 图文页阅读人数
      "share_count": 56,                // 分享次数
      "share_user_count": 45,           // 分享人数
      "user_read_count": 123,           // 微信收藏人数
      "user_read_user_count": 100       // 微信收藏人数
    }
  ]
}
```

### 获取 access_token

```typescript
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET

Response:
{
  "access_token": "ACCESS_TOKEN",
  "expires_in": 7200
}
```

---

## 技术实现

### 项目结构

```
wechat-mp-monitor/
├── SKILL.md
├── package.json
├── install.sh
├── scripts/
│   ├── get-token.js        # 获取 access_token
│   ├── fetch-articles.js   # 获取文章数据
│   ├── generate-report.js  # 生成报告
│   └── send-report.js      # 发送报告到微信
└── references/
    └── api-docs.md         # API 文档
```

### 核心流程

```
1. 获取 access_token（缓存 2 小时）
   ↓
2. 调用 getarticletotaldetail API
   ↓
3. 解析文章数据
   ↓
4. 生成 Markdown 报告
   ↓
5. 通过微信渠道发送
```

### access_token 管理

```typescript
// 缓存 token，避免频繁请求
const TOKEN_CACHE_FILE = '/tmp/wechat-mp-token.json';

function getCachedToken() {
  const cached = fs.readFileSync(TOKEN_CACHE_FILE);
  const { token, expiresAt } = JSON.parse(cached);
  
  if (Date.now() < expiresAt - 300000) { // 提前 5 分钟刷新
    return token;
  }
  return null;
}

async function refreshToken() {
  const url = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${APP_ID}&secret=${APP_SECRET}`;
  const resp = await fetch(url);
  const data = await resp.json();
  
  // 缓存到文件
  fs.writeFileSync(TOKEN_CACHE_FILE, JSON.stringify({
    token: data.access_token,
    expiresAt: Date.now() + (data.expires_in - 300) * 1000
  }));
  
  return data.access_token;
}
```

---

## 报告模板

### 日报模板

```markdown
# 📊 公众号日报 - 2026-03-23

## 今日概览
- 📝 发文数量：3 篇
- 👁️ 总阅读量：3456
- 👥 阅读人数：2890
- 📤 分享次数：234
- 👥 分享人数：198

## 文章详情

### 1. 文章标题一
- 阅读：1234 次 | 人数：1000 人
- 分享：89 次 | 人数：78 人
- 收藏：45 次

### 2. 文章标题二
- 阅读：1100 次 | 人数：950 人
- 分享：78 次 | 人数：65 人
- 收藏：34 次

### 3. 文章标题三
- 阅读：1122 次 | 人数：940 人
- 分享：67 次 | 人数：55 人
- 收藏：44 次

## 趋势分析
（图表：近 7 日阅读量趋势）

---
生成时间：2026-03-23 09:00
```

---

## 定时任务

### 每日 9:00 发送日报

```bash
# 添加 cron 任务
openclaw cron create \
  --schedule "0 9 * * *" \
  --command "wechat-mp-monitor daily-report"
```

### 每周一 9:00 发送周报

```bash
openclaw cron create \
  --schedule "0 9 * * 1" \
  --command "wechat-mp-monitor weekly-report"
```

---

## 错误处理

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 40001 | 凭证错误 | 检查 AppID/AppSecret |
| 40013 | AppID 无效 | 确认公众号配置 |
| 41001 | 缺少 access_token | 重新获取 token |
| 42001 | access_token 过期 | 刷新 token |
| 45009 | API 频率超限 | 等待后重试 |

---

## 注意事项

1. **access_token 有效期**：2 小时，需要缓存和刷新
2. **API 调用限制**：每个公众号有调用次数限制
3. **数据延迟**：当日数据可能不完整，建议次日查看
4. **时间范围**：单次查询最多 3 个月数据
5. **权限要求**：需要公众号管理员权限

---

## 后续计划

### v1.1（2 周后）
- [ ] 阅读量趋势图（ECharts）
- [ ] 异常提醒（阅读量暴跌）
- [ ] 竞品监控（需第三方 API）

### v2.0（1 月后）
- [ ] 舆情分析（情感分析）
- [ ] 用户画像（地域/设备）
- [ ] 自动优化建议

---

## 相关文件

- 官方文档：https://developers.weixin.qq.com/doc/offiaccount/Analysis/
- 配置路径：`~/.openclaw/wechat-mp/config.json`
- Token 缓存：`/tmp/wechat-mp-token.json`

---

## 许可证

MIT-0 License
