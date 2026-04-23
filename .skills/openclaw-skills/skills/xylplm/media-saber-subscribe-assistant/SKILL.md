---
name: media-saber-subscribe-assistant
description: 通过 Media Saber MCP 处理端到端订阅工作流，包括 tmdb 搜索、精确订阅操作和刷新。
---

# Media Saber 订阅助手

当用户想要通过 Media Saber MCP 订阅电影或电视剧时使用此技能。

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
  - 用途：所有订阅、查询等操作

### 所需网络/文件访问
- **配置文件修改**：`~/.claw/mcpServers.json`
  - 用途：存储 Media Saber MCP 端点配置
  - 访问类型：读和写
  - 操作：OpenClaw 安装时自动配置（需用户确认）

### 数据隐私
- 所有查询和订阅数据仅在 Media Saber 系统内处理
- API Key 从不发送至第三方
- 操作日志存储在本地

### ⚠️ 信任验证与最小权限

与外部端点交互时正常执行以下步骤，确保最小权限不超预期：

**1. API Key 最小权限原则**
- 需求介于想要接入的是什么 Media Saber 功能（生产空间或测试空间）
- 尽可能用于数据查看专用 API 密钥
- 不需要提供完整系统管理权限

**2. 端点信任**
- 校验端点是可信的（例如你拥有的属于团队的作地）
- 不要接入未知组织的远程端点
- 使用 HTTPS、验证证书等安全配置

**3. 配置文件保护**
- `~/.claw/mcpServers.json` 配置了你的整个端点信息，包含了敏感的 API 密钥
- 每次都要确保文件的文件权限（推荐：600）
- 定期更新、旋转 API 密钥

## ⚠️ 必须配置：MCP 服务连接

在使用此技能前，**您必须配置以下信息**：

### 1. MCP 地址配置（需要用户填写）

- **transport**: `streamable-http`
- **endpoint**: `<MCP_ENDPOINT_URL>` （例如：http://localhost:22698/message 或你的其他部署地址）
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

- 设置环境变量：`API_KEY=sk-your-api-key`
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

## 主要工具

- search_tmdb(query, mediaType)
- subscribe_movie(tmdbId)
- subscribe_tv(tmdbId, season, beginEpisode?, episodes?)
- refresh_subscribe()
- get_media_status(tmdbId, mediaType)
- get_miss_episodes()

## 工作流

1. 使用 search_tmdb 查找候选内容。
2. 当存在多个候选项时，要求用户确认确切目标。
3. 使用严格的参数调用 subscribe_movie 或 subscribe_tv。
4. 立即调用 refresh_subscribe。
5. 使用 get_media_status 报告最终状态。

## 防护措施

- 不要猜测 tmdbId。
- 未经用户意图确认，不要订阅。
- 切勿暴露授权令牌。
