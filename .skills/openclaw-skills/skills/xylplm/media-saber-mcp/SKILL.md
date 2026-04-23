---
name: media-saber-mcp
description: Media Saber 完整MCP工具集（28个工具）用于订阅、站点操作、推荐、云任务和系统检查。已针对OpenClaw和兼容客户端优化。
---

# Media Saber MCP 技能

这是 Media Saber MCP 的基础完整能力技能。

## 🔐 安全性和权限声明

本技能需要以下权限和凭证，确保完全透明：

### 所需凭证
- **MCP_ENDPOINT_URL**: Media Saber MCP 服务的实际地址
  - 示例：`http://localhost:22698/message`
  - 敏感性：**低**（地址通常是内部网络或已知地址）
  - 用途：连接到 Media Saber MCP 服务

- **API_KEY**: 用于验证与 Media Saber MCP 服务的连接
  - 存储位置：OpenClaw 环境变量或配置文件
  - 敏感性：**高**（不会在日志中显示）
  - 用途：所有 MCP 工具调用和操作

### 所需网络/文件访问
- **配置文件修改**：`~/.claw/mcpServers.json`
  - 用途：存储 Media Saber MCP 端点配置
  - 访问类型：读和写
  - 操作：OpenClaw 安装时自动配置（需用户确认）

### 数据隐私
- 所有 MCP 操作在 Media Saber 系统内执行
- API Key 从不发送至第三方
- 操作日志存储在本地

### ⚠️ 信任验证与最小权限

与外部端点交互时正常执行以下步骤，确保最小权限不超预期：

**1. API Key 最小权限原则**
- 需求介于想要接入的是 MCP 的功能(订阅、可下载、推荐等)
- 尽可能用于整个系统管理专用 API 密钥
- 不需要提供其他系统访问权限

**2. 端点信任**
- 校验端点是可信的（例如你拥有的属于团队的作地）
- 不要接入未知组织的远程端点
- 使用 HTTPS、验证证书等安全配置

**3. 配置文件保护**
- `~/.claw/mcpServers.json` 配置了你的整个端点信息，包含了敏感的 API 密钥
- 每次都要确保文件的文件权限（推荐：600）
- 定期更新、旋转 API 密钥

## ⚠️ 必须配置：连接配置

**使用此技能前，您必须配置以下信息**：

### 1. MCP 地址配置（需要用户填写）

- **transport**: `streamable-http`
- **url**: `<MCP_ENDPOINT_URL>` （例如：http://localhost:22698/message 或你的其他部署地址）
- **需要用户填写实际的 MCP 服务地址**

### 2. 认证信息配置（需要用户填写）

**请在以下位置之一配置您的 API_KEY**：

#### 方式 A：OpenClaw 配置（推荐）

在 `~/.claw/mcpServers.json` 中配置 Media Saber 连接：

```json
{
  "mcpServers": {
    "MediaSaber": {
      "transport": "streamable-http",
      "url": "http://localhost:22698/message",
      "headers": {
        "Authorization": "Bearer sk-YOUR_API_KEY_HERE"
      }
    }
  }
}
```

**替换 `sk-YOUR_API_KEY_HERE` 为您的实际 API 密钥**

#### 方式 B：环境变量配置

- 设置环境变量：`MEDIA_SABER_API_KEY=sk-your-api-key`
- 该密钥将被自动注入到请求头中

### 3. 获取 API_KEY

请从 Media Saber 系统获取您的 API 密钥：
- 访问 Media Saber Web 界面
- 进入 "设置" → "API 密钥"
- 复制您的密钥（通常以 `sk-` 开头）

**安全提示**：
- ⚠️ **切勿将 API_KEY 硬编码在代码、提示词或文档中**
- ⚠️ **切勿通过不安全的通道传输 API_KEY**
- ⚠️ **定期轮换您的 API_KEY**
- ⚠️ **不要与他人共享您的 API_KEY**

## 该技能可以做什么

- 搜索和检查 TMDB 媒体数据。
- 使用结构化参数订阅电影和电视内容。
- 刷新订阅并检查缺失的剧集。
- 运行站点签到、同步数据/通知/消息和诊断。
- 触发磁力/ed2k 和115转移链接的云任务。
- 查询媒体服务器并运行库同步。
- 运行系统网络和极空间检查。

## 工具契约规则

- 仅使用服务器公开的工具名称。
- 精确执行必需的参数。
- 对于推荐工具中的枚举式过滤器，仅传递允许的值。
- 将无参数工具视为无参数调用。

## 建议的默认工作流

**订阅工作流**:

1. search_tmdb(query, mediaType)
2. 用户确认候选项
3. subscribe_movie 或 subscribe_tv
4. refresh_subscribe
5. get_media_status

**站点操作工作流**:

1. get_sites/get_site_data
2. site_sign_in
3. sync_site_data/sync_site_notice/sync_site_message
4. today_site_data/total_site_data
5. 如需要运行 test_site/test_site_rss

**推荐工作流**:

1. 选择 recommend_movies 或 recommend_tvs
2. 应用过滤器（country/sort/tag/year）
3. 用 get_tmdb_info 补充热门选择

**云任务工作流**:

1. 验证链接类型
2. add_offline_download 或 cloud_share_receive
3. 清晰返回任务响应

## 安全规则

- 切勿打印API密钥或授权值。
- 在日志和示例中屏蔽敏感令牌。
- 当用户意图不清楚时，为有写入影响的操作请求确认。

## 配套技能

对于聚焦场景，还可使用：

- media-saber-subscribe-assistant
- media-saber-site-ops
- media-saber-recommend-helper
- media-saber-cloud-assistant

详细参数和示例见: docs/tool-reference.md
