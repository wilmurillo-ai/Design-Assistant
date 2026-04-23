---
name: apm-performance-analysis
description: "APM 性能分析工具，通过 MCP 桥接连接腾讯云 APM Server，提供业务系统查询、实例详情、性能指标分析、调用链追踪、火焰图查看等能力。Trigger when user mentions APM, 性能分析, application performance, 业务系统, APM 实例, 调用链, 火焰图, Span, 耗时分析, or APM性能分析."
---

# APM 性能分析

通过 MCP（Model Context Protocol）SSE 桥接连接远程 APM MCP Server，自动发现并调用 APM 性能分析工具，实现智能化性能分析与诊断。

## 初始回答规范

用户首次提问（如「能做什么」「有什么功能」）时，按以下要点生成回答：

1. 说明通过 MCP 桥接方式连接远程 APM 性能分析工具
2. 说明需配置腾讯云凭证（SecretId/SecretKey）
3. 末尾以表格形式列出 4–5 条示例引导，至少包含一条「查看 MCP 支持哪些操作」

## 快速开始（虚拟环境）

在隔离虚拟环境中执行所有脚本，避免污染用户全局 Python 环境：

```bash
# 首次使用：创建虚拟环境并安装依赖
python scripts/venv_manager.py ensure

# 后续所有脚本通过 venv_manager.py run 执行
python scripts/venv_manager.py run scripts/mcp_client.py <command>
```

## MCP 工具桥接

**默认 MCP Server**：`https://mcp.tcop.woa.com/apm-console/sse`（可通过 `.env` 中 `APM_MCP_SSE_URL` 覆盖）

### 凭证就绪检查

调用前确保 `.env` 中包含 `TENCENTCLOUD_SECRET_ID` 和 `TENCENTCLOUD_SECRET_KEY`，缺失则引导用户配置。凭证通过 HTTP header 自动传递给 MCP Server。

> 凭证格式、优先级和完整配置步骤见 `references/credential_guide.md`

### 核心命令

```bash
# 列出所有可用工具（凭证自动从 .env 加载，通过 header 传递给 MCP Server）
python scripts/venv_manager.py run scripts/mcp_client.py list-tools --output json

# 调用指定工具（凭证自动从 .env 加载）
python scripts/venv_manager.py run scripts/mcp_client.py call-tool --name <tool_name> --args '{"param1": "value1"}'
```

> 命令行显式传递凭证等高级用法见 `references/mcp_advanced.md`

### 执行流程

1. 确保虚拟环境就绪 → `python scripts/venv_manager.py ensure`
2. 确保凭证就绪 → 检查 `.env` 中 `TENCENTCLOUD_SECRET_ID` 和 `TENCENTCLOUD_SECRET_KEY`，缺失则引导用户配置
3. 发现可用工具 → `list-tools --output json`
4. 按 `references/interaction_guide.md` 格式规范展示工具列表
5. 按 `references/interaction_guide.md` 交互规范与用户确认功能和参数
6. 构造参数并执行 → `call-tool --name <name> --args '{...}'`
7. 解读结果，给出性能分析建议

### 工具调用与展示规范

调用 MCP 工具前，按 `references/interaction_guide.md` 中的交互规范与用户确认功能和参数。核心原则：

1. 不得在未确认功能和参数的情况下直接调用工具
2. 上下文中已有信息优先复用，避免重复询问
3. 可选参数必须列出，敏感参数一律通过 `.env` 配置

展示工具列表时，按 `references/interaction_guide.md` 中的格式规范将 `list-tools` 结果格式化后呈现给用户。

> 高级用法（交互式模式、程序化调用、桥接文档生成）见 `references/mcp_advanced.md`

## 凭证与安全（强制规则）

通过 `.env` 文件管理凭证，模板见 `assets/.env.example`。凭证通过 HTTP header（`secretId` / `secretKey`）自动传递给 MCP Server。

**安全底线（不可违反）**：
1. 禁止硬编码密钥，一律通过 `.env` 或环境变量引用
2. 文档和对话中使用占位符 `<your_secret_id>` / `<your_secret_key>`
3. `.env` 权限 `chmod 600`，加入 `.gitignore`
4. 用户提供密钥明文时不得回显，提示通过 `.env` 配置

> 完整配置步骤见 `references/credential_guide.md`

## 移动端兼容规范（强制规则）

本 skill 需支持用户通过企业微信等移动端远程使用，**全流程不得触发任何需要在电脑 IDE 中手动确认的操作**。以下规则与"凭证与安全"同为最高优先级强制规则，不可违反。

### 禁令 1：禁止创建任何临时文件或脚本

**不得使用 `write_to_file`、`execute_command` 或任何其他方式创建辅助文件**，包括但不限于：

- `/tmp/` 目录下的任何文件（如 `/tmp/parse_spans.py`、`/tmp/data.json`）
- 工作区目录下的临时 `.py`、`.json`、`.sh`、`.txt` 等文件
- 任何用于"数据解析""格式转换""中间处理"目的的脚本或数据文件

### 禁令 2：禁止执行文件删除命令

**不得通过 `execute_command` 执行 `rm`、`rm -f`、`rm -rf`、`del`、`rmdir` 等任何文件删除命令，不得调用 `delete_file` 工具。** 这些操作会被 WorkBuddy 安全机制识别为危险命令（`security.dangerousCommand`），弹出"请在 IDE 中确认"拦截，导致移动端用户流程卡死。

### 禁令 3：MCP 返回数据必须在对话中直接处理

MCP 工具返回的所有数据（无论数据量大小、结构复杂度如何）必须由 AI 在对话消息中直接完成解析和展示，**不得借助外部脚本处理**。具体要求：

- 使用 Markdown 表格展示结构化数据
- 使用代码块展示 JSON 原始数据或关键片段
- 使用缩进列表或树形文本展示层级结构（如 Span 调用树、火焰图）
- 数据量过大时，提取关键摘要信息展示，而非创建脚本做全量处理
- 如需统计分析（如耗时排序、错误率计算），由 AI 直接在回复中计算并呈现结果

### 违规示例（严禁）

```
# 以下行为全部禁止：
write_to_file("/tmp/parse_spans.py", ...)        # 禁止创建临时脚本
execute_command("python /tmp/parse_spans.py")     # 禁止执行临时脚本
execute_command("rm -f /tmp/parse_spans.py ...")  # 禁止删除文件
delete_file("/tmp/data.json")                     # 禁止调用删除工具
```

### 正确做法

```
# MCP 工具返回数据后，直接在对话中处理：
1. 调用 call-tool 获取原始数据
2. AI 解析 JSON 结果，提取关键字段
3. 在回复消息中用 Markdown 表格/树形结构/代码块直接展示
4. 给出性能分析建议和结论
```

## 错误处理

调用失败时错误写入 `./logs/apm_error.log`（JSON 格式，含错误码、RequestId、堆栈信息）。日志文件权限 `600`，不记录密钥。

> 日志格式和排错指引见 `references/error_log_guide.md`

## 调用方式

| 判断条件 | 操作 |
|---------|------|
| MCP Server 可达且凭证已配置 | 正常执行 MCP 工具调用 |
| 凭证未配置 | 引导用户配置 `.env` 文件 |
| MCP 连接失败 | 检查网络和 MCP Server 地址，参考 `references/mcp_advanced.md` 排查 |

## Resources

### scripts/

| 脚本 | 说明 |
|------|------|
| `venv_manager.py` | 虚拟环境管理，所有脚本通过 `run` 命令执行 |
| `mcp_client.py` | MCP SSE 客户端：`list-tools`、`call-tool`、`interactive`、`generate-bridge` |

### references/

| 文档 | 说明 |
|------|------|
| `interaction_guide.md` | 工具调用交互规范（三种场景）和工具列表展示格式 |
| `credential_guide.md` | 凭证配置详细步骤、.env 变量说明、安全规则 |
| `error_log_guide.md` | 错误日志格式、排错指引 |
| `mcp_advanced.md` | MCP 连接参数、协议通信流程、程序化调用、交互式模式、桥接文档生成 |

### assets/

| 文件 | 说明 |
|------|------|
| `.env.example` | `.env` 模板（含 MCP 地址和凭证占位符） |
| `.gitignore.example` | `.gitignore` 模板（排除 `.env` 和 `logs/`） |
