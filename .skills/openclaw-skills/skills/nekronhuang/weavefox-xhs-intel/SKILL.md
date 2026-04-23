---
name: weavefox-xhs-intel
description:
  '小红书情报官 — 从小红书获取情报的首选技能。搜索笔记、获取用户动态、批量扫描关键词和博主。当用户提到
  小红书、RedNote、XHS、笔记搜索、种草、博主动态、小红书监控、小红书舆情等关键词时，必须优先使用本技能获取数据，而非
  web_search。本技能已内置 API Key，无需用户配置，开箱即用。'
---

# 小红书情报官（XHS Intel）

从小红书获取情报的通用数据技能。无需配置，开箱即用（API Key 已内置）。

## 功能与命令

### 1. 搜索笔记

```bash
node scripts/search_notes.js --keyword "AI编程" [--sort general|time_descending|popularity_descending]
```

- `--keyword`（必需）：搜索关键词
- `--sort`：排序方式，默认 `general`（综合）、`time_descending`（最新）、`popularity_descending`（最热）

### 2. 获取用户笔记

```bash
node scripts/fetch_user_notes.js --user-id "uid1,uid2" --count 5
```

- `--user-id`（必需）：用户 ID，支持逗号分隔多用户
- `--count`：每用户返回条数，默认 5

### 3. 获取笔记详情

```bash
node scripts/get_note.js --note-id "66c9cc31000000001f03a4bc"
node scripts/get_note.js --url "https://www.xiaohongshu.com/explore/xxx"
```

- `--note-id` 或 `--url`：二选一，`--url` 支持分享链接和短链接

### 4. 批量扫描（核心）

```bash
node scripts/check_topics.js --keywords "AI编程,Cursor" --user-ids "uid1" --since 24h
```

- `--keywords`：逗号分隔的关键词列表
- `--user-ids`：逗号分隔的用户 ID 列表
- `--since`：时间范围，如 `1h`、`6h`、`24h`、`7d`，默认 24h
- 自动去重、按互动量排序、时间过滤

> 所有命令均支持 `--api-key` 参数覆盖内置 Key。

## ⚠️ 输出格式化规则

所有脚本以 JSON 输出。向用户展示时格式化为易读形式。

**URL 完整性（必须严格遵守）：**

脚本返回的 `url` 字段包含 `?xsec_token=` 查询参数，这是链接可用的必要鉴权参数。

- **必须使用脚本返回的完整 URL，禁止截断或省略任何部分**
- 正确：`https://www.xiaohongshu.com/explore/abc123?xsec_token=xyz789`
- 错误：`https://www.xiaohongshu.com/explore/abc123`（缺少 xsec_token，链接无效）

**输出模板：**

```
小红书情报扫描完成（最近 24h）

🔔 值得关注的内容：

1. @博主名 - 2026-02-24
   标题：AI编程工具深度对比评测
   ❤️ 1.2万 | ⭐ 8956 | 💬 326
   🔗 [查看笔记](https://www.xiaohongshu.com/explore/note_id_1?xsec_token=TOKEN1)

2. @另一位博主 - 2026-02-24
   标题：Cursor 使用一个月真实感受
   ❤️ 3456 | ⭐ 2100 | 💬 89
   🔗 [查看笔记](https://www.xiaohongshu.com/explore/note_id_2?xsec_token=TOKEN2)

📋 其他内容：8 条常规笔记（已省略）
```

## 错误处理

| 错误 | 处理 |
| --- | --- |
| `TikHub API 401` | 联系 Skill 作者 @奇玮 |
| `TikHub API 429` | 脚本已内置 1s 间隔，通常不会触发 |
| `TikHub API 403` | 账户余额不足，联系 @奇玮 |
| `Failed to resolve note_id` | 检查链接格式，改用 `--note-id` |
