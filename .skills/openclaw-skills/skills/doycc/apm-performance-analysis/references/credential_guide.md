# 凭证配置详细指南

本文档是 SKILL.md 的补充参考，包含腾讯云凭证的完整配置步骤。

## 凭证用途

腾讯云凭证（SecretId / SecretKey）用于 MCP Server 认证。`mcp_client.py` 自动从 `.env` 读取凭证并通过 HTTP header（`secretId` / `secretKey`）传递给 MCP Server。

## 配置步骤

### 步骤 1：创建 .env 文件

将 `assets/.env.example` 模板复制到用户项目根目录：

```bash
cp <skill_base_dir>/assets/.env.example /path/to/project/.env
```

### 步骤 2：填入真实凭证

编辑 `.env` 文件，将占位符替换为真实值：

```ini
# .env 文件内容（占位符示例，禁止写入真实值到代码文件）
TENCENTCLOUD_SECRET_ID=<your_secret_id>
TENCENTCLOUD_SECRET_KEY=<your_secret_key>
TENCENTCLOUD_REGION=ap-guangzhou
```

> **安全警告**: 在任何代码文件、文档、日志输出或对话交互中，一律使用 `<your_secret_id>` / `<your_secret_key>` 占位符，**绝不输出真实密钥内容**。

### 步骤 3：设置文件权限

```bash
chmod 600 .env
```

脚本加载 `.env` 时会自动检查权限，若检测到其他用户有读取权限会输出安全警告。

### 步骤 4：防止提交到版本控制

```bash
echo ".env" >> /path/to/project/.gitignore
echo "logs/" >> /path/to/project/.gitignore
```

## .env 文件查找顺序

1. 命令行参数 `--env-file` 显式指定的路径
2. 环境变量 `APM_ENV_FILE` 指定的路径
3. 当前工作目录下的 `.env`
4. 脚本所在目录的上级目录下的 `.env`

## 支持的 .env 变量

| 变量名 | 必填 | 说明 |
|-------|------|------|
| `APM_MCP_SSE_URL` | 否 | MCP SSE Server 地址，不设置则使用内置默认地址 |
| `APM_MCP_TIMEOUT` | 否 | MCP 连接超时（秒），默认 `30` |
| `APM_MCP_SSE_READ_TIMEOUT` | 否 | MCP SSE 读取超时（秒），默认 `300` |
| `APM_VENV_DIR` | 否 | 自定义虚拟环境目录路径，不设置则为 `./.apm-venv/` |
| `TENCENTCLOUD_SECRET_ID` | 是 | 腾讯云 API SecretId（通过 HTTP header 传递给 MCP Server） |
| `TENCENTCLOUD_SECRET_KEY` | 是 | 腾讯云 API SecretKey（通过 HTTP header 传递给 MCP Server） |
| `TENCENTCLOUD_REGION` | 否 | 默认地域，不设置则为 `ap-guangzhou` |
| `APM_ERROR_LOG_DIR` | 否 | 错误日志目录，不设置则为 `./logs/` |
| `APM_ENV_FILE` | 否 | 自定义 .env 文件路径 |

## 安全强制规则

1. **禁止硬编码**: 任何代码中不得出现真实的 SecretId 或 SecretKey 值。
2. **占位符引用**: 在文档、示例代码、终端输出中，必须使用占位符。
3. **权限控制**: `.env` 文件必须 `chmod 600`。
4. **版本控制排除**: `.env` 必须加入 `.gitignore`。
5. **日志脱敏**: 错误日志不记录密钥值，日志文件权限 `600`。
6. **对话安全**: 用户提供密钥明文时不得回显，应提示通过 `.env` 配置并建议更换已暴露密钥。
