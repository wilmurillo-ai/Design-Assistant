# TTPOS MCP Skill for OpenClaw

TTPOS 餐饮收银系统的 OpenClaw 技能包，通过 MCP 协议连接 TTPOS 后端，实现营业数据查询、订单管理、采购建议等能力。

## 首次使用（推荐）

直接对 AI 说「帮我查今天营业额」等，当 AI 提示「请提供你的 TTPOS 用户名和密码」时，输入账号密码即可，AI 会自动完成配置。

## 安装方式

### 方式一：手动安装

```bash
# 复制到 OpenClaw 技能目录
cp -r ttpos-mcp ~/.openclaw/workspace/skills/

# 配置 mcporter（首次需指定 MCP 地址）
mcporter config add ttpos --url https://你的TTPOS域名/api/v1/ai/mcp

# 认证：告诉 AI 你的用户名和密码，或手动运行
bash scripts/setup_auth.sh 用户名 密码 https://你的TTPOS域名
```

### 方式二：ClawHub 安装（发布后）

```bash
clawhub install ttpos-mcp
openclaw skills check
```

## 依赖

- [mcporter](https://www.npmjs.com/package/mcporter) - MCP 服务器连接工具
- 可访问的 TTPOS 服务实例
- TTPOS 店铺账号（用于获取 JWT Token）

## 文件说明

| 文件 | 说明 |
|------|------|
| SKILL.md | 技能定义（元数据 + 配置说明 + 工具清单） |
| README.md | 本说明文件 |

## 相关链接

- [OpenClaw 官网](https://openclawlab.com/)
- [ClawHub 技能中心](https://clawhub.ai/)
- [MCP 协议](https://modelcontextprotocol.io/)
