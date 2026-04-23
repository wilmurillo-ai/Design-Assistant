# OpenClaw Powpow Skill

将 OpenClaw 数字人发布到 Powpow 地图平台的 Skill。

## 功能

- 📝 在 Powpow 上注册账号（获得 3 个徽章）
- 🤖 创建 AI 数字人并设置人设（消耗 2 个徽章）
- 🗺️ 将数字人发布到真实地图位置
- 💬 让其他用户与数字人对话
- 🗑️ 管理（查看/删除）你的数字人
- ⏰ 数字人有效期 30 天

## 徽章系统

Powpow 使用徽章系统管理资源：
- **注册**: 获得 3 个徽章
- **创建数字人**: 消耗 2 个徽章
- **有效期**: 30 天

## 安装

### 1. 安装 Skill

将 `openclaw-powpow-skill` 文件夹复制到你的 OpenClaw workspace：

```bash
# 找到你的 OpenClaw workspace
# 通常是 ~/.openclaw/workspace/skills/

# 复制 Skill 文件夹
cp -r openclaw-powpow-skill ~/.openclaw/workspace/skills/powpow

# 安装依赖
cd ~/.openclaw/workspace/skills/powpow
npm install
```

### 2. 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

或者发送 `/new` 命令开始新会话。

## 使用方法

### 注册 Powpow 账号

告诉 OpenClaw：
> "帮我在 powpow 上注册一个账号"

提供：
- 用户名（唯一）
- 昵称（可选）
- 头像 URL（可选）

### 创建数字人

告诉 OpenClaw：
> "我要在 powpow 上创建一个数字人"

提供：
- 数字人名称
- 人设描述
- 位置（经纬度或城市名称）
- 头像 URL（可选）
- OpenClaw Gateway URL（如 http://localhost:18789）

### 查看数字人

> "查看我的 powpow 数字人"

### 删除数字人

> "删除 powpow 上的 [数字人名称]"

## 文件结构

```
openclaw-powpow-skill/
├── SKILL.md              # Skill 定义文件
├── README.md             # 本文件
├── package.json          # 依赖配置
├── tsconfig.json         # TypeScript 配置
└── scripts/
    └── powpow-client.ts  # API 客户端脚本
```

## Powpow API 端点

- `POST /api/openclaw/auth/register` - 注册
- `POST /api/openclaw/auth/login` - 登录
- `POST /api/openclaw/digital-humans` - 创建数字人
- `GET /api/openclaw/digital-humans?userId=xxx` - 获取数字人列表
- `DELETE /api/openclaw/digital-humans/[id]` - 删除数字人
- `POST /api/openclaw/chat/send` - 发送消息
- `POST /api/openclaw/webhook/reply` - 接收回复

## 命令行使用

```bash
# 注册
npx tsx scripts/powpow-client.ts register myuser "我的数字人"

# 登录
npx tsx scripts/powpow-client.ts login myuser

# 创建数字人
npx tsx scripts/powpow-client.ts create-agent "小明" "我是一个历史学家" 39.9042 116.4074 "北京" "http://localhost:18789"

# 列出数字人
npx tsx scripts/powpow-client.ts list-agents

# 删除数字人
npx tsx scripts/powpow-client.ts delete-agent <agent-id>

# 查看状态
npx tsx scripts/powpow-client.ts status

# 退出登录
npx tsx scripts/powpow-client.ts logout
```

## 配置存储

Skill 会自动在 `~/.openclaw/powpow-config.json` 中存储：
- 用户名
- JWT Token
- 用户ID
- 徽章数量

## 技术栈

- OpenClaw Skill 系统
- TypeScript
- Next.js (Powpow 后端)
- PostgreSQL + Drizzle ORM
- JWT 认证

## 许可证

MIT

## 支持

- Powpow: https://global.powpow.online
- OpenClaw: https://docs.openclaw.ai
