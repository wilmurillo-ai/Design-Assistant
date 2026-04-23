---
name: whole-network-search
description: Integrates with the web search API to fetch news and articles from Baidu, Google, or a pre-indexed Elasticsearch database. Use when the user needs to search the web, gather news, find articles by keyword, or retrieve references for research. Supports network mode (real-time crawling) and warehouse mode (ES index search).
metadata: {"openclaw":{"emoji":"🔍"}}
---

# 全网搜索 (Whole Network Search)

This skill guides the agent to call the web search API for retrieving articles and news from multiple sources.

## When to Use

Apply this skill when the user:
- Asks to search the web or gather information online
- Needs news articles or references by keyword
- Wants to retrieve content from Baidu, Google, or a local ES index
- Requires real-time web search or pre-indexed warehouse search

## API Overview

**Endpoint:** `POST /web_search`

**Base URL:** `http://1.95.148.209:9003`

**Authentication:** Required header `X-Appbuilder-Authorization` with API key

## Request

### Headers
| Header | Required | Description |
|--------|----------|-------------|
| X-Appbuilder-Authorization | Yes | API key for authentication |
| Content-Type | Yes | `application/x-www-form-urlencoded` (form data) |

### Form Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| keyword | string | Yes | - | Search keyword |
| search_source | string | No | baidu_search | Engine: `baidu_search`, `google_search`, `baidu_search_ai` |
| mode | string | No | network | `network` = live crawl, `warehouse` = ES index |
| page | int | No | 1 | Page number (starts from 1) |

### Parameter Constraints
- `search_source`: One of `baidu_search`, `google_search`, `baidu_search_ai`
- `mode`: One of `network`, `warehouse`
- When `mode=warehouse`, search is performed against the Elasticsearch index (ignores search_source)
- When `mode=network`, use `search_source` to select Baidu, Google, or Baidu AI search

## Response Format

```json
{
  "code": 200,
  "message": "success",
  "references": [
    {
      "title": "Article title",
      "sourceAddress": "https://example.com/article",
      "origin": "Source name",
      "publishDate": "2025-03-24 12:00:00",
      "summary": "Article summary or snippet"
    }
  ]
}
```

## Usage Examples

### Example 1: Search Baidu news
```
POST http://1.95.148.209:9003/web_search
Headers: X-Appbuilder-Authorization: <api_key>
Body (form): keyword=人工智能&search_source=baidu_search&mode=network&page=1
```

### Example 2: Search Google news
```
POST http://1.95.148.209:9003/web_search
Headers: X-Appbuilder-Authorization: <api_key>
Body (form): keyword=AI&search_source=google_search&mode=network&page=1
```

### Example 3: Search warehouse (ES index)
```
POST http://1.95.148.209:9003/web_search
Headers: X-Appbuilder-Authorization: <api_key>
Body (form): keyword=机器学习&mode=warehouse&page=1
```

### Example 4: cURL
```bash
curl -X POST "http://1.95.148.209:9003/web_search" \
  -H "X-Appbuilder-Authorization: <api_key>" \
  -d "keyword=科技新闻&search_source=baidu_search&mode=network&page=1"
```

## Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 401 | X-Appbuilder-Authorization参数缺失 | Missing auth header |
| 402 | ApiKey错误，请申请ApiKey | Invalid API key |
| 400 | search_source参数错误 | Invalid search_source value |
| 400 | mode参数错误 | Invalid mode value |
| 400 | page参数错误 | Invalid page (non-integer or 0) |

## Integration Steps

1. API base URL: `http://1.95.148.209:9003`，获取 API key 后配置
2. Determine the desired `search_source` (Baidu / Google / Baidu AI) or `mode` (network / warehouse)
3. Call `POST /web_search` with form-encoded parameters
4. Parse `references` from the response and use `title`, `sourceAddress`, `summary` as needed
