---
name: xia-zhua-zhua
description: 将任意网页抓取并保存为 Markdown 文件（中文名：虾抓抓）。使用 Playwright + Turndown 引擎，支持所有网页。触发条件：用户要求抓取网页、网页转 markdown、clip 网页、虾抓抓。
---

# 虾抓抓 - 网页转 Markdown（v2.1.3）

## 使用方式

```bash
# 单个网页（标准模式）
node markdown-clip.js <url> [输出目录]

# Smart 模式（Readability AI 内容识别）
node markdown-clip.js <url> [输出目录] --smart

# 抓取 + 自动分析（摘要/关键词/洞察）
node markdown-clip.js <url> [输出目录] --analyze

# 批量并发抓取
node batch-clip.js <url文件> [并发数] [输出目录]

# 查看配置和抓取历史
node markdown-clip.js --config
node markdown-clip.js --log
node markdown-clip.js --set outputDir /path
```

## v2.1.2 新功能：自动抓取后分析

```bash
node markdown-clip.js <url> --analyze
```

抓取完成后自动分析文章，生成：

| 分析维度 | 说明 |
|---------|------|
| **摘要** | TextRank 算法提取的 3-5 句核心内容 |
| **关键词** | 高频主题词（5个） |
| **关键洞察** | 含数据/结论/重要观点的句子 |
| **统计** | 字数、句子数、预计阅读时间 |

分析结果追加到 markdown 文件末尾。

## v2.1 Smart 模式

```
node markdown-clip.js <url> --smart
```

**「教它识字」**——用 Readability 算法自动识别主内容区域，不依赖预设 CSS 选择器。

| 模式 | 原理 | 适用场景 |
|------|------|---------|
| **标准模式** | CSS 选择器预设列表 | 大多数常规网站 |
| **Smart 模式** | Readability 算法自动判断"这里是正文" | 从未抓过的陌生网站 |

## Clip Log

记录文件：`~/.clips/clips.json`

```json
{
  "https://mp.weixin.qq.com/s/xxxxx": {
    "url": "https://mp.weixin.qq.com/s/xxxxx",
    "path": "C:/Users/262/Desktop/2026-04-17-mp-weixin-标题.md",
    "title": "文章标题",
    "clippedAt": "2026-04-17T03:30:00.000Z"
  }
}
```

## 反爬措施

- 随机 User-Agent（4种浏览器）
- 隐藏 `navigator.webdriver` 标志
- 随机等待 1~3s 模拟人类访问节奏
- 加载失败自动降级重试
- WeChat 二维码区域自动过滤

## 依赖

- playwright
- turndown
- python + readability-lxml（Smart 模式）
- python + scikit-learn（分析模式，可选，有则用 TF-IDF TextRank，无则降级）

## 发布（维护者用）

```bash
clawhub publish . --slug xia-zhua-zhua --version 2.1.3 --no-input
```
