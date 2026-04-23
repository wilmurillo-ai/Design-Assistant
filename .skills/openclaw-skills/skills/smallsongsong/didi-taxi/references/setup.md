# DiDi MCP Server 安装配置指南

本文档说明如何安装和配置 DiDi MCP Server，以便使用 didi-taxi skill。

## 1. 安装 mcporter

mcporter 是用于调用 MCP Server 的命令行工具。

```bash
npm install -g mcporter
```

验证安装：
```bash
mcporter --version
```

## 2. 获取 API Key

访问 https://mcp.didichuxing.com/api?tap=api 获取您的 API Key，或扫描下方二维码直达官网注册页面。

![DiDiMCP 注册二维码](https://s3-yspu-cdn.didistatic.com/mcp-web/qrcode/didi_skills_code.png)


## 3. 配置环境变量

使用环境变量配置 API Key：

```bash
export DIDI_MCP_KEY="YOUR_MCP_KEY"
```

在 `~/.zshrc` 或 `~/.bashrc` 中添加持久化配置。

## 4. 验证连接

设置 MCP_URL 变量：
```bash
export MCP_URL="https://mcp.didichuxing.com/mcp-servers?key=$DIDI_MCP_KEY"
```

测试地址解析功能：
```bash
mcporter call "$MCP_URL" maps_textsearch --args '{"keywords":"西二旗地铁站","city":"北京市"}'
```

测试价格预估功能：
```bash
mcporter call "$MCP_URL" taxi_estimate --args '{"from_lng":"116.322","from_lat":"39.893","from_name":"北京西站","to_lng":"116.482","to_lat":"40.004","to_name":"首都机场"}'
```

## 5. Claude Code 配置（可选）

如果使用 Claude Code，确保在 Claude Code 的 MCP 配置中添加了 didi-mcp 服务：

```json
{
  "mcpServers": {
    "didi-mcp": {
      "transport": "http",
      "url": "https://mcp.didichuxing.com/mcp-servers?key=YOUR_MCP_KEY"
    }
  }
}
```

## 6. OpenClaw 配置

如果使用 OpenClaw，还需要以下配置：

- 确保已安装 `openclaw` CLI
- 验证 mcporter 已安装：`which mcporter`
- 若未找到，执行 `npm install -g mcporter` 后重新验证

## 常见问题

**Q: API Key 无效**
A: 请检查 API Key 是否正确，以及是否已启用相应权限

**Q: 调用超时**
A: 检查网络连接，稍后重试

**Q: 地理位置限制**
A: 部分功能仅支持中国大陆地区
