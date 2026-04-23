---
name: volcengine-search
description: 使用火山引擎进行联网搜索问答。
---

## 脚本调用说明

本工具会向 `https://open.feedcoopapi.com` 发起网络请求。

### 1. 前置准备

请将 API Key 配置在系统的环境变量中：
```bash
export VOLC_SEARCH_API_KEY="your_api_key_here"
```

### 2. 调用方式 (CLI)
您可以直接在终端运行 `scripts/volcengine_search.py` 脚本进行快捷搜索测试。
```bash
python scripts/search_web.py -q <搜索词> [-t <搜索类型>] [-k <API_Key>]
```

**参数列表：**
- `-q` 或 `--query`：**必填**，想要搜索的关键词或问题。需要用双引号包裹以防空格截断。
- `-t` 或 `--type`：选填，搜索类型。默认为 `web`。支持以下两种：
  - `web`：常规网页搜索。默认选这个。
  - `web_summary`：网页搜索并附带大模型总结版。
- `-k` 或 `--key`：选填，手动传入 API Key。如果不传，脚本默认读取 `VOLC_SEARCH_API_KEY` 环境变量。

**调用示例：**
```bash
# 执行一次普通的网页搜索
python scripts/search_web.py -q "北京市这周末的天气"

# 执行带有大模型智能总结的搜索
python scripts/search_web.py -q "2026年量子计算的最新商业化进展" -t web_summary
```

### 3. 返回值说明 (Return Value)
核心函数 `volcengine_web_search` 返回的是一个解析好的 Python 字典 (`dict`)，其结构与火山引擎 API 的 JSON 响应一致。主要包含以下关键信息：
- `WebItem`: 包含多个网页或图片搜索的具体结果条目（标题、URL、摘要）。
- `Choice`: 若使用了 `web_summary` 模式，此处将包含大模型针对搜索结果生成的直接回答。
- `SearchContext`: 当前搜索的上下文标识信息。
```