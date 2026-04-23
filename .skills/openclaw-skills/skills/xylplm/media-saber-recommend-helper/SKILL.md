---
name: media-saber-recommend-helper
description: 通过 Media Saber MCP 生成带有结构化过滤器和可解释选择的电影和电视推荐。
---

# Media Saber 推荐助手

在推荐场景中使用此技能。

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
  - 用途：所有推荐查询和数据获取

### 所需网络/文件访问
- **配置文件修改**：`~/.claw/mcpServers.json`
  - 用途：存储 Media Saber MCP 端点配置
  - 访问类型：读和写
  - 操作：OpenClaw 安装时自动配置（需用户确认）

### 数据隐私
- 所有查询参数和推荐结果仅在本地处理
- API Key 从不发送至第三方
- 推荐历史不上报

### ⚠️ 信任验证与最小权限

与外部端点交互时正常执行以下步骤，确保最小权限不超预期：

**1. API Key 最小权限原则**
- 需求介于想要接入的是什么 Media Saber 功能（推荐查询等）
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

## 主要工具

- recommend_movies(country?, sort?, tag?, year?)
- recommend_tvs(country?, sort?, tag?, year?)
- get_tmdb_info(tmdbId, mediaType)

## 推荐策略

1. 向用户询问媒体类型和偏好维度。
2. 将偏好转换为工具过滤器。
3. 调用 recommend_movies 或 recommend_tvs。
4. 使用 get_tmdb_info 补充热门选择。
5. 返回简明的候选列表并说明理由。

## 防护措施

- 将过滤值保持在服务器允许的枚举集内。
- 如果用户给出不支持的值，映射到空值（全部）并解释。
- 切勿暴露授权令牌。
