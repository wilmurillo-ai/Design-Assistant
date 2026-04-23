---
name: dynamic-webfetch
description: 动态网页抓取工具 - 使用 Playwright 支持 JavaScript 渲染的网页内容抓取
version: 1.0.0
author: 鸭鸭 (Yaya)
license: MIT
tags:
  - web
  - fetch
  - playwright
  - dynamic
  - scraper
  - real-time
emoji: 🌐
---

# Dynamic Web Fetch Skill

支持 JavaScript 动态加载的网页内容抓取工具，使用 Playwright 无头浏览器。

## 特点

- 🚀 **支持动态加载** - 执行 JavaScript，等待页面完全渲染
- 🎯 **智能等待** - 可配置等待时间或等待特定元素
- 📝 **多格式输出** - 支持 Markdown、文本、HTML 格式
- 🔍 **元素提取** - 可选择性提取特定 CSS 选择器的内容
- 📸 **截图支持** - 可选保存页面截图
- ⚡ **快速加载** - 使用 DOMContentLoaded 策略，加快页面加载

## 依赖

```bash
pip install playwright
playwright install chromium
```

## 使用方法

### 基本用法

```python
result = main({
    "action": "fetch",
    "url": "https://example.com",
    "format": "text",
    "wait_seconds": 3
})
```

### 高级用法

```python
result = main({
    "action": "fetch",
    "url": "https://m.cngold.org/quote/gjs/jjs_hj9999.html",
    "format": "text",
    "wait_selector": ".price",
    "wait_seconds": 5,
    "screenshot": "/tmp/gold-price.png"
})
```

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | 是 | 操作类型：`fetch` |
| url | string | 是 | 目标 URL |
| format | string | 否 | 输出格式：`markdown`/`text`/`html`，默认 `markdown` |
| wait_seconds | int | 否 | 等待时间（秒），默认 3 |
| wait_selector | string | 否 | CSS 选择器，等待该元素出现 |
| screenshot | string | 否 | 截图保存路径（可选） |
| user_agent | string | 否 | 自定义 User-Agent |
| timeout | int | 否 | 页面加载超时时间（毫秒），默认 30000 |

## 输出格式

```json
{
    "success": true,
    "url": "https://...",
    "title": "页面标题",
    "format": "text",
    "content": "页面内容...",
    "timestamp": "2026-04-09T08:00:00Z"
}
```

## 示例

### 示例 1：抓取实时金价

```python
result = main({
    "action": "fetch",
    "url": "https://m.cngold.org/quote/gjs/jjs_hj9999.html",
    "format": "text",
    "wait_seconds": 5
})

if result["success"]:
    print(result["content"])
```

### 示例 2：抓取并截图

```python
result = main({
    "action": "fetch",
    "url": "https://finance.sina.com.cn/",
    "format": "markdown",
    "wait_seconds": 3,
    "screenshot": "/tmp/sina-finance.png"
})
```

### 示例 3：等待特定元素

```python
result = main({
    "action": "fetch",
    "url": "https://quote.eastmoney.com/globalfuture/au9999.html",
    "format": "text",
    "wait_selector": ".quote-price",
    "wait_seconds": 8
})
```

## 命令行用法

```bash
# JSON 模式
echo '{"url": "https://example.com", "wait_seconds": 5}' | python3 scripts/fetch.py

# 命令行模式
python3 scripts/fetch.py https://example.com text 5
```

## 注意事项

1. 首次运行需要安装 Playwright 和浏览器：`pip install playwright && playwright install chromium`
2. 动态页面加载时间较长，建议设置合理的 wait_seconds（3-8 秒）
3. 部分网站可能有反爬虫机制，建议设置合适的 User-Agent
4. 截图功能会增加执行时间
5. 东方财富等网站可能有反爬，建议使用金投网等替代源

## 推荐数据源

| 网站 | URL | 说明 |
|------|-----|------|
| 金投网 | https://m.cngold.org/quote/gjs/jjs_hj9999.html | AU9999 实时行情 ✅ |
| 上海黄金交易所 | https://www.sge.com.cn/ | 官方数据 |
| 新浪财经 | https://finance.sina.com.cn/ | 财经新闻 |

---

_动态，但稳定。_ 🦆
