# GitHub Collaborative Development System - 项目结构

## 📁 完整目录树

```
/workspace/gitwork/
├── 📁 src/                          # 源代码目录 (47 个 JS 文件)
│   ├── 📁 core/                     # 核心模块 (6 个文件)
│   │   ├── main-controller.js       # 主控制器
│   │   ├── agent-binding.js         # Agent 绑定
│   │   ├── openclaw-message.js      # 消息处理
│   │   ├── dev-agent.js             # 开发 Agent
│   │   ├── test-agent.js            # 测试 Agent
│   │   └── task-manager-enhanced.js # 增强任务管理
│   │
│   ├── 📁 db/                       # 数据库管理模块 (15 个文件 + 1 个数据库)
│   │   ├── README.md                # 数据库说明
│   │   ├── init.js                  # 数据库初始化
│   │   ├── database-manager.js      # 数据库管理器
│   │   ├── config-manager.js        # 配置管理
│   │   ├── config-sync.js           # 配置同步
│   │   ├── agent-manager.js         # Agent 管理
│   │   ├── agent-health-manager.js  # Agent 健康监控
│   │   ├── task-manager.js          # 任务管理
│   │   ├── task-dependency-manager.js # 任务依赖管理
│   │   ├── task-priority-manager.js # 任务优先级管理
│   │   ├── task-distribution-manager.js # 任务分发管理
│   │   ├── project-manager.js       # 项目管理
│   │   ├── session-validator.js     # 会话验证
│   │   ├── performance-monitor.js   # 性能监控
│   │   └── github-collab.db         # 统一数据库 (94KB)
│   │
│   ├── 📁 scripts/                  # 脚本工具 (16 个文件)
│   │   ├── README.md                # 脚本说明
│   │   ├── main.js                  # 主脚本
│   │   ├── cli-commands.js          # CLI 命令
│   │   ├── agent-assign.js          # Agent 分配
│   │   ├── agent-queue.js           # Agent 队列
│   │   ├── config-cli.js            # 配置 CLI
│   │   ├── project-manager.js       # 项目管理 CLI
│   │   ├── task-breakdown.js        # 任务分解
│   │   ├── task-cli.js              # 任务 CLI
│   │   ├── update-agent.js          # Agent 更新
│   │   ├── scheduler.js             # 调度器
│   │   ├── validate-config.js       # 配置验证
│   │   ├── init-db.js               # 数据库初始化
│   │   ├── sync-config.js           # 配置同步
│   │   └── progress-report.js       # 进度报告
│   │
│   ├── 📁 tests/                    # 测试用例 (2 个文件)
│   │   ├── test-database.js         # 数据库测试
│   │   └── test-cache.js            # 缓存测试
│   │
│   ├── index.js                     # 主入口
│   ├── config.js                    # 配置
│   ├── db.js                        # 数据库封装
│   ├── db-optimized.js              # 优化数据库
│   ├── cache.js                     # 缓存
│   ├── logger.js                    # 日志
│   └── utils.js                     # 工具函数
│
├── 📁 memory/                       # 记忆归档
│   └── archives/                    # 历史归档
│
├── 📁 references/                   # 引用资源
│
├── package.json                     # 项目配置
├── README.md                        # 项目说明
├── SKILL.md                         # Agent 技能说明
├── CONFIG.md                        # 配置说明
├── DATABASE_MIGRATION.md            # 数据库迁移说明
├── .gitignore                       # Git 忽略规则
├── .gitattributes                   # Git 属性配置
└── .gitconfig                       # 项目 Git 配置
```

## 📊 模块统计

### 文件统计
| 目录 | 文件数 | 说明 |
|------|--------|------|
| src/core/ | 6 | 核心控制模块 |
| src/db/ | 15 | 数据库管理模块 |
| src/scripts/ | 16 | 脚本工具 |
| src/tests/ | 2 | 测试用例 |
| 其他 | 6 | 配置文件和入口 |
| **总计** | **45** | JavaScript 文件 |

### 数据库统计
- **统一数据库**: `github-collab.db` (94KB)
- **表数量**: 12 个表
- **数据记录**:
  - agents: 4 条
  - configs: 1 条
  - 其他表：待填充

## 🗂️ 功能模块划分

### 1. 核心控制模块 (core/)
- **main-controller.js** - 总控主进程
  - Agent 启动/停止控制
  - 并行数量管理
  - 任务调度
  - 崩溃恢复
  
- **agent-binding.js** - Agent 绑定管理
  - Agent 地址配置
  - Agent 状态跟踪
  
- **openclaw-message.js** - 消息处理
  - 消息收发
  - 消息格式转换
  
- **dev-agent.js** - 开发 Agent
  - 代码编写
  - 功能实现
  
- **test-agent.js** - 测试 Agent
  - 单元测试生成
  - 集成测试
  
- **task-manager-enhanced.js** - 增强任务管理
  - 任务优先级
  - 任务依赖
  - 任务分发

### 2. 数据库管理模块 (db/)
- **数据库层**
  - database-manager.js - 数据库管理器
  - init.js - 数据库初始化
  
- **配置管理**
  - config-manager.js - 配置管理
  - config-sync.js - 配置同步
  
- **Agent 管理**
  - agent-manager.js - Agent 管理
  - agent-health-manager.js - 健康监控
  
- **任务管理**
  - task-manager.js - 任务管理
  - task-dependency-manager.js - 依赖管理
  - task-priority-manager.js - 优先级管理
  - task-distribution-manager.js - 分发管理
  
- **项目管理**
  - project-manager.js - 项目管理
  
- **其他**
  - session-validator.js - 会话验证
  - performance-monitor.js - 性能监控

### 3. 脚本工具 (scripts/)
- **CLI 工具**
  - cli-commands.js - CLI 命令
  - config-cli.js - 配置 CLI
  - task-cli.js - 任务 CLI
  - project-manager.js - 项目管理 CLI
  
- **Agent 工具**
  - agent-assign.js - Agent 分配
  - agent-queue.js - Agent 队列
  - update-agent.js - Agent 更新
  
- **任务工具**
  - task-breakdown.js - 任务分解
  
- **系统工具**
  - scheduler.js - 调度器
  - validate-config.js - 配置验证
  - init-db.js - 数据库初始化
  - sync-config.js - 配置同步
  - progress-report.js - 进度报告

## 🛠️ 技术栈

### 核心依赖
- **better-sqlite3** - SQLite 数据库
- **qqbot** - QQ 机器人
- **dotenv** - 环境变量
- **commander** - CLI 框架

### 开发规范
- **代码风格**: ESLint + Prettier
- **测试**: Jest
- **文档**: Markdown
- **版本控制**: Git

## 📝 开发规范

### 文件命名
- 小写 + 连字符：`task-manager.js`
- 类名：大驼峰 `TaskManager`
- 数据库表：小写 + 下划线 `task_dependencies`

### 代码组织
- 模块按功能分离
- 单一职责原则
- 依赖注入模式

### 数据库规范
- 统一使用 `github-collab.db`
- 表名使用复数形式
- 外键约束完整
- 索引优化查询

## 🔄 数据库迁移历史

### 2026-03-27
- 合并 4 个数据库为 1 个
- 统一表结构
- 保留所有数据

详见：[DATABASE_MIGRATION.md](./DATABASE_MIGRATION.md)
