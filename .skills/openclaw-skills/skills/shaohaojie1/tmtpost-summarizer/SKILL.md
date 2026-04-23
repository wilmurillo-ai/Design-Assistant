---
name: tmtpost-summarizer
description: 钛媒体（https://www.tmtpost.com/）文章阅读与资讯总结助手。支持四种模式：(1) 读取最新文章并深度总结；(2) 从快报频道汇总当前最新十条热点资讯；(3) 关键词过滤模式；(4) 指定URL直接总结；(5) 多篇横向对比分析。触发词：帮我看钛媒体、钛媒体快报、最新十条、关键词XX的钛媒体、总结这篇钛媒体、钛媒体对比。
---

# 钛媒体文章总结器

读取钛媒体最新文章或快报资讯，用专业科技媒体风格撰写结构化中文总结。支持四种模式。

## 四种模式

### 模式 A：最新文章深度总结（默认）

当用户说"帮我看钛媒体"、"总结 tmtpost"、"读一下这篇"时触发。

**步骤：**
1. `web_fetch url="https://www.tmtpost.com/" extractMode="markdown" maxChars=5000`
2. 从返回内容中找到最新文章 URL（时间最接近当前的文章）
3. `web_fetch url="<文章URL>" extractMode="markdown" maxChars=20000`
4. 按 `references/prompt-template.md` 单篇文章格式撰写总结

### 模式 B：最新十条快报汇总

当用户说"钛媒体快报"、"最新十条"、"快报"时触发。

**步骤：**
1. `web_fetch url="https://www.tmtpost.com/nictation" extractMode="markdown" maxChars=15000`
2. 可叠加 `web_fetch url="https://www.tmtpost.com/fm" extractMode="markdown" maxChars=5000`
3. 提取当前最新十条条目，按时间倒序
4. 按快报汇总格式输出

### 模式 C：关键词过滤快报

当用户说"关键词XX的钛媒体快报"、"只看我关注XX的钛媒体"时触发。

**步骤：**
1. 从用户 prompt 中提取关键词（可能有多个，用顿号、空格或逗号分隔）
2. 抓取 `/nictation`（如需更全可叠加 `/` 首页）
3. **在返回内容中搜索所有包含关键词的条目**，精确匹配或语义相关均可
4. 如关键词为多条，先按相关度排序，再按时间倒序
5. 输出时在每条目前标注匹配的关键词

> **关键词支持示例：**
> - "AI、半导体的钛媒体快报"
> - "人形机器人、新能源"
> - "美团、字节"

### 模式 D：指定 URL 直接总结

当用户粘贴了具体文章 URL（`https://www.tmtpost.com/数字.html`）时触发。

**步骤：**
1. 直接 `web_fetch url="<用户提供的URL>" extractMode="markdown" maxChars=20000`
2. 按单篇文章格式输出总结

### 模式 E：多篇横向对比分析

当用户提供多个 URL、或说"钛媒体对比"、"横向对比"时触发。

**步骤：**
1. 抓取所有文章正文
2. 读取 `references/prompt-template.md` 中的**对比分析格式**
3. 输出一份结构化对比报告

## 脚本工具

```bash
# 最新文章 URL
./scripts/fetch-article.sh [max_articles]

# 快报（近十天）
./scripts/fetch-nictation.sh

# 搜索含关键词的快报（支持多词，逗号分隔）
./scripts/search-nictation.sh "AI,人形机器人"
```

## 错误处理

- 抓取失败 → 换用 `/new` 页面或重试
- 内容为空 → 不硬凑，换关键词或换数据源
- 关键词匹配为空 → 告知用户该关键词近期无内容，列出最接近的条目

## 触发词

| 模式 | 触发词 |
|------|--------|
| A 文章总结 | "帮我看钛媒体"、"总结 tmtpost"、"钛媒体最新" |
| B 最新十条 | "钛媒体快报"、"最新十条"、"快报" |
| C 关键词过滤 | "AI的钛媒体快报"、"人形机器人关键词" |
| D 指定URL | 直接粘贴文章链接 |
| E 多篇对比 | "钛媒体对比"、"横向对比分析" |
