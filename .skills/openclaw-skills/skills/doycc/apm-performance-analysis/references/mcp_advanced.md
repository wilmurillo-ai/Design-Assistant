# MCP 高级用法

本文档包含 MCP 客户端的连接参数、凭证认证、程序化调用、交互式模式、桥接文档生成和协议通信流程等完整参考。

## SSE 连接参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `APM_MCP_SSE_URL` | MCP Server 的 SSE 端点地址 | `https://mcp.tcop.woa.com/apm-console/sse` |
| `APM_MCP_TIMEOUT` | 连接超时（秒） | `30` |
| `APM_MCP_SSE_READ_TIMEOUT` | SSE 读取超时（秒） | `300` |

## 凭证认证

MCP Server 通过 HTTP header（`secretId` / `secretKey`）进行凭证认证，`mcp_client.py` 自动从 `.env` 或环境变量中读取凭证并附加到 SSE 连接。也可通过 `--secret-id` / `--secret-key` 命令行参数显式覆盖。

> 凭证格式、优先级和配置步骤详见 `references/credential_guide.md`

## 协议通信流程

```
客户端                                 MCP Server (SSE)
  │                                        │
  │──── SSE 连接建立 ──────────────────────►│
  │     (header: secretId, secretKey)       │
  │◄─── endpoint URL ─────────────────────│
  │                                        │
  │──── initialize (JSON-RPC) ────────────►│
  │◄─── InitializeResponse ──────────────│
  │                                        │
  │──── tools/list (JSON-RPC) ────────────►│
  │◄─── ToolListResponse ───────────────│
  │                                        │
  │──── tools/call (JSON-RPC) ────────────►│
  │       tool_name + arguments            │
  │◄─── CallToolResponse ───────────────│
  │       content (text/data)              │
  │                                        │
  │──── 关闭连接 ──────────────────────────►│
```

## 工具发现与动态调用

MCP Server 暴露的工具列表是**动态的**，可能随服务器端更新而变化。每次执行运维操作前，建议先调用 `list-tools` 获取最新工具列表。每个工具包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | String | 工具唯一标识名称 |
| description | String | 工具功能描述 |
| inputSchema | Object | JSON Schema 格式的参数定义 |

工具调用结果包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| content | Array | 返回内容列表（通常包含 text 类型数据） |
| isError | Boolean | 是否调用失败 |

## 交互式模式（开发调试用）

```bash
python scripts/venv_manager.py run scripts/mcp_client.py interactive
```

## 生成 OpenClaw 桥接文档

```bash
# 输出到终端
python scripts/venv_manager.py run scripts/mcp_client.py generate-bridge

# 输出到文件
python scripts/venv_manager.py run scripts/mcp_client.py generate-bridge --output-file mcp_tools_doc.md
```

## 程序化调用（Python）

在 Python 代码中直接调用 MCP 客户端函数（需在虚拟环境中运行）：

```python
import asyncio
import sys
sys.path.insert(0, "<skill_base_dir>/scripts")
from mcp_client import list_mcp_tools, call_mcp_tool, get_mcp_url, get_mcp_headers, load_env

# 加载 .env 配置
load_env()
mcp_url = get_mcp_url()

# 构造认证 headers（自动从 .env 或环境变量获取凭证）
headers = get_mcp_headers()

# 列出可用工具（通过 headers 传递凭证）
tools = asyncio.run(list_mcp_tools(mcp_url, headers=headers))
for tool in tools:
    print(f"工具: {tool['name']} - {tool['description']}")
    schema = tool.get("inputSchema", {})
    required = schema.get("required", [])
    for param, info in schema.get("properties", {}).items():
        req_label = "必填" if param in required else "可选"
        print(f"  - {param} ({req_label}): {info.get('description', '')}")

# 调用指定工具（通过 headers 传递凭证）
result = asyncio.run(call_mcp_tool(mcp_url, "<tool_name>", {"param": "value"}, headers=headers))
if result["success"]:
    print(f"结果: {result['content']}")
else:
    print(f"失败: {result['content']}")
```

## 自定义 MCP Server 地址

```bash
# 通过命令行参数
python scripts/venv_manager.py run scripts/mcp_client.py --mcp-url https://your-mcp-server/sse list-tools

# 通过 .env 文件
# APM_MCP_SSE_URL=https://your-mcp-server/sse
```

## OpenClaw 集成工作流

由于 OpenClaw 尚未原生支持 MCP 协议，本 skill 通过 `mcp_client.py` 提供桥接层：

1. AI 加载本 skill → 识别用户 APM 运维意图
2. 确保虚拟环境就绪 → `python scripts/venv_manager.py ensure`
3. **确保凭证就绪** → 检查 `.env` 中是否包含 `TENCENTCLOUD_SECRET_ID` 和 `TENCENTCLOUD_SECRET_KEY`
4. 发现可用工具 → `list-tools`（凭证自动通过 header 传递给 MCP Server）
5. 根据用户需求选择工具 → 分析工具描述和参数（区分必填/可选）
6. **多功能工具交互确认** → 若工具支持多种功能，先向用户展示可用功能并确认；收集参数时优先从上下文提取，缺失的再询问用户
7. 执行运维操作 → `call-tool`（凭证自动通过 header 传递）
8. 解读结果 → 提供运维建议

## MCP 客户端错误码

| 错误码 | 描述 |
|-------|------|
| MCP_SDK_NOT_INSTALLED | MCP SDK 未安装，需执行 `pip install mcp httpx` |
| MCP_CONNECTION_FAILED | 无法连接到 MCP Server，检查网络和地址 |
| MCP_TOOL_ERROR | MCP 工具执行返回错误 |
| MCP_TIMEOUT | 连接或调用超时 |
