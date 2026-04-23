---
name: zhipu-tools-coding-plan
description: 智谱 AI 原生工具 - 网络搜索、网页读取、仓库文档搜索和文件解析。基于 Z.AI Coding Plan MCP 端点，全部免费使用。
license: MIT
---

# 智谱工具 Coding Plan (Zhipu Tools)

基于 **Z.AI Coding Plan MCP 端点** 的免费工具集：网络搜索、网页读取、GitHub 仓库文档搜索和文件解析。

## 功能

| 功能 | MCP 工具 | 端点 | 说明 |
|------|----------|------|------|
| **网络搜索** | `web_search_prime` | `/web_search_prime/mcp` | 实时互联网搜索，支持过滤 |
| **网页读取** | `webReader` | `/web_reader/mcp` | 抓取网页标题、正文、元数据 |
| **仓库文档搜索** | `search_doc` | `/zread/mcp` | 搜索 GitHub 仓库文档 |
| **仓库目录结构** | `get_repo_structure` | `/zread/mcp` | 查看 GitHub 仓库目录树 |
| **仓库文件读取** | `read_file` | `/zread/mcp` | 读取 GitHub 仓库指定文件 |
| **文件解析** | — | Legacy API | 解析 PDF/Word/Excel/PPT 等 |

> 前五项通过 Coding Plan MCP 端点免费调用，文件解析仅支持旧版 API。

## 配置

在 `openclaw.json` 中配置 API Key：

```json
{
  "skills": {
    "entries": {
      "zhipu-tools": {
        "apiKey": "YOUR_ZHIPU_API_KEY"
      }
    }
  }
}
```

或设置环境变量：`ZHIPU_API_KEY`

### MCP vs Legacy 模式

| 模式 | 端点 | 额度 | 切换方式 |
|------|------|------|----------|
| **MCP (默认)** | `api.z.ai/api/mcp/...` | Z.AI Coding Plan 免费 | 默认启用 |
| Legacy | `open.bigmodel.cn/api/paas/v4/...` | 账户余额 | `ZHIPU_USE_MCP=false` |

MCP 模式自动 fallback：MCP 失败时会自动尝试 Legacy API。

## 使用方式

### 网络搜索 (web_search_prime)

```bash
cd ~/.openclaw/workspace/skills/zhipu-tools

# Shell
./scripts/web_search.sh "搜索关键词" [count]

# Python（支持更多参数）
python3 scripts/zhipu_tool.py web_search "搜索关键词" \
  --count 10 --recency week --domain example.com
```

### 网页读取 (webReader)

```bash
# Shell
./scripts/web_reader.sh "https://www.example.com"

# Python
python3 scripts/zhipu_tool.py web_reader "https://www.example.com"
```

### GitHub 仓库文档搜索 (Zread)

```bash
# Shell - 搜索仓库文档
./scripts/zread.sh search "openai/openai" "how to use"

# Shell - 查看目录结构
./scripts/zread.sh structure "openai/openai"
./scripts/zread.sh structure "openai/openai" "src/"

# Shell - 读取文件
./scripts/zread.sh read "openai/openai" "README.md"

# Python
python3 scripts/zhipu_tool.py zread search "openai/openai" "how to use"
python3 scripts/zhipu_tool.py zread structure "openai/openai" --path src/
python3 scripts/zhipu_tool.py zread read "openai/openai" "README.md"
```

### 文件解析 (Legacy only)

```bash
./scripts/file_parser.sh /path/to/document.pdf PDF
python3 scripts/zhipu_tool.py file_parser /path/to/document.docx --file-type DOCX
```

## MCP 工具参数详情

### web_search_prime

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| search_query | string | 是 | 搜索内容，建议不超过 70 字符 |
| search_recency_filter | string | 否 | oneDay, oneWeek, oneMonth, oneYear, noLimit |
| content_size | string | 否 | medium (默认), high |
| location | string | 否 | cn, us |
| search_domain_filter | string | 否 | 限制搜索域名 |

### webReader

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 目标网页 URL |

返回：标题、正文内容、元数据、链接列表。

### search_doc

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| repo | string | 是 | GitHub 仓库，如 "openai/openai" |
| query | string | 是 | 搜索关键词 |

### get_repo_structure

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| repo | string | 是 | GitHub 仓库 |
| path | string | 否 | 子目录路径 |

### read_file

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| repo | string | 是 | GitHub 仓库 |
| path | string | 是 | 文件路径，如 "README.md" |

## MCP 协议

所有远程 MCP 端点通过 streamableHttp 协议交互：

1. **POST initialize** → 响应 header 返回 `mcp-session-id`
2. **POST notifications/initialized** → 通知就绪
3. **POST tools/call** → 调用具体工具

Headers: `Authorization: Bearer $API_KEY`, `Content-Type: application/json`, `Accept: text/event-stream, application/json`

## Coding Plan 套餐额度

| 套餐 | 搜索/网页读取/仓库搜索 次数/月 | 价格 |
|------|:----------------------------:|:----:|
| **Lite** | 100 次 | 免费 |
| **Pro** | 1,000 次 | 免费 |
| **Max** | 4,000 次 | 免费 |

额度次月自动重置。

## 注意事项

- API Key 敏感信息，不要提交到 Git
- Zread（仓库文档搜索）仅支持 MCP 模式
- 文件解析仅支持旧版 API（bigmodel 端点）
- 所有 MCP 工具通过 Coding Plan 免费额度调用
