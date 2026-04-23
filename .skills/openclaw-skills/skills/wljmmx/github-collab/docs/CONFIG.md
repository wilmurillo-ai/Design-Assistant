# 配置说明

## 📋 配置方式

系统支持多种配置方式，优先级从高到低：

1. **环境变量** (最高优先级)
2. **配置文件** `.env`
3. **默认配置** (最低优先级)

## 🔧 配置项

### 数据库配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 数据库类型 | `DATABASE_TYPE` | `sqlite` | sqlite, mysql, postgresql |
| 数据库名称 | `DATABASE_NAME` | `github-collab` | 数据库文件名（不含扩展名） |
| 数据库目录 | `DATABASE_DIR` | `./src/db` | 数据库文件存放目录 |
| 数据库路径 | `DATABASE_PATH` | `null` | 完整路径（覆盖上述配置） |
| 连接池大小 | `DATABASE_POOL_SIZE` | `10` | 连接池最大连接数 |
| 查询超时 | `DATABASE_TIMEOUT` | `5000` | 查询超时时间（毫秒） |

### Agent 配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 最大并行数 | `AGENT_MAX_PARALLEL` | `3` | 同时运行的 Agent 数量 |
| 自动恢复 | `AGENT_AUTO_RECOVERY` | `true` | Agent 崩溃后自动重启 |
| 心跳间隔 | `AGENT_HEARTBEAT_INTERVAL` | `30000` | Agent 心跳间隔（毫秒） |

### 日志配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 日志级别 | `LOG_LEVEL` | `info` | debug, info, warn, error |
| 日志目录 | `LOG_DIR` | `./logs` | 日志文件存放目录 |

### 缓存配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 启用缓存 | `CACHE_ENABLED` | `true` | 是否启用缓存 |
| 缓存过期 | `CACHE_TTL` | `300` | 缓存过期时间（秒） |

### QQBot 配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| Token | `QQBOT_TOKEN` | `` | QQBot Token |
| App ID | `QQBOT_APP_ID` | `` | QQBot App ID |
| Secret | `QQBOT_SECRET` | `` | QQBot Secret |

### 项目配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 项目根目录 | `PROJECT_ROOT` | `./` | 项目根目录 |
| 运行环境 | `NODE_ENV` | `development` | development, production, test |

## 📝 配置示例

### 示例 1: 使用默认配置

```bash
# 直接使用默认配置
node src/index.js
```

### 示例 2: 使用环境变量

```bash
# 修改数据库路径
DATABASE_DIR=./custom/db DATABASE_NAME=mydb node src/index.js

# 修改数据库类型
DATABASE_TYPE=postgresql DATABASE_NAME=myapp node src/index.js

# 修改日志级别
LOG_LEVEL=debug node src/index.js
```

### 示例 3: 使用配置文件

1. 复制示例配置文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件：
```env
DATABASE_TYPE=sqlite
DATABASE_NAME=github-collab
DATABASE_DIR=./src/db
LOG_LEVEL=debug
```

3. 启动应用：
```bash
node src/index.js
```

### 示例 4: 指定完整数据库路径

```bash
# 指定绝对路径
DATABASE_PATH=/data/database/github-collab.db node src/index.js
```

## 🔍 验证配置

启动应用后，会显示当前配置信息：

```
📋 配置信息:
  数据库类型：sqlite
  数据库名称：github-collab
  数据库路径：/workspace/gitwork/src/db/github-collab.db
  项目根目录：/workspace/gitwork/
```

## 💡 最佳实践

### 1. 开发环境

```env
# .env.development
DATABASE_TYPE=sqlite
DATABASE_NAME=github-collab-dev
LOG_LEVEL=debug
CACHE_ENABLED=false
```

### 2. 生产环境

```env
# .env.production
DATABASE_TYPE=postgresql
DATABASE_NAME=github-collab-prod
DATABASE_POOL_SIZE=20
LOG_LEVEL=warn
CACHE_ENABLED=true
```

### 3. 测试环境

```env
# .env.test
DATABASE_TYPE=sqlite
DATABASE_NAME=github-collab-test
DATABASE_DIR=./test/db
LOG_LEVEL=error
```

## 🛠️ 配置管理工具

### 查看当前配置

```javascript
const config = require('./src/config');
console.log(config.config);
```

### 获取数据库配置

```javascript
const { getDatabaseConfig } = require('./src/config');
const dbConfig = getDatabaseConfig();
console.log(dbConfig);
```

### 获取数据库路径

```javascript
const { getDatabasePath } = require('./src/config');
const dbPath = getDatabasePath();
console.log(dbPath);
```

## 📚 相关文档

- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 项目结构
- [README.md](./README.md) - 项目说明
- [SKILL.md](./SKILL.md) - Agent 技能说明
