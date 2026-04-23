# 安装指南

## 📋 系统要求

- Node.js >= 14.0.0
- npm >= 6.0.0
- SQLite3 支持（通过 better-sqlite3 自动安装）

## 🚀 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/openclaw/github-collab.git
cd github-collab
```

### 2. 安装依赖

```bash
npm install
```

### 3. 验证安装

```bash
npm test
```

## 📦 依赖说明

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| better-sqlite3 | ^9.0.0 | SQLite 数据库操作 |

### 可选依赖

| 包名 | 用途 |
|------|------|
| axios | HTTP 请求（GitHub API） |
| ws | WebSocket 通信 |
| dotenv | 环境变量管理 |

## ⚙️ 配置步骤

### 1. 创建配置文件

```bash
cp .env.example .env
```

### 2. 编辑环境变量

编辑 `.env` 文件：

```env
# GitHub 配置
GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_username

# Agent 配置
DEV_AGENT_COUNT=2
TEST_AGENT_COUNT=1
REVIEW_AGENT_COUNT=1

# 日志配置
LOG_LEVEL=info

# QQ 通知（可选）
QQ_ENABLED=false
QQ_TOKEN=your_qq_token
QQ_TARGET=your_qq_target
```

### 3. 创建项目配置

创建 `core/.github-collab-config.json`：

```json
{
  "github": {
    "token": "your_token",
    "owner": "your_username"
  },
  "agents": {
    "dev_count": 2,
    "test_count": 1,
    "review_count": 1
  },
  "logging": {
    "level": "info"
  },
  "max_parallel_agents": 3
}
```

## 🔧 常见问题

### 问题 1: better-sqlite3 安装失败

**解决方案：**

```bash
# 安装 Python 和构建工具
sudo apt-get install python3 build-essential

# 重新安装
npm install better-sqlite3
```

### 问题 2: 数据库文件权限错误

**解决方案：**

```bash
# 修改数据库文件权限
chmod 666 github-collab.db
```

### 问题 3: Agent 无法启动

**解决方案：**

1. 检查配置文件是否正确
2. 检查环境变量是否设置
3. 查看日志文件：`core/controller-state.json`

## 📝 安装检查清单

- [ ] Node.js 已安装（版本 >= 14.0.0）
- [ ] npm 已安装（版本 >= 6.0.0）
- [ ] 依赖已安装（`npm install` 成功）
- [ ] 环境变量已配置（`.env` 文件存在）
- [ ] 项目配置已创建（`core/.github-collab-config.json`）
- [ ] 测试通过（`npm test` 成功）

## 🎯 下一步

安装完成后，参考 [README.md](README.md) 开始使用：

```bash
# 运行示例
npm run example

# 启动主控制器
npm start
```

## 📞 技术支持

如有问题，请提交 Issue 或联系 OpenClaw 社区。
