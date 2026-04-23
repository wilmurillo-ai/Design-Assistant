# dynamic-webfetch

动态网页抓取技能 - 使用 Playwright 支持 JavaScript 渲染的网页内容抓取

## 安装

```bash
# 安装技能
clawhub install dynamic-webfetch

# 安装依赖
pip install playwright
playwright install chromium
```

## 快速开始

```python
result = main({
    "action": "fetch",
    "url": "https://m.cngold.org/quote/gjs/jjs_hj9999.html",
    "format": "text",
    "wait_seconds": 5
})
```

## 文档

详见 [SKILL.md](./SKILL.md)
