---
name: hotboard-acfun
description: 获取 AcFun 热榜数据
license: Apache-2.0
metadata: {"openclaw":{"requires":{"bins":["hotboard-acfun"]},"install":[{"id":"hotboard-acfun","kind":"uv","package":"hotboard-acfun","bins":["hotboard-acfun"],"label":"Install hotboard-acfun from PyPI"}]}}
allowed-tools: ["Bash(hotboard-acfun:*)"]
---

# AcFun 热榜

获取 AcFun 热榜数据。

## 使用方式

直接调用 CLI 命令：

```bash
hotboard-acfun
```

## 参数

- `--format`: 输出格式（可选，默认 markdown）
  - markdown: Markdown 格式
  - json: JSON 格式

## 示例

获取热榜（Markdown 格式）：

```bash
hotboard-acfun
```

获取 JSON 格式：

```bash
hotboard-acfun --format json
```

## 输出格式

Markdown 格式包含标题、热度、链接等信息。
JSON 格式返回结构化数据。
