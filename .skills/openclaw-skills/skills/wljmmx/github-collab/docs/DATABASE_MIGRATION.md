# 数据库迁移说明

## 迁移日期
2026-03-27

## 迁移内容
将 4 个独立的 SQLite 数据库合并为 1 个统一的数据库文件。

### 迁移前
- `agents.db` - Agent 相关数据
- `config.db` - 配置数据
- `github-collab.db` - 主数据库
- `tasks.db` - 任务数据（空文件）

### 迁移后
- `github-collab.db` - 统一数据库（包含所有表）

### 保留的表
1. **agents** - Agent 信息 (4 条记录)
2. **agent_configs** - Agent 配置
3. **message_logs** - 消息日志
4. **tasks** - 任务信息
5. **task_assignments** - 任务分配
6. **task_history** - 任务历史
7. **configs** - 系统配置 (1 条记录)
8. **config** - 配置表（备用）
9. **task_dependencies** - 任务依赖
10. **projects** - 项目信息
11. **performance_metrics** - 性能指标
12. **sessions** - 会话管理

### 数据完整性
- ✅ 所有数据已完整迁移
- ✅ 表结构已统一
- ✅ 无数据丢失

## 数据库文件
- **位置**: `/workspace/gitwork/src/db/github-collab.db`
- **大小**: 94KB
- **格式**: SQLite 3

## 后续操作
- 更新代码中的数据库路径引用
- 删除旧数据库文件
- 更新文档说明
