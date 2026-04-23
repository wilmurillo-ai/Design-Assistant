---
name: news-api-aggregator
version: 1.0.0
description: Aggregate news from multiple sources into a unified API. Each call charges 0.001 USDT via SkillPay.
category: News
tags:
  - news
  - aggregator
  - API
  - multi-source
author: moson
price: 0.001
currency: USDT
triggers:
  - "news aggregator"
  - "multi-source news"
  - "news API"
  - "unified news"
config:
  NEWSAPI_KEY:
    type: string
    required: false
    secret: true
---

# News API Aggregator

## 功能

- 聚合多个新闻源的数据
- 统一格式输出
- 支持关键词搜索
- 过滤和排序选项

## 使用方法

```json
{
  "query": "Bitcoin",
  "sources": ["reuters", "bloomberg", "coindesk"],
  "limit": 10
}
```

## 输出

```json
{
  "success": true,
  "count": 10,
  "articles": [
    {"title": "...", "source": "reuters", "url": "...", "publishedAt": "..."}
  ]
}
```

## 定价

每次调用: 0.001 USDT
