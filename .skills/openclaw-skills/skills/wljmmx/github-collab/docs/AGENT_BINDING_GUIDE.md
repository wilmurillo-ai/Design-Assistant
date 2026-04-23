# Agent 绑定机制指南

## 📋 概述

本文档说明 GitHub Collaboration 系统中任务分配的 agent 与 OpenClaw agent 之间的关联绑定机制。

## 🏗️ 架构设计

### 核心组件

```
┌─────────────┐
│  OpenClaw   │  ← 用户接口
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│  MainController  │  ← 中枢控制器
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│  AgentRegistry   │  ← Agent 注册表
├──────────────────┤
│  - DevAgent      │
│  - TestAgent     │
│  - ReviewAgent   │
└──────────────────┘
       │
       ↓
┌──────────────────┐
│  TaskManager     │  ← 任务存储
└──────────────────┘
```

## 🔗 绑定机制

### 1. Agent 注册

```javascript
// AgentRegistry 管理所有 Agent 实例
class AgentRegistry {
    constructor() {
        this.agents = new Map(); // agentId -> Agent 实例
    }
    
    register(agentId, agentInstance, agentType) {
        this.agents.set(agentId, agentInstance);
    }
    
    get(agentId) {
        return this.agents.get(agentId);
    }
}
```

### 2. 任务分配流程

```javascript
// MainController.assignTask()
async assignTask(taskId, agentId) {
    // 1. 更新任务状态到数据库
    await this.taskManager.assignTaskToAgent(taskId, agentId);
    
    // 2. 通过 AgentRegistry 调用对应 Agent
    await this.registry.dispatchTask(taskId, agentId);
}
```

### 3. Agent 处理任务

```javascript
// AgentRegistry.dispatchTask()
async dispatchTask(taskId, agentId) {
    const agent = this.get(agentId);
    if (agent) {
        await agent.processTask(taskId);
    }
}

// DevAgent.processTask()
async processTask(taskId) {
    // 获取任务详情
    const task = await this.taskManager.getTask(taskId);
    
    // 验证任务分配
    if (task.assigned_agent !== this.agentId) {
        return false;
    }
    
    // 执行任务
    await this.executeTask(task, { ... });
}
```

## 📝 使用示例

### 创建控制器

```javascript
const { MainController } = require('./core/main-controller');

const controller = new MainController();
await controller.initialize();
```

### 启动 Agent

```javascript
// 启动 Dev Agent
const devAgent = await controller.startAgent('dev', 'my-dev-agent');

// 启动 Test Agent
const testAgent = await controller.startAgent('test', 'my-test-agent');
```

### 创建任务

```javascript
const task = await controller.taskManager.createTask({
    project_id: 1,
    name: 'Implement Feature',
    description: 'Add new feature',
    priority: 10
});
```

### 分配任务

```javascript
// 分配任务给 Dev Agent
await controller.assignTask(task.id, 'my-dev-agent');

// 分配任务给 Test Agent
await controller.assignTask(task.id, 'my-test-agent');
```

## ✅ 验证绑定

### 检查 Agent 注册

```javascript
const registeredAgents = controller.registry.getAll();
console.log('Registered agents:', registeredAgents);
```

### 检查任务状态

```javascript
const taskStatus = await controller.taskManager.getTask(taskId);
console.log('Task status:', taskStatus.status);
console.log('Assigned to:', taskStatus.assigned_agent);
```

### 检查 Agent 状态

```javascript
const agentStatus = await controller.registry.getAgentStatus('my-dev-agent');
console.log('Agent current task:', agentStatus.currentTask);
```

## 🔄 工作流程

1. **用户创建任务** → TaskManager 存储任务
2. **MainController 分配任务** → 更新数据库状态
3. **AgentRegistry 调用 Agent** → 触发 Agent.processTask()
4. **Agent 执行任务** → 更新任务状态
5. **TaskManager 记录日志** → 保存操作历史

## 🎯 关键特性

- ✅ **自动绑定**: 任务分配时自动调用对应 Agent
- ✅ **状态同步**: 数据库和 Agent 实例状态同步
- ✅ **错误处理**: 任务失败时自动重试
- ✅ **日志记录**: 完整记录任务操作历史
- ✅ **并发控制**: 限制并行 Agent 数量

## 🚀 下一步

1. 集成 OpenClaw 消息系统
2. 实现事件驱动架构
3. 添加性能监控
4. 完善错误恢复机制
