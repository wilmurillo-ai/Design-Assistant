---
name: slonaide
description: Query and manage SlonAide voice recording notes - list recordings, get transcriptions and AI summaries.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - SLONAIDE_API_KEY
      bins:
        - curl
    primaryEnv: SLONAIDE_API_KEY
    emoji: "\U0001F399"
    homepage: https://h5.aidenote.cn/
---

# SlonAide 录音笔记

管理 SlonAide 录音笔记：查询列表、获取转写文本和 AI 总结。使用 `exec` 工具运行 curl 命令调用 SlonAide API。

## 认证流程

SlonAide 使用两步认证：先用 API Key 换取 Token，再用 Token 调用业务接口。

### 获取 Token

```bash
curl -s -X POST "https://api.aidenote.cn/api/userapikeyMstr/getToken/$SLONAIDE_API_KEY" \
  -H "Content-Type: application/json"
```

成功返回：
```json
{
  "code": 200,
  "result": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "userId": "13000000001xx"
  }
}
```

提取 `result.token`，后续所有请求携带 Header：`Authorization: Bearer <token>`

Token 有效期约 7 天。返回 401 或认证失败时重新获取。

## 操作

### 获取录音笔记列表

```bash
curl -s -X POST "https://api.aidenote.cn/api/audiofileMstr/audiofileseleUserAllList" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order": "descending",
    "orderField": "createTime",
    "page": 1,
    "pageSize": 10
  }'
```

可选：请求体加 `"keyword": "搜索词"` 进行关键词搜索。

返回字段说明：
- `result.items`：笔记数组
- `result.total`：总条数
- 每条笔记关键字段：
  - `audiofileFileid`：文件 ID（字符串），用于获取转写详情
  - `audiofileTitle`：标题
  - `audiofileFileName`：文件名
  - `createTime`：创建时间（格式 `"2026-02-28 20:27:08"`）
  - `audiofileTimeLength`：时长（毫秒）
  - `audiofileTranscription`：转写状态（0=未开始, 1=进行中, 2=已完成）
  - `audiofileSummaryStatus`：总结状态（0=未开始, 1=进行中, 2=已完成）
  - `audiofileText`：转写文本（列表中可能为 null）
  - `audiofileSummary`：AI 总结文本
  - `audiofileTag`：标签

### 获取录音转写详情

用列表中的 `audiofileFileid` 获取完整转写：

```bash
curl -s -X POST "https://api.aidenote.cn/api/audiofileMstr/audiofileToText" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "audiototextFileid": "<audiofileFileid>",
    "audiototextLanguage": "zh"
  }'
```

参数：
- `audiototextFileid`：必填，从列表的 `audiofileFileid` 获取
- `audiototextLanguage`：语言，默认 `"zh"`

返回的转写分段包含：
- `audiototextContent`：该段文本
- `audiototextParaNum`：段落号
- `audiototextStartSecond` / `audiototextEndSecond`：时间范围（秒）
- `audiototextRoleName`：说话人

## 输出格式

列表展示：
```
📋 SlonAide 录音笔记（共 N 条）

1. [标题]
   时间：[createTime]  时长：[X分X秒]
   转写：[✅ 已完成 / ⏳ 未开始]  总结：[✅ 已完成 / ⏳ 未开始]
```

转写详情：按段落顺序拼接 `audiototextContent`，标注说话人。

## 错误处理

- Token 获取失败（code != 200）：提示检查 API Key
- 业务接口返回 401：Token 过期，重新获取
- 网络失败：提示检查网络
- 列表为空：告知暂无录音笔记

## 配置

用户需在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "skills": {
    "entries": {
      "slonaide": {
        "enabled": true,
        "env": {
          "SLONAIDE_API_KEY": "sk-你的API密钥"
        }
      }
    }
  }
}
```

API Key 获取：访问 https://h5.aidenote.cn/ → 登录 → 我的 → API Key → 生成访问密钥。
