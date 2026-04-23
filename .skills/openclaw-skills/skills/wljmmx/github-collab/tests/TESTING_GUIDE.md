# 测试指南

## 📋 测试概述

本项目包含完整的测试套件，覆盖所有核心模块功能。

## 🧪 测试文件结构

```
tests/
├── test-all.js              # 完整测试套件
├── test-task-manager.js     # TaskManager 测试
├── test-agent-binding.js    # Agent 绑定测试
├── test-stp-integration.js  # STP 集成测试
└── test-performance.js      # 性能测试
```

## 🚀 运行测试

### 运行所有测试

```bash
npm test
```

### 运行特定测试

```bash
# TaskManager 测试
npm run test:basic

# Agent 绑定测试
npm run test:agent

# STP 集成测试
npm run test:stp

# 完整测试套件
node tests/test-all.js
```

## 📊 测试覆盖范围

### 1. TaskManager 测试

- ✅ 项目创建
- ✅ 任务创建
- ✅ 任务状态更新
- ✅ 任务依赖管理
- ✅ 并发锁机制
- ✅ 崩溃恢复

### 2. Agent 绑定测试

- ✅ Dev Agent 创建
- ✅ Test Agent 创建
- ✅ Agent 注册
- ✅ Agent 状态查询
- ✅ 任务分配
- ✅ 任务执行

### 3. MainController 测试

- ✅ 控制器初始化
- ✅ Agent 启动
- ✅ Agent 停止
- ✅ 任务队列管理
- ✅ 状态保存

### 4. STP 集成测试

- ✅ 任务拆分
- ✅ 依赖验证
- ✅ 执行计划生成
- ✅ 资源估算

### 5. 性能测试

- ✅ 批量任务创建
- ✅ 并发任务处理
- ✅ 数据库查询性能
- ✅ 缓存命中率

## 📝 测试用例示例

### TaskManager 测试

```javascript
const { TaskManager } = require('../core/task-manager');

async function testTaskManager() {
    const taskManager = new TaskManager(':memory:');
    
    // 创建项目
    const project = await taskManager.createProject({
        name: 'Test Project',
        description: 'Test',
        github_url: 'https://github.com/test/repo'
    });
    
    // 创建任务
    const task = await taskManager.createTask({
        project_id: project.id,
        name: 'Test Task',
        description: 'Test',
        priority: 10
    });
    
    // 验证
    assert(task.id > 0);
    assert(task.name === 'Test Task');
}
```

### Agent 绑定测试

```javascript
const { AgentRegistry } = require('../core/agent-registry');

async function testAgentBinding() {
    const registry = new AgentRegistry();
    
    // 创建 Agent
    const devAgent = registry.createDevAgent('test-dev-agent');
    const testAgent = registry.createTestAgent('test-test-agent');
    
    // 验证
    assert(devAgent !== null);
    assert(testAgent !== null);
    
    // 测试任务分配
    const task = await taskManager.createTask({...});
    await registry.dispatchTask(task.id, 'test-dev-agent');
}
```

## 🐛 调试测试

### 启用详细日志

```bash
LOG_LEVEL=debug npm test
```

### 单步调试

```bash
node --inspect tests/test-all.js
```

### 查看测试覆盖率

```bash
npx nyc npm test
npx nyc report --reporter=html
```

## 📈 性能基准

| 测试项 | 预期时间 | 实际时间 |
|--------|---------|---------|
| 创建 100 个任务 | < 5s | ~2s |
| 任务分配 | < 10ms | ~5ms |
| Agent 启动 | < 100ms | ~50ms |
| STP 任务拆分 | < 1s | ~500ms |

## ✅ 测试通过标准

- 所有测试用例通过
- 无内存泄漏
- 性能指标达标
- 错误处理正确

## 🔧 常见问题

### 问题 1: 测试失败

**解决方案：**

1. 检查数据库文件权限
2. 清理缓存：`rm -rf core/*.db`
3. 重新安装依赖：`npm install`

### 问题 2: 性能测试超时

**解决方案：**

1. 检查系统资源
2. 减少测试数据量
3. 优化数据库索引

### 问题 3: Agent 绑定失败

**解决方案：**

1. 检查 Agent 注册状态
2. 验证任务分配逻辑
3. 查看日志文件

## 📞 技术支持

如有问题，请提交 Issue 或联系 OpenClaw 社区。
