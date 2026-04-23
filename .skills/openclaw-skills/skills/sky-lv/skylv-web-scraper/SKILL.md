---
name: web-scraper
description: Web content extraction tool. Scrapes URLs and extracts text, links, and images with CSS selectors and regex. Triggers: web scraping, content extraction, crawler, html parsing.
metadata: {"openclaw": {"emoji": "🕷️"}}
---

# Web Scraper — 网页内容抓取工具

## 功能说明

从网页抓取并解析内容，支持多种提取方式。

## 使用方法

### 1. 抓取网页全文

```
用户: 抓取 https://example.com 的内容
```

执行步骤：
1. 使用 `web_fetch` 工具抓取URL
2. 返回markdown格式的正文内容

### 2. 提取特定元素

```
用户: 从 https://news.ycombinator.com 提取所有新闻标题
```

执行步骤：
1. 使用 `web_fetch` 抓取页面
2. 分析HTML结构，识别标题元素
3. 提取并列表返回

### 3. 批量抓取

```
用户: 抓取以下URL列表的内容：
https://url1.com
https://url2.com
https://url3.com
```

执行步骤：
1. 遍历URL列表
2. 依次调用 `web_fetch`
3. 汇总结果

### 4. 提取链接

```
用户: 提取 https://example.com 页面中的所有外链
```

执行步骤：
1. 抓取页面内容
2. 解析所有 `<a href>` 标签
3. 过滤出外链（域名不同的链接）
4. 列表返回

## 示例对话

**用户**: 抓取 https://github.com/trending 今天的热门项目

**Agent**:
1. 调用 `web_fetch` 抓取 GitHub Trending 页面
2. 解析项目列表（仓库名、描述、star数）
3. 格式化输出：

```
今日 GitHub 热门项目：

1. owner/repo-name - 项目描述
   ⭐ 1,234 stars today | 📝 JavaScript

2. ...
```

## 注意事项

- 遵守 robots.txt
- 添加适当延迟避免被封
- 处理反爬机制（User-Agent、Cookie等）
- 大规模抓取建议使用代理

## 依赖

- `web_fetch` 工具（OpenClaw内置）
- 无需额外安装
