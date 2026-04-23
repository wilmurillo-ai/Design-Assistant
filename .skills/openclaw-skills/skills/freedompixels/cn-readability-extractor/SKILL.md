name: 网页内容提取器
description: 输入任意网页URL，提取干净正文（去除广告/导航/脚本），支持标题/描述/正文分离，可用于内容整理/知识库构建/SEO分析。
version: "1.0.0"
entry: scripts/readability.py
install: ""

scope:
  - 从URL提取干净正文
  - 去除广告、导航栏、脚本、样式
  - 提取页面标题和meta描述
  - 中英文网页均支持
  - 显示字数统计

env: []
test: |
  python3 scripts/readability.py https://example.com

example:
  input: "python readability.py https://news.ycombinator.com/item?id=1"
  output: "📄 标题 + 正文内容 + 字数统计"
